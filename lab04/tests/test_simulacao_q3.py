"""Testes unitários para as simulações de violação dos pressupostos estatísticos — Q3 (#55)."""

import numpy as np
import pandas as pd
import pytest

from lab04.src.cenario import CENARIO
from lab04.src.simulacao import GeradorDadosSimulados
from lab04.src.simulacao_q3 import (
    EFEITOS_PADRAO_Q3,
    carregar_ou_executar_q3,
    construir_tabela_comparativa_impacto,
    executar_simulacao_q3,
    gerar_relatorio_q3,
    gerar_texto_interpretativo_q3,
    obter_dados_q3_para_g3,
    obter_dados_q3_para_g4,
    obter_pressupostos_e_violacoes,
    salvar_resultados_q3,
)


def test_pressupostos_e_violacoes_documentados():
    violacoes = obter_pressupostos_e_violacoes()
    assert len(violacoes) == 2
    codigos = {v.codigo_violacao for v in violacoes}
    assert codigos == {"Q3_Outliers", "Q3_AmostraPequena"}
    for v in violacoes:
        assert len(v.pressuposto_violado) > 20
        assert len(v.justificativa_cenario_se) > 30
        assert len(v.impacto_teorico_welch) > 30
        assert len(v.impacto_teorico_mann_whitney) > 30


def test_validacao_parametros_matrizes_q3():
    gerador = GeradorDadosSimulados(semente=42)

    with pytest.raises(ValueError, match="efeito_reducao deve pertencer"):
        gerador.gerar_matrizes_experimento(n_simulacoes=10, efeito_reducao=-0.1)
    with pytest.raises(ValueError, match="efeito_reducao deve pertencer"):
        gerador.gerar_matrizes_experimento(n_simulacoes=10, efeito_reducao=1.0)
    with pytest.raises(ValueError, match="inteiro positivo"):
        gerador.gerar_matrizes_experimento(n_simulacoes=0)
    with pytest.raises(ValueError, match="inteiros positivos"):
        gerador.gerar_matrizes_experimento(n_simulacoes=10, n_sem_bot=0)
    with pytest.raises(ValueError, match="estritamente positivo"):
        gerador.gerar_matrizes_experimento(n_simulacoes=10, sigma_log_base=-1.0)

    with pytest.raises(ValueError, match="prop_outliers deve estar"):
        gerador.gerar_matrizes_com_outliers(n_simulacoes=10, prop_outliers=0.0)
    with pytest.raises(ValueError, match="prop_outliers deve estar"):
        gerador.gerar_matrizes_com_outliers(n_simulacoes=10, prop_outliers=1.0)

    # Sem arredondamento
    s_raw, c_raw = gerador.gerar_matrizes_com_outliers(
        n_simulacoes=5, n_sem_bot=10, n_com_bot=10, arredondar=None
    )
    assert s_raw.shape == (5, 10)
    assert c_raw.shape == (5, 10)


def test_validacao_efeitos_minimos_q3():
    with pytest.raises(ValueError, match="pelo menos 5 tamanhos de efeito"):
        executar_simulacao_q3(n_simulacoes=20, efeitos=(0.0, 0.1, 0.2))
    with pytest.raises(ValueError, match="incluindo 0.0"):
        executar_simulacao_q3(n_simulacoes=20, efeitos=(0.1, 0.2, 0.3, 0.4, 0.5))


