"""Testes unitários para o pipeline de seleção e funil de coleta."""

from unittest.mock import MagicMock, patch
import pandas as pd
import pytest

from lab03.src.config import Config
from lab03.src.github_client import GitHubClient
from lab03.src.selecao_repositorios import (
    FunnelCollector,
    check_github_actions_workflows,
    count_valid_releases_in_window,
    count_valid_workflow_runs_in_window,
)


def test_check_github_actions_workflows_positive(
    mock_workflows_response_positive,
):
    client = MagicMock(spec=GitHubClient)
    client.request.return_value = (mock_workflows_response_positive, {})

    has_actions, total = check_github_actions_workflows(client, "owner", "repo")
    assert has_actions is True
    assert total == 3


def test_check_github_actions_workflows_negative(
    mock_workflows_response_empty,
):
    client = MagicMock(spec=GitHubClient)
    client.request.return_value = (mock_workflows_response_empty, {})

    has_actions, total = check_github_actions_workflows(client, "owner", "repo")
    assert has_actions is False
    assert total == 0


def test_count_valid_releases_in_window(mock_releases_list, sample_config: Config):
    client = MagicMock(spec=GitHubClient)
    client.paginate.return_value = mock_releases_list

    # Das 8 releases do mock, 6 estão no intervalo 2024-03 a 2025-02, 1 fora da janela e 1 é draft
    valid_count = count_valid_releases_in_window(client, "owner", "repo", sample_config)
    assert valid_count == 6


def test_count_valid_workflow_runs_in_window(mock_workflow_runs_list, sample_config: Config):
    client = MagicMock(spec=GitHubClient)
    client.paginate.return_value = mock_workflow_runs_list

    # O mock possui 55 runs válidos + 1 cancelled + 1 schedule + 1 fora da janela
    valid_count = count_valid_workflow_runs_in_window(
        client, "owner", "repo", "main", sample_config
    )
    assert valid_count == 55


def test_funnel_process_complete_flow(
    sample_config: Config,
    mock_candidate_repo,
    mock_workflows_response_positive,
    mock_workflows_response_empty,
    mock_releases_list,
    mock_workflow_runs_list,
):
    collector = FunnelCollector(sample_config)

    # 4 cenários de teste:
    # 1. repo_ok: Atende todos os critérios
    # 2. repo_no_actions: total_count = 0
    # 3. repo_few_releases: apenas 2 releases (< 5)
    # 4. repo_few_runs: apenas 10 runs (< 50)

    repo_ok = dict(mock_candidate_repo, full_name="user/repo_ok", name="repo_ok")
    repo_no_actions = dict(mock_candidate_repo, full_name="user/repo_no_actions", name="repo_no_actions")
    repo_few_releases = dict(mock_candidate_repo, full_name="user/repo_few_releases", name="repo_few_releases")
    repo_few_runs = dict(mock_candidate_repo, full_name="user/repo_few_runs", name="repo_few_runs")

    collector.search_candidate_repositories = MagicMock(
        return_value=[repo_ok, repo_no_actions, repo_few_releases, repo_few_runs]
    )

    def mock_request(endpoint, *args, **kwargs):
        if "actions/workflows" in endpoint:
            if "repo_no_actions" in endpoint:
                return mock_workflows_response_empty, {}
            return mock_workflows_response_positive, {}
        return {}, {}

    def mock_paginate(endpoint, *args, **kwargs):
        if "releases" in endpoint:
            if "repo_few_releases" in endpoint:
                return mock_releases_list[:2]  # apenas 2 releases
            return mock_releases_list
        if "actions/runs" in endpoint:
            if "repo_few_runs" in endpoint:
                return mock_workflow_runs_list[:10]  # apenas 10 runs
            return mock_workflow_runs_list
        return []

    collector.client.request = MagicMock(side_effect=mock_request)
    collector.client.paginate = MagicMock(side_effect=mock_paginate)
    collector.client.count_contributors = MagicMock(return_value=120)

    selected, detailed, counts = collector.process_funnel(target_count=10)

    # Apenas o repo_ok deve ser selecionado
    assert len(selected) == 1
    assert selected[0]["full_name"] == "user/repo_ok"
    assert selected[0]["contributors_count"] == 120
    assert selected[0]["releases_window_count"] == 6
    assert selected[0]["runs_window_count"] == 55

    # Auditoria detalhada
    assert len(detailed) == 4
    status_by_name = {d["full_name"]: d["status"] for d in detailed}
    assert status_by_name["user/repo_ok"] == "SELECIONADO"
    assert status_by_name["user/repo_no_actions"] == "DESCARTADO"
    assert status_by_name["user/repo_few_releases"] == "DESCARTADO"
    assert status_by_name["user/repo_few_runs"] == "DESCARTADO"

    # Exportação de arquivos
    collector.export_results(selected, detailed, counts)

    assert sample_config.output.selected_repositories_path.exists()
    assert sample_config.output.funnel_summary_path.exists()
    assert sample_config.output.funnel_detailed_path.exists()

    df_selected = pd.read_csv(sample_config.output.selected_repositories_path)
    assert len(df_selected) == 1
    assert "contributors_count" in df_selected.columns
    assert "age_years" in df_selected.columns


def test_search_candidate_repositories(sample_config: Config, mock_candidate_repo):
    collector = FunnelCollector(sample_config)
    collector.client.paginate = MagicMock(return_value=[mock_candidate_repo])

    candidates = collector.search_candidate_repositories(limit=1)
    assert len(candidates) == 1
    assert candidates[0]["full_name"] == "tiangolo/fastapi"


def test_main_cli_execution(tmp_path, sample_config: Config, monkeypatch):
    from lab03.src.selecao_repositorios import main

    with patch.object(FunnelCollector, "process_funnel") as mock_funnel, \
         patch.object(FunnelCollector, "export_results") as mock_export:
        mock_funnel.return_value = ([], [], {"1_candidatos": 0, "2_com_actions": 0, "3_com_releases": 0, "4_com_runs": 0, "5_selecionados": 0})
        monkeypatch.setattr("sys.argv", ["selecao_repositorios.py", "--target", "5", "--no-cache"])
        main()
        assert mock_funnel.called
        assert mock_export.called
