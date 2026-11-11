"""Gráfico G4: Curvas de poder estatístico dos dois testes (Q2 e Q3).

Issue #54 / #56: [ LAB04S02 ] Implementar gráfico G4 das curvas de poder estatístico
e integrar simulações e gráficos ao dashboard.

Este módulo constrói o gráfico G4 (1x2 painéis):
- Painel esquerdo: Curvas de poder estatístico (proporção de rejeições de H0 × tamanho do
  efeito percentual) dos dois testes no mesmo gráfico para o Cenário Original (Q2, n=30)
  e para as duas situações de Violação de Pressupostos (Q3: Outliers 10% com n=30 e
  Amostra Pequena com n=10), mantendo as cores oficiais (Azul para t de Welch e Laranja
  para U de Mann-Whitney).
- Painel direito: Diferença de poder (Poder_Mann-Whitney - Poder_Welch, em pontos
  percentuais) em função do tamanho do efeito, contrastando os cenários log-normais (Q2 e Q3,
  onde Mann-Whitney domina) com o Controle Teórico Gaussiano (Normal simétrica sem outliers,
  onde a vantagem muda de lado em favor do teste t de Welch).

Uso via linha de comando:
    python -m lab04.src.grafico_g4
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from lab04.src.cenario import CENARIO
from lab04.src.simulacao_q2 import ResultadoSimulacaoQ2, carregar_ou_executar_q2
from lab04.src.simulacao_q3 import ResultadoSimulacaoQ3, carregar_ou_executar_q3

# Cores oficiais padronizadas para cada teste em todas as visualizações (G2, G3 e G4)
COR_WELCH = "#1f77b4"  # Azul para o teste paramétrico (t de Welch)
COR_MANN_WHITNEY = "#ff7f0e"  # Laranja para o teste não-paramétrico (Mann-Whitney)
COR_META_PODER = "#2ca02c"  # Verde para a referência clássica de 80% de poder
COR_ALPHA = "#d62728"  # Vermelho para o nível nominal α = 5% em efeito zero

CAMINHO_DADOS_DIR = Path(__file__).resolve().parent.parent / "data"
CAMINHO_G4_PADRAO = CAMINHO_DADOS_DIR / "g4_curvas_poder.png"


def carregar_ou_simular_dados_g4(
    semente: int = 42,
    n_simulacoes: int = 10_000,
    forcar_reexecucao: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Retorna (df_poder_largo_q2_q3, df_controle_gaussiano) para plotagem do G4."""
    res_q3: ResultadoSimulacaoQ3 = carregar_ou_executar_q3(
        semente=semente,
        n_simulacoes=n_simulacoes,
        forcar_reexecucao=forcar_reexecucao,
    )
    res_q2: ResultadoSimulacaoQ2 = carregar_ou_executar_q2(
        semente=semente,
        n_simulacoes=n_simulacoes,
        forcar_reexecucao=forcar_reexecucao,
    )
    return res_q3.df_poder_largo.copy(), res_q2.df_controle_gaussiano.copy()


