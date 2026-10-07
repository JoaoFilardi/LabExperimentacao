"""Testes das regras de classificação, CFR (CI) e tempo de recuperação."""

from lab03.src.metricas_ci import (
    CLASS_FAILURE,
    CLASS_IGNORE,
    CLASS_SUCCESS,
    classify_conclusion,
    classify_run,
    compute_cfr_ci,
    compute_failure_episodes,
    summarize_repository_ci,
)
from lab03.tests.fakes import make_workflow_run


def test_classify_sucesso():
    run = make_workflow_run(1, "2024-08-01T09:00:00Z", "success")
    assert classify_run(run) == CLASS_SUCCESS
    assert classify_conclusion("success") == CLASS_SUCCESS


def test_classify_falhas():
    assert classify_conclusion("failure") == CLASS_FAILURE
    assert classify_conclusion("timed_out") == CLASS_FAILURE
    assert classify_conclusion("startup_failure") == CLASS_FAILURE


def test_classify_conclusoes_ignoradas():
    for conclusion in (
        "cancelled",
        "skipped",
        "neutral",
        "action_required",
        "stale",
        None,
        "",
        "  ",
    ):
        assert classify_conclusion(conclusion) == CLASS_IGNORE


def test_cfr_ci_sucesso_e_falha():
    runs = [
        make_workflow_run(1, "2024-08-01T09:00:00Z", "success"),
        make_workflow_run(2, "2024-08-01T10:00:00Z", "failure"),
        make_workflow_run(3, "2024-08-01T11:00:00Z", "cancelled"),
        make_workflow_run(4, "2024-08-01T12:00:00Z", "success"),
    ]
    # 1 falha / (1 falha + 2 sucessos) = 1/3
    assert compute_cfr_ci(runs) == 1 / 3


def test_cfr_ci_sem_runs_validos_retorna_none():
    runs = [
        make_workflow_run(1, "2024-08-01T09:00:00Z", "cancelled"),
        make_workflow_run(2, "2024-08-01T10:00:00Z", "skipped"),
    ]
    assert compute_cfr_ci(runs) is None
    assert compute_cfr_ci([]) is None


def test_episodio_inicio_e_termino_rq04():
    """Exemplo da RQ 04: 10:00 failure ... 11:20 success = 1h20."""
    runs = [
        make_workflow_run(
            1, "2024-08-01T09:00:00Z", "success", updated_at="2024-08-01T09:05:00Z"
        ),
        make_workflow_run(
            2,
            "2024-08-01T10:00:00Z",
            "failure",
            run_started_at="2024-08-01T10:00:00Z",
            updated_at="2024-08-01T10:10:00Z",
        ),
        make_workflow_run(
            3,
            "2024-08-01T10:30:00Z",
            "failure",
            run_started_at="2024-08-01T10:30:00Z",
        ),
        make_workflow_run(
            4,
            "2024-08-01T11:15:00Z",
            "success",
            run_started_at="2024-08-01T11:15:00Z",
            updated_at="2024-08-01T11:20:00Z",
        ),
    ]
    episodes = compute_failure_episodes("o/r", runs)
    assert len(episodes) == 1
    ep = episodes[0]
    assert ep.censored is False
    assert ep.failures_in_episode == 2
    assert ep.first_failure_id == 2
    assert ep.recovery_run_id == 4
    assert ep.recovery_hours == 1 + 20 / 60


def test_episodio_censurado():
    runs = [
        make_workflow_run(1, "2024-08-01T09:00:00Z", "success"),
        make_workflow_run(
            2, "2024-08-01T10:00:00Z", "failure", run_started_at="2024-08-01T10:00:00Z"
        ),
    ]
    episodes = compute_failure_episodes("o/r", runs)
    assert len(episodes) == 1
    assert episodes[0].censored is True
    assert episodes[0].recovery_hours is None
    assert episodes[0].first_failure_id == 2


def test_multiplas_falhas_antes_da_recuperacao():
    runs = [
        make_workflow_run(1, "2024-08-01T08:00:00Z", "success"),
        make_workflow_run(2, "2024-08-01T09:00:00Z", "failure"),
        make_workflow_run(3, "2024-08-01T09:10:00Z", "timed_out"),
        make_workflow_run(4, "2024-08-01T09:20:00Z", "startup_failure"),
        make_workflow_run(
            5,
            "2024-08-01T10:00:00Z",
            "success",
            updated_at="2024-08-01T10:05:00Z",
        ),
    ]
    episodes = compute_failure_episodes("o/r", runs)
    assert len(episodes) == 1
    assert episodes[0].failures_in_episode == 3
    assert episodes[0].censored is False
    assert episodes[0].first_failure_id == 2


def test_falha_inicial_sem_sucesso_previo_nao_abre_episodio():
    runs = [
        make_workflow_run(1, "2024-08-01T09:00:00Z", "failure"),
        make_workflow_run(2, "2024-08-01T10:00:00Z", "success"),
    ]
    assert compute_failure_episodes("o/r", runs) == []


def test_runs_ignorados_nao_interrompem_episodio():
    runs = [
        make_workflow_run(1, "2024-08-01T08:00:00Z", "success"),
        make_workflow_run(2, "2024-08-01T09:00:00Z", "failure"),
        make_workflow_run(3, "2024-08-01T09:05:00Z", "cancelled"),
        make_workflow_run(4, "2024-08-01T09:10:00Z", "skipped"),
        make_workflow_run(
            5,
            "2024-08-01T10:00:00Z",
            "success",
            updated_at="2024-08-01T10:00:00Z",
        ),
    ]
    episodes = compute_failure_episodes("o/r", runs)
    assert len(episodes) == 1
    assert episodes[0].failures_in_episode == 1
    assert episodes[0].recovery_run_id == 5


def test_episodios_sao_independentes_por_workflow():
    runs = [
        make_workflow_run(1, "2024-08-01T08:00:00Z", "success", workflow_id=10),
        make_workflow_run(2, "2024-08-01T09:00:00Z", "failure", workflow_id=10),
        make_workflow_run(
            3,
            "2024-08-01T10:00:00Z",
            "success",
            workflow_id=10,
            updated_at="2024-08-01T10:00:00Z",
        ),
        make_workflow_run(4, "2024-08-01T08:00:00Z", "success", workflow_id=20),
        make_workflow_run(5, "2024-08-01T11:00:00Z", "failure", workflow_id=20),
    ]
    episodes = compute_failure_episodes("o/r", runs)
    by_wf = {ep.workflow_id: ep for ep in episodes}
    assert by_wf[10].censored is False
    assert by_wf[20].censored is True


def test_summarize_repository_ci():
    runs = [
        make_workflow_run(1, "2024-08-01T08:00:00Z", "success"),
        make_workflow_run(2, "2024-08-01T09:00:00Z", "failure"),
        make_workflow_run(3, "2024-08-01T09:30:00Z", "cancelled"),
        make_workflow_run(
            4,
            "2024-08-01T10:00:00Z",
            "success",
            updated_at="2024-08-01T10:00:00Z",
        ),
        make_workflow_run(5, "2024-08-01T11:00:00Z", "failure"),
    ]
    episodes = compute_failure_episodes("acme/app", runs)
    summary = summarize_repository_ci("acme/app", runs, episodes, default_branch="main")
    assert summary.runs_sucesso == 2
    assert summary.runs_falha == 2
    assert summary.runs_ignorados == 1
    assert summary.cfr_ci == 0.5
    assert summary.episodios_recuperados == 1
    assert summary.episodios_censurados == 1
    assert summary.proporcao_censurados == 0.5
    assert summary.mediana_recuperacao_horas == 1.0
