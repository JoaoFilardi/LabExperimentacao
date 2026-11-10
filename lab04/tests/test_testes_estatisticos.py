"""Testes unitários para aplicação e interpretação dos dois testes estatísticos (#49)."""

import numpy as np
import pandas as pd
import pytest

from lab04.src.testes_estatisticos import (
    aplicar_ambos_testes,
    avaliar_dataframe_rapido,
    avaliar_matrizes_rapido,
    avaliar_par_rapido,
    calcular_correlacao_rank_biserial,
    calcular_d_cohen_welch,
    calcular_graus_liberdade_welch,
    calcular_z_mann_whitney,
    carregar_ou_gerar_simulados_s01,
    classificar_d_cohen,
    classificar_rank_biserial,
    comparacao_para_dataframe,
    executar_analise_dados_reais,
    executar_analise_simulados_s01,
    executar_teste_mann_whitney,
    executar_teste_welch,
    extrair_grupos_dataframe,
    gerar_relatorio_testes_s01,
    normalizar_alternativa,
    salvar_resultados_testes_s01,
    validar_amostras,
)


def test_normalizar_alternativa_valida_e_invalida():
    assert normalizar_alternativa("bicaudal") == "two-sided"
    assert normalizar_alternativa("two-sided") == "two-sided"
    assert normalizar_alternativa("menor") == "less"
    assert normalizar_alternativa("maior") == "greater"
    with pytest.raises(ValueError, match="Direção de teste inválida"):
        normalizar_alternativa("invalida")


def test_validacao_amostras_E_extrair_grupos():
    with pytest.raises(ValueError, match="pelo menos 2 observações"):
        validar_amostras(np.array([1.0]), np.array([1.0, 2.0]))

    with pytest.raises(ValueError, match="NaN ou infinitos"):
        validar_amostras(np.array([1.0, np.nan]), np.array([1.0, 2.0]))

    df_invalido = pd.DataFrame({"outra": [1, 2]})
    with pytest.raises(ValueError, match="deve conter as colunas"):
        extrair_grupos_dataframe(df_invalido)


def test_funcoes_auxiliares_e_classificacoes():
    # Amostras idênticas constantes -> variância zero
    const = np.array([10.0, 10.0, 10.0])
    assert calcular_graus_liberdade_welch(const, const) == 4.0
    assert calcular_d_cohen_welch(const, const) == 0.0
    assert calcular_correlacao_rank_biserial(0.0, 0, 0) == 0.0
    assert calcular_z_mann_whitney(0.0, 0, 0) == 0.0

    assert "trivial" in classificar_d_cohen(0.10)
    assert "pequeno" in classificar_d_cohen(-0.35)
    assert "médio" in classificar_d_cohen(0.65)
    assert "grande" in classificar_d_cohen(-0.95)

    assert "trivial" in classificar_rank_biserial(0.05)
    assert "pequeno" in classificar_rank_biserial(-0.22)
    assert "médio" in classificar_rank_biserial(0.40)
    assert "grande" in classificar_rank_biserial(-0.60)


def test_execucao_dados_simulados_s01_semente_42():
    """Verifica os valores exatos e reproduzíveis sobre o dataset simulado oficial (semente = 42)."""
    comp = executar_analise_simulados_s01(semente=42, alpha=0.05)

    assert comp.alpha == 0.05
    assert comp.direcao_teste == "bicaudal"
    assert comp.concordam_decisao is True

    # Teste t de Welch
    w = comp.welch
    assert w.n_sem_bot == 30 and w.n_com_bot == 30
    assert w.nome_estatistica == "t"
    assert pytest.approx(w.medida_central_sem_bot, rel=1e-4) == 24.0110
    assert pytest.approx(w.medida_central_com_bot, rel=1e-4) == 21.3330
    assert pytest.approx(w.estatistica, abs=1e-4) == -0.5828
    assert pytest.approx(w.graus_liberdade_ou_auxiliar, abs=1e-3) == 50.6112
    assert pytest.approx(w.p_valor, abs=1e-5) == 0.562615
    assert w.rejeitar_h0 is False
    assert "Não rejeitar H₀" in w.decisao_estatistica
    assert "médias" in w.o_que_compara.lower()

    # Teste U de Mann-Whitney
    m = comp.mann_whitney
    assert m.n_sem_bot == 30 and m.n_com_bot == 30
    assert m.nome_estatistica == "U"
    assert pytest.approx(m.medida_central_sem_bot, rel=1e-4) == 21.2500
    assert pytest.approx(m.medida_central_com_bot, rel=1e-4) == 16.4650
    assert pytest.approx(m.estatistica, abs=1e-4) == 347.5
    assert pytest.approx(m.p_valor, abs=1e-5) == 0.131546
    assert m.rejeitar_h0 is False
    assert "Não rejeitar H₀" in m.decisao_estatistica
    assert "postos" in m.o_que_compara.lower()

    # Verifica que Mann-Whitney teve p-valor menor que Welch na amostra S01 com outlier
    assert m.p_valor < w.p_valor
    assert "Mann-Whitney" in comp.explicacao_diferencas


