"""Testes unitários para o módulo de conclusão e consolidação final do dashboard (#57)."""

import pandas as pd
import pytest

from lab04.src.cenario import CENARIO
from lab04.src.conclusao_dashboard import (
    obter_expectativa_vs_resultados,
    obter_limitacoes_estudo,
    obter_recomendacao_final,
    obter_resumo_conclusao_markdown,
    obter_tabela_expectativa_vs_resultados,
)


def test_obter_expectativa_vs_resultados_estrutura():
    """Valida a estrutura de confronto entre expectativa prévia e resultados observados."""
    itens = obter_expectativa_vs_resultados()
    assert len(itens) == 5

    dimensoes = [item.dimensao for item in itens]
    assert any("Q1" in d for d in dimensoes)
    assert any("Q2" in d for d in dimensoes)
    assert any("Outliers" in d for d in dimensoes)
    assert any("Normalidade" in d for d in dimensoes)
    assert any("Reais" in d for d in dimensoes)

    for item in itens:
        assert len(item.previsao_pre_simulacao) > 20
        assert len(item.resultado_pos_simulacao) > 20
        assert "Confirmada" in item.status_confirmacao
        assert len(item.resumo_evidencia) > 10


def test_obter_tabela_expectativa_vs_resultados():
    """Valida a conversão da expectativa para DataFrame do Dashboard."""
    df = obter_tabela_expectativa_vs_resultados()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 5
    assert set(df.columns) == {
        "Dimensão Avaliada",
        "Expectativa Prévia (Antes de Simular)",
        "Resultado Observado (Simulações / Reais)",
        "Status da Previsão",
        "Evidência Central",
    }


def test_obter_recomendacao_final():
    """Valida a recomendação estatística oficial do grupo e critérios de transição."""
    rec = obter_recomendacao_final()
    assert rec.teste_recomendado == CENARIO.teste_nao_parametrico
    assert "Não-paramétrico" in rec.tipo_abordagem
    assert "Mann-Whitney" in rec.justificativa_principal
    assert "Rank-Biserial" in rec.tamanho_efeito_recomendado or "r_rb" in rec.tamanho_efeito_recomendado
    assert "Welch" in rec.quando_muda_a_recomendacao
    assert "simétricos" in rec.quando_muda_a_recomendacao
    assert len(rec.sintese_executiva_conclusao) > 50


def test_obter_limitacoes_estudo():
    """Valida as 4 principais limitações metodológicas identificadas no estudo."""
    lims = obter_limitacoes_estudo()
    assert len(lims) == 4

    titulos = [l.titulo.lower() for l in lims]
    assert any("amostral" in t for t in titulos)
    assert any("ecossistema" in t or "repositório" in t or "tiangolo" in t for t in titulos)
    assert any("univariado" in t or "covariáveis" in t for t in titulos)
    assert any("temporal" in t or "sazonalidade" in t for t in titulos)

    for l in lims:
        assert len(l.descricao) > 50
        assert len(l.impacto_na_inferencia) > 30
        assert len(l.como_mitigar_futuramente) > 30


def test_obter_resumo_conclusao_markdown():
    """Valida a geração do texto da síntese executiva de conclusão."""
    texto = obter_resumo_conclusao_markdown()
    assert "Mann-Whitney" in texto
    assert "Welch" in texto
    assert "Erro Tipo I" in texto
    assert "Poder" in texto or "poder" in texto
    assert "fastapi" in texto.lower()
    assert len(texto) > 200

