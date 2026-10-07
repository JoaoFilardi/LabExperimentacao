"""Coleta de workflow runs do GitHub Actions (LAB03S01).

Para cada repositório:
1. identifica a branch padrão;
2. consulta GET /repos/{owner}/{repo}/actions/runs com branch e event=push;
3. restringe à janela de observação (filtro `created` da API);
4. pagina os resultados e particiona a janela quando a consulta atinge o
   teto de 1.000 resultados da API.

Todas as requisições passam pelo GitHubClient compartilhado (cache, retry e
rate limit). Períodos e repositórios já processados ficam marcados no
CacheManager para retomada após interrupção.
"""

from __future__ import annotations

import calendar
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from .config import WindowConfig, parse_iso_datetime
from .github_client import GitHubClient
from .metricas_ci import VALID_CONCLUSIONS, classify_run

logger = logging.getLogger(__name__)

PER_PAGE = 100
MAX_RESULTS_PER_QUERY = 1000
CACHE_CATEGORY_PERIOD = "workflow_runs_period"
CACHE_CATEGORY_PAGES = "workflow_runs"
PROGRESS_TASK = "workflow_runs"
MIN_PERIOD_SECONDS = 60


def iter_monthly_periods(
    start: datetime, end: datetime
) -> List[Tuple[datetime, datetime]]:
    """Divide a janela em períodos mensais (último mês pode ser parcial)."""
    if end < start:
        return []

    periods: List[Tuple[datetime, datetime]] = []
    current = start
    while current <= end:
        last_day = calendar.monthrange(current.year, current.month)[1]
        month_end = datetime(
            current.year, current.month, last_day, 23, 59, 59, tzinfo=timezone.utc
        )
        period_end = min(month_end, end)
        periods.append((current, period_end))
        if current.month == 12:
            current = datetime(current.year + 1, 1, 1, tzinfo=timezone.utc)
        else:
            current = datetime(current.year, current.month + 1, 1, tzinfo=timezone.utc)
    return periods


def format_created_range(start: datetime, end: datetime) -> str:
    """Monta o parâmetro `created` da API no formato ISO UTC."""

    def _fmt(dt: datetime) -> str:
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return f"{_fmt(start)}..{_fmt(end)}"


def period_cache_key(
    owner: str, repo: str, branch: str, start: datetime, end: datetime
) -> str:
    return f"{owner}_{repo}_{branch}_{format_created_range(start, end)}"


def normalize_workflow_run(raw: Any, default_branch: str = "") -> Optional[Dict[str, Any]]:
    """Extrai os campos necessários para as métricas a partir do JSON da API."""
    if not isinstance(raw, dict):
        return None
    run_id = raw.get("id")
    if run_id is None:
        return None
    return {
        "id": run_id,
        "workflow_id": raw.get("workflow_id"),
        "name": raw.get("name") or "",
        "created_at": raw.get("created_at") or "",
        "run_started_at": raw.get("run_started_at") or raw.get("created_at") or "",
        "updated_at": raw.get("updated_at") or "",
        "status": raw.get("status") or "",
        "conclusion": raw.get("conclusion"),
        "branch": raw.get("head_branch") or default_branch,
        "event": raw.get("event") or "",
        "classificacao": classify_run(raw),
    }


def _is_in_window(created_at: str, window: WindowConfig) -> bool:
    if not created_at:
        return False
    try:
        return window.is_in_window(created_at)
    except Exception:
        return False


def filter_collected_runs(
    runs: List[Dict[str, Any]],
    window: WindowConfig,
    default_branch: str,
) -> List[Dict[str, Any]]:
    """Mantém apenas push na branch padrão dentro da janela (defesa em profundidade)."""
    filtered: List[Dict[str, Any]] = []
    seen_ids = set()
    for run in runs:
        run_id = run.get("id")
        if run_id in seen_ids:
            continue
        if run.get("event") != "push":
            continue
        branch = run.get("branch") or run.get("head_branch")
        if default_branch and branch and branch != default_branch:
            continue
        created = run.get("created_at") or ""
        if not _is_in_window(created, window):
            continue
        seen_ids.add(run_id)
        filtered.append(run)
    return filtered


def fetch_default_branch(client: GitHubClient, owner: str, repo: str) -> str:
    """Obtém `default_branch` via GET /repos/{owner}/{repo}, com cache."""
    data, _ = client.request(
        f"repos/{owner}/{repo}",
        cache_category="repos_meta",
        cache_key=f"{owner}_{repo}",
    )
    if isinstance(data, dict) and data.get("default_branch"):
        return str(data["default_branch"])
    return "main"


