"""G2: distribuição da estatística de teste sob H0, região de rejeição e p-valor.

Issue #50: [LAB04S01] Implementar gráfico G2 e integrar dashboard inicial.

Este módulo constrói o gráfico G2 lado a lado para os dois testes do Par P1:
- Painel esquerdo: Teste t de Welch (distribuição t de Student sob H0 com gl de Welch-Satterthwaite).
- Painel direito: Teste U de Mann-Whitney (distribuição amostral de U sob H0 com média n1*n2/2).

Em ambos os painéis são destacados:
1. A curva de densidade de probabilidade teórica quando H0 é verdadeira;
2. A região crítica de rejeição bicaudal (α = 0,05, 2,5% em cada cauda) sombreada;
3. O valor observado da estatística no conjunto de dados simulado da S01 (semente = 42)
   e seu espelho simétrico bicaudal;
4. A área acumulada nas duas caudas correspondente ao p-valor observado.

Uso como script (a partir da raiz do repositório):
    python -m lab04.src.grafico_g2
"""

from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from lab04.src.cenario import CENARIO
from lab04.src.grafico_g1 import carregar_simulados
from lab04.src.testes_estatisticos import ComparacaoTestes, aplicar_ambos_testes

# Cores padronizadas para cada teste em todo o dashboard (G2, G3 e G4)
COR_WELCH = "#1f77b4"  # Azul para o teste paramétrico (t de Welch)
COR_MANN_WHITNEY = "#ff7f0e"  # Laranja para o teste não-paramétrico (Mann-Whitney)
COR_REJEICAO = "#d62728"  # Vermelho para a região crítica de rejeição (α = 0,05)

CAMINHO_G2_PADRAO = (
    Path(__file__).resolve().parent.parent / "data" / "g2_distribuicao_sob_h0.png"
)


def _obter_comparacao(
    simulados: pd.DataFrame | None = None,
    semente: int = 42,
    alpha: float = CENARIO.alpha,
) -> ComparacaoTestes:
    """Obtém o objeto `ComparacaoTestes` a partir do DataFrame simulado ou gera com semente fixa."""
    df = simulados if simulados is not None else carregar_simulados(semente=semente)
    return aplicar_ambos_testes(
        df,
        alpha=alpha,
        alternativa=CENARIO.tipo_teste,
        origem_dados=f"Dados Simulados S01 (semente = {semente})",
        semente=semente,
    )


def _plotar_painel_welch(ax: plt.Axes, comp: ComparacaoTestes) -> None:
    """Desenha o painel do Teste t de Welch sob H0."""
    w = comp.welch
    alpha = comp.alpha
    gl = w.graus_liberdade_ou_auxiliar
    t_obs = w.estatistica
    t_abs = abs(t_obs)
    t_crit = float(stats.t.ppf(1.0 - alpha / 2.0, df=gl))

    limite_x = max(4.2, t_abs + 1.0, t_crit + 1.2)
    x = np.linspace(-limite_x, limite_x, 800)
    y = stats.t.pdf(x, df=gl)

    # 1. Curva da distribuição nula t(gl)
    ax.plot(
        x,
        y,
        color=COR_WELCH,
        lw=2.3,
        label=f"Teste t de Welch — Distribuição sob H₀ (t com gl = {gl:.1f})",
    )

    # 2. Área do p-valor bicaudal (|t| >= |t_obs|)
    mascara_p_esq = x <= -t_abs
    mascara_p_dir = x >= t_abs
    ax.fill_between(
        x[mascara_p_esq],
        0,
        y[mascara_p_esq],
        color=COR_WELCH,
        alpha=0.22,
        hatch="///",
        edgecolor=COR_WELCH,
        label=f"Área do p-valor bicaudal (|t| ≥ {t_abs:.2f}, p = {w.p_valor:.4f})",
    )
    ax.fill_between(
        x[mascara_p_dir],
        0,
        y[mascara_p_dir],
        color=COR_WELCH,
        alpha=0.22,
        hatch="///",
        edgecolor=COR_WELCH,
    )

    # 3. Região de rejeição bicaudal (|t| >= t_crit, α = 0,05)
    mascara_rej_esq = x <= -t_crit
    mascara_rej_dir = x >= t_crit
    ax.fill_between(
        x[mascara_rej_esq],
        0,
        y[mascara_rej_esq],
        color=COR_REJEICAO,
        alpha=0.50,
        label=f"Região de rejeição α = {alpha:.2f} (|t| ≥ {t_crit:.2f}; 2,5% por cauda)",
    )
    ax.fill_between(
        x[mascara_rej_dir],
        0,
        y[mascara_rej_dir],
        color=COR_REJEICAO,
        alpha=0.50,
    )

    # 4. Linhas dos valores críticos e da estatística observada
    ax.axvline(-t_crit, color=COR_REJEICAO, ls="--", lw=1.3)
    ax.axvline(t_crit, color=COR_REJEICAO, ls="--", lw=1.3)

    ax.axvline(
        t_obs,
        color="#0b3c68",
        ls="-",
        lw=2.2,
        label=f"Estatística observada: t = {t_obs:.4f}",
    )
    ax.axvline(
        t_abs if t_obs < 0 else -t_abs,
        color="#0b3c68",
        ls=":",
        lw=1.5,
        label=f"Espelho simétrico bicaudal: t = {-t_obs:+.4f}",
    )

    decisao_curta = "Rejeita H₀" if w.rejeitar_h0 else "Não rejeita H₀"
    ax.set_title(
        f"Teste t de Welch (Paramétrico — Médias)\n"
        f"t = {t_obs:.4f} | gl = {gl:.1f} | p = {w.p_valor:.4f} → {decisao_curta}",
        fontsize=11,
        fontweight="bold",
    )
    ax.set_xlabel("Estatística t de Welch (diferença padronizada em erros-padrão)")
    ax.set_ylabel("Densidade de probabilidade f(t | H₀)")
    ax.set_ylim(bottom=0, top=max(y) * 1.42)
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", fontsize=8.2, framealpha=0.95)


