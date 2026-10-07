"""Orquestração da coleta de workflow runs, CFR (CI) e tempo de recuperação.

Para cada repositório selecionado:
1. coleta os workflow runs da branch padrão com event=push na janela;
2. classifica as execuções (sucesso / falha / ignorar);
3. calcula o CFR — variante CI;
4. identifica episódios de falha e o Failed Deployment Recovery Time;
5. exporta CSVs para o pipeline principal.

Uso (a partir da raiz do repositório):
    python -m lab03.src.coleta_workflow_runs [--limit N] [--no-cache]

Uso como biblioteca:
    run_workflow_collection(config)
    collect_repositories(client, [("owner", "repo", "main"), ...], config)
"""

from __future__ import annotations

import argparse
import csv
import logging
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple, Union

import pandas as pd

from .cache_manager import CacheManager
from .config import Config
from .github_client import GitHubClient
from .metricas_ci import (
    FailureEpisode,
    RepoCiSummary,
    compute_failure_episodes,
    summarize_repository_ci,
)
from .workflow_runs import collect_workflow_runs

logger = logging.getLogger("coleta_workflow_runs")

RUNS_CSV = "workflow_runs.csv"
EPISODES_CSV = "recovery_episodes.csv"
SUMMARY_CSV = "qualidade_ci_repositorio.csv"

RepoRef = Union[Tuple[str, str], Tuple[str, str, str]]


@dataclass
class RepoCiResult:
    """Tudo o que o pipeline precisa sobre a qualidade das entregas de um repositório."""

    summary: RepoCiSummary
    runs: List[dict] = field(default_factory=list)
    episodes: List[FailureEpisode] = field(default_factory=list)


def collect_repository(
    client: GitHubClient,
    owner: str,
    repo: str,
    config: Config,
    default_branch: Optional[str] = None,
) -> RepoCiResult:
    """Coleta runs e calcula CFR (CI) e tempo de recuperação de um repositório."""
    full_name = f"{owner}/{repo}"
    branch = default_branch or ""
    try:
        runs = collect_workflow_runs(
            client, owner, repo, config.window, default_branch=default_branch or None
        )
        if runs and not branch:
            branch = str(runs[0].get("branch") or "")
        episodes = compute_failure_episodes(full_name, runs)
        summary = summarize_repository_ci(
            full_name, runs, episodes, default_branch=branch
        )
        return RepoCiResult(summary=summary, runs=runs, episodes=episodes)
    except Exception as err:  # noqa: BLE001 - um repositório não interrompe os demais
        logger.error("Falha ao processar %s: %s", full_name, err)
        summary = summarize_repository_ci(
            full_name, [], [], default_branch=branch, erro=str(err)
        )
        return RepoCiResult(summary=summary)


def collect_repositories(
    client: GitHubClient,
    repositories: Iterable[RepoRef],
    config: Config,
) -> List[RepoCiResult]:
    """Processa uma lista de repositórios. Falha em um item não interrompe os demais."""
    repos = list(repositories)
    results: List[RepoCiResult] = []
    for idx, item in enumerate(repos, 1):
        owner, name = item[0], item[1]
        branch = item[2] if len(item) > 2 else None
        result = collect_repository(client, owner, name, config, default_branch=branch)
        s = result.summary
        logger.info(
            "[%d/%d] %s: %d runs | sucesso=%d falha=%d ignorados=%d | CFR=%s | "
            "recuperados=%d censurados=%d | mediana recuperação=%s h",
            idx,
            len(repos),
            s.repo,
            s.total_runs_coletados,
            s.runs_sucesso,
            s.runs_falha,
            s.runs_ignorados,
            _fmt_ratio(s.cfr_ci),
            s.episodios_recuperados,
            s.episodios_censurados,
            _fmt(s.mediana_recuperacao_horas),
        )
        results.append(result)
    return results


def _fmt(value: Optional[float]) -> str:
    return "n/d" if value is None else f"{value:.2f}"


def _fmt_ratio(value: Optional[float]) -> str:
    return "n/d" if value is None else f"{value:.3f}"


