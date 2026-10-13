"""Script orquestrador para cálculo e consolidação das métricas DORA (LAB03S02).

Lê os repositórios selecionados, processa os dados de releases, commits e workflow runs
a partir do cache/API, calcula todas as métricas com tratamento de censura e exporta
o dataset consolidado para lab03/data/metricas_dora.csv.
"""

from __future__ import annotations

import argparse
import csv
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from .cache_manager import CacheManager
from .config import Config, parse_iso_datetime
from .github_client import GitHubClient
from .metricas import compute_all_metrics_for_repository

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("coletor_metricas")


def load_repository_releases_from_cache(
    cache: CacheManager, owner: str, repo: str, config: Config
) -> List[Dict[str, Any]]:
    """Carrega releases do repositório a partir do cache local."""
    releases: List[Dict[str, Any]] = []
    page = 1
    while True:
        key = f"releases_{owner}_{repo}_p{page}"
        data = cache.get("releases", key)
        if not data or not isinstance(data, list):
            break
        releases.extend(data)
        page += 1
    return releases


def load_repository_workflow_runs_from_cache(
    cache: CacheManager, owner: str, repo: str, default_branch: str
) -> List[Dict[str, Any]]:
    """Carrega workflow runs do repositório a partir do cache local."""
    runs: List[Dict[str, Any]] = []
    page = 1
    while True:
        key = f"runs_{owner}_{repo}_{default_branch}_p{page}"
        data = cache.get("workflow_runs", key)
        if not data:
            break
        if isinstance(data, dict):
            runs.extend(data.get("workflow_runs", []))
        elif isinstance(data, list):
            runs.extend(data)
        page += 1
    return runs