def _plotar_painel_mann_whitney(ax: plt.Axes, comp: ComparacaoTestes) -> None:
    """Desenha o painel do Teste U de Mann-Whitney sob H0."""
    m = comp.mann_whitney
    alpha = comp.alpha
    n1, n2 = m.n_com_bot, m.n_sem_bot
    mu_u = (n1 * n2) / 2.0
    sigma_u = float(np.sqrt((n1 * n2 * (n1 + n2 + 1)) / 12.0))

    u_obs = m.estatistica
    z_obs = m.graus_liberdade_ou_auxiliar
    desvio_obs = abs(u_obs - mu_u)
    u_esq = mu_u - desvio_obs
    u_dir = mu_u + desvio_obs

    z_crit = float(stats.norm.ppf(1.0 - alpha / 2.0))
    u_crit_esq = mu_u - z_crit * sigma_u
    u_crit_dir = mu_u + z_crit * sigma_u

    limite_u = max(4.2 * sigma_u, desvio_obs + 1.0 * sigma_u)
    x = np.linspace(max(0.0, mu_u - limite_u), min(float(n1 * n2), mu_u + limite_u), 800)
    y = stats.norm.pdf(x, loc=mu_u, scale=sigma_u)

    # 1. Curva da distribuição nula de U sob H0
    ax.plot(
        x,
        y,
        color=COR_MANN_WHITNEY,
        lw=2.3,
        label=(
            f"Teste U de Mann-Whitney — Distribuição sob H₀ "
            f"(μ_U = {mu_u:.0f}, σ_U = {sigma_u:.1f})"
        ),
    )

    # 2. Área do p-valor bicaudal (|U - μ_U| >= |U_obs - μ_U|)
    mascara_p_esq = x <= u_esq
    mascara_p_dir = x >= u_dir
    ax.fill_between(
        x[mascara_p_esq],
        0,
        y[mascara_p_esq],
        color=COR_MANN_WHITNEY,
        alpha=0.22,
        hatch="///",
        edgecolor=COR_MANN_WHITNEY,
        label=(
            f"Área do p-valor bicaudal "
            f"(U ≤ {u_esq:.1f} ou U ≥ {u_dir:.1f}, p = {m.p_valor:.4f})"
        ),
    )
    ax.fill_between(
        x[mascara_p_dir],
        0,
        y[mascara_p_dir],
        color=COR_MANN_WHITNEY,
        alpha=0.22,
        hatch="///",
        edgecolor=COR_MANN_WHITNEY,
    )

    # 3. Região de rejeição bicaudal (α = 0,05)
    mascara_rej_esq = x <= u_crit_esq
    mascara_rej_dir = x >= u_crit_dir
    ax.fill_between(
        x[mascara_rej_esq],
        0,
        y[mascara_rej_esq],
        color=COR_REJEICAO,
        alpha=0.50,
        label=(
            f"Região de rejeição α = {alpha:.2f} "
            f"(U ≤ {u_crit_esq:.1f} ou U ≥ {u_crit_dir:.1f}; |z| ≥ {z_crit:.2f})"
        ),
    )
    ax.fill_between(
        x[mascara_rej_dir],
        0,
        y[mascara_rej_dir],
        color=COR_REJEICAO,
        alpha=0.50,
    )

    # 4. Linhas dos valores críticos e da estatística observada
    ax.axvline(u_crit_esq, color=COR_REJEICAO, ls="--", lw=1.3)
    ax.axvline(u_crit_dir, color=COR_REJEICAO, ls="--", lw=1.3)

    u_espelho = u_dir if u_obs <= mu_u else u_esq
    ax.axvline(
        u_obs,
        color="#8c3b00",
        ls="-",
        lw=2.2,
        label=f"Estatística observada: U = {u_obs:.1f} (z = {z_obs:.2f})",
    )
    ax.axvline(
        u_espelho,
        color="#8c3b00",
        ls=":",
        lw=1.5,
        label=f"Espelho simétrico bicaudal: U = {u_espelho:.1f} (z = {-z_obs:+.2f})",
    )

    decisao_curta = "Rejeita H₀" if m.rejeitar_h0 else "Não rejeita H₀"
    ax.set_title(
        f"Teste U de Mann-Whitney (Não-Paramétrico — Postos)\n"
        f"U = {u_obs:.1f} (z = {z_obs:.2f}) | p = {m.p_valor:.4f} → {decisao_curta}",
        fontsize=11,
        fontweight="bold",
    )
    ax.set_xlabel("Estatística U de Mann-Whitney (contagem de pares favoráveis de postos)")
    ax.set_ylabel("Densidade de probabilidade f(U | H₀)")
    ax.set_ylim(bottom=0, top=max(y) * 1.42)
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", fontsize=8.2, framealpha=0.95)


