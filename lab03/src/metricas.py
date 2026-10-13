"""Módulo de cálculo e validação das métricas DORA (LAB03S02).

Implementa as 4 métricas clássicas DORA e suas variantes obrigatórias:
- RQ 01: Deployment Frequency (releases/semana)
- RQ 02: Lead Time for Changes (Variante a: por release; Variante b: por commit)
- RQ 03: Change Failure Rate (Variante a: proxy CI; Variante b: proxy entrega com censura)
- RQ 04: Failed Deployment Recovery Time (episódios por workflow com censura)
- Classificação DORA de Referência (Elite, High, Medium, Low)
"""

from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .config import parse_iso_datetime

# Conclusões de workflow válidas conforme Seção 3
VALID_SUCCESS_CONCLUSIONS = {"success"}
VALID_FAILURE_CONCLUSIONS = {"failure", "timed_out", "startup_failure"}
ALL_VALID_CONCLUSIONS = VALID_SUCCESS_CONCLUSIONS | VALID_FAILURE_CONCLUSIONS

# Padrão regex para SemVer (major.minor.patch)
SEMVER_REGEX = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:-.*)?$")

# Palavras-chave de releases/commits corretivos
CORRECTIVE_KEYWORDS = {"fix", "hotfix", "bugfix", "patch", "revert"}


def calculate_iqr(values: List[float]) -> Tuple[float, float, float]:
    """Calcula mediana, Q1 (25%), Q3 (75%) e IQR para uma lista numérica.

    Retorna tupla: (mediana, q1, q3).
    """
    if not values:
        return 0.0, 0.0, 0.0
    arr = np.array(values, dtype=float)
    q1 = float(np.percentile(arr, 25))
    med = float(np.median(arr))
    q3 = float(np.percentile(arr, 75))
    return med, q1, q3


# ==============================================================================
# RQ 01: Deployment Frequency
# ==============================================================================

def calculate_deployment_frequency(
    releases: List[Dict[str, Any]],
    window_start: datetime,
    window_end: datetime,
) -> Dict[str, Any]:
    """Calcula a frequência de deploy em releases publicadas por semana.

    Considera apenas releases com draft=False e prerelease=False na janela.
    """
    total_seconds = (window_end - window_start).total_seconds()
    total_weeks = max(1.0, total_seconds / (7.0 * 86400.0))

    valid_releases = []
    for rel in releases:
        if rel.get("draft", False) or rel.get("prerelease", False):
            continue
        pub_str = rel.get("published_at")
        if not pub_str:
            continue
        try:
            pub_dt = parse_iso_datetime(pub_str)
            if window_start <= pub_dt <= window_end:
                valid_releases.append(rel)
        except Exception:
            continue

    count = len(valid_releases)
    freq_weekly = count / total_weeks

    return {
        "valid_releases_count": count,
        "total_weeks": round(total_weeks, 2),
        "deployment_frequency_weekly": round(freq_weekly, 4),
        "releases_per_month": round(freq_weekly * (52.14 / 12.0), 4),
    }


# ==============================================================================
# RQ 02: Lead Time for Changes
# ==============================================================================