def gerar_g4(
    df_poder_largo: Optional[pd.DataFrame] = None,
    df_gaussiano: Optional[pd.DataFrame] = None,
    semente: int = 42,
    n_simulacoes: int = 10_000,
    alpha: float = CENARIO.alpha,
) -> plt.Figure:
    """Constrói a Figure 1x2 do Gráfico G4 com as curvas de poder (Q2 e Q3)."""
    if df_poder_largo is None or df_gaussiano is None:
        df_largo_padrao, df_gauss_padrao = carregar_ou_simular_dados_g4(
            semente=semente, n_simulacoes=n_simulacoes
        )
        df_poder = df_poder_largo if df_poder_largo is not None else df_largo_padrao
        df_gauss = df_gaussiano if df_gaussiano is not None else df_gauss_padrao
    else:
        df_poder = df_poder_largo
        df_gauss = df_gaussiano

    fig, (ax_curvas, ax_vantagem) = plt.subplots(1, 2, figsize=(13.5, 6.0), dpi=100)

    estilos_cenarios = [
        ("Q2_Base", "Cenário Original (Q2: n=30)", "-", "o", 2.4, 1.0),
        ("Q3_Outliers", "Violação: Outliers 10% (Q3: n=30)", "--", "s", 2.0, 0.92),
        ("Q3_AmostraPequena", "Violação: Amostra Pequena (Q3: n=10)", ":", "^", 1.9, 0.85),
    ]

    # -------------------------------------------------------------------------
    # Painel Esquerdo: Curvas de Poder dos Dois Testes no Mesmo Gráfico (Q2 e Q3)
    # -------------------------------------------------------------------------
    for cod, rotulo, ls, marker, lw, alpha_linha in estilos_cenarios:
        sub = df_poder[df_poder["cenario_codigo"] == cod].sort_values("efeito_pct")
        if len(sub) == 0:
            continue
        x = sub["efeito_pct"].to_numpy()
        yw = sub["poder_welch_pct"].to_numpy()
        ym = sub["poder_mann_whitney_pct"].to_numpy()

        ax_curvas.plot(
            x,
            ym,
            color=COR_MANN_WHITNEY,
            linestyle=ls,
            marker=marker,
            linewidth=lw,
            markersize=6.5,
            alpha=alpha_linha,
            label=f"Mann-Whitney — {rotulo}",
        )
        ax_curvas.plot(
            x,
            yw,
            color=COR_WELCH,
            linestyle=ls,
            marker=marker,
            linewidth=lw,
            markersize=6.5,
            alpha=alpha_linha,
            label=f"t de Welch — {rotulo}",
        )

    ax_curvas.axhline(
        alpha * 100.0,
        color=COR_ALPHA,
        linestyle="-.",
        linewidth=1.3,
        alpha=0.8,
        label=f"Nível de significância α = {alpha * 100:.0f}% (efeito = 0%)",
    )
    ax_curvas.axhline(
        80.0,
        color=COR_META_PODER,
        linestyle="--",
        linewidth=1.3,
        alpha=0.8,
        label="Meta de poder estatístico = 80%",
    )

    ax_curvas.set_title(
        "Curvas de Poder Estatístico: Cenário Original (Q2) vs. Violações (Q3)",
        fontsize=11.5,
        fontweight="bold",
    )
    ax_curvas.set_xlabel(
        "Tamanho do efeito: redução no tempo até o merge (%)",
        fontsize=10.5,
        fontweight="bold",
    )
    ax_curvas.set_ylabel(
        "Proporção de rejeições de H₀ / Poder (%)",
        fontsize=10.5,
        fontweight="bold",
    )
    ax_curvas.set_xticks([0, 10, 20, 30, 40, 50])
    ax_curvas.set_ylim(0.0, 90.0)
    ax_curvas.grid(True, linestyle=":", alpha=0.5)
    ax_curvas.legend(loc="upper left", fontsize=8.0, framealpha=0.94)

    # -------------------------------------------------------------------------
    # Painel Direito: Vantagem de Poder (MW - Welch) e Mudança de Lado
    # -------------------------------------------------------------------------
    ax_vantagem.axhline(0.0, color="black", linestyle="-", linewidth=1.2)
    ax_vantagem.axhspan(
        0.0,
        45.0,
        color=COR_MANN_WHITNEY,
        alpha=0.06,
        label="Zona de vantagem: Mann-Whitney mais poderoso (Δ > 0)",
    )
    ax_vantagem.axhspan(
        -8.0,
        0.0,
        color=COR_WELCH,
        alpha=0.08,
        label="Zona de vantagem: t de Welch mais poderoso (Δ < 0)",
    )

    estilos_vantagem = [
        ("Q2_Base", "Log-normal Original (Q2, n=30)", "-", "o", "#d95f02"),
        ("Q3_Outliers", "Violação: Outliers 10% (Q3, n=30)", "--", "s", "#8c2d04"),
        ("Q3_AmostraPequena", "Violação: Amostra Pequena (Q3, n=10)", ":", "^", "#fe9929"),
    ]
    for cod, rotulo, ls, marker, cor_cenario in estilos_vantagem:
        sub = df_poder[df_poder["cenario_codigo"] == cod].sort_values("efeito_pct")
        if len(sub) == 0:
            continue
        ax_vantagem.plot(
            sub["efeito_pct"].to_numpy(),
            sub["vantagem_mw_pp"].to_numpy(),
            color=cor_cenario,
            linestyle=ls,
            marker=marker,
            linewidth=2.2,
            markersize=6.5,
            label=rotulo,
        )

    if len(df_gauss) > 0:
        sub_g = df_gauss.sort_values("efeito_pct")
        ax_vantagem.plot(
            sub_g["efeito_pct"].to_numpy(),
            sub_g["vantagem_mw_pp"].to_numpy(),
            color=COR_WELCH,
            linestyle="-.",
            marker="D",
            linewidth=2.2,
            markersize=6.0,
            label="Controle Normal Simétrico sem Outliers (vantagem muda p/ Welch)",
        )

    ax_vantagem.set_title(
        "Diferença de Poder (Mann-Whitney − Welch) e Quando Muda de Lado",
        fontsize=11.5,
        fontweight="bold",
    )
    ax_vantagem.set_xlabel(
        "Tamanho do efeito: redução no tempo até o merge (%)",
        fontsize=10.5,
        fontweight="bold",
    )
    ax_vantagem.set_ylabel(
        "Diferença de poder: Poder(Mann-Whitney) − Poder(Welch) (p.p.)",
        fontsize=10.5,
        fontweight="bold",
    )
    ax_vantagem.set_xticks([0, 10, 20, 30, 40, 50])
    ax_vantagem.set_ylim(-6.0, 44.0)
    ax_vantagem.grid(True, linestyle=":", alpha=0.5)
    ax_vantagem.legend(loc="upper left", fontsize=8.0, framealpha=0.94)

    fig.suptitle(
        f"G4 — Curvas de Poder Estatístico dos Dois Testes × Tamanho do Efeito (Q2 e Q3 | 10.000 simulações, semente = {semente})",
        fontsize=13,
        fontweight="bold",
    )
    fig.tight_layout()
    return fig