def test_resultados_oficiais_q3_10000_simulacoes_semente_42():
    """Valida a reprodutibilidade e os números oficiais de Q3 com 10.000 simulações."""
    res = carregar_ou_executar_q3(semente=42, n_simulacoes=10_000)

    assert res.semente == 42
    assert res.n_simulacoes == 10_000
    assert res.efeitos_avaliados == EFEITOS_PADRAO_Q3
    assert len(res.df_erro_tipo_1) == 6
    assert len(res.df_poder_largo) == 18  # 3 condições x 6 tamanhos de efeito
    assert len(res.df_curvas_g4) == 36  # 3 condições x 6 tamanhos de efeito x 2 testes

    # Verifica consistência exata do Erro Tipo I (Q1 vs Q3)
    df_t1 = res.df_erro_tipo_1.set_index(["cenario_codigo", "teste"])
    assert pytest.approx(df_t1.loc[("Q1_Base", CENARIO.teste_parametrico), "taxa_empirica_pct"]) == 3.93
    assert pytest.approx(df_t1.loc[("Q1_Base", CENARIO.teste_nao_parametrico), "taxa_empirica_pct"]) == 4.58
    assert pytest.approx(df_t1.loc[("Q3_Outliers", CENARIO.teste_parametrico), "taxa_empirica_pct"]) == 3.28
    assert pytest.approx(df_t1.loc[("Q3_Outliers", CENARIO.teste_nao_parametrico), "taxa_empirica_pct"]) == 4.52
    assert pytest.approx(df_t1.loc[("Q3_AmostraPequena", CENARIO.teste_parametrico), "taxa_empirica_pct"]) == 2.90
    assert pytest.approx(df_t1.loc[("Q3_AmostraPequena", CENARIO.teste_nao_parametrico), "taxa_empirica_pct"]) == 4.33

    # Verifica crescimento monotônico do poder conforme o tamanho do efeito aumenta
    for cenario_cod in ("Q2_Base", "Q3_Outliers", "Q3_AmostraPequena"):
        sub = res.df_poder_largo[res.df_poder_largo["cenario_codigo"] == cenario_cod].sort_values(
            "efeito_reducao"
        )
        assert np.all(np.diff(sub["poder_welch_pct"].to_numpy()) > 0)
        assert np.all(np.diff(sub["poder_mann_whitney_pct"].to_numpy()) > 0)
        # Mann-Whitney supera Welch em todos os tamanhos de efeito
        assert (sub["vantagem_mw_pp"] > 0).all()

    # Verifica que t de Welch é identificado como o teste que sofre maior alteração
    imp = res.df_comparativo_impacto.set_index("cenario_codigo")
    assert imp.loc["Q3_Outliers", "teste_maior_alteracao_erro_tipo_1"] == CENARIO.teste_parametrico
    assert imp.loc["Q3_Outliers", "teste_maior_alteracao_poder"] == CENARIO.teste_parametrico
    assert imp.loc["Q3_AmostraPequena", "teste_maior_alteracao_erro_tipo_1"] == CENARIO.teste_parametrico
    assert imp.loc["Q3_AmostraPequena", "teste_maior_alteracao_poder"] == CENARIO.teste_parametrico


def test_execucao_reduzida_persistencia_e_adaptadores_g3_g4(tmp_path):
    """Testa a execução completa com n_simulacoes reduzido, salvamento CSV e adaptadores G3/G4."""
    p1 = tmp_path / "t1.csv"
    p2 = tmp_path / "pod.csv"
    p3 = tmp_path / "g4.csv"
    p4 = tmp_path / "imp.csv"

    res_curto = carregar_ou_executar_q3(
        semente=99,
        n_simulacoes=50,
        forcar_reexecucao=True,
        caminho_erro_tipo_1=p1,
        caminho_poder_largo=p2,
        caminho_curvas_g4=p3,
        caminho_impacto=p4,
    )
    salvar_resultados_q3(res_curto, p1, p2, p3, p4)
    assert p1.exists() and p2.exists() and p3.exists() and p4.exists()

    df_g3 = obter_dados_q3_para_g3(res_curto)
    df_g4 = obter_dados_q3_para_g4(res_curto)
    assert len(df_g3) == 6
    assert len(df_g4) == 36

    relatorio = gerar_relatorio_q3(semente=42, n_simulacoes=10_000)
    assert "QUESTÃO Q3" in relatorio
    assert "Q3_Outliers" in relatorio
    assert "Q3_AmostraPequena" in relatorio
