"""Testes unitários para o gráfico G2 e integração do dashboard inicial (#50)."""

from pathlib import Path
import matplotlib

matplotlib.use("Agg")

import numpy as np
import pandas as pd

from lab04.src.grafico_g1 import carregar_simulados
from lab04.src.grafico_g2 import (
    COR_MANN_WHITNEY,
    COR_REJEICAO,
    COR_WELCH,
    gerar_g2,
    texto_interpretativo_g2,
)


def test_g2_possui_dois_paineis_com_titulos_eixos_e_legendas():
    simulados = carregar_simulados(semente=42)
    fig = gerar_g2(simulados=simulados, semente=42)

    assert len(fig.axes) == 2
    assert fig._suptitle.get_text().startswith("G2")

    ax_welch, ax_mw = fig.axes
    assert "Welch" in ax_welch.get_title()
    assert "Mann-Whitney" in ax_mw.get_title()
    assert "t de Welch" in ax_welch.get_xlabel()
    assert "U de Mann-Whitney" in ax_mw.get_xlabel()
    assert "Densidade" in ax_welch.get_ylabel()
    assert "Densidade" in ax_mw.get_ylabel()

    # Ambos os painéis devem ter curvas nas cores padronizadas e regiões sombreadas
    assert ax_welch.lines[0].get_color() == COR_WELCH
    assert ax_mw.lines[0].get_color() == COR_MANN_WHITNEY
    assert len(ax_welch.collections) >= 4  # 2 caudas p-valor + 2 caudas região de rejeição
    assert len(ax_mw.collections) >= 4
    assert ax_welch.get_legend() is not None
    assert ax_mw.get_legend() is not None
    assert COR_REJEICAO != COR_WELCH and COR_REJEICAO != COR_MANN_WHITNEY


def test_g2_ramo_estatistica_positiva_e_rejeicao_h0():
    """Garante cobertura quando com_bot > sem_bot (t_obs > 0 e U_obs > mu_U) e há rejeição de H0."""
    sem = np.linspace(5.0, 10.0, 20)
    com = np.linspace(30.0, 40.0, 20)
    df_positivo = pd.DataFrame(
        [{"pr_id": i + 1, "grupo": "sem_bot", "tempo_horas": float(v)} for i, v in enumerate(sem)]
        + [{"pr_id": i + 21, "grupo": "com_bot", "tempo_horas": float(v)} for i, v in enumerate(com)]
    )
    fig = gerar_g2(simulados=df_positivo, semente=42)
    ax_welch, ax_mw = fig.axes
    assert "Rejeita H₀" in ax_welch.get_title()
    assert "Rejeita H₀" in ax_mw.get_title()


def test_texto_interpretativo_g2_consistente():
    texto = texto_interpretativo_g2(semente=42)
    assert len(texto) > 150
    assert "Welch" in texto
    assert "Mann-Whitney" in texto
    assert "0.5626" in texto
    assert "0.1315" in texto


def test_dashboard_app_contem_secoes_e_graficos_g1_g2():
    caminho_app = Path(__file__).resolve().parent.parent / "app.py"
    conteudo = caminho_app.read_text(encoding="utf-8")

    for secao in [
        "1. Cenário",
        "2. Os dados",
        "3. Como os testes funcionam",
        "4. Erro tipo I",
        "5. Poder",
        "6. Dados reais",
        "7. Conclusão",
    ]:
        assert secao in conteudo

    assert "gerar_g1" in conteudo
    assert "gerar_g2" in conteudo
    assert "https://github.com/JoaoFilardi/LabExperimentacao" in conteudo
