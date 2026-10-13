"""Testes unitários rigorosos para o módulo de métricas DORA (lab03/src/metricas.py).

Cobre:
- RQ 01: Deployment Frequency
- RQ 02: Lead Time for Changes (Variante a e b + casos de borda 404/sem release anterior)
- RQ 03: Change Failure Rate (Proxy CI e Proxy Entrega com censura de 7 dias)
- RQ 04: Recovery Time (episódios por workflow, duração em horas, censura estatística)
- Classificação DORA C1
"""

from datetime import datetime, timezone
import pytest

from lab03.src.metricas import (
    calculate_cfr_ci_proxy,
    calculate_cfr_delivery_proxy,
    calculate_deployment_frequency,
    calculate_iqr,
    calculate_lead_time,
    calculate_recovery_time_episodes,
    classify_dora_reference,
    compute_all_metrics_for_repository,
    is_corrective_release,
    is_patch_bump,
)


# ==============================================================================
# Testes RQ 01: Deployment Frequency
# ==============================================================================

def test_deployment_frequency_standard():
    win_start = datetime(2025, 10, 1, 0, 0, 0, tzinfo=timezone.utc)
    win_end = datetime(2026, 9, 30, 23, 59, 59, tzinfo=timezone.utc)

    # Cria 52 releases (1 por semana em média)
    releases = []
    for week in range(52):
        releases.append({
            "tag_name": f"v1.{week}.0",
            "draft": False,
            "prerelease": False,
            "published_at": f"2025-10-{(week % 25) + 1:02d}T12:00:00Z",
        })

    # Adiciona 1 release draft e 1 prerelease (devem ser ignoradas)
    releases.append({
        "tag_name": "v1.99.0-rc1",
        "draft": False,
        "prerelease": True,
        "published_at": "2025-11-01T12:00:00Z",
    })
    releases.append({
        "tag_name": "v1.99.0-draft",
        "draft": True,
        "prerelease": False,
        "published_at": "2025-11-02T12:00:00Z",
    })

    res = calculate_deployment_frequency(releases, win_start, win_end)
    assert res["valid_releases_count"] == 52
    assert 0.98 <= res["deployment_frequency_weekly"] <= 1.02


def test_deployment_frequency_empty():
    win_start = datetime(2025, 10, 1, 0, 0, 0, tzinfo=timezone.utc)
    win_end = datetime(2026, 9, 30, 23, 59, 59, tzinfo=timezone.utc)

    res = calculate_deployment_frequency([], win_start, win_end)
    assert res["valid_releases_count"] == 0
    assert res["deployment_frequency_weekly"] == 0.0


# ==============================================================================
# Testes RQ 02: Lead Time for Changes
# ==============================================================================

def test_lead_time_official_example():
    """Valida o exemplo numérico oficial da Seção 5 do enunciado:

    A release v1.1 foi publicada em 15/03 e inclui três commits, de 02/03, 10/03 e 14/03.
    - Variante (a): lead time de v1.1 é 15/03 - 02/03 = 13 dias.
    - Variante (b): três commits com 13, 5 e 1 dias. Mediana = 5 dias.
    """
    releases_data = [
        {
            "tag_name": "v1.1",
            "published_at": "2026-03-15T00:00:00Z",
            "has_previous_release": True,
            "compare_status_code": 200,
            "commits": [
                {"sha": "c1", "author_date": "2026-03-02T00:00:00Z"},
                {"sha": "c2", "author_date": "2026-03-10T00:00:00Z"},
                {"sha": "c3", "author_date": "2026-03-14T00:00:00Z"},
            ],
        }
    ]

    res = calculate_lead_time(releases_data)
    # Variante (a)
    assert res["lead_time_by_release_median_days"] == 13.0
    # Variante (b)
    assert res["lead_time_by_commit_median_days"] == 5.0
    assert res["total_commits_evaluated"] == 3
    assert res["evaluated_releases_count"] == 1