def load_selected_repositories(
    csv_path: Path | str,
) -> List[Tuple[str, str, str]]:
    """Lê (owner, name, default_branch) de repositorios_selecionados.csv."""
    repos: List[Tuple[str, str, str]] = []
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            owner = (row.get("owner") or "").strip()
            name = (row.get("name") or "").strip()
            branch = (row.get("default_branch") or "").strip()
            if owner and name:
                repos.append((owner, name, branch))
    return repos


def _to_dataframe(rows: Sequence, dataclass_type) -> pd.DataFrame:
    columns = [f.name for f in fields(dataclass_type)]
    return pd.DataFrame([asdict(r) for r in rows], columns=columns)


def export_results(
    results: Sequence[RepoCiResult], data_dir: Path | str
) -> Tuple[Path, Path, Path]:
    """Grava runs, episódios de recuperação e resumo por repositório."""
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    runs_with_repo: List[dict] = []
    for result in results:
        for row in result.runs:
            item = dict(row)
            item.setdefault("repo", result.summary.repo)
            runs_with_repo.append(item)

    episodes = [ep for r in results for ep in r.episodes]
    summaries = [r.summary for r in results]

    runs_path = data_dir / RUNS_CSV
    episodes_path = data_dir / EPISODES_CSV
    summary_path = data_dir / SUMMARY_CSV

    pd.DataFrame(runs_with_repo).to_csv(runs_path, index=False, encoding="utf-8")
    _to_dataframe(episodes, FailureEpisode).to_csv(
        episodes_path, index=False, encoding="utf-8"
    )
    _to_dataframe(summaries, RepoCiSummary).to_csv(
        summary_path, index=False, encoding="utf-8"
    )

    logger.info("Workflow runs salvos em: %s", runs_path)
    logger.info("Episódios de recuperação salvos em: %s", episodes_path)
    logger.info("Resumo de qualidade CI salvo em: %s", summary_path)
    return runs_path, episodes_path, summary_path


def build_client(config: Config) -> GitHubClient:
    """Cria o GitHubClient compartilhado (mesmo cache e rate limit da seleção)."""
    cache = CacheManager(config.cache.cache_dir, enabled=config.cache.enabled)
    return GitHubClient(
        token=config.github_token,
        base_url=config.api.base_url,
        timeout=config.api.timeout_seconds,
        max_retries=config.api.max_retries,
        backoff_factor=config.api.backoff_factor,
        safety_margin=config.api.rate_limit_safety_margin,
        cache_manager=cache,
    )


def run_workflow_collection(
    config: Config,
    client: Optional[GitHubClient] = None,
    repositories: Optional[Iterable[RepoRef]] = None,
    limit: Optional[int] = None,
) -> List[RepoCiResult]:
    """Executa a coleta completa e exporta os CSVs. Ponto de entrada do pipeline."""
    client = client or build_client(config)
    if repositories is None:
        repositories = load_selected_repositories(config.output.selected_repositories_path)
    repos = list(repositories)
    if limit:
        repos = repos[:limit]

    results = collect_repositories(client, repos, config)
    export_results(results, config.output.data_dir)
    return results


def main() -> None:  # pragma: no cover - CLI fina
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(
        description="Coleta de workflow runs, CFR (CI) e tempo de recuperação - Lab03"
    )
    parser.add_argument("--config", type=str, default=None, help="Caminho para config.yaml")
    parser.add_argument("--limit", type=int, default=None, help="Processa apenas os N primeiros repositórios")
    parser.add_argument("--no-cache", action="store_true", help="Desativa o cache local")
    args = parser.parse_args()

    config = Config.load(args.config)
    if args.no_cache:
        config.cache.enabled = False

    results = run_workflow_collection(config, limit=args.limit)
    failed = [r.summary.repo for r in results if r.summary.erro]
    logger.info("Concluído: %d repositórios (%d com erro).", len(results), len(failed))


if __name__ == "__main__":  # pragma: no cover
    main()
