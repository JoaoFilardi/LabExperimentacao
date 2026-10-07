"""Orquestração da coleta de Lead Time for Changes (LAB03S01).

Para cada repositório selecionado:
1. coleta as releases válidas (releases.py);
2. obtém os commits entre releases consecutivas (releases.py);
3. calcula as duas variantes de Lead Time e suas medianas (lead_time.py);
4. exporta os resultados em CSV.

Uso como pipeline (a partir da raiz do repositório):
    python -m lab03.src.coleta_lead_time [--limit N] [--no-cache]

Uso como biblioteca (pelo pipeline principal):
    results = collect_repositories(client, [("owner", "repo"), ...], config)
    # ou: run_lead_time_collection(config) lendo repositorios_selecionados.csv

Um repositório nunca é descartado por situações de borda (sem release anterior,
comparação 404, etc.): ele permanece nos resultados com contagens e status.
"""

from __future__ import annotations

import argparse
import csv
import logging
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

import pandas as pd

from .cache_manager import CacheManager
from .config import Config
from .github_client import GitHubClient
from .lead_time import (
    CommitLeadTime,
    ReleaseLeadTime,
    RepoLeadTimeSummary,
    compute_release_lead_time,
    summarize_repository,
)
from .releases import build_release_pairs, fetch_commits_between, fetch_valid_releases

logger = logging.getLogger("coleta_lead_time")

RELEASES_CSV = "lead_time_releases.csv"
COMMITS_CSV = "lead_time_commits.csv"
SUMMARY_CSV = "lead_time_repositorio.csv"


@dataclass
class RepoLeadTimeResult:
    """Tudo o que o pipeline precisa sobre um repositório."""

    summary: RepoLeadTimeSummary
    releases: List[ReleaseLeadTime] = field(default_factory=list)
    commits: List[CommitLeadTime] = field(default_factory=list)


def collect_repository(
    client: GitHubClient, owner: str, repo: str, config: Config
) -> RepoLeadTimeResult:
    """Coleta e calcula as duas variantes de Lead Time de um repositório."""
    full_name = f"{owner}/{repo}"

    try:
        all_releases = fetch_valid_releases(client, owner, repo)
    except Exception as err:  # noqa: BLE001 - mantém o repositório no processamento
        logger.error("Falha ao listar releases de %s: %s", full_name, err)
        return RepoLeadTimeResult(summary=summarize_repository(full_name, [], [], erro=str(err)))

    pairs = build_release_pairs(all_releases, config.window)

    release_rows: List[ReleaseLeadTime] = []
    commit_rows: List[CommitLeadTime] = []
    seen_shas: set = set()

    # pairs está em ordem cronológica: um commit repetido fica com a release mais antiga
    for release, previous in pairs:
        compare = None
        if previous is not None:
            compare = fetch_commits_between(
                client, owner, repo, previous.tag_name, release.tag_name
            )
        row, commits = compute_release_lead_time(full_name, release, previous, compare, seen_shas)
        release_rows.append(row)
        commit_rows.extend(commits)

    summary = summarize_repository(full_name, release_rows, commit_rows)
    return RepoLeadTimeResult(summary=summary, releases=release_rows, commits=commit_rows)


def collect_repositories(
    client: GitHubClient,
    repositories: Iterable[Tuple[str, str]],
    config: Config,
) -> List[RepoLeadTimeResult]:
    """Processa uma lista de (owner, name). Falhas em um repositório não interrompem os demais."""
    repos = list(repositories)
    results: List[RepoLeadTimeResult] = []
    for idx, (owner, name) in enumerate(repos, 1):
        result = collect_repository(client, owner, name, config)
        s = result.summary
        logger.info(
            "[%d/%d] %s: %d releases na janela | %d calculadas | %d commits | "
            "mediana release=%s h | mediana commit=%s h",
            idx,
            len(repos),
            s.repo,
            s.releases_na_janela,
            s.releases_calculadas,
            s.commits_usados,
            _fmt(s.mediana_lead_time_release_horas),
            _fmt(s.mediana_lead_time_commit_horas),
        )
        results.append(result)
    return results


def _fmt(value: Optional[float]) -> str:
    return "n/d" if value is None else f"{value:.1f}"


def load_selected_repositories(csv_path: Path | str) -> List[Tuple[str, str]]:
    """Lê (owner, name) de repositorios_selecionados.csv."""
    repos: List[Tuple[str, str]] = []
    with open(csv_path, "r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            owner = (row.get("owner") or "").strip()
            name = (row.get("name") or "").strip()
            if owner and name:
                repos.append((owner, name))
    return repos


def _to_dataframe(rows: Sequence, dataclass_type) -> pd.DataFrame:
    columns = [f.name for f in fields(dataclass_type)]
    return pd.DataFrame([asdict(r) for r in rows], columns=columns)


def export_results(results: Sequence[RepoLeadTimeResult], data_dir: Path | str) -> Tuple[Path, Path, Path]:
    """Grava os três CSVs (por release, por commit e resumo por repositório)."""
    data_dir = Path(data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    releases = [row for r in results for row in r.releases]
    commits = [row for r in results for row in r.commits]
    summaries = [r.summary for r in results]

    releases_path = data_dir / RELEASES_CSV
    commits_path = data_dir / COMMITS_CSV
    summary_path = data_dir / SUMMARY_CSV

    _to_dataframe(releases, ReleaseLeadTime).to_csv(releases_path, index=False, encoding="utf-8")
    _to_dataframe(commits, CommitLeadTime).to_csv(commits_path, index=False, encoding="utf-8")
    _to_dataframe(summaries, RepoLeadTimeSummary).to_csv(summary_path, index=False, encoding="utf-8")

    logger.info("Lead time por release salvo em: %s", releases_path)
    logger.info("Lead time por commit salvo em: %s", commits_path)
    logger.info("Resumo por repositório salvo em: %s", summary_path)
    return releases_path, commits_path, summary_path


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


def run_lead_time_collection(
    config: Config,
    client: Optional[GitHubClient] = None,
    repositories: Optional[Iterable[Tuple[str, str]]] = None,
    limit: Optional[int] = None,
) -> List[RepoLeadTimeResult]:
    """Executa a coleta completa e exporta os CSVs. Ponto de entrada para o pipeline."""
    client = client or build_client(config)
    if repositories is None:
        repositories = load_selected_repositories(config.output.selected_repositories_path)
    repos = list(repositories)
    if limit:
        repos = repos[:limit]

    results = collect_repositories(client, repos, config)
    export_results(results, config.output.data_dir)
    return results


def main() -> None:  # pragma: no cover - CLI fina sobre run_lead_time_collection
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description="Coleta de Lead Time for Changes - Lab03")
    parser.add_argument("--config", type=str, default=None, help="Caminho alternativo para config.yaml")
    parser.add_argument("--limit", type=int, default=None, help="Processa apenas os N primeiros repositórios")
    parser.add_argument("--no-cache", action="store_true", help="Desativa o cache local")
    args = parser.parse_args()

    config = Config.load(args.config)
    if args.no_cache:
        config.cache.enabled = False

    results = run_lead_time_collection(config, limit=args.limit)
    failed = [r.summary.repo for r in results if r.summary.erro]
    logger.info("Concluído: %d repositórios (%d com erro).", len(results), len(failed))


if __name__ == "__main__":  # pragma: no cover
    main()
