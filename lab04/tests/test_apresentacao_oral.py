"""Testes unitários para o módulo de preparação da apresentação oral — Perguntas 11 a 15 (#62)."""

import pytest

from lab04.src.apresentacao_oral import (
    avaliar_cenario_subdimensionado_n15_efeito_5pct,
    avaliar_impacto_alpha_001,
    construir_tabela_resumo_perguntas_6_a_10,
    construir_tabela_resumo_perguntas_11_a_15,
    gerar_roteiro_markdown_perguntas_6_a_10,
    gerar_roteiro_markdown_perguntas_11_a_15,
    obter_perguntas_6_a_10,
    obter_perguntas_11_a_15,
    obter_todas_perguntas,
)


def test_estrutura_perguntas_6_a_10():
    """Valida a estrutura e conteúdo do roteiro das Perguntas 6 a 10 (Issue #60)."""
    perguntas = obter_perguntas_6_a_10()
    assert len(perguntas) == 5
    assert [p.numero for p in perguntas] == [6, 7, 8, 9, 10]

    for p in perguntas:
        assert len(p.titulo_curto) > 8
        assert len(p.pergunta_oficial) > 20
        assert len(p.onde_apontar_no_dashboard) > 20
        assert len(p.fala_30_segundos) > 150
        assert len(p.pontos_chave_argicao) >= 3

    # Pergunta 6: Distribuição sob H0 e região de rejeição
    p6 = perguntas[0]
    assert p6.numero == 6
    assert "G2" in p6.pergunta_oficial
    assert "2,5%" in p6.fala_30_segundos
    assert "Student" in p6.fala_30_segundos
    assert "Normal padrão Z" in p6.fala_30_segundos

    # Pergunta 7: p-valor no exemplo
    p7 = perguntas[1]
    assert p7.numero == 7
    assert "56,26%" in p7.fala_30_segundos
    assert "13,15%" in p7.fala_30_segundos
    assert "NÃO" in p7.fala_30_segundos

    # Pergunta 8: Erro Tipo I vs Tipo II
    p8 = perguntas[2]
    assert p8.numero == 8
    assert "Erro Tipo I" in p8.fala_30_segundos
    assert "Erro Tipo II" in p8.fala_30_segundos
    assert "mais grave" in p8.fala_30_segundos

    # Pergunta 9: Erro Tipo I em G3
    p9 = perguntas[3]
    assert p9.numero == 9
    assert "conservador" in p9.fala_30_segundos
    assert "3,93%" in p9.fala_30_segundos
    assert "Mann-Whitney" in p9.fala_30_segundos

    # Pergunta 10: Poder em G4
    p10 = perguntas[4]
    assert p10.numero == 10
    assert "Mann-Whitney" in p10.fala_30_segundos
    assert "79,08%" in p10.fala_30_segundos
    assert "64,20%" in p10.fala_30_segundos


def test_tabela_resumo_e_roteiro_markdown_6_a_10():
    """Valida a tabela resumo e o markdown para as Perguntas 6 a 10."""
    df_resumo = construir_tabela_resumo_perguntas_6_a_10()
    assert len(df_resumo) == 5
    assert list(df_resumo["Nº"]) == [f"Pergunta {i}" for i in range(6, 11)]

    md = gerar_roteiro_markdown_perguntas_6_a_10()
    for n in range(6, 11):
        assert f"## Pergunta {n}" in md
    assert "Tiago Boaventura Amaral" in md

    todas = obter_todas_perguntas()
    assert len(todas) == 10
    assert [p.numero for p in todas] == list(range(6, 16))


def test_estrutura_perguntas_11_a_15():
    perguntas = obter_perguntas_11_a_15()
    assert len(perguntas) == 5
    assert [p.numero for p in perguntas] == [11, 12, 13, 14, 15]

    for p in perguntas:
        assert len(p.titulo_curto) > 10
        assert len(p.pergunta_oficial) > 20
        assert len(p.onde_apontar_no_dashboard) > 20
        assert len(p.fala_30_segundos) > 150
        assert len(p.pontos_chave_argicao) >= 3

    # Verifica que a Pergunta 13 também cobre a variante sobre n=15 e δ=5%
    p13 = perguntas[2]
    assert p13.numero == 13
    assert p13.pergunta_variante is not None
    assert p13.fala_variante_30_segundos is not None
    assert "4,45%" in p13.fala_variante_30_segundos


def test_avaliar_impacto_alpha_001_e_subdimensionamento():
    df_alpha = avaliar_impacto_alpha_001(semente=42, n_simulacoes=10_000)
    assert len(df_alpha) == 6
    # Em todos os efeitos, adotar alpha=0.01 reduz a taxa de rejeicao frente a alpha=0.05
    assert (df_alpha["reducao_welch_pp"] < 0).all()
    assert (df_alpha["reducao_mw_pp"] < 0).all()

    linha_h0 = df_alpha[df_alpha["efeito_pct"] == 0.0].iloc[0]
    assert pytest.approx(linha_h0["mw_alpha_001_pct"], abs=0.01) == 0.81
    assert pytest.approx(linha_h0["welch_alpha_001_pct"], abs=0.01) == 0.42

    sub_n15 = avaliar_cenario_subdimensionado_n15_efeito_5pct(semente=42, n_simulacoes=10_000)
    assert pytest.approx(sub_n15["poder_mann_whitney_pct"], abs=0.01) == 4.45
    assert pytest.approx(sub_n15["poder_welch_pct"], abs=0.01) == 3.35
    assert sub_n15["erro_tipo_2_mw_pct"] > 95.0
    assert sub_n15["erro_tipo_2_welch_pct"] > 96.0


def test_tabela_resumo_e_roteiro_markdown():
    df_resumo = construir_tabela_resumo_perguntas_11_a_15()
    assert len(df_resumo) == 5
    assert list(df_resumo["Nº"]) == [f"Pergunta {i}" for i in range(11, 16)]

    md = gerar_roteiro_markdown_perguntas_11_a_15()
    for n in range(11, 16):
        assert f"## Pergunta {n}" in md
    assert "55.47" in md
    assert "34.14" in md