def calculate_lead_time(
    releases_data: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Calcula Lead Time for Changes em duas variantes obrigatórias.

    Estrutura esperada por elemento de releases_data:
    {
        "tag_name": "v1.1",
        "published_at": "2026-03-15T00:00:00Z",
        "has_previous_release": True,
        "compare_status_code": 200,   # ou 404 se compare falhou
        "commits": [
            {"sha": "abc", "author_date": "2026-03-02T00:00:00Z"},
            ...
        ]
    }

    Variante (a) Por Release:
      Lead time de R = data de R - data do commit mais antigo incluído em R.
      Valor do repositório = mediana entre suas releases.

    Variante (b) Por Commit:
      Cada commit incluído em R tem lead time = data de R - data do commit.
      Valor do repositório = mediana de todos os commits de todas as releases.
    """
    releases_lead_times_days: List[float] = []
    all_commits_lead_times_days: List[float] = []

    excluded_first_release_count = 0
    excluded_404_count = 0
    excluded_no_commits_count = 0
    evaluated_releases_count = 0

    for item in releases_data:
        # Se for a primeira release da história (sem release anterior)
        if not item.get("has_previous_release", True):
            excluded_first_release_count += 1
            continue

        # Se o endpoint de compare retornou 404
        if item.get("compare_status_code") == 404:
            excluded_404_count += 1
            continue

        pub_str = item.get("published_at")
        if not pub_str:
            continue
        rel_dt = parse_iso_datetime(pub_str)

        commits = item.get("commits", [])
        if not commits:
            excluded_no_commits_count += 1
            continue

        evaluated_releases_count += 1
        commit_dates: List[datetime] = []

        for c in commits:
            c_date_str = c.get("author_date") or c.get("commit", {}).get("author", {}).get("date")
            if not c_date_str:
                continue
            try:
                c_dt = parse_iso_datetime(c_date_str)
                commit_dates.append(c_dt)
                # Variante (b): lead time individual do commit em dias
                diff_days = max(0.0, (rel_dt - c_dt).total_seconds() / 86400.0)
                all_commits_lead_times_days.append(diff_days)
            except Exception:
                continue

        if commit_dates:
            oldest_commit_dt = min(commit_dates)
            # Variante (a): data de R - commit mais antigo em dias
            rel_lead_time_days = max(0.0, (rel_dt - oldest_commit_dt).total_seconds() / 86400.0)
            releases_lead_times_days.append(rel_lead_time_days)

    med_a, q1_a, q3_a = calculate_iqr(releases_lead_times_days)
    med_b, q1_b, q3_b = calculate_iqr(all_commits_lead_times_days)

    return {
        # Variante (a) - Por Release
        "lead_time_by_release_median_days": round(med_a, 3),
        "lead_time_by_release_q1_days": round(q1_a, 3),
        "lead_time_by_release_q3_days": round(q3_a, 3),
        "lead_time_by_release_iqr_days": round(q3_a - q1_a, 3),
        "evaluated_releases_count": evaluated_releases_count,
        # Variante (b) - Por Commit
        "lead_time_by_commit_median_days": round(med_b, 3),
        "lead_time_by_commit_q1_days": round(q1_b, 3),
        "lead_time_by_commit_q3_days": round(q3_b, 3),
        "lead_time_by_commit_iqr_days": round(q3_b - q1_b, 3),
        "total_commits_evaluated": len(all_commits_lead_times_days),
        # Casos de exclusão e borda
        "excluded_first_release_count": excluded_first_release_count,
        "excluded_404_count": excluded_404_count,
        "excluded_no_commits_count": excluded_no_commits_count,
    }


# ==============================================================================
# RQ 03: Change Failure Rate (CFR)
# ==============================================================================

def calculate_cfr_ci_proxy(
    workflow_runs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Calcula Change Failure Rate pela Variante (a) - Proxy de CI.

    Fórmula: nº de runs com falha ÷ (nº de falhas + nº de sucessos)
    Considera apenas runs do default branch disparados por push com conclusões válidas.
    """
    success_count = 0
    failure_count = 0
    ignored_count = 0

    for run in workflow_runs:
        conclusion = run.get("conclusion")
        if conclusion in VALID_SUCCESS_CONCLUSIONS:
            success_count += 1
        elif conclusion in VALID_FAILURE_CONCLUSIONS:
            failure_count += 1
        else:
            ignored_count += 1

    total_valid = success_count + failure_count
    cfr_ci = (failure_count / total_valid) if total_valid > 0 else 0.0

    return {
        "cfr_ci_proxy": round(cfr_ci, 4),
        "cfr_ci_percentage": round(cfr_ci * 100.0, 2),
        "success_runs_count": success_count,
        "failure_runs_count": failure_count,
        "ignored_runs_count": ignored_count,
        "total_valid_runs": total_valid,
    }


def is_patch_bump(tag_a: str, tag_b: str) -> bool:
    """Verifica se tag_b representa apenas um bump de PATCH no SemVer em relação a tag_a."""
    ma = SEMVER_REGEX.match(tag_a.strip())
    mb = SEMVER_REGEX.match(tag_b.strip())
    if not ma or not mb:
        return False
    maj_a, min_a, pat_a = map(int, ma.groups())
    maj_b, min_b, pat_b = map(int, mb.groups())
    return (maj_a == maj_b) and (min_a == min_b) and (pat_b > pat_a)


def is_corrective_release(
    current_release: Dict[str, Any],
    next_release: Dict[str, Any],
    commits_between: Optional[List[Dict[str, Any]]] = None,
) -> bool:
    """Aplica a heurística automática de release corretiva conforme Seção 5 (RQ 03 b).

    Critérios:
    1. A versão subsequente altera apenas o patch do SemVer (ex: 2.3.0 -> 2.3.1); e/ou
    2. O nome/tag da release subsequente contém palavras-chave (fix, hotfix, patch, bugfix, revert); e/ou
    3. Há commits entre as duas releases com 'fix', 'hotfix' ou 'revert' na mensagem.
    """
    tag_curr = current_release.get("tag_name", "")
    tag_next = next_release.get("tag_name", "")

    # 1. Checagem SemVer
    if is_patch_bump(tag_curr, tag_next):
        return True

    # 2. Checagem de palavras-chave no nome e na tag da release
    next_title = f"{next_release.get('name', '')} {tag_next}".lower()
    for kw in CORRECTIVE_KEYWORDS:
        if re.search(rf"\b{kw}\b", next_title):
            return True

    # 3. Checagem nos commits intermediários
    if commits_between:
        for c in commits_between:
            msg = (c.get("commit", {}).get("message") or c.get("message") or "").lower()
            for kw in CORRECTIVE_KEYWORDS:
                if re.search(rf"\b{kw}\b", msg):
                    return True

    return False


def calculate_cfr_delivery_proxy(
    releases: List[Dict[str, Any]],
    window_end: datetime,
    window_start: Optional[datetime] = None,
    commits_by_release_pair: Optional[Dict[str, List[Dict[str, Any]]]] = None,
) -> Dict[str, Any]:
    """Calcula Change Failure Rate pela Variante (b) - Proxy de Entrega.

    Uma release R é considerada FALHA se for seguida, em até 7 dias, por uma release corretiva.
    Censura obrigatória: Releases nos últimos 7 dias da janela ficam fora do denominador.
    """
    valid_releases = []
    for r in releases:
        if r.get("draft", False) or r.get("prerelease", False):
            continue
        pub_str = r.get("published_at")
        if not pub_str:
            continue
        try:
            r_dt = parse_iso_datetime(pub_str)
            if window_start and r_dt < window_start:
                continue
            if r_dt > window_end:
                continue
            valid_releases.append((r_dt, r))
        except Exception:
            continue

    # Ordena cronologicamente
    valid_releases.sort(key=lambda x: x[0])

    censorship_threshold = window_end.timestamp() - (7 * 86400.0)
    evaluated_count = 0
    failed_count = 0
    censored_count = 0

    n = len(valid_releases)
    for i in range(n):
        dt_curr, rel_curr = valid_releases[i]

        # Se publicada nos últimos 7 dias da janela, é censurada (fora do denominador)
        if dt_curr.timestamp() > censorship_threshold:
            censored_count += 1
            continue

        evaluated_count += 1
        is_failure = False

        # Procura release corretiva subsequente em até 7 dias (604.800s)
        for j in range(i + 1, n):
            dt_next, rel_next = valid_releases[j]
            diff_seconds = (dt_next - dt_curr).total_seconds()
            if diff_seconds > 7 * 86400.0:
                break  # Ultrapassou a janela de 7 dias

            pair_key = f"{rel_curr.get('tag_name')}...{rel_next.get('tag_name')}"
            commits = (commits_by_release_pair or {}).get(pair_key)

            if is_corrective_release(rel_curr, rel_next, commits):
                is_failure = True
                break

        if is_failure:
            failed_count += 1

    cfr_delivery = (failed_count / evaluated_count) if evaluated_count > 0 else 0.0

    return {
        "cfr_delivery_proxy": round(cfr_delivery, 4),
        "cfr_delivery_percentage": round(cfr_delivery * 100.0, 2),
        "evaluated_releases_count": evaluated_count,
        "failed_releases_count": failed_count,
        "censored_releases_count": censored_count,
    }


# ==============================================================================
# RQ 04: Failed Deployment Recovery Time
# ==============================================================================

def calculate_recovery_time_episodes(
    workflow_runs: List[Dict[str, Any]],
    window_end: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Calcula o tempo de recuperação em horas agrupando execuções por workflow.

    Um episódio começa na primeira falha após um sucesso (ou no primeiro run da série se falha)
    e encerra no run de sucesso subsequente desse mesmo workflow.
    Fórmula: fim da execução bem-sucedida (updated_at) - início da primeira falha (run_started_at).
    Episódio que nunca é recuperado antes do fim da janela é registrado como censurado.
    """
    # 1. Agrupa por workflow_id ou workflow_name
    runs_by_workflow: Dict[str, List[Dict[str, Any]]] = {}
    for run in workflow_runs:
        conclusion = run.get("conclusion")
        if conclusion not in ALL_VALID_CONCLUSIONS:
            continue

        wf_id = str(run.get("workflow_id") or run.get("name") or "default_workflow")
        if wf_id not in runs_by_workflow:
            runs_by_workflow[wf_id] = []
        runs_by_workflow[wf_id].append(run)

    recovery_times_hours: List[float] = []
    total_episodes = 0
    censored_episodes = 0

    for wf_id, runs in runs_by_workflow.items():
        # Ordena cronologicamente por created_at ou run_started_at
        runs_sorted = sorted(
            runs,
            key=lambda r: parse_iso_datetime(r.get("run_started_at") or r.get("created_at")),
        )

        in_episode = False
        episode_start_dt: Optional[datetime] = None

        for r in runs_sorted:
            conclusion = r.get("conclusion")
            r_start = parse_iso_datetime(r.get("run_started_at") or r.get("created_at"))
            r_end = parse_iso_datetime(r.get("updated_at") or r.get("created_at"))

            if conclusion in VALID_FAILURE_CONCLUSIONS:
                if not in_episode:
                    # Início de um novo episódio de falha
                    in_episode = True
                    episode_start_dt = r_start
                    total_episodes += 1
                # Se já estiver em episódio, continua no mesmo episódio (falhas consecutivas)
            elif conclusion in VALID_SUCCESS_CONCLUSIONS:
                if in_episode and episode_start_dt is not None:
                    # Término do episódio de falha!
                    duration_hours = max(0.0, (r_end - episode_start_dt).total_seconds() / 3600.0)
                    recovery_times_hours.append(duration_hours)
                    in_episode = False
                    episode_start_dt = None

        # Se terminou a lista de runs e o episódio não foi recuperado -> Censurado
        if in_episode:
            censored_episodes += 1

    med_rec, q1_rec, q3_rec = calculate_iqr(recovery_times_hours)
    censored_ratio = (censored_episodes / total_episodes) if total_episodes > 0 else 0.0

    return {
        "recovery_time_median_hours": round(med_rec, 3),
        "recovery_time_q1_hours": round(q1_rec, 3),
        "recovery_time_q3_hours": round(q3_rec, 3),
        "recovery_time_iqr_hours": round(q3_rec - q1_rec, 3),
        "total_episodes_count": total_episodes,
        "recovered_episodes_count": len(recovery_times_hours),
        "censored_episodes_count": censored_episodes,
        "censored_episodes_ratio": round(censored_ratio, 4),
    }


# ==============================================================================
# Classificação DORA de Referência (C1)
# ==============================================================================

def classify_metric_category(
    value: float,
    thresholds: List[Tuple[float, str]],
    lower_is_better: bool = False,
) -> str:
    """Classifica um valor nas categorias DORA ('Elite', 'High', 'Medium', 'Low')."""
    if lower_is_better:
        # Menor é melhor (Lead Time, CFR, Recovery Time)
        for limit, category in thresholds:
            if value < limit or math.isclose(value, limit, rel_tol=1e-5):
                return category
        return "Low"
    else:
        # Maior é melhor (Deployment Frequency)
        for limit, category in thresholds:
            if value >= limit:
                return category
        return "Low"


def classify_dora_reference(
    deployment_frequency_weekly: float,
    lead_time_days: float,
    cfr: float,
    recovery_time_hours: float,
) -> Dict[str, Any]:
    """Aplica a tabela oficial de cortes DORA da Seção 5 do enunciado.

    Pontuação: Elite=4, High=3, Medium=2, Low=1.
    Classificação geral: mediana dos 4 valores arredondada para baixo.
    """
    # 1. Deployment frequency (releases por semana)
    # Elite: >= 7 | High: >= 1 e < 7 | Medium: >= 0.23 (1/mes) e < 1 | Low: < 0.23
    if deployment_frequency_weekly >= 7.0:
        cat_df = "Elite"
    elif deployment_frequency_weekly >= 1.0:
        cat_df = "High"
    elif deployment_frequency_weekly >= (52.14 / 12.0) / 4.345 or deployment_frequency_weekly >= 0.23:
        cat_df = "Medium"
    else:
        cat_df = "Low"

    # 2. Lead time (dias)
    # Elite: < 1 | High: 1 a < 7 | Medium: 7 a < 30 | Low: >= 30
    if lead_time_days < 1.0:
        cat_lt = "Elite"
    elif lead_time_days < 7.0:
        cat_lt = "High"
    elif lead_time_days < 30.0:
        cat_lt = "Medium"
    else:
        cat_lt = "Low"

    # 3. Change failure rate (proporção decimal 0.0 a 1.0)
    # Elite: <= 15% (0.15) | High: > 15% e <= 30% | Medium: > 30% e <= 45% | Low: > 45%
    if cfr <= 0.15:
        cat_cfr = "Elite"
    elif cfr <= 0.30:
        cat_cfr = "High"
    elif cfr <= 0.45:
        cat_cfr = "Medium"
    else:
        cat_cfr = "Low"

    # 4. Recovery time (horas)
    # Elite: < 1 hora | High: 1 hora a < 24 horas (1 dia) | Medium: 24h a < 168h (1 semana) | Low: >= 168h
    if recovery_time_hours < 1.0:
        cat_rec = "Elite"
    elif recovery_time_hours < 24.0:
        cat_rec = "High"
    elif recovery_time_hours < 168.0:
        cat_rec = "Medium"
    else:
        cat_rec = "Low"

    score_map = {"Elite": 4, "High": 3, "Medium": 2, "Low": 1}
    scores = [score_map[cat_df], score_map[cat_lt], score_map[cat_cfr], score_map[cat_rec]]
    overall_median_score = math.floor(float(np.median(scores)))

    inv_score_map = {4: "Elite", 3: "High", 2: "Medium", 1: "Low"}
    overall_category = inv_score_map.get(overall_median_score, "Low")

    return {
        "df_category": cat_df,
        "lead_time_category": cat_lt,
        "cfr_category": cat_cfr,
        "recovery_time_category": cat_rec,
        "scores": scores,
        "overall_score": overall_median_score,
        "overall_dora_category": overall_category,
    }


# ==============================================================================
# Consolidação Completa por Repositório
# ==============================================================================

def compute_all_metrics_for_repository(
    repo_meta: Dict[str, Any],
    releases: List[Dict[str, Any]],
    releases_data_with_commits: List[Dict[str, Any]],
    workflow_runs: List[Dict[str, Any]],
    window_start: datetime,
    window_end: datetime,
    commits_by_release_pair: Optional[Dict[str, List[Dict[str, Any]]]] = None,
) -> Dict[str, Any]:
    """Calcula todas as 4 métricas DORA e a classificação C1 para um repositório."""
    # RQ 01
    df_res = calculate_deployment_frequency(releases, window_start, window_end)

    # RQ 02
    lt_res = calculate_lead_time(releases_data_with_commits)

    # RQ 03
    cfr_ci_res = calculate_cfr_ci_proxy(workflow_runs)
    cfr_del_res = calculate_cfr_delivery_proxy(
        releases, window_end, window_start, commits_by_release_pair
    )

    # RQ 04
    rt_res = calculate_recovery_time_episodes(workflow_runs, window_end)

    # Classificação DORA C1 (referência oficial: DF, LT variante a, CFR variante a, RT)
    dora_c1 = classify_dora_reference(
        deployment_frequency_weekly=df_res["deployment_frequency_weekly"],
        lead_time_days=lt_res["lead_time_by_release_median_days"],
        cfr=cfr_ci_res["cfr_ci_proxy"],
        recovery_time_hours=rt_res["recovery_time_median_hours"],
    )

    consolidated = {
        "full_name": repo_meta.get("full_name"),
        "stars": repo_meta.get("stars", 0),
        "primary_language": repo_meta.get("primary_language", "Unknown"),
        "age_years": repo_meta.get("age_years", 0.0),
        "contributors_count": repo_meta.get("contributors_count", -1),
        # RQ 01
        "deployment_frequency_weekly": df_res["deployment_frequency_weekly"],
        "valid_releases_count": df_res["valid_releases_count"],
        # RQ 02
        "lead_time_by_release_days": lt_res["lead_time_by_release_median_days"],
        "lead_time_by_release_iqr_days": lt_res["lead_time_by_release_iqr_days"],
        "lead_time_by_commit_days": lt_res["lead_time_by_commit_median_days"],
        "lead_time_by_commit_iqr_days": lt_res["lead_time_by_commit_iqr_days"],
        "total_commits_evaluated": lt_res["total_commits_evaluated"],
        "excluded_first_release_count": lt_res["excluded_first_release_count"],
        # RQ 03
        "cfr_ci_proxy": cfr_ci_res["cfr_ci_proxy"],
        "cfr_ci_percentage": cfr_ci_res["cfr_ci_percentage"],
        "cfr_delivery_proxy": cfr_del_res["cfr_delivery_proxy"],
        "cfr_delivery_percentage": cfr_del_res["cfr_delivery_percentage"],
        "cfr_delivery_censored_count": cfr_del_res["censored_releases_count"],
        # RQ 04
        "recovery_time_hours": rt_res["recovery_time_median_hours"],
        "recovery_time_iqr_hours": rt_res["recovery_time_iqr_hours"],
        "recovery_total_episodes": rt_res["total_episodes_count"],
        "recovery_censored_episodes": rt_res["censored_episodes_count"],
        "recovery_censored_ratio": rt_res["censored_episodes_ratio"],
        # Classificação DORA C1
        "dora_overall_category": dora_c1["overall_dora_category"],
        "dora_df_category": dora_c1["df_category"],
        "dora_lt_category": dora_c1["lead_time_category"],
        "dora_cfr_category": dora_c1["cfr_category"],
        "dora_rt_category": dora_c1["recovery_time_category"],
    }

    return consolidated
