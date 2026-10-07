"""Classificação de workflow runs e métricas de qualidade das entregas (LAB03S01).

Este módulo é puro (sem I/O de rede): recebe runs já coletados e aplica as
definições operacionais da Seção 3 do laboratório.

- Classificação centralizada de `conclusion` (sucesso / falha / ignorar).
- CFR — variante CI (RQ 03a): falhas / (falhas + sucessos).
- Failed Deployment Recovery Time (RQ 04): episódios de falha por workflow,
  com censura quando a recuperação não ocorre dentro da janela.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence

from .config import parse_iso_datetime

SUCCESS_CONCLUSIONS = frozenset({"success"})
FAILURE_CONCLUSIONS = frozenset({"failure", "timed_out", "startup_failure"})
IGNORED_CONCLUSIONS = frozenset(
    {"cancelled", "skipped", "neutral", "action_required", "stale"}
)
VALID_CONCLUSIONS = SUCCESS_CONCLUSIONS | FAILURE_CONCLUSIONS

CLASS_SUCCESS = "sucesso"
CLASS_FAILURE = "falha"
CLASS_IGNORE = "ignorar"


def classify_conclusion(conclusion: Optional[str]) -> str:
    """Classifica o campo `conclusion` segundo a tabela obrigatória do laboratório."""
    if conclusion is None:
        return CLASS_IGNORE
    value = str(conclusion).strip().lower()
    if not value:
        return CLASS_IGNORE
    if value in SUCCESS_CONCLUSIONS:
        return CLASS_SUCCESS
    if value in FAILURE_CONCLUSIONS:
        return CLASS_FAILURE
    return CLASS_IGNORE


def classify_run(run: Any) -> str:
    """Classifica um workflow run (dict ou objeto com atributo/campo conclusion)."""
    if isinstance(run, dict):
        return classify_conclusion(run.get("conclusion"))
    conclusion = getattr(run, "conclusion", None)
    return classify_conclusion(conclusion)


def is_valid_run(run: Any) -> bool:
    """True quando o run entra no denominador das métricas (sucesso ou falha)."""
    return classify_run(run) in {CLASS_SUCCESS, CLASS_FAILURE}


def compute_cfr_ci(runs: Iterable[Any]) -> Optional[float]:
    """Change Failure Rate — variante CI.

    CFR = n_falhas / (n_falhas + n_sucessos).
    Runs ignorados não entram. Retorna None se não houver runs válidos.
    """
    n_success = 0
    n_failure = 0
    for run in runs:
        outcome = classify_run(run)
        if outcome == CLASS_SUCCESS:
            n_success += 1
        elif outcome == CLASS_FAILURE:
            n_failure += 1
    denominator = n_success + n_failure
    if denominator == 0:
        return None
    return n_failure / denominator


def _parse_optional_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return parse_iso_datetime(value)
    except (ValueError, TypeError, AttributeError):
        return None


def _run_started_at(run: Dict[str, Any]) -> Optional[datetime]:
    return _parse_optional_datetime(run.get("run_started_at")) or _parse_optional_datetime(
        run.get("created_at")
    )


def _run_updated_at(run: Dict[str, Any]) -> Optional[datetime]:
    return _parse_optional_datetime(run.get("updated_at")) or _run_started_at(run)


def _workflow_id(run: Dict[str, Any]) -> Any:
    return run.get("workflow_id")


_EPOCH = parse_iso_datetime("1970-01-01T00:00:00Z")


def _sort_key(run: Dict[str, Any]) -> datetime:
    started = _run_started_at(run)
    return started if started is not None else _EPOCH


@dataclass
class FailureEpisode:
    """Um episódio de falha de um workflow (RQ 04)."""

    repo: str
    workflow_id: Any
    first_failure_id: Any
    first_failure_started_at: str
    failures_in_episode: int
    censored: bool
    recovery_run_id: Any = ""
    recovery_updated_at: str = ""
    recovery_hours: Optional[float] = None


def compute_failure_episodes(
    repo: str,
    runs: Sequence[Dict[str, Any]],
) -> List[FailureEpisode]:
    """Identifica episódios de falha por workflow.

    Ordena as execuções válidas de cada workflow. Um episódio começa na
    primeira falha após um sucesso e termina na próxima execução bem-sucedida.
    O tempo de recuperação é `updated_at` do sucesso − `run_started_at` da
    primeira falha. Sem sucesso posterior na janela, o episódio é censurado.
    """
    by_workflow: Dict[Any, List[Dict[str, Any]]] = {}
    for run in runs:
        if not isinstance(run, dict):
            continue
        outcome = classify_run(run)
        if outcome == CLASS_IGNORE:
            continue
        by_workflow.setdefault(_workflow_id(run), []).append(run)

    episodes: List[FailureEpisode] = []
    for workflow_id, workflow_runs in by_workflow.items():
        ordered = sorted(workflow_runs, key=_sort_key)
        seen_success = False
        episode_failures: List[Dict[str, Any]] = []

        for run in ordered:
            outcome = classify_run(run)
            if outcome == CLASS_SUCCESS:
                if episode_failures:
                    first = episode_failures[0]
                    started = _run_started_at(first)
                    ended = _run_updated_at(run)
                    hours = None
                    if started is not None and ended is not None:
                        hours = (ended - started).total_seconds() / 3600.0
                    episodes.append(
                        FailureEpisode(
                            repo=repo,
                            workflow_id=workflow_id,
                            first_failure_id=first.get("id"),
                            first_failure_started_at=started.isoformat() if started else "",
                            failures_in_episode=len(episode_failures),
                            censored=False,
                            recovery_run_id=run.get("id"),
                            recovery_updated_at=ended.isoformat() if ended else "",
                            recovery_hours=hours,
                        )
                    )
                    episode_failures = []
                seen_success = True
            elif outcome == CLASS_FAILURE:
                if seen_success:
                    episode_failures.append(run)

        if episode_failures:
            first = episode_failures[0]
            started = _run_started_at(first)
            episodes.append(
                FailureEpisode(
                    repo=repo,
                    workflow_id=workflow_id,
                    first_failure_id=first.get("id"),
                    first_failure_started_at=started.isoformat() if started else "",
                    failures_in_episode=len(episode_failures),
                    censored=True,
                )
            )

    return episodes


def median_or_none(values: Iterable[float]) -> Optional[float]:
    data = list(values)
    if not data:
        return None
    return float(statistics.median(data))


@dataclass
class RepoCiSummary:
    """Resumo de CFR (CI) e tempo de recuperação por repositório."""

    repo: str
    default_branch: str = ""
    total_runs_coletados: int = 0
    runs_sucesso: int = 0
    runs_falha: int = 0
    runs_ignorados: int = 0
    cfr_ci: Optional[float] = None
    episodios_recuperados: int = 0
    episodios_censurados: int = 0
    proporcao_censurados: Optional[float] = None
    mediana_recuperacao_horas: Optional[float] = None
    erro: str = ""


def summarize_repository_ci(
    repo: str,
    runs: Sequence[Dict[str, Any]],
    episodes: Sequence[FailureEpisode],
    default_branch: str = "",
    erro: str = "",
) -> RepoCiSummary:
    """Agrega classificação, CFR e episódios de um repositório."""
    n_success = n_failure = n_ignore = 0
    for run in runs:
        outcome = classify_run(run)
        if outcome == CLASS_SUCCESS:
            n_success += 1
        elif outcome == CLASS_FAILURE:
            n_failure += 1
        else:
            n_ignore += 1

    recovered = [ep for ep in episodes if not ep.censored]
    censored = [ep for ep in episodes if ep.censored]
    total_episodes = len(episodes)
    recovery_hours = [
        ep.recovery_hours for ep in recovered if ep.recovery_hours is not None
    ]

    return RepoCiSummary(
        repo=repo,
        default_branch=default_branch,
        total_runs_coletados=len(runs),
        runs_sucesso=n_success,
        runs_falha=n_failure,
        runs_ignorados=n_ignore,
        cfr_ci=compute_cfr_ci(runs),
        episodios_recuperados=len(recovered),
        episodios_censurados=len(censored),
        proporcao_censurados=(len(censored) / total_episodes) if total_episodes else None,
        mediana_recuperacao_horas=median_or_none(recovery_hours),
        erro=erro,
    )