def gerar_g2(
    simulados: pd.DataFrame | None = None,
    semente: int = 42,
    alpha: float = CENARIO.alpha,
) -> plt.Figure:
    """Retorna a Figure 1x2 do Gráfico G2 com a distribuição sob H0, região de rejeição e p-valor."""
    comp = _obter_comparacao(simulados=simulados, semente=semente, alpha=alpha)

    fig, (ax_welch, ax_mw) = plt.subplots(1, 2, figsize=(13, 5.6))
    _plotar_painel_welch(ax_welch, comp)
    _plotar_painel_mann_whitney(ax_mw, comp)

    fig.suptitle(
        f"G2 – Distribuição da estatística do teste sob H₀, região de rejeição (α = {alpha:.2f}) e p-valor (semente = {semente})",
        fontsize=13.5,
        fontweight="bold",
    )
    fig.tight_layout()
    return fig


def texto_interpretativo_g2(
    simulados: pd.DataFrame | None = None,
    semente: int = 42,
    alpha: float = CENARIO.alpha,
) -> str:
    """Texto curto de 4 frases para a Seção 3 do Dashboard explicando o G2."""
    comp = _obter_comparacao(simulados=simulados, semente=semente, alpha=alpha)
    w = comp.welch
    m = comp.mann_whitney
    t_crit = float(stats.t.ppf(1.0 - alpha / 2.0, df=w.graus_liberdade_ou_auxiliar))
    mu_u = (m.n_com_bot * m.n_sem_bot) / 2.0
    sigma_u = float(np.sqrt((m.n_com_bot * m.n_sem_bot * (m.n_com_bot + m.n_sem_bot + 1)) / 12.0))
    z_crit = float(stats.norm.ppf(1.0 - alpha / 2.0))
    u_crit_esq = mu_u - z_crit * sigma_u
    u_crit_dir = mu_u + z_crit * sigma_u

    return (
        f"O teste t de Welch (azul) compara as médias aritméticas dos grupos sob uma distribuição t de Student "
        f"centrada em 0 (gl = {w.graus_liberdade_ou_auxiliar:.1f}), enquanto o teste U de Mann-Whitney (laranja) "
        f"compara a soma dos postos ordenados sob uma distribuição centrada em μ_U = {mu_u:.0f} pares. "
        f"Como o teste é bicaudal com α = {alpha:.2f}, a região de rejeição de H₀ (sombreada em vermelho) divide-se "
        f"nas duas caudas extremas (2,5% de cada lado: |t| ≥ {t_crit:.2f} para Welch e U ≤ {u_crit_esq:.1f} ou "
        f"U ≥ {u_crit_dir:.1f} para Mann-Whitney). "
        f"Na amostra simulada (semente = {semente}), as estatísticas observadas (t = {w.estatistica:.4f} e "
        f"U = {m.estatistica:.1f}) caíram na região central de não rejeição, e a área hachurada além delas "
        f"representa o p-valor bicaudal (p = {w.p_valor:.4f} no Welch e p = {m.p_valor:.4f} no Mann-Whitney), "
        f"isto é, a probabilidade de obter um desvio igual ou mais extremo do que o observado se H₀ for verdadeira. "
        f"Nota-se visualmente que o teste de Mann-Whitney chegou muito mais perto da fronteira de rejeição do que "
        f"o t de Welch, pois o ranqueamento por postos impediu que o outlier extremo do grupo com bot (110,1 h) "
        f"inflasse o erro padrão e esmagasse a estatística do teste."
    )


if __name__ == "__main__":  # pragma: no cover
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sim = carregar_simulados(semente=42)
    fig = gerar_g2(simulados=sim, semente=42)
    saida = CAMINHO_G2_PADRAO
    saida.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(saida, dpi=150, bbox_inches="tight")
    print(f"G2 salvo em: {saida}")
    print(texto_interpretativo_g2(simulados=sim, semente=42))
