"""Testes unitários para o gerenciador de cache local."""

from pathlib import Path
import pytest

from lab03.src.cache_manager import CacheManager, sanitize_filename


def test_sanitize_filename():
    assert sanitize_filename("owner/repo:branch*name?v=1") == "owner_repo_branch_name_v=1"
    assert sanitize_filename("clean_filename") == "clean_filename"


def test_cache_set_and_get(tmp_path: Path):
    cache = CacheManager(cache_dir=tmp_path / "cache")
    data = {"repos": ["repo1", "repo2"], "count": 2}

    assert not cache.has("test_cat", "my_key")
    assert cache.get("test_cat", "my_key") is None

    cache.set("test_cat", "my_key", data)

    assert cache.has("test_cat", "my_key")
    assert cache.get("test_cat", "my_key") == data


def test_cache_disabled(tmp_path: Path):
    cache = CacheManager(cache_dir=tmp_path / "cache", enabled=False)
    cache.set("cat", "key", {"test": True})

    assert not cache.has("cat", "key")
    assert cache.get("cat", "key") is None


def test_cache_long_key_handling(tmp_path: Path):
    cache = CacheManager(cache_dir=tmp_path / "cache")
    long_key = "a" * 120
    cache.set("cat", long_key, {"long": True})

    assert cache.has("cat", long_key)
    assert cache.get("cat", long_key) == {"long": True}


def test_progresso_de_repositorio_e_periodo(tmp_path: Path):
    cache = CacheManager(cache_dir=tmp_path / "cache")
    assert not cache.is_processed("workflow_runs", "owner/repo")
    cache.mark_processed(
        "workflow_runs",
        "owner/repo",
        metadata={"periods": 12, "runs": 80},
    )
    assert cache.is_processed("workflow_runs", "owner/repo")
    progress = cache.get_progress("workflow_runs", "owner/repo")
    assert progress is not None
    assert progress["metadata"]["runs"] == 80
    cache.set("workflow_runs_period", "owner_repo_main_2024-08", [{"id": 1}])
    assert "owner_repo_main_2024-08" in cache.list_keys("workflow_runs_period")
