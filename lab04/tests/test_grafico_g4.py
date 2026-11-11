"""Testes unitários para Q2, gráfico G4 e integração completa do dashboard na S02 (#56)."""

from pathlib import Path
import matplotlib

matplotlib.use("Agg")

import pytest

from lab04.src.grafico_g4 import (
    COR_MANN_WHITNEY,
    COR_WELCH,
    carregar_ou_simular_dados_g4,
    gerar_g4,
    salvar_grafico_g4,
    texto_interpretativo_g4,
)
from lab04.src.simulacao_q2 import (
    carregar_ou_executar_q2,
    executar_simulacao_q2,
    executar_simulacao_q2_gaussiano,
)


def test_simulacao_q2_validacao_e_execucao(tmp_path):
    with pytest.raises(ValueError, match="pelo menos 5 tamanhos de efeito"):
        executar_simulacao_q2(n_simulacoes=20, efeitos=(0.0, 0.1, 0.2))

    res_oficial = carregar_ou_executar_q2(semente=42, n_simulacoes=10_000)
    assert len(res_oficial.df_poder_q2) == 6
    assert len(res_oficial.df_controle_gaussiano) == 6
    assert "Mann-Whitney" in res_oficial.sintese_comparativa

    # No controle Gaussiano para efeitos > 0, t de Welch tem mais poder (vantagem_mw_pp < 0)
    sub_gauss_pos = res_oficial.df_controle_gaussiano[
        res_oficial.df_controle_gaussiano["efeito_pct"] > 0
    ]
    assert (sub_gauss_pos["vantagem_mw_pp"] < 0).all()

    # Execução reduzida com salvamento em caminho temporário
    csv_tmp = tmp_path / "q2_tmp.csv"
    res_curto = carregar_ou_executar_q2(
        semente=77, n_simulacoes=40, forcar_reexecucao=True, caminho_csv=csv_tmp
    )
    assert len(res_curto.df_poder_q2) == 6


def test_grafico_g4_estrutura_cores_e_salvamento(tmp_path):
    df_p, df_g = carregar_ou_simular_dados_g4(semente=42, n_simulacoes=10_000)
    fig = gerar_g4(df_poder_largo=df_p, df_gaussiano=df_g)

    assert len(fig.axes) == 2
    assert fig._suptitle.get_text().startswith("G4")

    ax_curvas, ax_vantagem = fig.axes
    assert "Poder" in ax_curvas.get_ylabel()
    assert "Tamanho do efeito" in ax_curvas.get_xlabel()
    assert "Diferença de poder" in ax_vantagem.get_ylabel()
    assert ax_curvas.get_legend() is not None
    assert ax_vantagem.get_legend() is not None

    cores_linhas = {linha.get_color() for linha in ax_curvas.lines}
    assert COR_WELCH in cores_linhas
    assert COR_MANN_WHITNEY in cores_linhas

    saida_png = tmp_path / "g4_teste.png"
    caminho_salvo = salvar_grafico_g4(fig=fig, caminho_saida=saida_png, dpi=100)
    assert caminho_salvo.exists()

    texto = texto_interpretativo_g4(df_p, df_g)
    assert len(texto) > 150
    assert "79.08%" in texto
    assert "64.20%" in texto


def test_integracao_dashboard_s02_completa():
    """Verifica que o app.py integra Q1, Q2, Q3 e os 4 gráficos G1, G2, G3 e G4 na ordem exigida."""
    caminho_app = Path(__file__).resolve().parent.parent / "app.py"
    conteudo = caminho_app.read_text(encoding="utf-8")

    secoes_ordenadas = [
        "st.header(\"1. Cenário\")",
        "st.header(\"2. Os dados\")",
        "st.header(\"3. Como os testes funcionam\")",
        "st.header(\"4. Erro tipo I\")",
        "st.header(\"5. Poder\")",
        "st.header(\"6. Dados reais\")",
        "st.header(\"7. Conclusão\")",
    ]
    posicoes = [conteudo.index(s) for s in secoes_ordenadas]
    assert posicoes == sorted(posicoes), "As seções do dashboard devem estar na ordem exigida!"

    for funcao_grafico in ("gerar_g1", "gerar_g2", "gerar_g3", "gerar_g4"):
        assert funcao_grafico in conteudo