def test_lead_time_exclusions():
    """Valida casos de borda: primeira release (sem anterior) e erro 404 em compare."""
    releases_data = [
        # 1ª release da história do repositório
        {
            "tag_name": "v1.0",
            "published_at": "2026-01-01T00:00:00Z",
            "has_previous_release": False,
            "commits": [{"sha": "c0", "author_date": "2025-12-01T00:00:00Z"}],
        },
        # Release com compare 404 (tag apagada)
        {
            "tag_name": "v1.2",
            "published_at": "2026-02-01T00:00:00Z",
            "has_previous_release": True,
            "compare_status_code": 404,
            "commits": [],
        },
        # Release sem novos commits
        {
            "tag_name": "v1.3",
            "published_at": "2026-03-01T00:00:00Z",
            "has_previous_release": True,
            "compare_status_code": 200,
            "commits": [],
        },
    ]

    res = calculate_lead_time(releases_data)
    assert res["excluded_first_release_count"] == 1
    assert res["excluded_404_count"] == 1
    assert res["excluded_no_commits_count"] == 1
    assert res["evaluated_releases_count"] == 0
    assert res["lead_time_by_release_median_days"] == 0.0


# ==============================================================================
# Testes RQ 03: Change Failure Rate
# ==============================================================================

def test_cfr_ci_proxy():
    workflow_runs = [
        {"id": 1, "conclusion": "success"},
        {"id": 2, "conclusion": "success"},
        {"id": 3, "conclusion": "success"},
        {"id": 4, "conclusion": "failure"},
        {"id": 5, "conclusion": "timed_out"},         # conta como falha
        {"id": 6, "conclusion": "startup_failure"},   # conta como falha
        {"id": 7, "conclusion": "cancelled"},         # ignorado
        {"id": 8, "conclusion": "skipped"},           # ignorado
    ]

    res = calculate_cfr_ci_proxy(workflow_runs)
    # Sucessos: 3, Falhas: 3 (failure + timed_out + startup_failure) -> Total válido: 6
    # CFR = 3 / 6 = 0.50 (50%)
    assert res["success_runs_count"] == 3
    assert res["failure_runs_count"] == 3
    assert res["ignored_runs_count"] == 2
    assert res["cfr_ci_proxy"] == 0.50
    assert res["cfr_ci_percentage"] == 50.0


def test_is_patch_bump():
    assert is_patch_bump("v2.3.0", "v2.3.1")
    assert is_patch_bump("1.0.0", "1.0.1")
    assert not is_patch_bump("v2.3.0", "v2.4.0")  # Minor bump
    assert not is_patch_bump("v2.3.0", "v3.0.0")  # Major bump


def test_cfr_delivery_proxy_official_example():
    """Valida o exemplo oficial da Seção 5:

    - v2.3.0 (10/05) seguida por v2.3.1 (12/05) patch com fix -> v2.3.0 falhou!
    - v2.4.0 (01/06) seguida por v2.5.0 (20/06) -> v2.4.0 não falhou!
    - Release nos últimos 7 dias da janela -> Censurada do denominador.
    """
    win_end = datetime(2026, 10, 1, 0, 0, 0, tzinfo=timezone.utc)

    releases = [
        {"tag_name": "v2.3.0", "published_at": "2026-05-10T00:00:00Z"},
        {"tag_name": "v2.3.1", "name": "Patch release", "published_at": "2026-05-12T00:00:00Z"},
        {"tag_name": "v2.4.0", "published_at": "2026-06-01T00:00:00Z"},
        {"tag_name": "v2.5.0", "published_at": "2026-06-20T00:00:00Z"},
        # Release nos últimos 7 dias (ex: 29/09 quando a janela termina em 01/10)
        {"tag_name": "v2.6.0", "published_at": "2026-09-29T00:00:00Z"},
    ]

    commits_by_pair = {
        "v2.3.0...v2.3.1": [
            {"commit": {"message": "fix: crash ao abrir arquivo"}}
        ]
    }

    res = calculate_cfr_delivery_proxy(
        releases=releases,
        window_end=win_end,
        commits_by_release_pair=commits_by_pair,
    )

    # v2.6.0 foi censurada (últimos 7 dias)
    assert res["censored_releases_count"] == 1
    # Das outras releases elegíveis avaliadas, apenas v2.3.0 falhou
    assert res["failed_releases_count"] == 1
    assert res["cfr_delivery_proxy"] > 0.0