def salvar_grafico_g4(
    fig: Optional[plt.Figure] = None,
    caminho_saida: Path | str = CAMINHO_G4_PADRAO,
    dpi: int = 200,
) -> Path:
    """Salva o gráfico G4 em PNG."""
    p_saida = Path(caminho_saida)
    p_saida.parent.mkdir(parents=True, exist_ok=True)
    figura = fig if fig is not None else gerar_g4()
    figura.savefig(p_saida, dpi=dpi, bbox_inches="tight")
    plt.close(figura)
    return p_saida


def texto_interpretativo_g4(
    df_poder_largo: Optional[pd.DataFrame] = None,
    df_gaussiano: Optional[pd.DataFrame] = None,
) -> str:
    """Gera o texto explicativo de 2 a 4 frases para a Seção 5 ('Poder') do Dashboard."""
    if df_poder_largo is None or df_gaussiano is None:
        df_p, df_g = carregar_ou_simular_dados_g4()
    else:
        df_p, df_g = df_poder_largo, df_gaussiano

    base_50 = df_p[(df_p["cenario_codigo"] == "Q2_Base") & (df_p["efeito_pct"] == 50.0)].iloc[0]
    out_50 = df_p[(df_p["cenario_codigo"] == "Q3_Outliers") & (df_p["efeito_pct"] == 50.0)].iloc[0]
    small_50 = df_p[
        (df_p["cenario_codigo"] == "Q3_AmostraPequena") & (df_p["efeito_pct"] == 50.0)
    ].iloc[0]
    gauss_30 = df_g[df_g["efeito_pct"] == 30.0].iloc[0]

    return (
        f"O gráfico G4 mostra que o poder estatístico cresce com o tamanho do efeito e que o teste "
        f"U de Mann-Whitney (laranja) supera o teste t de Welch (azul) em todas as situações log-normais "
        f"simuladas, ampliando sua vantagem à medida que o efeito aumenta (em δ = 50%, atinge "
        f"{float(base_50['poder_mann_whitney_pct']):.2f}% contra {float(base_50['poder_welch_pct']):.2f}% "
        f"no cenário original, uma vantagem de +{float(base_50['vantagem_mw_pp']):.2f} p.p.). "
        f"Sob violação de pressupostos por outliers severos (Q3), o poder de Welch sofre um colapso "
        f"drástico (caindo para {float(out_50['poder_welch_pct']):.2f}% em δ = 50%), enquanto Mann-Whitney "
        f"mantém {float(out_50['poder_mann_whitney_pct']):.2f}% (+{float(out_50['vantagem_mw_pp']):.2f} p.p. "
        f"de vantagem), e com amostra pequena (n = 10) Mann-Whitney também lidera "
        f"({float(small_50['poder_mann_whitney_pct']):.2f}% vs. {float(small_50['poder_welch_pct']):.2f}%). "
        f"Como demonstra o painel direito, a vantagem só muda de lado em favor do teste t de Welch "
        f"quando os dados seguem uma distribuição Normal simétrica sem outliers (onde Welch atinge "
        f"{float(gauss_30['poder_welch_pct']):.2f}% contra {float(gauss_30['poder_mann_whitney_pct']):.2f}% "
        f"de Mann-Whitney em δ = 30%, devido à eficiência assintótica relativa de 95,5% dos postos sob normalidade)."
    )


if __name__ == "__main__":  # pragma: no cover
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    df_p, df_g = carregar_ou_simular_dados_g4(semente=42, n_simulacoes=10_000)
    caminho = salvar_grafico_g4(gerar_g4(df_p, df_g))
    print(f"G4 salvo em: {caminho}")
    print(texto_interpretativo_g4(df_p, df_g))
