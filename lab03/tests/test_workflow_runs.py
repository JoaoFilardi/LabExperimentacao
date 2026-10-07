"""Testes de coleta de workflow runs: janela, paginação, partição, cache e erros."""

from datetime import datetime, timezone

from lab03.src.cache_manager import CacheManager
from lab03.src.workflow_runs import (
    CACHE_CATEGORY_PERIOD,
    PROGRESS_TASK,
    collect_workflow_runs,
    fetch_default_branch,
    fetch_runs_for_period,
    filter_collected_runs,
    format_created_range,
    iter_monthly_periods,
    normalize_workflow_run,
)
from lab03.tests.fakes import FakeWorkflowClient, make_workflow_run


def test_iter_monthly_periods_cobre_a_janela():
    start = datetime(2024, 3, 1, tzinfo=timezone.utc)
    end = datetime(2024, 5, 15, 23, 59, 59, tzinfo=timezone.utc)
    periods = iter_monthly_periods(start, end)
    assert len(periods) == 3
    assert periods[0][0] == start
    assert periods[-1][1] == end
    assert periods[1][0] == datetime(2024, 4, 1, tzinfo=timezone.utc)


def test_normalize_e_filtro_da_janela(sample_window_config):
    raw = make_workflow_run(1, "2024-08-01T10:00:00Z", "success", head_branch="main")
    normalized = normalize_workflow_run(raw, default_branch="main")
    assert normalized is not None
    assert normalized["id"] == 1
    assert normalized["branch"] == "main"
    assert normalized["event"] == "push"
    assert normalized["classificacao"] == "sucesso"

    outside = normalize_workflow_run(
        make_workflow_run(2, "2022-01-01T10:00:00Z", "success"), "main"
    )
    schedule = normalize_workflow_run(
        make_workflow_run(3, "2024-08-01T10:00:00Z", "success", event="schedule"), "main"
    )
    filtered = filter_collected_runs(
        [normalized, outside, schedule], sample_window_config, "main"
    )
    assert [r["id"] for r in filtered] == [1]


def test_paginacao_de_workflow_runs(sample_window_config, mock_cache: CacheManager):
    runs = [
        make_workflow_run(i, f"2024-08-{(i % 27) + 1:02d}T10:00:00Z", "success")
        for i in range(1, 151)
    ]
    client = FakeWorkflowClient(runs=runs, cache=mock_cache)
    start = datetime(2024, 8, 1, tzinfo=timezone.utc)
    end = datetime(2024, 8, 31, 23, 59, 59, tzinfo=timezone.utc)
    collected = fetch_runs_for_period(client, "o", "r", "main", start, end)
    assert len(collected) == 150
    pages = [c for c in client.calls if c["endpoint"].endswith("/actions/runs")]
    assert len(pages) == 2
    assert pages[0]["params"]["page"] == 1
    assert pages[1]["params"]["page"] == 2
    assert pages[0]["params"]["event"] == "push"
    assert pages[0]["params"]["branch"] == "main"


def test_particiona_quando_consulta_excede_1000(sample_window_config):
    runs = []
    for i in range(1200):
        day = (i % 28) + 1
        hour = (i // 28) % 24
        minute = i % 60
        runs.append(
            make_workflow_run(
                i + 1,
                f"2024-08-{day:02d}T{hour:02d}:{minute:02d}:00Z",
                "success",
            )
        )
    client = FakeWorkflowClient(runs=runs, cap_at=1000)
    start = datetime(2024, 8, 1, tzinfo=timezone.utc)
    end = datetime(2024, 8, 31, 23, 59, 59, tzinfo=timezone.utc)
    collected = fetch_runs_for_period(client, "o", "r", "main", start, end)
    assert len(collected) == 1200
    created_ranges = {
        c["params"].get("created")
        for c in client.calls
        if c["endpoint"].endswith("/actions/runs")
    }
    assert len(created_ranges) >= 2


def test_cache_de_periodo_evita_nova_requisicao(mock_cache: CacheManager):
    runs = [make_workflow_run(1, "2024-08-10T10:00:00Z", "success")]
    client = FakeWorkflowClient(runs=runs, cache=mock_cache)
    start = datetime(2024, 8, 1, tzinfo=timezone.utc)
    end = datetime(2024, 8, 31, 23, 59, 59, tzinfo=timezone.utc)
    first = fetch_runs_for_period(client, "o", "r", "main", start, end)
    calls_after_first = len(client.calls)
    second = fetch_runs_for_period(client, "o", "r", "main", start, end)
    assert first == second
    assert len(client.calls) == calls_after_first
    assert mock_cache.list_keys(CACHE_CATEGORY_PERIOD)
    assert mock_cache.is_processed(
        PROGRESS_TASK,
        f"o_r_main_{format_created_range(start, end)}",
    )


def test_collect_respeita_janela_branch_e_evento(sample_config, mock_cache: CacheManager):
    runs = [
        make_workflow_run(1, "2024-08-10T10:00:00Z", "success", head_branch="main"),
        make_workflow_run(2, "2024-08-10T11:00:00Z", "failure", head_branch="main"),
        make_workflow_run(3, "2024-08-10T12:00:00Z", "success", event="schedule"),
        make_workflow_run(4, "2024-08-10T13:00:00Z", "success", head_branch="dev"),
        make_workflow_run(5, "2022-01-01T10:00:00Z", "success"),
    ]
    client = FakeWorkflowClient(runs=runs, cache=mock_cache, default_branch="main")
    collected = collect_workflow_runs(client, "o", "r", sample_config.window, "main")
    assert {r["id"] for r in collected} == {1, 2}
    assert mock_cache.is_processed(PROGRESS_TASK, "o/r")


def test_fetch_default_branch(mock_cache: CacheManager):
    client = FakeWorkflowClient(default_branch="master", cache=mock_cache)
    assert fetch_default_branch(client, "o", "r") == "master"
    assert fetch_default_branch(client, "o", "r") == "master"
    repo_calls = [c for c in client.calls if c["endpoint"] == "repos/o/r"]
    assert len(repo_calls) == 1


def test_erro_temporario_nao_marca_repositorio_como_processado(sample_config, mock_cache):
    runs = [make_workflow_run(1, "2024-08-10T10:00:00Z", "success")]
    client = FakeWorkflowClient(
        runs=runs,
        cache=mock_cache,
        fail_on_created="2024-04-01",
    )
    try:
        collect_workflow_runs(client, "o", "r", sample_config.window, "main")
        assert False, "esperava falha no período de abril"
    except RuntimeError:
        pass
    assert not mock_cache.is_processed(PROGRESS_TASK, "o/r")