# ==============================================================================
# Testes RQ 04: Failed Deployment Recovery Time
# ==============================================================================

def test_recovery_time_official_example():
    """Valida o exemplo oficial da Seção 5 (workflow CI, branch main):

    09:00 success
    10:00 failure <- início do episódio
    10:30 failure (mesmo episódio)
    11:15 success <- fim do episódio (terminou às 11:20)
    Tempo de recuperação: 11:20 - 10:00 = 1h20 (1.333 horas).
    """
    runs = [
        {
            "id": 1,
            "workflow_id": "CI",
            "conclusion": "success",
            "run_started_at": "2026-05-10T09:00:00Z",
            "updated_at": "2026-05-10T09:05:00Z",
        },
        {
            "id": 2,
            "workflow_id": "CI",
            "conclusion": "failure",
            "run_started_at": "2026-05-10T10:00:00Z",
            "updated_at": "2026-05-10T10:05:00Z",
        },
        {
            "id": 3,
            "workflow_id": "CI",
            "conclusion": "failure",
            "run_started_at": "2026-05-10T10:30:00Z",
            "updated_at": "2026-05-10T10:35:00Z",
        },
        {
            "id": 4,
            "workflow_id": "CI",
            "conclusion": "success",
            "run_started_at": "2026-05-10T11:15:00Z",
            "updated_at": "2026-05-10T11:20:00Z",
        },
    ]

    res = calculate_recovery_time_episodes(runs)
    assert res["total_episodes_count"] == 1
    assert res["recovered_episodes_count"] == 1
    assert res["censored_episodes_count"] == 0
    # 1h20 = 1 + 20/60 = 1.333 horas
    assert round(res["recovery_time_median_hours"], 2) == 1.33


def test_recovery_time_censored_episode():
    """Episódio que inicia em falha e não tem execução bem-sucedida até o fim da janela."""
    runs = [
        {
            "id": 1,
            "workflow_id": "CI",
            "conclusion": "success",
            "run_started_at": "2026-05-10T09:00:00Z",
            "updated_at": "2026-05-10T09:05:00Z",
        },
        {
            "id": 2,
            "workflow_id": "CI",
            "conclusion": "failure",
            "run_started_at": "2026-05-10T10:00:00Z",
            "updated_at": "2026-05-10T10:05:00Z",
        },
    ]

    res = calculate_recovery_time_episodes(runs)
    assert res["total_episodes_count"] == 1
    assert res["recovered_episodes_count"] == 0
    assert res["censored_episodes_count"] == 1
    assert res["censored_episodes_ratio"] == 1.0


# ==============================================================================
# Testes Classificação DORA C1
# ==============================================================================

def test_classify_dora_reference_official_example():
    """Valida o exemplo oficial da Seção 5:

    Notas (4, 3, 3, 1) -> mediana 3 -> 'High'.
    DF: Elite (>=7) -> 4
    LT: High (1 a < 7) -> 3
    CFR: High (>15% e <=30%) -> 3
    RT: Low (>= 168h) -> 1
    """
    res = classify_dora_reference(
        deployment_frequency_weekly=8.0,  # Elite -> 4
        lead_time_days=3.0,              # High -> 3
        cfr=0.20,                        # High -> 3
        recovery_time_hours=200.0,       # Low -> 1
    )

    assert res["df_category"] == "Elite"
    assert res["lead_time_category"] == "High"
    assert res["cfr_category"] == "High"
    assert res["recovery_time_category"] == "Low"
    assert res["overall_score"] == 3
    assert res["overall_dora_category"] == "High"