def test_rejeicao_h0_e_divergencia_entre_testes():
    """Valida os ramos de rejeição de H0 para ambos os testes e de divergência entre eles."""
    sem = np.array([50.0, 52.0, 48.0, 51.0, 49.0, 53.0, 47.0, 50.5, 51.5, 49.5])
    com = np.array([10.0, 12.0, 11.0, 9.0, 10.5, 11.5, 8.5, 10.2, 9.8, 11.2])

    df_forte = pd.DataFrame(
        [{"pr_id": i + 1, "grupo": "sem_bot", "tempo_horas": v} for i, v in enumerate(sem)]
        + [{"pr_id": i + 11, "grupo": "com_bot", "tempo_horas": v} for i, v in enumerate(com)]
    )
    comp_forte = aplicar_ambos_testes(df_forte, alpha=0.05)
    assert comp_forte.welch.rejeitar_h0 is True
    assert comp_forte.mann_whitney.rejeitar_h0 is True
    assert comp_forte.concordam_decisao is True
    assert "REJEIÇÃO de H₀" in comp_forte.resumo_comparativo

    # Caso com outlier extremo em com_bot que impede Welch de rejeitar H0 mas Mann-Whitney rejeita
    com_com_outlier = com.copy()
    com_com_outlier[0] = 450.0
    df_div = pd.DataFrame(
        [{"pr_id": i + 1, "grupo": "sem_bot", "tempo_horas": v} for i, v in enumerate(sem)]
        + [
            {"pr_id": i + 11, "grupo": "com_bot", "tempo_horas": v}
            for i, v in enumerate(com_com_outlier)
        ]
    )
    comp_div = aplicar_ambos_testes(df_div, alpha=0.05)
    assert comp_div.mann_whitney.rejeitar_h0 is True
    assert comp_div.welch.rejeitar_h0 is False
    assert comp_div.concordam_decisao is False
    assert "divergiram" in comp_div.resumo_comparativo


def test_avaliacao_rapida_para_s02():
    """Garante que as funções rápidas para S02 retornam as chaves e decisões consistentes."""
    df = carregar_ou_gerar_simulados_s01(semente=99)
    res_rapido = avaliar_dataframe_rapido(df, alpha=0.05)

    assert set(res_rapido.keys()) == {
        "t_stat",
        "p_welch",
        "rejeita_welch",
        "u_stat",
        "p_mann_whitney",
        "rejeita_mann_whitney",
    }
    sem, com = extrair_grupos_dataframe(df)
    res_par = avaliar_par_rapido(sem, com, alpha=0.05)
    assert res_rapido == res_par

    # Validação da avaliação matricial rápida
    mat_sem = np.array([sem, sem])
    mat_com = np.array([com, com])
    res_mat = avaliar_matrizes_rapido(mat_sem, mat_com, alpha=0.05)
    assert len(res_mat["t_stat"]) == 2
    assert pytest.approx(res_mat["p_welch"][0]) == res_par["p_welch"]
    assert pytest.approx(res_mat["p_mann_whitney"][0]) == res_par["p_mann_whitney"]


def test_exportacao_csv_e_relatorio(tmp_path):
    """Testa a geração do CSV consolidado e do relatório textual completo."""
    comp_reais = executar_analise_dados_reais()
    assert comp_reais.welch.n_sem_bot == 30
    assert comp_reais.mann_whitney.n_com_bot == 30

    caminho_csv = tmp_path / "resultados_teste.csv"
    salvo = salvar_resultados_testes_s01(caminho_saida=caminho_csv, semente=42)
    assert salvo.exists()

    df_lido = pd.read_csv(salvo)
    assert len(df_lido) == 4  # 2 testes (simulados S01) + 2 testes (dados reais)
    assert set(df_lido["nome_estatistica"]) == {"t", "U"}

    relatorio = gerar_relatorio_testes_s01(semente=42)
    assert "LAB04S01" in relatorio
    assert "Welch" in relatorio
    assert "Mann-Whitney" in relatorio
