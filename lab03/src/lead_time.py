"""Cálculo das duas variantes de Lead Time for Changes (LAB03S01).

Variante por release:
    lead time da release = published_at da release - commit.author.date do commit
    mais antigo entre a release anterior e a release atual.
    Uma observação por release; mediana por repositório sobre as releases.

Variante por commit:
    lead time do commit = published_at da release - commit.author.date.
    Uma observação por commit; mediana por repositório sobre todos os commits.

As duas variantes são mantidas separadas. Cada release gera uma linha
(ReleaseLeadTime) com o status do cálculo, e cada commit usado na variante por
commit gera uma linha (CommitLeadTime), de modo que seja possível auditar quais
releases/commits entraram em cada variante e por que alguma ficou de fora.

Este módulo é puro (sem I/O): recebe dados já coletados por releases.py.
Todos os lead times são expressos em horas.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, List, Optional, Set, Tuple

from .config import parse_iso_datetime
from .releases import CompareResult, Release

# Status do cálculo por release
STATUS_OK = "OK"
STATUS_SEM_RELEASE_ANTERIOR = "SEM_RELEASE_ANTERIOR"
STATUS_COMPARACAO_INDISPONIVEL = "COMPARACAO_INDISPONIVEL"
STATUS_SEM_COMMITS = "SEM_COMMITS"
STATUS_SEM_DATA_COMMIT = "SEM_DATA_COMMIT"


@dataclass
class ReleaseLeadTime:
    """Uma linha por release dentro da janela (variante por release + auditoria)."""

    repo: str
    release_id: int
    release_name: str
    tag_name: str
    published_at: str
    release_anterior_tag: str = ""
    release_anterior_published_at: str = ""
    status: str = STATUS_OK
    total_commits_api: int = 0
    commits_coletados: int = 0
    comparacao_truncada: bool = False
    commits_sem_data: int = 0
    commits_duplicados_ignorados: int = 0
    commit_mais_antigo_sha: str = ""
    commit_mais_antigo_data: str = ""
    lead_time_release_horas: Optional[float] = None
    observacao: str = ""


@dataclass
class CommitLeadTime:
    """Uma linha por commit usado na variante por commit."""

    repo: str
    release_tag: str
    release_published_at: str
    sha: str
    author_date: str
    lead_time_commit_horas: float


@dataclass
class RepoLeadTimeSummary:
    """Resumo por repositório, com medianas e contagens das duas variantes."""

    repo: str
    releases_na_janela: int = 0
    releases_calculadas: int = 0  # n de observações da variante por release
    commits_usados: int = 0  # n de observações da variante por commit
    releases_sem_release_anterior: int = 0
    releases_comparacao_indisponivel: int = 0
    releases_sem_commits: int = 0
    releases_sem_data_commit: int = 0
    releases_truncadas: int = 0
    commits_sem_data: int = 0
    commits_duplicados_ignorados: int = 0
    mediana_lead_time_release_horas: Optional[float] = None
    mediana_lead_time_commit_horas: Optional[float] = None
    erro: str = ""


def hours_between(later: datetime, earlier: datetime) -> float:
    """Diferença em horas (later - earlier). Pode ser negativa."""
    return (later - earlier).total_seconds() / 3600.0


def median_or_none(values: Iterable[float]) -> Optional[float]:
    """Mediana dos valores, ou None quando não há observações."""
    data = list(values)
    if not data:
        return None
    return float(statistics.median(data))


def extract_commit_date(commit: Any) -> Optional[datetime]:
    """Retorna commit.author.date (e NÃO committer.date), ou None se ausente/inválida."""
    try:
        raw = commit["commit"]["author"]["date"]
    except (KeyError, TypeError):
        return None
    if not raw:
        return None
    try:
        return parse_iso_datetime(raw)
    except (ValueError, TypeError, AttributeError):
        return None


def compute_release_lead_time(
    repo: str,
    release: Release,
    previous: Optional[Release],
    compare: Optional[CompareResult],
    seen_shas: Set[str],
) -> Tuple[ReleaseLeadTime, List[CommitLeadTime]]:
    """Calcula as duas variantes para uma release.

    `seen_shas` é compartilhado entre as releases do mesmo repositório (processadas
    da mais antiga para a mais nova): um commit presente em mais de um intervalo
    entra na variante por commit apenas uma vez, associado à primeira release.
    A variante por release usa todos os commits do intervalo.
    """
    row = ReleaseLeadTime(
        repo=repo,
        release_id=release.release_id,
        release_name=release.name,
        tag_name=release.tag_name,
        published_at=release.published_at.isoformat(),
        release_anterior_tag=previous.tag_name if previous else "",
        release_anterior_published_at=previous.published_at.isoformat() if previous else "",
    )

    if previous is None:
        row.status = STATUS_SEM_RELEASE_ANTERIOR
        return row, []

    if compare is None or not compare.available:
        row.status = STATUS_COMPARACAO_INDISPONIVEL
        row.observacao = compare.error if compare else ""
        return row, []

    row.total_commits_api = compare.total_commits
    row.commits_coletados = len(compare.commits)
    row.comparacao_truncada = compare.truncated
    if compare.truncated:
        row.observacao = (
            f"comparacao truncada pela API: {len(compare.commits)} de {compare.total_commits} commits"
        )

    if not compare.commits:
        row.status = STATUS_SEM_COMMITS
        return row, []

    dated: List[Tuple[datetime, str]] = []
    for commit in compare.commits:
        commit_date = extract_commit_date(commit)
        if commit_date is None:
            row.commits_sem_data += 1
            continue
        dated.append((commit_date, commit.get("sha") or ""))

    if not dated:
        row.status = STATUS_SEM_DATA_COMMIT
        return row, []

    # Variante por release: commit mais antigo do intervalo
    oldest_date, oldest_sha = min(dated, key=lambda item: item[0])
    row.commit_mais_antigo_sha = oldest_sha
    row.commit_mais_antigo_data = oldest_date.isoformat()
    row.lead_time_release_horas = hours_between(release.published_at, oldest_date)

    # Variante por commit: um lead time por commit (sem repetir commits entre releases)
    commit_rows: List[CommitLeadTime] = []
    for commit_date, sha in dated:
        if sha:
            if sha in seen_shas:
                row.commits_duplicados_ignorados += 1
                continue
            seen_shas.add(sha)
        commit_rows.append(
            CommitLeadTime(
                repo=repo,
                release_tag=release.tag_name,
                release_published_at=release.published_at.isoformat(),
                sha=sha,
                author_date=commit_date.isoformat(),
                lead_time_commit_horas=hours_between(release.published_at, commit_date),
            )
        )

    return row, commit_rows


def summarize_repository(
    repo: str,
    release_rows: List[ReleaseLeadTime],
    commit_rows: List[CommitLeadTime],
    erro: str = "",
) -> RepoLeadTimeSummary:
    """Agrega as linhas de um repositório: medianas e contagens das duas variantes."""
    summary = RepoLeadTimeSummary(repo=repo, erro=erro)
    summary.releases_na_janela = len(release_rows)

    release_values: List[float] = []
    for row in release_rows:
        if row.status == STATUS_OK and row.lead_time_release_horas is not None:
            release_values.append(row.lead_time_release_horas)
        elif row.status == STATUS_SEM_RELEASE_ANTERIOR:
            summary.releases_sem_release_anterior += 1
        elif row.status == STATUS_COMPARACAO_INDISPONIVEL:
            summary.releases_comparacao_indisponivel += 1
        elif row.status == STATUS_SEM_COMMITS:
            summary.releases_sem_commits += 1
        elif row.status == STATUS_SEM_DATA_COMMIT:
            summary.releases_sem_data_commit += 1

        if row.comparacao_truncada:
            summary.releases_truncadas += 1
        summary.commits_sem_data += row.commits_sem_data
        summary.commits_duplicados_ignorados += row.commits_duplicados_ignorados

    commit_values = [row.lead_time_commit_horas for row in commit_rows]

    summary.releases_calculadas = len(release_values)
    summary.commits_usados = len(commit_values)
    summary.mediana_lead_time_release_horas = median_or_none(release_values)
    summary.mediana_lead_time_commit_horas = median_or_none(commit_values)
    return summary
