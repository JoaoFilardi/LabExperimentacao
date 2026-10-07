"""Testes unitários para o módulo de configuração."""

from pathlib import Path
import pytest
import yaml

from lab03.src.config import (
    Config,
    WindowConfig,
    find_github_token,
    parse_iso_datetime,
)


def test_window_config_invalid_range():
    with pytest.raises(ValueError, match="end_date deve ser posterior a start_date"):
        WindowConfig(
            start_date_str="2025-01-01T00:00:00Z",
            end_date_str="2024-01-01T00:00:00Z",
        )


def test_load_real_config_yaml():
    # Testa o carregamento do config.yaml real de lab03/config.yaml
    cfg = Config.load("lab03/config.yaml")
    assert cfg.funnel_criteria.min_stars == 1000
    assert cfg.funnel_criteria.min_releases == 5
    assert cfg.funnel_criteria.min_workflow_runs == 50
    assert cfg.funnel_criteria.target_repositories == 100
    assert cfg.output.selected_repositories_csv == "repositorios_selecionados.csv"
    assert cfg.output.selected_repositories_path.name == "repositorios_selecionados.csv"
    assert cfg.output.funnel_summary_path.name == "funil_selecao.csv"
    assert cfg.output.funnel_detailed_path.name == "funil_detalhado.csv"


def test_find_github_token_from_env(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "mock_token_from_env")
    token = find_github_token()
    assert token == "mock_token_from_env"


def test_config_load_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        Config.load("caminho_inexistente_12345.yaml")
