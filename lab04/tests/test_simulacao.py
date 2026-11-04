"""Testes unitários para o módulo de simulação e geração de dados reproduzíveis (#46)."""

import numpy as np
import pandas as pd
import pytest

from lab04.src.dados_reais import (
    carregar_dados_reais,
    perfilar_grupo,
    obter_resumo_estatistico_reais,
    CAMINHO_DADOS_REAIS_PADRAO,
)
from lab04.src.simulacao import (
    GeradorDadosSimulados,
    ParametrosSimulacao,
    gerar_e_salvar_dataset_s01,
    CAMINHO_DADOS_SIMULADOS_S01,
)


def test_dados_reais_existencia_e_estrutura():
    """Valida o carregamento dos dados reais e presença das colunas esperadas."""
    df_reais = carregar_dados_reais(CAMINHO_DADOS_REAIS_PADRAO)
    assert len(df_reais) == 60
    assert set(df_reais["grupo"].unique()) == {"com_bot", "sem_bot"}
    assert df_reais["tempo_horas"].min() > 0


def test_perfilamento_dados_reais():
    """Valida as estatísticas descritivas calculadas para os grupos reais."""
    resumo = obter_resumo_estatistico_reais()
    est_sem = resumo["sem_bot"]
    est_com = resumo["com_bot"]

    assert est_sem.n == 30
    assert est_com.n == 30
    # Ambas as distribuições devem exibir assimetria positiva típica de tempos de software
    assert est_sem.assimetria > 1.0
    assert est_com.assimetria > 1.0
    # Parâmetros lognormais devem ser consistentes
    assert 2.0 < est_sem.log_mu < 3.5
    assert 0.5 < est_sem.log_sigma < 1.5


def test_reprodutibilidade_semente_fixa():
    """Garante que a mesma semente gera exatamente o mesmo dataset (bit a bit)."""
    gerador1 = GeradorDadosSimulados(semente=42)
    df1 = gerador1.gerar_dataset_experimento(n_sem_bot=30, n_com_bot=30)

    gerador2 = GeradorDadosSimulados(semente=42)
    df2 = gerador2.gerar_dataset_experimento(n_sem_bot=30, n_com_bot=30)

    pd.testing.assert_frame_equal(df1, df2)


def test_sementes_distintas_geram_dados_diferentes():
    """Garante que sementes diferentes geram sequências pseudoaleatórias distintas."""
    gerador1 = GeradorDadosSimulados(semente=42)
    df1 = gerador1.gerar_dataset_experimento(n_sem_bot=15, n_com_bot=15)

    gerador2 = GeradorDadosSimulados(semente=99)
    df2 = gerador2.gerar_dataset_experimento(n_sem_bot=15, n_com_bot=15)

    assert not np.allclose(df1["tempo_horas"].values, df2["tempo_horas"].values)


def test_geracao_sob_h0():
    """Valida a geração sob H0 com parâmetros idênticos entre grupos."""
    gerador = GeradorDadosSimulados(semente=123)
    df = gerador.gerar_dataset_experimento(n_sem_bot=5000, n_com_bot=5000, sob_h0=True)

    sem = df[df["grupo"] == "sem_bot"]["tempo_horas"]
    com = df[df["grupo"] == "com_bot"]["tempo_horas"]

    # Sob H0 com 5000 amostras, as médias e medianas devem ser muito próximas
    assert abs(np.median(sem) - np.median(com)) < 1.5
    assert abs(np.mean(sem) - np.mean(com)) < 2.5


def test_geracao_com_efeito_configuravel():
    """Valida que a redução percentual diminui os tempos do grupo com_bot."""
    gerador = GeradorDadosSimulados(semente=77)
    df = gerador.gerar_dataset_experimento(
        n_sem_bot=2000, n_com_bot=2000, sob_h0=False, efeito_reducao=0.30
    )

    sem = df[df["grupo"] == "sem_bot"]["tempo_horas"]
    com = df[df["grupo"] == "com_bot"]["tempo_horas"]

    # Com 30% de redução, a mediana do com_bot deve ser substancialmente menor
    assert np.median(com) < np.median(sem)


def test_geracao_com_outliers_q3():
    """Valida a injeção controlada de outliers para testes de violação de pressupostos."""
    gerador = GeradorDadosSimulados(semente=42)
    df_normal = gerador.gerar_dataset_experimento(n_sem_bot=30, n_com_bot=30, sob_h0=True)

    gerador.redefinir_semente(42)
    df_outliers, idx_outliers = gerador.gerar_dataset_com_outliers(
        n_sem_bot=30, n_com_bot=30, prop_outliers=0.10, fator_multiplicador=5.0, sob_h0=True
    )

    # Verifica que os índices selecionados receberam valores estritamente maiores
    assert len(idx_outliers) == 6
    assert (
        df_outliers.loc[idx_outliers, "tempo_horas"]
        > df_normal.loc[idx_outliers, "tempo_horas"]
    ).all()
    # A média do dataset contaminado deve ser superior à média do dataset base
    assert df_outliers["tempo_horas"].mean() > df_normal["tempo_horas"].mean()


def test_geracao_dataset_gaussiano():
    """Valida geração de dados sob normalidade pura."""
    gerador = GeradorDadosSimulados(semente=42)
    df = gerador.gerar_dataset_gaussiano(n_sem_bot=1000, n_com_bot=1000, media=20.0, desvio=3.0)
    assert len(df) == 2000
    assert 19.5 < df["tempo_horas"].mean() < 20.5


def test_gerar_e_salvar_dataset_s01(tmp_path):
    """Valida a função de conveniência para salvar o dataset da S01."""
    caminho_teste = tmp_path / "dados_teste.csv"
    df = gerar_e_salvar_dataset_s01(semente=42, caminho_saida=caminho_teste)

    assert caminho_teste.exists()
    assert len(df) == 60
    assert set(df["grupo"].unique()) == {"com_bot", "sem_bot"}