def load_or_fetch_release_commits(
    client: GitHubClient,
    cache: CacheManager,
    owner: str,
    repo: str,
    valid_releases: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
    """Gera a estrutura de comparação entre releases consecutivas e obtém seus commits.

    As releases devem estar ordenadas cronologicamente.
    """
    sorted_releases = sorted(
        valid_releases,
        key=lambda r: parse_iso_datetime(r["published_at"]),
    )

    releases_data_with_commits: List[Dict[str, Any]] = []
    commits_by_release_pair: Dict[str, List[Dict[str, Any]]] = {}

    for idx, curr_rel in enumerate(sorted_releases):
        tag_curr = curr_rel.get("tag_name", "")
        pub_curr = curr_rel.get("published_at", "")

        if idx == 0:
            # Primeira release da história no dataset
            releases_data_with_commits.append({
                "tag_name": tag_curr,
                "published_at": pub_curr,
                "has_previous_release": False,
                "compare_status_code": None,
                "commits": [],
            })
            continue

        prev_rel = sorted_releases[idx - 1]
        tag_prev = prev_rel.get("tag_name", "")
        pair_key = f"{tag_prev}...{tag_curr}"
        cache_key = f"compare_{owner}_{repo}_{tag_prev}_{tag_curr}"

        commits: List[Dict[str, Any]] = []
        status_code = 200

        # Verifica cache primeiro
        cached_compare = cache.get("compare", cache_key)
        if cached_compare is not None:
            if isinstance(cached_compare, dict):
                commits = cached_compare.get("commits", [])
            elif isinstance(cached_compare, list):
                commits = cached_compare
        else:
            endpoint = f"repos/{owner}/{repo}/compare/{tag_prev}...{tag_curr}"
            try:
                data, headers = client.request(
                    endpoint,
                    cache_category="compare",
                    cache_key=cache_key,
                )
                if data is None:
                    status_code = 404
                elif isinstance(data, dict):
                    commits = data.get("commits", [])
            except Exception as err:
                logger.warning("Falha ao comparar %s: %s", pair_key, err)
                status_code = 404

        commits_by_release_pair[pair_key] = commits
        releases_data_with_commits.append({
            "tag_name": tag_curr,
            "published_at": pub_curr,
            "has_previous_release": True,
            "compare_status_code": status_code,
            "commits": commits,
        })

    return releases_data_with_commits, commits_by_release_pair


def process_repository_metrics(
    config: Config,
    client: GitHubClient,
    cache: CacheManager,
    repo_row: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Executa o cálculo de todas as métricas para um único repositório."""
    owner = repo_row.get("owner")
    name = repo_row.get("name")
    full_name = repo_row.get("full_name")
    default_branch = repo_row.get("default_branch", "main")

    if not owner or not name:
        if full_name and "/" in full_name:
            owner, name = full_name.split("/", 1)
        else:
            return None

    logger.info("Processando métricas para: %s/%s", owner, name)

    # 1. Carrega releases
    raw_releases = load_repository_releases_from_cache(cache, owner, name, config)
    if not raw_releases:
        # Se não estiver em cache, consulta via client
        endpoint = f"repos/{owner}/{name}/releases"
        raw_releases = client.paginate(
            endpoint=endpoint,
            params={"per_page": 100},
            max_pages=5,
            cache_category="releases",
            cache_key_prefix=f"releases_{owner}_{name}",
        )

    # Filtra releases válidas na janela
    valid_releases = []
    for r in raw_releases:
        if r.get("draft", False) or r.get("prerelease", False):
            continue
        pub_str = r.get("published_at")
        if not pub_str:
            continue
        try:
            pub_dt = parse_iso_datetime(pub_str)
            if config.window.is_in_window(pub_dt):
                valid_releases.append(r)
        except Exception:
            continue

    # 2. Obtém commits entre releases consecutivas
    releases_with_commits, commits_by_pair = load_or_fetch_release_commits(
        client, cache, owner, name, valid_releases
    )

    # 3. Carrega workflow runs
    workflow_runs = load_repository_workflow_runs_from_cache(
        cache, owner, name, default_branch
    )
    if not workflow_runs:
        endpoint = f"repos/{owner}/{name}/actions/runs"
        workflow_runs = client.paginate(
            endpoint=endpoint,
            params={"branch": default_branch, "event": "push", "per_page": 100},
            max_pages=10,
            cache_category="workflow_runs",
            cache_key_prefix=f"runs_{owner}_{name}_{default_branch}",
        )

    # 4. Computa todas as métricas DORA
    metrics = compute_all_metrics_for_repository(
        repo_meta=repo_row,
        releases=valid_releases,
        releases_data_with_commits=releases_with_commits,
        workflow_runs=workflow_runs,
        window_start=config.window.start_date,
        window_end=config.window.end_date,
        commits_by_release_pair=commits_by_pair,
    )

    return metrics


def run_metrics_pipeline(
    config_path: Optional[str] = None,
    repos_csv_path: Optional[str] = None,
    output_csv_path: Optional[str] = None,
) -> pd.DataFrame:
    """Executa o pipeline de cálculo de métricas para todos os repositórios da amostra."""
    config = Config.load(config_path)
    cache = CacheManager(config.cache.cache_dir, enabled=config.cache.enabled)
    client = GitHubClient(
        token=config.github_token,
        base_url=config.api.base_url,
        timeout=config.api.timeout_seconds,
        max_retries=config.api.max_retries,
        backoff_factor=config.api.backoff_factor,
        safety_margin=config.api.rate_limit_safety_margin,
        cache_manager=cache,
    )

    # Localiza arquivo de repositórios selecionados
    repos_file = Path(repos_csv_path) if repos_csv_path else config.output.selected_repositories_path
    if not repos_file.is_file():
        raise FileNotFoundError(f"Arquivo de repositórios não encontrado: {repos_file}")

    df_repos = pd.read_csv(repos_file)
    logger.info("Total de repositórios a processar: %d", len(df_repos))

    results: List[Dict[str, Any]] = []
    for _, row in df_repos.iterrows():
        res = process_repository_metrics(config, client, cache, row.to_dict())
        if res:
            results.append(res)

    df_results = pd.DataFrame(results)

    out_file = Path(output_csv_path) if output_csv_path else config.output.data_dir / "metricas_dora.csv"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    df_results.to_csv(out_file, index=False, encoding="utf-8")
    logger.info("Dataset de métricas DORA consolidado com sucesso em: %s", out_file)

    return df_results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pipeline de Cálculo e Validação das Métricas DORA (LAB03S02)"
    )
    parser.add_argument("--config", type=str, default=None, help="Caminho para config.yaml")
    parser.add_argument("--input", type=str, default=None, help="Caminho para repositorios_selecionados.csv")
    parser.add_argument("--output", type=str, default=None, help="Caminho para metricas_dora.csv")

    args = parser.parse_args()
    run_metrics_pipeline(
        config_path=args.config,
        repos_csv_path=args.input,
        output_csv_path=args.output,
    )


if __name__ == "__main__":
    main()
