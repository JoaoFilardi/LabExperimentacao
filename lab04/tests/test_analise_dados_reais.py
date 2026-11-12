"""Testes unitários para a análise dos dados reais e consolidação comparativa (LAB04FINAL)."""

from pathlib import Path
import re

import numpy as np
import pandas as pd
import pytest

from lab04.src.analise_dados_reais import (
    CAMINHO_TABELA_COMPARATIVA_CSV,
    calcular_probabilidade_superioridade,
    executar_analise_completa_dados_reais,
    gerar_relatorio_textual_dados_reais,
    gerar_tabela_comparativa_secao6,
    salvar_tabela_comparativa_csv,
    verificar_integridade_dados,
    verificar_pressupostos_e_compatibilidade,
)
from lab04.src.cenario import CENARIO
from lab04.src.dados_reais import carregar_dados_reais
from lab04.src.grafico_g3 import texto_interpretativo_g3
from lab04.src.grafico_g4 import texto_interpretativo_g4


def test_verificar_integridade_dados_reais():
    """Valida a integridade técnica da amostra minerada do repositório tiangolo/fastapi."""
    df = carregar_dados_reais()
    diag = verificar_integridade_dados(df)

    assert diag.n_total == 60
    assert diag.n_sem_bot == 30
    assert diag.n_com_bot == 30
    assert diag.n_nulos == 0
    assert diag.n_duplicados == 0
    assert diag.n_tempos_negativos_ou_zero == 0
    assert diag.n_inconsistencias_temporais == 0
    assert diag.dados_integros is True
    assert any("íntegra" in m for m in diag.mensagens_validacao)


def test_verificar_pressupostos_e_compatibilidade():
    """Valida que os dados reais violam normalidade e justificam a robustez de Mann-Whitney."""
    df = carregar_dados_reais()
    pressup = verificar_pressupostos_e_compatibilidade(df)

    # Rejeição da normalidade por Shapiro-Wilk (p < 0.001)
    assert pressup.shapiro_p_sem_bot < 0.001
    assert pressup.shapiro_p_com_bot < 0.001
    assert pressup.normalidade_aceita_sem_bot is False
    assert pressup.normalidade_aceita_com_bot is False

    # Forte assimetria à direita
    assert pressup.assimetria_sem_bot > 1.5
    assert pressup.assimetria_com_bot > 1.5

    # Outliers de Tukey
    assert pressup.n_outliers_sem_bot == 3
    assert pressup.n_outliers_com_bot == 3

    assert "Mann-Whitney" in pressup.resumo_compatibilidade
    assert "Welch" in pressup.resumo_compatibilidade


def test_probabilidade_superioridade():
    """Valida o cálculo do Common Language Effect Size / probabilidade de superioridade."""
    sem = np.array([10.0, 20.0, 30.0])
    com = np.array([5.0, 15.0, 25.0])
    # 5 < 10,20,30 (3); 15 < 20,30 (2); 25 < 30 (1) -> 6 vitórias em 9 pares = 6/9 = 0.6667
    prob = calcular_probabilidade_superioridade(sem, com)
    assert prob == pytest.approx(6.0 / 9.0, abs=1e-4)

    # Array vazio retorna 0.5
    assert calcular_probabilidade_superioridade(np.array([]), np.array([])) == 0.5


def test_executar_analise_completa_dados_reais_welch():
    """Valida os resultados empíricos calculados para o Teste t de Welch nos dados reais."""
    rel = executar_analise_completa_dados_reais(alpha=0.05)
    w = rel.welch

    assert w.nome_teste == CENARIO.teste_parametrico
    assert w.n_controle == 30
    assert w.n_tratamento == 30

    # Médias: 27.42 h vs. 20.95 h (redução de 6.47 h ou ~23.6%)
    assert w.medida_central_controle == pytest.approx(27.4233, abs=0.01)
    assert w.medida_central_tratamento == pytest.approx(20.9500, abs=0.01)
    assert w.diferenca_central == pytest.approx(-6.4733, abs=0.01)
    assert w.percentual_reducao_central == pytest.approx(-23.605, abs=0.1)

    # Estatística t e graus de liberdade
    assert w.estatistica_valor == pytest.approx(-1.1280, abs=0.001)
    assert w.parametro_auxiliar_valor == pytest.approx(56.07, abs=0.1)

    # p-valor = 0.2641
    assert w.p_valor == pytest.approx(0.264132, abs=0.001)

    # Decisão formal em alpha = 0.05: Não rejeitar H0
    assert w.rejeitar_h0 is False
    assert "Não rejeitar H₀" in w.decisao_formal

    # Tamanho do efeito: d de Cohen = -0.2912 (pequeno)
    assert w.tamanho_efeito.valor == pytest.approx(-0.2912, abs=0.001)
    assert "pequeno" in w.tamanho_efeito.magnitude


