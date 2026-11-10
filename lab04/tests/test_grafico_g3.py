"""Testes unitários para o módulo do gráfico G3 (Erro Tipo I comparativo) - Issue #52."""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest

from lab04.src.cenario import CENARIO
from lab04.src.grafico_g3 import (
    COR_MANN_WHITNEY,
    COR_REFERENCIA,
    COR_WELCH,
    CAMINHO_G3_PADRAO,
    CAMINHO_DADOS_G3_CONSOLIDADO,
    carregar_ou_simular_dados_g3,
    gerar_g3,
    salvar_grafico_g3,
    simular_condicoes_g3,
    texto_interpretativo_g3,
)


def test_cores_padronizadas_g3():
    """Valida as constantes de cores padronizadas em todo o laboratório."""
    assert COR_WELCH == "#1f77b4"
    assert COR_MANN_WHITNEY == "#ff7f0e"
    assert COR_REFERENCIA == "#d62728"


def test_simular_condicoes_g3_estrutura_e_valores():
    """Valida a simulação das 3 condições experimentais sob H0 para o G3."""
    df = simular_condicoes_g3(semente=42, n_simulacoes=100)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 6  # 3 cenários x 2 testes
    assert set(df["cenario_codigo"].unique()) == {
        "Q1_Base",
        "Q3_Outliers",
        "Q3_AmostraPequena",
    }
    assert set(df["teste"].unique()) == {
        CENARIO.teste_parametrico,
        CENARIO.teste_nao_parametrico,
    }

    colunas_obrigatorias = {
        "cenario_codigo",
        "cenario_rotulo",
        "condicao",
        "teste",
        "abordagem",
        "n_simulacoes",
        "n_rejeicoes",
        "taxa_empirica",
        "taxa_empirica_pct",
        "taxa_teorica",
        "taxa_teorica_pct",
        "desvio_nominal_pct",
        "ic_inf",
        "ic_sup",
        "ic_inf_pct",
        "ic_sup_pct",
        "comportamento",
        "ordem_cenario",
    }
    assert colunas_obrigatorias.issubset(set(df.columns))

    # Todas as taxas teóricas devem ser exatamente 5%
    assert (df["taxa_teorica"] == 0.05).all()
    assert (df["taxa_teorica_pct"] == 5.0).all()


def test_dados_consolidados_10000_simulacoes():
    """Valida as taxas oficiais com 10.000 repetições (semente = 42)."""
    df = carregar_ou_simular_dados_g3(semente=42, n_simulacoes=10_000)

    assert len(df) == 6
    df_w = df[df["teste"] == CENARIO.teste_parametrico].set_index("cenario_codigo")
    df_mw = df[df["teste"] == CENARIO.teste_nao_parametrico].set_index("cenario_codigo")

    # Welch: 3.93% (Base), 3.28% (Outliers), 2.90% (Amostra Pequena)
    assert df_w.loc["Q1_Base", "taxa_empirica_pct"] == pytest.approx(3.93, abs=0.01)
    assert df_w.loc["Q3_Outliers", "taxa_empirica_pct"] == pytest.approx(3.28, abs=0.01)
    assert df_w.loc["Q3_AmostraPequena", "taxa_empirica_pct"] == pytest.approx(2.90, abs=0.01)

    # Mann-Whitney: 4.58% (Base), 4.52% (Outliers), 4.33% (Amostra Pequena)
    assert df_mw.loc["Q1_Base", "taxa_empirica_pct"] == pytest.approx(4.58, abs=0.01)
    assert df_mw.loc["Q3_Outliers", "taxa_empirica_pct"] == pytest.approx(4.52, abs=0.01)
    assert df_mw.loc["Q3_AmostraPequena", "taxa_empirica_pct"] == pytest.approx(4.33, abs=0.01)

    # Nenhum teste é liberal
    assert (df["taxa_empirica_pct"] <= 5.0).all()


def test_gerar_g3_elementos_graficos():
    """Valida a construção visual da Figure do gráfico G3."""
    df_amostra = simular_condicoes_g3(semente=42, n_simulacoes=50)
    fig = gerar_g3(df_dados=df_amostra, semente=42, n_simulacoes=50)

    assert isinstance(fig, plt.Figure)
    axes = fig.get_axes()
    assert len(axes) == 1
    ax = axes[0]

    # Validação do título
    titulo = ax.get_title()
    assert "G3" in titulo
    assert "Erro Tipo I" in titulo

    # Validação dos eixos
    ylabel = ax.get_ylabel()
    assert "Taxa Empírica de Erro Tipo I (%)" in ylabel

    xlabel = ax.get_xlabel()
    assert "Cenário" in xlabel

    # Validação da linha de referência de 5%
    linhas_horizontais = [line for line in ax.lines if hasattr(line, "get_ydata")]
    # Pelo menos a linha axhline em y=5%
    valores_y_linhas = [line.get_ydata()[0] for line in ax.lines if len(line.get_ydata()) > 0]
    assert any(pytest.approx(y, abs=0.1) == 5.0 for y in valores_y_linhas)

    # Validação da legenda
    legenda = ax.get_legend()
    assert legenda is not None
    textos_legenda = [t.get_text() for t in legenda.get_texts()]
    assert any("Welch" in t for t in textos_legenda)
    assert any("Mann-Whitney" in t for t in textos_legenda)
    assert any("5,0%" in t or "5.0%" in t for t in textos_legenda)

    plt.close(fig)


def test_salvar_grafico_g3(tmp_path):
    """Valida a persistência em arquivo de imagem PNG."""
    caminho_teste = tmp_path / "teste_g3.png"
    p_salvo = salvar_grafico_g3(caminho_saida=caminho_teste)

    assert p_salvo.exists()
    assert p_salvo.stat().st_size > 1000  # Imagem PNG não-vazia


def test_texto_interpretativo_g3_tamanho_e_conteudo():
    """Valida que o texto interpretativo atende às 2-4 frases e cita os elementos exigidos."""
    import re
    texto = texto_interpretativo_g3()

    # Contagem de frases completas separadas por ponto final seguido de espaço e letra maiúscula
    frases = [f.strip() for f in re.split(r"\.\s+(?=[A-ZÀ-Ú])", texto.strip()) if f.strip()]
    assert 2 <= len(frases) <= 4

    assert "G3" in texto
    assert "Mann-Whitney" in texto
    assert "Welch" in texto
    assert "5%" in texto
    assert "conservador" in texto
    assert "maiores desvios" in texto or "desvios" in texto
