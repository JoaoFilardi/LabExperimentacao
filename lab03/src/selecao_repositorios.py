"""Módulo central de Seleção de Repositórios e Funil de Coleta (LAB03S01).

Responsável pelo papel do Integrante A:
1. Buscar repositórios candidatos populares no GitHub (stars > 1000).
2. Aplicar o funil de seleção em 4 etapas conforme as definições operacionais:
   - Filtro 1: Candidatos brutos
   - Filtro 2: Adoção de GitHub Actions (total_count > 0)
   - Filtro 3: Atividade na janela de 12 meses (>= 5 releases e >= 50 workflow runs válidos)
   - Filtro 4: Amostra qualificada final (meta: 100 repositórios para o S01)
3. Extrair metadados para as RQs (estrelas, linguagem, contribuidores, idade).
4. Gerar datasets estruturados:
   - repositorios_selecionados.csv
   - funil_selecao.csv (tabela agregada do funil)
   - funil_detalhado.csv (auditoria repo a repo)
"""

from __future__ import annotations

import argparse
import csv
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from .cache_manager import CacheManager
from .config import Config, parse_iso_datetime
from .github_client import GitHubClient
from .metricas_ci import VALID_CONCLUSIONS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("selecao_repositorios")


def calculate_age_years(created_at_str: str, reference_date: Optional[datetime] = None) -> float:
    """Calcula a idade do repositório em anos decimais com precisão."""
    created_dt = parse_iso_datetime(created_at_str)
    ref_dt = reference_date or datetime.now(timezone.utc)
    delta_days = (ref_dt - created_dt).total_seconds() / 86400.0
    return round(max(0.0, delta_days / 365.25), 2)


def check_github_actions_workflows(
    client: GitHubClient, owner: str, repo: str
) -> Tuple[bool, int]:
    """Verifica se o repositório usa GitHub Actions via GET /repos/{owner}/{repo}/actions/workflows."""
    cache_key = f"{owner}_{repo}"
    endpoint = f"repos/{owner}/{repo}/actions/workflows"
    data, _ = client.request(
        endpoint,
        cache_category="workflows",
        cache_key=cache_key,
    )
    if not data or not isinstance(data, dict):
        return False, 0

    total_count = data.get("total_count", 0)
    return total_count > 0, total_count


def count_valid_releases_in_window(
    client: GitHubClient,
    owner: str,
    repo: str,
    config: Config,
) -> int:
    """Conta releases publicadas (draft=false, prerelease=false) dentro da janela de 12 meses."""
    cache_key_prefix = f"releases_{owner}_{repo}"
    endpoint = f"repos/{owner}/{repo}/releases"

    # Pagina as releases usando o cliente com cache
    releases = client.paginate(
        endpoint=endpoint,
        params={"per_page": 100},
        max_pages=5,  # 500 releases recentes são mais que suficientes para avaliar a janela
        cache_category="releases",
        cache_key_prefix=cache_key_prefix,
    )

    valid_count = 0
    for rel in releases:
        if not isinstance(rel, dict):
            continue

        # Definição operacional: draft=false e prerelease=false
        if rel.get("draft", False) or rel.get("prerelease", False):
            continue

        published_at_str = rel.get("published_at")
        if not published_at_str:
            continue

        try:
            if config.window.is_in_window(published_at_str):
                valid_count += 1
        except Exception:
            continue

    return valid_count


def count_valid_workflow_runs_in_window(
    client: GitHubClient,
    owner: str,
    repo: str,
    default_branch: str,
    config: Config,
) -> int:
    """Conta workflow runs válidos no default branch disparados por push dentro da janela.

    Conforme Tabela da Seção 3:
    - branch = default_branch
    - event = push
    - conclusion in {success, failure, timed_out, startup_failure}
    - created_at dentro da janela
    """
    cache_key_prefix = f"runs_{owner}_{repo}_{default_branch}"
    endpoint = f"repos/{owner}/{repo}/actions/runs"

    runs = client.paginate(
        endpoint=endpoint,
        params={
            "branch": default_branch,
            "event": "push",
            "per_page": 100,
        },
        max_pages=10,  # até 1000 runs recentes
        cache_category="workflow_runs",
        cache_key_prefix=cache_key_prefix,
    )

    valid_count = 0
    for run in runs:
        if not isinstance(run, dict):
            continue

        # Garante que apenas runs disparados por push sejam contabilizados
        if run.get("event") != "push":
            continue

        conclusion = run.get("conclusion")
        if conclusion not in VALID_CONCLUSIONS:
            continue

        created_at_str = run.get("created_at")
        if not created_at_str:
            continue

        try:
            if config.window.is_in_window(created_at_str):
                valid_count += 1
        except Exception:
            continue

    return valid_count