def test_compute_all_metrics_for_repository():
    win_start = datetime(2025, 10, 1, 0, 0, 0, tzinfo=timezone.utc)
    win_end = datetime(2026, 9, 30, 23, 59, 59, tzinfo=timezone.utc)

    repo_meta = {
        "full_name": "tiangolo/fastapi",
        "stars": 75000,
        "primary_language": "Python",
        "age_years": 6.0,
        "contributors_count": 500,
    }

    releases = [
        {"tag_name": "0.115.0", "draft": False, "prerelease": False, "published_at": "2026-05-01T10:00:00Z"},
        {"tag_name": "0.115.1", "draft": False, "prerelease": False, "published_at": "2026-05-04T10:00:00Z"},
    ]

    releases_data_with_commits = [
        {
            "tag_name": "0.115.0",
            "published_at": "2026-05-01T10:00:00Z",
            "has_previous_release": True,
            "commits": [{"author_date": "2026-04-20T10:00:00Z"}],
        }
    ]

    workflow_runs = [
        {"conclusion": "success", "run_started_at": "2026-05-01T08:00:00Z", "updated_at": "2026-05-01T08:10:00Z"},
        {"conclusion": "failure", "run_started_at": "2026-05-02T08:00:00Z", "updated_at": "2026-05-02T08:05:00Z"},
        {"conclusion": "success", "run_started_at": "2026-05-02T09:00:00Z", "updated_at": "2026-05-02T09:15:00Z"},
    ]

    consolidated = compute_all_metrics_for_repository(
        repo_meta=repo_meta,
        releases=releases,
        releases_data_with_commits=releases_data_with_commits,
        workflow_runs=workflow_runs,
        window_start=win_start,
        window_end=win_end,
    )

    assert consolidated["full_name"] == "tiangolo/fastapi"
    assert "deployment_frequency_weekly" in consolidated
    assert "lead_time_by_release_days" in consolidated
    assert "lead_time_by_commit_days" in consolidated
    assert "cfr_ci_proxy" in consolidated
    assert "cfr_delivery_proxy" in consolidated
    assert "recovery_time_hours" in consolidated
    assert "dora_overall_category" in consolidated


def test_is_corrective_release_via_commit_messages():
    curr = {"tag_name": "v1.2.0", "name": "Feature Release"}
    next_rel = {"tag_name": "v1.2.1", "name": "Maintenance"}

    # Commit com 'fix'
    commits_fix = [{"commit": {"message": "fix(core): resolve null pointer exception"}}]
    assert is_corrective_release(curr, next_rel, commits_fix)

    # Commit com 'revert'
    commits_revert = [{"commit": {"message": "revert: rollback broken commit"}}]
    assert is_corrective_release(curr, next_rel, commits_revert)

    # Commit sem termos corretivos e sem patch bump
    curr_minor = {"tag_name": "v1.2.0"}
    next_minor = {"tag_name": "v1.3.0"}
    commits_feat = [{"commit": {"message": "feat: add new dashboard UI"}}]
    assert not is_corrective_release(curr_minor, next_minor, commits_feat)


def test_classify_dora_reference_low_and_medium():
    # Caso Low em todas
    res_low = classify_dora_reference(
        deployment_frequency_weekly=0.05,  # Low (< 0.23)
        lead_time_days=45.0,              # Low (>= 30)
        cfr=0.60,                         # Low (> 45%)
        recovery_time_hours=200.0,        # Low (>= 168h)
    )
    assert res_low["overall_dora_category"] == "Low"
    assert res_low["df_category"] == "Low"
    assert res_low["lead_time_category"] == "Low"
    assert res_low["cfr_category"] == "Low"
    assert res_low["recovery_time_category"] == "Low"

    # Caso Medium
    res_med = classify_dora_reference(
        deployment_frequency_weekly=0.5,   # Medium (>= 0.23 e < 1.0)
        lead_time_days=15.0,              # Medium (7 a < 30)
        cfr=0.35,                         # Medium (> 30% e <= 45%)
        recovery_time_hours=50.0,         # Medium (24h a < 168h)
    )
    assert res_med["overall_dora_category"] == "Medium"
    assert res_med["df_category"] == "Medium"
    assert res_med["lead_time_category"] == "Medium"
    assert res_med["cfr_category"] == "Medium"
    assert res_med["recovery_time_category"] == "Medium"
