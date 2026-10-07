"""Fixtures compartilhadas para a suíte de testes unitários do Lab03."""

import pytest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock
import requests

from lab03.src.cache_manager import CacheManager
from lab03.src.config import (
    ApiConfig,
    CacheConfig,
    Config,
    FunnelCriteria,
    OutputConfig,
    WindowConfig,
)
from lab03.src.github_client import GitHubClient


@pytest.fixture
def sample_window_config() -> WindowConfig:
    return WindowConfig(
        start_date_str="2024-03-01T00:00:00Z",
        end_date_str="2025-02-28T23:59:59Z",
        description="Janela de teste",
    )


@pytest.fixture
def sample_config(tmp_path: Path, sample_window_config: WindowConfig) -> Config:
    cache_dir = tmp_path / "cache"
    data_dir = tmp_path / "data"
    cache_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    return Config(
        window=sample_window_config,
        funnel_criteria=FunnelCriteria(
            min_stars=1000,
            min_releases=5,
            min_workflow_runs=50,
            target_repositories=2,
            target_repositories_s02=10,
        ),
        api=ApiConfig(
            base_url="https://api.github.com",
            timeout_seconds=5,
            max_retries=2,
            backoff_factor=1.1,
            rate_limit_safety_margin=5,
        ),
        cache=CacheConfig(enabled=True, cache_dir=cache_dir),
        output=OutputConfig(data_dir=data_dir),
        github_token="fake_test_token_xyz",
    )


@pytest.fixture
def mock_cache(tmp_path: Path) -> CacheManager:
    return CacheManager(cache_dir=tmp_path / "test_cache", enabled=True)


@pytest.fixture
def mock_candidate_repo() -> dict:
    return {
        "id": 12345,
        "name": "fastapi",
        "full_name": "tiangolo/fastapi",
        "owner": {"login": "tiangolo"},
        "html_url": "https://github.com/tiangolo/fastapi",
        "description": "FastAPI framework, high performance, easy to learn",
        "stargazers_count": 75000,
        "language": "Python",
        "forks_count": 6000,
        "open_issues_count": 250,
        "default_branch": "main",
        "created_at": "2018-12-08T14:00:00Z",
    }


@pytest.fixture
def mock_workflows_response_positive() -> dict:
    return {
        "total_count": 3,
        "workflows": [
            {"id": 1, "name": "CI", "path": ".github/workflows/ci.yml", "state": "active"},
            {"id": 2, "name": "Release", "path": ".github/workflows/release.yml", "state": "active"},
        ],
    }


@pytest.fixture
def mock_workflows_response_empty() -> dict:
    return {"total_count": 0, "workflows": []}


@pytest.fixture
def mock_releases_list() -> list:
    """Gera 6 releases válidas dentro da janela de observação 2024-03 a 2025-02."""
    return [
        {
            "id": 101,
            "tag_name": "0.115.0",
            "name": "Release 0.115.0",
            "draft": False,
            "prerelease": False,
            "published_at": "2024-09-10T12:00:00Z",
        },
        {
            "id": 102,
            "tag_name": "0.114.0",
            "name": "Release 0.114.0",
            "draft": False,
            "prerelease": False,
            "published_at": "2024-08-01T10:00:00Z",
        },
        {
            "id": 103,
            "tag_name": "0.113.0",
            "name": "Release 0.113.0",
            "draft": False,
            "prerelease": False,
            "published_at": "2024-07-01T15:30:00Z",
        },
        {
            "id": 104,
            "tag_name": "0.112.0",
            "name": "Release 0.112.0",
            "draft": False,
            "prerelease": False,
            "published_at": "2024-06-05T08:00:00Z",
        },
        {
            "id": 105,
            "tag_name": "0.111.0",
            "name": "Release 0.111.0",
            "draft": False,
            "prerelease": False,
            "published_at": "2024-05-02T19:00:00Z",
        },
        {
            "id": 106,
            "tag_name": "0.110.0",
            "name": "Release 0.110.0",
            "draft": False,
            "prerelease": False,
            "published_at": "2024-04-01T11:00:00Z",
        },
        # Fora da janela (deve ser ignorada)
        {
            "id": 99,
            "tag_name": "0.100.0",
            "name": "Release antiga",
            "draft": False,
            "prerelease": False,
            "published_at": "2023-01-01T00:00:00Z",
        },
        # Draft (deve ser ignorada)
        {
            "id": 107,
            "tag_name": "0.116.0",
            "name": "Draft release",
            "draft": True,
            "prerelease": False,
            "published_at": "2024-10-01T00:00:00Z",
        },
    ]


@pytest.fixture
def mock_workflow_runs_list() -> list:
    """Gera 55 runs válidos dentro da janela."""
    runs = []
    for i in range(55):
        runs.append({
            "id": 1000 + i,
            "name": "Test Suite",
            "event": "push",
            "head_branch": "main",
            "conclusion": "success" if i % 10 != 0 else "failure",
            "created_at": f"2024-08-{(i % 25) + 1:02d}T10:00:00Z",
            "run_started_at": f"2024-08-{(i % 25) + 1:02d}T10:01:00Z",
            "updated_at": f"2024-08-{(i % 25) + 1:02d}T10:05:00Z",
        })
    # Adiciona runs que devem ser descartados (cancelled, evento manual, fora da janela)
    runs.append({
        "id": 9999,
        "name": "Test Suite Cancelled",
        "event": "push",
        "conclusion": "cancelled",  # ignorar
        "created_at": "2024-08-10T10:00:00Z",
    })
    runs.append({
        "id": 9998,
        "name": "Scheduled Run",
        "event": "schedule",  # ignorar
        "conclusion": "success",
        "created_at": "2024-08-10T10:00:00Z",
    })
    runs.append({
        "id": 9997,
        "name": "Run Fora da Janela",
        "event": "push",
        "conclusion": "success",
        "created_at": "2022-01-01T10:00:00Z",  # fora da janela
    })
    return runs
