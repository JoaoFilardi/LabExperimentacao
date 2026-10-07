"""Testes da orquestração, exportação e integração com o pipeline."""

from lab03.src.coleta_workflow_runs import (
    EPISODES_CSV,
    RUNS_CSV,
    SUMMARY_CSV,
    collect_repositories,
    collect_repository,
    export_results,
    load_selected_repositories,
    run_workflow_collection,
)
from lab03.tests.fakes import FakeWorkflowClient, make_workflow_run


def _runs_rq04():
    return [
        make_workflow_run(
            1, "2024-08-01T09:00:00Z", "success", updated_at="2024-08-01T09:05:00Z"
        ),
        make_workflow_run(
            2,
            "2024-08-01T10:00:00Z",
            "failure",
            run_started_at="2024-08-01T10:00:00Z",
        ),
        make_workflow_run(3, "2024-08-01T10:30:00Z", "failure"),
        make_workflow_run(
            4,
            "2024-08-01T11:15:00Z",
            "success",
            updated_at="2024-08-01T11:20:00Z",
        ),
        make_workflow_run(5, "2024-08-01T12:00:00Z", "cancelled"),
    ]


def test_collect_repository_fim_a_fim(sample_config):
    client = FakeWorkflowClient(runs=_runs_rq04())
    result = collect_repository(client, "o", "r", sample_config, default_branch="main")
    s = result.summary
    assert s.repo == "o/r"
    assert s.runs_sucesso == 2
    assert s.runs_falha == 2
    assert s.runs_ignorados == 1
    assert s.cfr_ci == 0.5
    assert s.episodios_recuperados == 1
    assert s.episodios_censurados == 0
    assert s.mediana_recuperacao_horas == 1 + 20 / 60
    assert not s.erro


def test_collect_repository_erro_nao_interrompe_lote(sample_config):
    ok_client = FakeWorkflowClient(runs=_runs_rq04())
    bad_client = FakeWorkflowClient(fail_on_created="2024-03-01")
    results = collect_repositories(
        bad_client, [("bad", "repo", "main")], sample_config
    )
    assert results[0].summary.erro
    results_ok = collect_repositories(
        ok_client, [("o", "r", "main")], sample_config
    )
    assert not results_ok[0].summary.erro


def test_export_e_run_pipeline(sample_config, tmp_path):
    selected = tmp_path / "repositorios_selecionados.csv"
    selected.write_text(
        "owner,name,default_branch\no,r,main\n",
        encoding="utf-8",
    )
    sample_config.output.data_dir = tmp_path
    sample_config.output.selected_repositories_csv = selected.name
    # OutputConfig.selected_repositories_path usa data_dir / csv name
    loaded = load_selected_repositories(selected)
    assert loaded == [("o", "r", "main")]

    client = FakeWorkflowClient(runs=_runs_rq04())
    results = run_workflow_collection(
        sample_config, client=client, repositories=loaded
    )
    assert (tmp_path / RUNS_CSV).is_file()
    assert (tmp_path / EPISODES_CSV).is_file()
    assert (tmp_path / SUMMARY_CSV).is_file()
    assert results[0].summary.cfr_ci == 0.5

    paths = export_results(results, tmp_path)
    assert all(p.is_file() for p in paths)