class FunnelCollector:
    """Executa a coleta e o funil de seleção de repositórios."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.cache = CacheManager(
            config.cache.cache_dir, enabled=config.cache.enabled
        )
        self.client = GitHubClient(
            token=config.github_token,
            base_url=config.api.base_url,
            timeout=config.api.timeout_seconds,
            max_retries=config.api.max_retries,
            backoff_factor=config.api.backoff_factor,
            safety_margin=config.api.rate_limit_safety_margin,
            cache_manager=self.cache,
        )

    def search_candidate_repositories(self, limit: int = 400) -> List[Dict[str, Any]]:
        """Busca repositórios candidatos utilizando fatiamento por estrelas para evitar o teto da API."""
        candidates: List[Dict[str, Any]] = []
        seen_full_names = set()

        for star_slice in self.config.funnel_criteria.star_slices:
            if len(candidates) >= limit:
                break

            query = f"{star_slice} is:public fork:false archived:false"
            logger.info("Buscando candidatos na faixa: %s", star_slice)

            # Busca primeiras 3 páginas (300 resultados por faixa)
            items = self.client.paginate(
                endpoint="search/repositories",
                params={"q": query, "sort": "stars", "order": "desc", "per_page": 100},
                max_pages=3,
                cache_category="search",
                cache_key_prefix=f"search_{star_slice}",
            )

            for repo_item in items:
                if not isinstance(repo_item, dict):
                    continue
                full_name = repo_item.get("full_name")
                if not full_name or full_name in seen_full_names:
                    continue

                seen_full_names.add(full_name)
                candidates.append(repo_item)
                if len(candidates) >= limit:
                    break

        logger.info("Total de repositórios candidatos minerados: %d", len(candidates))
        return candidates

    def process_funnel(
        self,
        target_count: Optional[int] = None,
        candidate_limit: int = 500,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, int]]:
        """Executa a triagem dos repositórios no funil de 4 etapas.

        Retorna:
            - selected_repos: lista de repositórios aprovados com metadados
            - detailed_log: registro completo de todos os repositórios avaliados
            - funnel_counts: contadores de cada etapa
        """
        target = target_count or self.config.funnel_criteria.target_repositories
        candidates = self.search_candidate_repositories(limit=candidate_limit)

        funnel_counts = {
            "1_candidatos": len(candidates),
            "2_com_actions": 0,
            "3_com_releases": 0,
            "4_com_runs": 0,
            "5_selecionados": 0,
        }

        selected_repos: List[Dict[str, Any]] = []
        detailed_log: List[Dict[str, Any]] = []

        logger.info(
            "Iniciando triagem no funil para atingir meta de %d repositórios qualificados...",
            target,
        )

        for idx, repo in enumerate(candidates, 1):
            if len(selected_repos) >= target:
                logger.info("Meta de %d repositórios qualificados atingida!", target)
                break

            owner = repo["owner"]["login"]
            name = repo["name"]
            full_name = repo["full_name"]
            stars = repo.get("stargazers_count", 0)
            language = repo.get("language") or "Unknown"
            default_branch = repo.get("default_branch", "main")
            created_at_str = repo.get("created_at", "")

            # Etapa 2: Checagem de GitHub Actions
            has_actions, total_workflows = check_github_actions_workflows(
                self.client, owner, name
            )
            if not has_actions:
                detailed_log.append({
                    "full_name": full_name,
                    "stars": stars,
                    "language": language,
                    "status": "DESCARTADO",
                    "motivo": "Sem GitHub Actions (total_count = 0)",
                    "total_workflows": 0,
                    "releases_na_janela": 0,
                    "runs_na_janela": 0,
                })
                continue

            funnel_counts["2_com_actions"] += 1

            # Etapa 3.1: Mínimo de 5 releases na janela
            releases_in_window = count_valid_releases_in_window(
                self.client, owner, name, self.config
            )
            if releases_in_window < self.config.funnel_criteria.min_releases:
                detailed_log.append({
                    "full_name": full_name,
                    "stars": stars,
                    "language": language,
                    "status": "DESCARTADO",
                    "motivo": f"Menos de {self.config.funnel_criteria.min_releases} releases na janela ({releases_in_window})",
                    "total_workflows": total_workflows,
                    "releases_na_janela": releases_in_window,
                    "runs_na_janela": 0,
                })
                continue

            funnel_counts["3_com_releases"] += 1

            # Etapa 3.2: Mínimo de 50 workflow runs válidos no default branch
            runs_in_window = count_valid_workflow_runs_in_window(
                self.client, owner, name, default_branch, self.config
            )
            if runs_in_window < self.config.funnel_criteria.min_workflow_runs:
                detailed_log.append({
                    "full_name": full_name,
                    "stars": stars,
                    "language": language,
                    "status": "DESCARTADO",
                    "motivo": f"Menos de {self.config.funnel_criteria.min_workflow_runs} runs válidos na janela ({runs_in_window})",
                    "total_workflows": total_workflows,
                    "releases_na_janela": releases_in_window,
                    "runs_na_janela": runs_in_window,
                })
                continue

            funnel_counts["4_com_runs"] += 1

            # Repositório Aprovado! Coleta de metadados enriquecidos
            age_years = calculate_age_years(created_at_str, self.config.window.end_date)
            contributors_count = self.client.count_contributors(owner, name)

            repo_meta = {
                "owner": owner,
                "name": name,
                "full_name": full_name,
                "html_url": repo.get("html_url", f"https://github.com/{full_name}"),
                "default_branch": default_branch,
                "stars": stars,
                "forks_count": repo.get("forks_count", 0),
                "open_issues_count": repo.get("open_issues_count", 0),
                "primary_language": language,
                "created_at": created_at_str,
                "age_years": age_years,
                "contributors_count": contributors_count if contributors_count is not None else -1,
                "total_workflows": total_workflows,
                "releases_window_count": releases_in_window,
                "runs_window_count": runs_in_window,
                "description": (repo.get("description") or "").replace("\n", " ").strip(),
            }

            selected_repos.append(repo_meta)
            detailed_log.append({
                "full_name": full_name,
                "stars": stars,
                "language": language,
                "status": "SELECIONADO",
                "motivo": "Atende a todos os critérios operacionais",
                "total_workflows": total_workflows,
                "releases_na_janela": releases_in_window,
                "runs_na_janela": runs_in_window,
            })

            funnel_counts["5_selecionados"] = len(selected_repos)
            logger.info(
                "[%d/%d] Aprovado: %s (Stars: %d | Releases: %d | Runs: %d | Contrib: %s)",
                len(selected_repos),
                target,
                full_name,
                stars,
                releases_in_window,
                runs_in_window,
                contributors_count,
            )

        return selected_repos, detailed_log, funnel_counts

    def export_results(
        self,
        selected_repos: List[Dict[str, Any]],
        detailed_log: List[Dict[str, Any]],
        funnel_counts: Dict[str, int],
    ) -> None:
        """Gera os arquivos CSV de saída e o sumário do funil."""
        data_dir = self.config.output.data_dir
        data_dir.mkdir(parents=True, exist_ok=True)

        # 1. repositorios_selecionados.csv
        df_selected = pd.DataFrame(selected_repos)
        selected_path = self.config.output.selected_repositories_path
        df_selected.to_csv(selected_path, index=False, encoding="utf-8")
        logger.info("Arquivo de repositórios selecionados salvo em: %s", selected_path)

        # 2. funil_detalhado.csv
        df_detailed = pd.DataFrame(detailed_log)
        detailed_path = self.config.output.funnel_detailed_path
        df_detailed.to_csv(detailed_path, index=False, encoding="utf-8")
        logger.info("Auditoria detalhada do funil salva em: %s", detailed_path)

        # 3. funil_selecao.csv (tabela agregada)
        candidatos = funnel_counts["1_candidatos"]
        actions = funnel_counts["2_com_actions"]
        releases = funnel_counts["3_com_releases"]
        runs = funnel_counts["4_com_runs"]
        selecionados = funnel_counts["5_selecionados"]

        funnel_summary = [
            {
                "etapa_num": 1,
                "etapa_nome": "Candidatos Iniciais (Busca por estrelas > 1000)",
                "total_restante": candidatos,
                "descartados_na_etapa": 0,
                "taxa_retencao_etapa_pct": 100.0,
                "taxa_retencao_acumulada_pct": 100.0,
                "criterio_ou_motivo": "stars:>1000, is:public, fork:false, archived:false",
            },
            {
                "etapa_num": 2,
                "etapa_nome": "Adoção de CI/CD (GitHub Actions)",
                "total_restante": actions,
                "descartados_na_etapa": candidatos - actions,
                "taxa_retencao_etapa_pct": round((actions / candidatos * 100), 2) if candidatos else 0,
                "taxa_retencao_acumulada_pct": round((actions / candidatos * 100), 2) if candidatos else 0,
                "criterio_ou_motivo": "total_count > 0 em /actions/workflows",
            },
            {
                "etapa_num": 3,
                "etapa_nome": "Mínimo de Releases na Janela (>= 5)",
                "total_restante": releases,
                "descartados_na_etapa": actions - releases,
                "taxa_retencao_etapa_pct": round((releases / actions * 100), 2) if actions else 0,
                "taxa_retencao_acumulada_pct": round((releases / candidatos * 100), 2) if candidatos else 0,
                "criterio_ou_motivo": f">= {self.config.funnel_criteria.min_releases} releases (draft=false, prerelease=false)",
            },
            {
                "etapa_num": 4,
                "etapa_nome": "Mínimo de Workflow Runs na Janela (>= 50)",
                "total_restante": runs,
                "descartados_na_etapa": releases - runs,
                "taxa_retencao_etapa_pct": round((runs / releases * 100), 2) if releases else 0,
                "taxa_retencao_acumulada_pct": round((runs / candidatos * 100), 2) if candidatos else 0,
                "criterio_ou_motivo": f">= {self.config.funnel_criteria.min_workflow_runs} runs válidos no default branch (event=push)",
            },
            {
                "etapa_num": 5,
                "etapa_nome": "Amostra Selecionada (Lab03S01)",
                "total_restante": selecionados,
                "descartados_na_etapa": runs - selecionados,
                "taxa_retencao_etapa_pct": round((selecionados / runs * 100), 2) if runs else 0,
                "taxa_retencao_acumulada_pct": round((selecionados / candidatos * 100), 2) if candidatos else 0,
                "criterio_ou_motivo": f"Meta de {self.config.funnel_criteria.target_repositories} repositórios qualificados para S01",
            },
        ]

        df_summary = pd.DataFrame(funnel_summary)
        summary_path = self.config.output.funnel_summary_path
        df_summary.to_csv(summary_path, index=False, encoding="utf-8")
        logger.info("Resumo do funil de seleção salvo em: %s", summary_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pipeline de Seleção de Repositórios e Funil de Coleta - Lab03"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Caminho alternativo para o arquivo config.yaml",
    )
    parser.add_argument(
        "--target",
        type=int,
        default=None,
        help="Quantidade alvo de repositórios qualificados a selecionar (default: config.yaml)",
    )
    parser.add_argument(
        "--candidate-limit",
        type=int,
        default=500,
        help="Limite de candidatos a minerar na busca preliminar por estrelas",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Desativa temporariamente o uso do cache local",
    )

    args = parser.parse_args()

    config = Config.load(args.config)
    if args.no_cache:
        config.cache.enabled = False

    collector = FunnelCollector(config)
    selected, detailed, counts = collector.process_funnel(
        target_count=args.target, candidate_limit=args.candidate_limit
    )
    collector.export_results(selected, detailed, counts)
    logger.info("Execução concluída com sucesso!")


if __name__ == "__main__":
    main()
