"""Testes automatizados para o módulo de simulação do Erro Tipo I (Q1) - Issue #51."""

import numpy as np
import pandas as pd
import pytest

from lab04.src.cenario import CENARIO
from lab04.src.simulacao_q1 import (
    calcular_intervalo_confianca_wilson,
    classificar_comportamento_erro_tipo_1,
    executar_simulacao_q1,
    carregar_ou_executar_q1,
    salvar_resultados_q1,
    obter_tabela_para_g3,
    gerar_texto_interpretativo_q1,
    ResultadoSimulacaoQ1,
    MetricasErroTipo1,
    CAMINHO_Q1_RESUMO_CSV,
    CAMINHO_Q1_PVALORES_CSV,
)


def test_calcular_intervalo_confianca_wilson():
    """Valida o cálculo do intervalo de confiança de Wilson para proporções."""
    p, inf, sup = calcular_intervalo_confianca_wilson(500, 10000, 0.95)
    assert p == 0.05
    assert 0.045 < inf < 0.05
    assert 0.05 < sup < 0.055

    # Validações de limites e erros
    with pytest.raises(ValueError, match="estritamente positivo"):
        calcular_intervalo_confianca_wilson(10, 0)
    with pytest.raises(ValueError, match="entre 0 e n_total"):
        calcular_intervalo_confianca_wilson(-1, 100)
    with pytest.raises(ValueError, match="entre 0 e n_total"):
        calcular_intervalo_confianca_wilson(105, 100)


def test_classificar_comportamento_erro_tipo_1():
    """Valida a classificação dos limiares de comportamento (Conservador, Liberal, Nominal)."""
    # Para n=10000 e alpha=0.05, a margem de erro a 95% é ~ 0.00427 -> [4.57%, 5.43%]
    classe_cons, _ = classificar_comportamento_erro_tipo_1(0.0393, alpha=0.05, n_simulacoes=10000)
    assert classe_cons == "Conservador"

    classe_nom, _ = classificar_comportamento_erro_tipo_1(0.0495, alpha=0.05, n_simulacoes=10000)
    assert classe_nom == "Nominal / Bem calibrado"

    classe_lib, _ = classificar_comportamento_erro_tipo_1(0.0650, alpha=0.05, n_simulacoes=10000)
    assert classe_lib == "Liberal"


def test_consistencia_vetorizado_vs_iterativo():
    """Garante que a execução vetorizada e a iterativa produzem exatamente os mesmos resultados."""
    n_test = 50
    semente = 123

    res_vet = executar_simulacao_q1(n_simulacoes=n_test, semente=semente, usar_vetorizado=True)
    res_ite = executar_simulacao_q1(n_simulacoes=n_test, semente=semente, usar_vetorizado=False)

    np.testing.assert_allclose(res_vet.df_detalhado["t_stat"], res_ite.df_detalhado["t_stat"], rtol=1e-4)
    np.testing.assert_allclose(res_vet.df_detalhado["p_welch"], res_ite.df_detalhado["p_welch"], rtol=1e-4)
    np.testing.assert_array_equal(res_vet.df_detalhado["rejeita_welch"], res_ite.df_detalhado["rejeita_welch"])

    np.testing.assert_allclose(res_vet.df_detalhado["u_stat"], res_ite.df_detalhado["u_stat"], rtol=1e-4)
    np.testing.assert_allclose(res_vet.df_detalhado["p_mann_whitney"], res_ite.df_detalhado["p_mann_whitney"], rtol=1e-4)
    np.testing.assert_array_equal(res_vet.df_detalhado["rejeita_mann_whitney"], res_ite.df_detalhado["rejeita_mann_whitney"])


def test_execucao_q1_completa_10000_simulacoes():
    """Valida as 10.000 simulações com semente 42 sob H0 e verifica valores exatos."""
    res = carregar_ou_executar_q1(semente=42, n_simulacoes=10_000)

    assert isinstance(res, ResultadoSimulacaoQ1)
    assert res.n_simulacoes == 10_000
    assert res.semente == 42
    assert res.alpha == 0.05
    assert len(res.df_detalhado) == 10_000

    # 1. Teste t de Welch
    w = res.metricas_welch
    assert w.n_simulacoes == 10_000
    assert w.n_rejeicoes == 393
    assert pytest.approx(w.taxa_erro_tipo_1, abs=1e-4) == 0.0393
    assert w.comportamento == "Conservador"
    assert w.criterio_bradley_estrito is False  # Welch < 0.045
    assert w.criterio_bradley_liberal is True   # Welch > 0.025
    assert w.ks_pvalor_uniforme < 0.001        # Desvia da uniforme U(0,1)

    # 2. Teste U de Mann-Whitney
    mw = res.metricas_mann_whitney
    assert mw.n_simulacoes == 10_000
    assert mw.n_rejeicoes == 458
    assert pytest.approx(mw.taxa_erro_tipo_1, abs=1e-4) == 0.0458
    assert mw.comportamento == "Nominal / Bem calibrado"
    assert mw.criterio_bradley_estrito is True   # Mann-Whitney em [0.045, 0.055]
    assert mw.criterio_bradley_liberal is True   # Mann-Whitney em [0.025, 0.075]
    assert mw.ks_pvalor_uniforme > 0.05          # Aderente à uniforme U(0,1)

    # Ambos os testes devem respeitar a taxa teórica máxima de falsos positivos (nenhum é liberal)
    assert w.taxa_erro_tipo_1 <= 0.05
    assert mw.taxa_erro_tipo_1 <= 0.05


def test_obter_tabela_para_g3():
    """Valida a estrutura de dados preparada para o Gráfico G3."""
    res = carregar_ou_executar_q1(semente=42, n_simulacoes=10_000)
    df_g3 = obter_tabela_para_g3(res)

    assert isinstance(df_g3, pd.DataFrame)
    assert len(df_g3) == 2
    assert set(df_g3.columns) == {
        "cenario",
        "condicao",
        "teste",
        "tipo_abordagem",
        "taxa_empirica",
        "taxa_teorica",
        "n_rejeicoes",
        "n_simulacoes",
        "ic_inf",
        "ic_sup",
        "comportamento",
    }
    assert (df_g3["taxa_teorica"] == 0.05).all()


def test_gerar_texto_interpretativo_q1():
    """Valida geração do texto interpretativo para o Dashboard."""
    res = carregar_ou_executar_q1(semente=42, n_simulacoes=10_000)
    texto = gerar_texto_interpretativo_q1(res)

    assert "10.000 simulações" in texto
    assert "Mann-Whitney" in texto
    assert "Welch" in texto
    assert "conservador" in texto
    assert "liberal" in texto


def test_salvamento_e_carregamento_disco(tmp_path):
    """Valida salvamento e recarregamento em arquivos customizados."""
    res = executar_simulacao_q1(n_simulacoes=20, semente=99)
    p_res = tmp_path / "resumo.csv"
    p_det = tmp_path / "detalhado.csv"

    salvar_resultados_q1(res, caminho_resumo=p_res, caminho_detalhado=p_det)
    assert p_res.exists()
    assert p_det.exists()

    df_det = pd.read_csv(p_det)
    assert len(df_det) == 20
    assert "p_welch" in df_det.columns
    assert "p_mann_whitney" in df_det.columns

