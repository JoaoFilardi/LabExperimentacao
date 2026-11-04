import matplotlib
matplotlib.use("Agg")

from lab04.src.grafico_g1 import (
    carregar_reais, carregar_simulados, gerar_g1, texto_interpretativo,
)


def test_g1_tem_quatro_paineis_com_rotulos():
    fig = gerar_g1(carregar_reais(), carregar_simulados())
    assert len(fig.axes) == 4
    assert fig._suptitle.get_text().startswith("G1")
    assert "horas" in fig.axes[2].get_xlabel()
    assert fig.axes[0].get_ylabel() != ""


def test_g1_reprodutivel():
    a = carregar_simulados(semente=42)
    b = carregar_simulados(semente=42)
    assert a.equals(b)


def test_texto_interpretativo_nao_vazio():
    assert len(texto_interpretativo(carregar_reais(), carregar_simulados())) > 100