def _split_period(
    start: datetime, end: datetime
) -> Optional[List[Tuple[datetime, datetime]]]:
    delta = end - start
    if delta.total_seconds() < MIN_PERIOD_SECONDS:
        return None
    mid = start + delta / 2
    second_start = mid + timedelta(seconds=1)
    if second_start > end:
        return None
    return [(start, mid), (second_start, end)]


def _extract_runs_payload(data: Any) -> Tuple[List[Any], Optional[int]]:
    if data is None:
        return [], 0
    if isinstance(data, list):
        return data, len(data)
    if isinstance(data, dict):
        runs = data.get("workflow_runs")
        if isinstance(runs, list):
            total = data.get("total_count")
            return runs, int(total) if total is not None else len(runs)
    return [], 0


def fetch_runs_for_period(
    client: GitHubClient,
    owner: str,
    repo: str,
    branch: str,
    start: datetime,
    end: datetime,
) -> List[Dict[str, Any]]:
    """Coleta runs de um intervalo, particionando se a API saturar em 1.000 itens."""
    cache = getattr(client, "cache", None)
    period_key = period_cache_key(owner, repo, branch, start, end)
    if cache:
        cached = cache.get(CACHE_CATEGORY_PERIOD, period_key)
        if isinstance(cached, list):
            return cached

    created_range = format_created_range(start, end)
    collected: List[Any] = []
    reported_total: Optional[int] = None
    max_pages = MAX_RESULTS_PER_QUERY // PER_PAGE

    for page in range(1, max_pages + 1):
        page_key = f"{period_key}_p{page}"
        data, _headers = client.request(
            f"repos/{owner}/{repo}/actions/runs",
            params={
                "branch": branch,
                "event": "push",
                "created": created_range,
                "per_page": PER_PAGE,
                "page": page,
            },
            cache_category=CACHE_CATEGORY_PAGES,
            cache_key=page_key,
        )
        page_runs, total_count = _extract_runs_payload(data)
        if reported_total is None:
            reported_total = total_count
        if not page_runs:
            break
        collected.extend(page_runs)
        if (reported_total or 0) > MAX_RESULTS_PER_QUERY:
            break
        if len(page_runs) < PER_PAGE:
            break

    truncated = (reported_total or 0) > MAX_RESULTS_PER_QUERY or len(collected) >= MAX_RESULTS_PER_QUERY
    if truncated:
        halves = _split_period(start, end)
        if halves:
            logger.info(
                "Consulta de %s/%s no intervalo %s atingiu o teto da API; particionando.",
                owner,
                repo,
                created_range,
            )
            merged: List[Dict[str, Any]] = []
            for half_start, half_end in halves:
                merged.extend(
                    fetch_runs_for_period(
                        client, owner, repo, branch, half_start, half_end
                    )
                )
            if cache:
                cache.set(CACHE_CATEGORY_PERIOD, period_key, merged)
                cache.mark_processed(PROGRESS_TASK, period_key)
            return merged
        logger.warning(
            "Intervalo %s de %s/%s não pode ser particionado e pode estar truncado.",
            created_range,
            owner,
            repo,
        )

    normalized = []
    for raw in collected:
        item = normalize_workflow_run(raw, default_branch=branch)
        if item is not None:
            normalized.append(item)

    if cache:
        cache.set(CACHE_CATEGORY_PERIOD, period_key, normalized)
        cache.mark_processed(PROGRESS_TASK, period_key)
    return normalized


def collect_workflow_runs(
    client: GitHubClient,
    owner: str,
    repo: str,
    window: WindowConfig,
    default_branch: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Coleta todos os workflow runs válidos da janela para um repositório."""
    branch = default_branch or fetch_default_branch(client, owner, repo)
    cache = getattr(client, "cache", None)
    repo_progress_id = f"{owner}/{repo}"

    all_runs: List[Dict[str, Any]] = []
    periods = iter_monthly_periods(window.start_date, window.end_date)
    for start, end in periods:
        try:
            all_runs.extend(
                fetch_runs_for_period(client, owner, repo, branch, start, end)
            )
        except Exception as err:  # noqa: BLE001 - retomada período a período
            logger.error(
                "Falha ao coletar %s/%s em %s..%s: %s",
                owner,
                repo,
                start.isoformat(),
                end.isoformat(),
                err,
            )
            raise

    filtered = filter_collected_runs(all_runs, window, branch)
    if cache:
        cache.mark_processed(
            PROGRESS_TASK,
            repo_progress_id,
            metadata={"periods": len(periods), "runs": len(filtered)},
        )
    return filtered


def count_valid_runs(runs: List[Dict[str, Any]]) -> int:
    """Conta runs com conclusão válida (sucesso ou falha)."""
    return sum(1 for run in runs if run.get("conclusion") in VALID_CONCLUSIONS)
