"""Testes unitários para as definições de cenário e hipóteses do LAB04 (#45)."""

from lab04.src.cenario import CENARIO, get_info_cenario, DefinicaoCenario


def test_definicao_cenario_valores_padrao():
    assert CENARIO.par_id == "P1"
    assert "Welch" in CENARIO.nome_par
    assert "Mann-Whitney" in CENARIO.nome_par
    assert CENARIO.alpha == 0.05
    assert CENARIO.tipo_teste == "bicaudal"


def test_pergunta_pesquisa_e_hipoteses():
    assert len(CENARIO.pergunta_pesquisa) > 10
    assert CENARIO.pergunta_pesquisa.endswith("?")
    assert "bots" in CENARIO.pergunta_pesquisa
    assert len(CENARIO.h0_conceitual) > 0
    assert len(CENARIO.h1_conceitual) > 0
    assert CENARIO.h0_welch != CENARIO.h1_welch
    assert CENARIO.h0_mann_whitney != CENARIO.h1_mann_whitney


def test_previsao_inicial_registrada():
    assert CENARIO.teste_esperado_melhor_desempenho == "Mann-Whitney (Wilcoxon rank-sum)"
    assert len(CENARIO.justificativa_previsao) > 50


def test_get_info_cenario_dashboard():
    info = get_info_cenario()
    assert isinstance(info, dict)
    assert info["par_id"] == "P1"
    assert info["alpha"] == 0.05
    assert "bots" in str(info["pergunta_pesquisa"])
    assert len(info["texto_dashboard"]) > 100