def test_executar_analise_completa_dados_reais_mann_whitney():
    """Valida os resultados empíricos calculados para o Teste U de Mann-Whitney nos dados reais."""
    rel = executar_analise_completa_dados_reais(alpha=0.05)
    mw = rel.mann_whitney

    assert mw.nome_teste == CENARIO.teste_nao_parametrico
    assert mw.n_controle == 30
    assert mw.n_tratamento == 30

    # Medianas: 18.90 h vs. 13.60 h (redução de 5.30 h ou ~28.0%)
    assert mw.medida_central_controle == pytest.approx(18.90, abs=0.01)
    assert mw.medida_central_tratamento == pytest.approx(13.60, abs=0.01)
    assert mw.diferenca_central == pytest.approx(-5.30, abs=0.01)
    assert mw.percentual_reducao_central == pytest.approx(-28.04, abs=0.1)

    # Estatística U e aproximação normal z
    assert mw.estatistica_valor == pytest.approx(357.0, abs=0.1)
    assert mw.parametro_auxiliar_valor == pytest.approx(-1.3750, abs=0.001)

    # p-valor = 0.1715
    assert mw.p_valor == pytest.approx(0.171450, abs=0.001)

    # Decisão formal em alpha = 0.05: Não rejeitar H0
    assert mw.rejeitar_h0 is False
    assert "Não rejeitar H₀" in mw.decisao_formal

    # Tamanho do efeito: Rank-Biserial r = -0.2067 (pequeno)
    assert mw.tamanho_efeito.valor == pytest.approx(-0.2067, abs=0.001)
    assert "pequeno" in mw.tamanho_efeito.magnitude

    # Probabilidade de superioridade P(com < sem) ≈ 60.33%
    assert rel.probabilidade_superioridade == pytest.approx(0.6033, abs=0.01)


def test_concordancia_e_discussao_diferencas():
    """Valida a concordância na decisão e a discussão das divergências de sensibilidade."""
    rel = executar_analise_completa_dados_reais()

    # Ambos chegam à mesma decisão: não rejeitar H0
    assert rel.concordam_decisao is True
    assert rel.welch.rejeitar_h0 is False
    assert rel.mann_whitney.rejeitar_h0 is False

    # Mann-Whitney mais sensível (menor p-valor)
    assert rel.mann_whitney.p_valor < rel.welch.p_valor
    assert rel.diferenca_p_valor == pytest.approx(0.092682, abs=0.001)

    assert "assimetria" in rel.discussao_diferencas.lower()
    assert "outlier" in rel.discussao_diferencas.lower()
    assert "postos" in rel.discussao_diferencas.lower()


def test_tabela_comparativa_secao6_formato_e_salvamento(tmp_path):
    """Valida a tabela comparativa oficial da Seção 6 em DataFrame e CSV."""
    df_tab = gerar_tabela_comparativa_secao6()

    assert isinstance(df_tab, pd.DataFrame)
    assert len(df_tab) == 2

    colunas_exigidas = [
        "Teste",
        "Abordagem",
        "O que compara",
        "Estatística",
        "p-valor",
        "Tamanho do Efeito",
        "Decisão (α = 0,05)",
        "Conclusão Prática",
    ]
    assert list(df_tab.columns) == colunas_exigidas

    assert df_tab.loc[0, "Teste"] == CENARIO.teste_parametrico
    assert df_tab.loc[1, "Teste"] == CENARIO.teste_nao_parametrico

    assert "t = -1.1280" in df_tab.loc[0, "Estatística"]
    assert "U = 357.0" in df_tab.loc[1, "Estatística"]
    assert df_tab.loc[0, "p-valor"] == "0.2641"
    assert df_tab.loc[1, "p-valor"] == "0.1715"

    # Persistência em arquivo CSV
    csv_temp = tmp_path / "tabela_comparativa_teste.csv"
    p_salvo = salvar_tabela_comparativa_csv(caminho_saida=csv_temp)
    assert p_salvo.exists()
    assert p_salvo.stat().st_size > 200

    # Verifica arquivo salvo no caminho padrão
    assert CAMINHO_TABELA_COMPARATIVA_CSV.exists()


def test_gerar_relatorio_textual():
    """Valida a integridade do relatório textual estruturado."""
    texto = gerar_relatorio_textual_dados_reais()

    assert "LAB04FINAL" in texto
    assert "tiangolo/fastapi" in texto
    assert "Shapiro-Wilk" in texto
    assert "d de Cohen" in texto
    assert "Rank-Biserial" in texto
    assert "Não rejeitar H₀" in texto
    assert "G4" in texto


def test_textos_explicativos_g3_e_g4_frases_e_desempenho():
    """Garante que G3 e G4 tenham textos explicativos de 2 a 4 frases e destaquem melhor desempenho."""
    # 1. Gráfico G3
    t_g3 = texto_interpretativo_g3()
    frases_g3 = [f.strip() for f in re.split(r"\.\s+(?=[A-ZÀ-Ú])", t_g3.strip()) if f.strip()]
    assert 2 <= len(frases_g3) <= 4, f"G3 deve ter entre 2 e 4 frases, mas tem {len(frases_g3)}"
    assert "melhor desempenho" in t_g3
    assert "Mann-Whitney" in t_g3
    assert "Welch" in t_g3

    # 2. Gráfico G4
    t_g4 = texto_interpretativo_g4()
    frases_g4 = [f.strip() for f in re.split(r"\.\s+(?=[A-ZÀ-Ú])", t_g4.strip()) if f.strip()]
    assert 2 <= len(frases_g4) <= 4, f"G4 deve ter entre 2 e 4 frases, mas tem {len(frases_g4)}"
    assert "melhor desempenho" in t_g4
    assert "Mann-Whitney" in t_g4
    assert "Welch" in t_g4
    assert "Normal simétrica" in t_g4
