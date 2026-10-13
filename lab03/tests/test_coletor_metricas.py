"""Testes unitários para o pipeline coletor_metricas.py."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import pandas as pd
import pytest

from lab03.src.cache_manager import CacheManager
from lab03.src.coletor_metricas import (
    load_or_fetch_release_commits,
    load_repository_releases_from_cache,
    load_repository_workflow_runs_from_cache,
    process_repository_metrics,
    run_metrics_pipeline,
)
from lab03.src.config import Config


def test_load_or_fetch_release_commits_flow(mock_cache: CacheManager):
    client = MagicMock()
    # Duas releases
    releases = [
        {"tag_name": "v1.0.0", "published_at": "2026-01-01T00:00:00Z"},
        {"tag_name": "v1.1.0", "published_at": "2026-01-10T00:00:00Z"},
    ]

    client.request.return_value = (
        {"commits": [{"author_date": "2026-01-05T00:00:00Z"}]},
        {},
    )

    releases_with_commits, commits_by_pair = load_or_fetch_release_commits(
        client=client,
        cache=mock_cache,
        owner="owner",
        repo="repo",
        valid_releases=releases,
    )

    assert len(releases_with_commits) == 2
    # 1ª release não tem anterior
    assert not releases_with_commits[0]["has_previous_release"]
    # 2ª release tem anterior e commits
    assert releases_with_commits[1]["has_previous_release"]
    assert len(releases_with_commits[1]["commits"]) == 1
    assert "v1.0.0...v1.1.0" in commits_by_pair


def test_process_repository_metrics(sample_config: Config, mock_cache: CacheManager):
    client = MagicMock()
    repo_row = {
        "owner": "test_owner",
        "name": "test_repo",
        "full_name": "test_owner/test_repo",
        "default_branch": "main",
        "stars": 5000,
        "primary_language": "Python",
        "age_years": 3.0,
        "contributors_count": 50,
    }

    # Releases em cache
    mock_cache.set("releases", "releases_test_owner_test_repo_p1", [
        {"tag_name": "v1.0.0", "published_at": "2024-04-01T10:00:00Z", "draft": False, "prerelease": False},
        {"tag_name": "v1.0.1", "published_at": "2024-04-03T10:00:00Z", "draft": False, "prerelease": False},
    ])

    # Workflow runs em cache
    mock_cache.set("workflow_runs", "runs_test_owner_test_repo_main_p1", [
        {"conclusion": "success", "run_started_at": "2024-04-01T09:00:00Z", "updated_at": "2024-04-01T09:05:00Z"},
    ])

    metrics = process_repository_metrics(sample_config, client, mock_cache, repo_row)
    assert metrics is not None
    assert metrics["full_name"] == "test_owner/test_repo"
    assert "dora_overall_category" in metrics


def test_run_metrics_pipeline(tmp_path: Path, sample_config: Config):
    input_csv = tmp_path / "repositorios_selecionados.csv"
    output_csv = tmp_path / "metricas_dora.csv"

    df_sample = pd.DataFrame([{
        "owner": "test",
        "name": "repo",
        "full_name": "test/repo",
        "default_branch": "main",
        "stars": 1000,
        "primary_language": "Python",
        "age_years": 2.0,
        "contributors_count": 10,
    }])
    df_sample.to_csv(input_csv, index=False)

    with patch("lab03.src.coletor_metricas.process_repository_metrics") as mock_proc:
        mock_proc.return_value = {
            "full_name": "test/repo",
            "stars": 1000,
            "dora_overall_category": "Elite",
        }

        df_out = run_metrics_pipeline(
            config_path=None,
            repos_csv_path=str(input_csv),
            output_csv_path=str(output_csv),
        )

        assert output_csv.exists()
        assert len(df_out) == 1
        assert df_out.iloc[0]["dora_overall_category"] == "Elite"
