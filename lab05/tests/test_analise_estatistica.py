"""Testes automatizados para o módulo de análise estatística (Issue #68)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from lab05.src.analise_estatistica import (
    METRICS,
    RESULTS_DIR,
    compute_cohens_d,
    compute_rank_biserial,
    interpret_cohens_d,
    interpret_rank_biserial,
    run_analysis,
    run_hypothesis_test_for_metric,
)
from lab05.src.validar_dados import PROCESSED_DIR


def test_effect_size_helpers_and_interpretations() -> None:
    """Valida fórmulas e classificações de d de Cohen e r rank-biserial."""
    g17 = np.array([10.0, 11.0, 12.0, 10.5, 11.5])
    g18 = np.array([12.0, 13.0, 14.0, 12.5, 13.5])
    d = compute_cohens_d(g18, g17)
    assert d > 0.8
    assert interpret_cohens_d(d) == "grande"
    assert interpret_cohens_d(0.1) == "negligenciável"

    assert compute_rank_biserial(25.0, 5, 5) == pytest.approx(1.0)
    assert compute_rank_biserial(0.0, 5, 5) == pytest.approx(-1.0)
    assert interpret_rank_biserial(0.35) == "médio"


def test_hypothesis_selector_switches_between_parametric_and_nonparametric() -> None:
    """Confirma seleção automática entre Student/Welch e Mann-Whitney U."""
    spec = METRICS[0]
    rng = np.random.default_rng(123)
    norm_17 = rng.normal(3.0, 0.1, size=30)
    norm_18 = rng.normal(3.2, 0.1, size=30)
    res_norm = run_hypothesis_test_for_metric(norm_17, norm_18, spec)
    assert "Teste t" in res_norm["teste_selecionado"]
    assert res_norm["medida_tamanho_efeito"] == "d de Cohen"
    assert res_norm["rejeita_h0_bonferroni"] is True

    # Distribuição fortemente assimétrica deve acionar Mann-Whitney U
    skew_17 = np.concatenate([np.full(27, 2.8), np.array([10.0, 12.0, 15.0])])
    skew_18 = np.concatenate([np.full(27, 2.9), np.array([11.0, 13.0, 16.0])])
    res_skew = run_hypothesis_test_for_metric(skew_17, skew_18, spec)
    assert res_skew["teste_selecionado"] == "Mann-Whitney U (bilateral)"
    assert res_skew["medida_tamanho_efeito"] == "r rank-biserial"


def test_run_analysis_on_real_validated_dataset(tmp_path: Path) -> None:
    """Executa análise completa sobre os dados reais validados em pasta temporária."""
    summary = run_analysis(processed_dir=PROCESSED_DIR, results_dir=tmp_path)
    assert summary["n_execucoes_validadas"] == 60
    assert summary["n_por_versao"] == {"PG17": 30, "PG18": 30}
    assert len(summary["testes_hipotese_efeito"]) == 4
    assert len(summary["analise_sensibilidade"]) == 4

    for expected_csv in (
        "estatisticas_descritivas.csv",
        "testes_hipotese_efeito.csv",
        "analise_sensibilidade_outliers.csv",
        "correlacoes_metricas.csv",
        "resumo_analise_estatistica.json",
    ):
        assert (tmp_path / expected_csv).exists()

    graficos_dir = tmp_path / "graficos"
    assert len(list(graficos_dir.glob("*.png"))) == 6
    assert RESULTS_DIR.name == "results"
