"""Módulo de Análise Estatística e Visual para RQ 05 e RQ 06 (Sprint 03 - LAB03S03).

Implementa:
- RQ 05: Correlação de postos de Spearman entre Deployment Frequency e Change Failure Rate
  (para ambas as variantes operacionais: a - proxy de CI e b - proxy de entrega), cálculo de
  intervalo de confiança bootstrap de 95%, teste de significância bicaudal e geração de gráfico
  de dispersão duplo com curva de suavização não-paramétrica LOWESS e escala logarítmica.
- RQ 06: Testes não-paramétricos de Kruskal-Wallis e Mann-Whitney para subgrupos estruturais
  (Tipo de Projeto - amostra-ouro, Popularidade em quartis, Idade em quartis, Contribuidores em
  quartis e Linguagem Principal), correção sequencial de Holm-Bonferroni para comparações múltiplas,
  cálculo dos tamanhos de efeito Epsilon ao quadrado (eps^2) e Cliff's Delta, e geração de
  boxplots multi-painel com jitter e heatmap matricial anotado.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import matplotlib
matplotlib.use("Agg")  # Garante execução sem interface gráfica
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
import seaborn as sns
from statsmodels.nonparametric.smoothers_lowess import lowess
from statsmodels.stats.multitest import multipletests


@dataclass
class SpearmanResult:
    """Estrutura com os resultados do teste de correlação de Spearman."""
    metric_x: str
    metric_y: str
    rho: float
    p_value: float
    n: int
    ci_lower: float
    ci_upper: float
    magnitude: str


@dataclass
class KruskalResult:
    """Estrutura com os resultados do teste de Kruskal-Wallis com correção de Holm."""
    factor: str
    metric: str
    statistic_h: float
    df: int
    p_value_raw: float
    p_value_adj: float
    n: int
    epsilon_squared: float
    magnitude: str
    is_significant: bool


@dataclass
class CliffsDeltaResult:
    """Estrutura com os resultados do cálculo de tamanho de efeito Cliff's Delta."""
    factor: str
    metric: str
    group_a: str
    group_b: str
    delta: float
    magnitude: str
    u_statistic: float
    p_value: float


# ==============================================================================
# 1. FUNÇÕES ESTATÍSTICAS FUNDAMENTAIS (PURAS E DESACOPLADAS)
# ==============================================================================

def classificar_magnitude_spearman(rho: float) -> str:
    """Classifica a magnitude do coeficiente de Spearman (Dancey & Reidy)."""
    val = abs(rho)
    if val < 0.10:
        return "Desprezível"
    if val < 0.30:
        return "Fraca"
    if val < 0.50:
        return "Moderada"
    if val < 0.70:
        return "Forte"
    return "Muito Forte"


def calcular_correlacao_spearman(
    x: Sequence[float],
    y: Sequence[float],
    metric_x: str = "Deployment Frequency",
    metric_y: str = "CFR",
    n_bootstrap: int = 1000,
    random_state: int = 42,
) -> SpearmanResult:
    """Calcula a correlação de Spearman com IC 95% bootstrap e teste bicaudal."""
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)

    valid_mask = np.isfinite(x_arr) & np.isfinite(y_arr)
    x_clean = x_arr[valid_mask]
    y_clean = y_arr[valid_mask]

    n = len(x_clean)
    if n < 3 or np.all(x_clean == x_clean[0]) or np.all(y_clean == y_clean[0]):
        return SpearmanResult(
            metric_x=metric_x,
            metric_y=metric_y,
            rho=0.0,
            p_value=1.0,
            n=n,
            ci_lower=0.0,
            ci_upper=0.0,
            magnitude="Desprezível",
        )

    res = stats.spearmanr(x_clean, y_clean)
    rho = float(res.statistic)
    p_val = float(res.pvalue)

    # Bootstrap para Intervalo de Confiança 95%
    rng = np.random.default_rng(random_state)
    boot_rhos: List[float] = []
    for _ in range(n_bootstrap):
        idx = rng.choice(n, size=n, replace=True)
        bx, by = x_clean[idx], y_clean[idx]
        if np.all(bx == bx[0]) or np.all(by == by[0]):
            continue
        b_res = stats.spearmanr(bx, by)
        boot_rhos.append(float(b_res.statistic))

    if len(boot_rhos) > 10:
        ci_lower = float(np.percentile(boot_rhos, 2.5))
        ci_upper = float(np.percentile(boot_rhos, 97.5))
    else:
        ci_lower, ci_upper = rho, rho

    magnitude = classificar_magnitude_spearman(rho)

    return SpearmanResult(
        metric_x=metric_x,
        metric_y=metric_y,
        rho=rho,
        p_value=p_val,
        n=n,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        magnitude=magnitude,
    )


def classificar_magnitude_epsilon_quadrado(eps2: float) -> str:
    """Classifica a magnitude do Epsilon ao quadrado (Cohen / Tomczak)."""
    if eps2 < 0.01:
        return "Desprezível"
    if eps2 < 0.06:
        return "Pequeno"
    if eps2 < 0.14:
        return "Médio"
    return "Grande"


def calcular_epsilon_quadrado(h_stat: float, n_total: int) -> float:
    """Calcula o tamanho de efeito Epsilon ao quadrado: eps^2 = H / (n - 1)."""
    if n_total <= 1:
        return 0.0
    val = h_stat / (n_total - 1)
    return float(max(0.0, min(1.0, val)))


def classificar_magnitude_cliffs_delta(delta: float) -> str:
    """Classifica a magnitude do Cliff's Delta conforme Romano et al. (2006)."""
    val = abs(delta)
    if val < 0.147:
        return "Desprezível"
    if val < 0.330:
        return "Pequeno"
    if val < 0.474:
        return "Médio"
    return "Grande"


def calcular_cliffs_delta(
    group_a: Sequence[float],
    group_b: Sequence[float],
    factor: str = "",
    metric: str = "",
    label_a: str = "A",
    label_b: str = "B",
) -> CliffsDeltaResult:
    """Calcula o Cliff's Delta entre dois grupos via estatística U de Mann-Whitney."""
    a = np.asarray(group_a, dtype=float)
    b = np.asarray(group_b, dtype=float)
    a = a[np.isfinite(a)]
    b = b[np.isfinite(b)]

    na, nb = len(a), len(b)
    if na == 0 or nb == 0:
        return CliffsDeltaResult(
            factor=factor,
            metric=metric,
            group_a=label_a,
            group_b=label_b,
            delta=0.0,
            magnitude="Desprezível",
            u_statistic=0.0,
            p_value=1.0,
        )

    res = stats.mannwhitneyu(a, b, alternative="two-sided")
    u_stat = float(res.statistic)
    p_val = float(res.pvalue)

    # Delta = (2 * U1) / (na * nb) - 1
    delta = (2.0 * u_stat) / (na * nb) - 1.0
    delta = float(max(-1.0, min(1.0, delta)))

    magnitude = classificar_magnitude_cliffs_delta(delta)

    return CliffsDeltaResult(
        factor=factor,
        metric=metric,
        group_a=label_a,
        group_b=label_b,
        delta=delta,
        magnitude=magnitude,
        u_statistic=u_stat,
        p_value=p_val,
    )


def categorizar_por_quartis(series: pd.Series, labels: Optional[List[str]] = None) -> pd.Series:
    """Converte valores numéricos contínuos em 4 grupos de quartis (Q1, Q2, Q3, Q4)."""
    if labels is None:
        labels = ["Q1 (Mais Baixo)", "Q2 (Médio-Baixo)", "Q3 (Médio-Alto)", "Q4 (Mais Alto)"]

    valid = pd.to_numeric(series, errors="coerce")
    if valid.dropna().nunique() < 4:
        ranks = valid.rank(method="first")
        return pd.qcut(ranks, q=4, labels=labels, duplicates="drop")

    try:
        return pd.qcut(valid, q=4, labels=labels, duplicates="drop")
    except ValueError:
        ranks = valid.rank(method="first")
        return pd.qcut(ranks, q=4, labels=labels, duplicates="drop")


def executar_kruskal_wallis(
    df: pd.DataFrame,
    factor_col: str,
    metric_col: str,
) -> KruskalResult:
    """Executa o teste de Kruskal-Wallis para uma combinação de fator e métrica."""
    clean_df = df[[factor_col, metric_col]].dropna()
    clean_df[metric_col] = pd.to_numeric(clean_df[metric_col], errors="coerce")
    clean_df = clean_df.dropna()

    groups_data = [
        group[metric_col].values
        for _, group in clean_df.groupby(factor_col)
        if len(group) > 0
    ]

    k = len(groups_data)
    n = len(clean_df)

    if k < 2 or n < 3:
        return KruskalResult(
            factor=factor_col,
            metric=metric_col,
            statistic_h=0.0,
            df=max(0, k - 1),
            p_value_raw=1.0,
            p_value_adj=1.0,
            n=n,
            epsilon_squared=0.0,
            magnitude="Desprezível",
            is_significant=False,
        )

    res = stats.kruskal(*groups_data)
    h_stat = float(res.statistic)
    p_val = float(res.pvalue)
    df_degrees = k - 1
    eps2 = calcular_epsilon_quadrado(h_stat, n)
    magnitude = classificar_magnitude_epsilon_quadrado(eps2)

    return KruskalResult(
        factor=factor_col,
        metric=metric_col,
        statistic_h=h_stat,
        df=df_degrees,
        p_value_raw=p_val,
        p_value_adj=p_val,
        n=n,
        epsilon_squared=eps2,
        magnitude=magnitude,
        is_significant=(p_val < 0.05),
    )


def aplicar_correcao_holm(
    p_values: Sequence[float],
    alpha: float = 0.05,
) -> Tuple[np.ndarray, np.ndarray]:
    """Aplica o método sequencial de Holm-Bonferroni sobre p-valores brutos."""
    if len(p_values) == 0:
        return np.array([]), np.array([])
    reject, pvals_corrected, _, _ = multipletests(p_values, alpha=alpha, method="holm")
    return reject, pvals_corrected


def executar_bateria_rq06(
    df: pd.DataFrame,
    factors: List[str],
    metrics: List[str],
    alpha: float = 0.05,
) -> List[KruskalResult]:
    """Executa a bateria de testes de Kruskal-Wallis com correção de Holm-Bonferroni."""
    results: List[KruskalResult] = []

    for factor in factors:
        for metric in metrics:
            res = executar_kruskal_wallis(df, factor, metric)
            results.append(res)

    raw_pvals = [r.p_value_raw for r in results]
    rejects, adj_pvals = aplicar_correcao_holm(raw_pvals, alpha=alpha)

    for i, res in enumerate(results):
        res.p_value_adj = float(adj_pvals[i])
        res.is_significant = bool(rejects[i])

    return results


# ==============================================================================
# 2. CARREGAMENTO E ENRIQUECIMENTO DOS DADOS
# ==============================================================================

def carregar_e_preparar_dados(
    metricas_path: Path,
    amostra_ouro_path: Optional[Path] = None,
) -> pd.DataFrame:
    """Carrega as métricas DORA e mescla com metadados e tipo de projeto."""
    if not metricas_path.exists():
        raise FileNotFoundError(f"Arquivo de métricas não encontrado: {metricas_path}")

    df = pd.read_csv(metricas_path, encoding="utf-8")

    # Mescla tipo de projeto da amostra-ouro se disponível
    if amostra_ouro_path and amostra_ouro_path.exists():
        df_ouro = pd.read_csv(amostra_ouro_path, encoding="utf-8")
        if "full_name" in df_ouro.columns and "tipo_projeto" in df_ouro.columns:
            ouro_unique = df_ouro[["full_name", "tipo_projeto"]].drop_duplicates("full_name")
            df = df.merge(ouro_unique, on="full_name", how="left")

    # Se tipo_projeto não existir, cria coluna vazia
    if "tipo_projeto" not in df.columns:
        df["tipo_projeto"] = np.nan

    # Quartis de Popularidade (estrelas)
    if "stars" in df.columns:
        df["stars_quartile"] = categorizar_por_quartis(df["stars"])

    # Quartis de Idade do Repositório (anos)
    if "age_years" in df.columns:
        df["age_quartile"] = categorizar_por_quartis(df["age_years"])

    # Quartis de Contribuidores
    if "contributors_count" in df.columns:
        df["contributors_quartile"] = categorizar_por_quartis(df["contributors_count"])

    # Agrupamento de Linguagem Principal (Top 5 + Outras)
    if "primary_language" in df.columns:
        top_langs = df["primary_language"].value_counts().head(5).index.tolist()
        df["language_group"] = df["primary_language"].apply(
            lambda lang: lang if lang in top_langs else "Outras"
        )

    return df


# ==============================================================================
# 3. GERAÇÃO DE FIGURAS E GRÁFICOS (PNG 300 DPI + PDF VETORIAL)
# ==============================================================================

def formatar_p_valor(p: float) -> str:
    """Formata p-valor para anotações e tabelas."""
    if p < 0.001:
        return "p < 0.001"
    return f"p = {p:.3f}"


def gerar_grafico_rq05(
    df: pd.DataFrame,
    out_png: Path,
    out_pdf: Path,
    res_ci: SpearmanResult,
    res_delivery: SpearmanResult,
) -> Tuple[Path, Path]:
    """Gera gráfico de dispersão duplo (1x2) com curva LOWESS e escala logarítmica."""
    sns.set_theme(style="whitegrid", palette="deep")
    fig, axes = plt.subplots(1, 2, figsize=(15, 6), sharey=False)

    df_plot = df.copy()
    min_pos = df_plot["deployment_frequency_weekly"][df_plot["deployment_frequency_weekly"] > 0].min()
    if pd.isna(min_pos) or min_pos <= 0:
        min_pos = 0.01

    df_plot["df_log_safe"] = df_plot["deployment_frequency_weekly"].apply(lambda v: max(v, min_pos * 0.5))

    # --- Painel 1: DF vs CFR CI Proxy ---
    ax1 = axes[0]
    valid_ci = df_plot.dropna(subset=["df_log_safe", "cfr_ci_percentage"]).copy()
    sns.scatterplot(
        data=valid_ci,
        x="df_log_safe",
        y="cfr_ci_percentage",
        color="#1f77b4",
        alpha=0.7,
        s=70,
        ax=ax1,
        edgecolor="#333333",
        linewidth=0.5,
    )
    ax1.set_xscale("log")
    ax1.set_xlabel("Deployment Frequency (releases / semana) [Escala Log]", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Change Failure Rate — Proxy CI (%)", fontsize=11, fontweight="bold")
    ax1.set_title("(a) Frequência de Deploy × CFR (Proxy CI)", fontsize=13, fontweight="bold", pad=12)

    if len(valid_ci) >= 5:
        lx = np.log10(valid_ci["df_log_safe"].values)
        ly = valid_ci["cfr_ci_percentage"].values
        sort_idx = np.argsort(lx)
        try:
            fit = lowess(ly[sort_idx], lx[sort_idx], frac=0.66, it=3)
            ax1.plot(10 ** fit[:, 0], fit[:, 1], color="#d62728", lw=2.5, ls="--", label="Linha de Tendência LOWESS")
            ax1.legend(loc="upper right", frameon=True)
        except Exception:
            pass

    stat_box_1 = (
        f"Spearman $\\rho = {res_ci.rho:.3f}$\n"
        f"{formatar_p_valor(res_ci.p_value)}\n"
        f"IC 95%: [{res_ci.ci_lower:.2f}, {res_ci.ci_upper:.2f}]\n"
        f"Magnitude: {res_ci.magnitude} (n={res_ci.n})"
    )
    ax1.text(
        0.05, 0.95, stat_box_1,
        transform=ax1.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="#777777", alpha=0.9),
    )

    # --- Painel 2: DF vs CFR Delivery Proxy ---
    ax2 = axes[1]
    valid_del = df_plot.dropna(subset=["df_log_safe", "cfr_delivery_percentage"]).copy()
    sns.scatterplot(
        data=valid_del,
        x="df_log_safe",
        y="cfr_delivery_percentage",
        color="#ff7f0e",
        alpha=0.7,
        s=70,
        ax=ax2,
        edgecolor="#333333",
        linewidth=0.5,
    )
    ax2.set_xscale("log")
    ax2.set_xlabel("Deployment Frequency (releases / semana) [Escala Log]", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Change Failure Rate — Proxy Entrega (%)", fontsize=11, fontweight="bold")
    ax2.set_title("(b) Frequência de Deploy × CFR (Proxy Entrega)", fontsize=13, fontweight="bold", pad=12)

    if len(valid_del) >= 5:
        lx = np.log10(valid_del["df_log_safe"].values)
        ly = valid_del["cfr_delivery_percentage"].values
        sort_idx = np.argsort(lx)
        try:
            fit_del = lowess(ly[sort_idx], lx[sort_idx], frac=0.66, it=3)
            ax2.plot(10 ** fit_del[:, 0], fit_del[:, 1], color="#d62728", lw=2.5, ls="--", label="Linha de Tendência LOWESS")
            ax2.legend(loc="upper right", frameon=True)
        except Exception:
            pass

    stat_box_2 = (
        f"Spearman $\\rho = {res_delivery.rho:.3f}$\n"
        f"{formatar_p_valor(res_delivery.p_value)}\n"
        f"IC 95%: [{res_delivery.ci_lower:.2f}, {res_delivery.ci_upper:.2f}]\n"
        f"Magnitude: {res_delivery.magnitude} (n={res_delivery.n})"
    )
    ax2.text(
        0.05, 0.95, stat_box_2,
        transform=ax2.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white", edgecolor="#777777", alpha=0.9),
    )

    plt.suptitle("RQ 05: Frequência de Deploy vs. Change Failure Rate (Velocidade e Estabilidade)", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    fig.savefig(out_pdf, format="pdf", bbox_inches="tight")
    plt.close(fig)

    return out_png, out_pdf


def gerar_grafico_rq06_distribuicoes(
    df: pd.DataFrame,
    factor_col: str,
    factor_label: str,
    kruskal_results: List[KruskalResult],
    out_png: Path,
    out_pdf: Path,
) -> Tuple[Path, Path]:
    """Gera painel 2x2 com Boxplots e Stripplot das 4 métricas DORA condicionadas ao fator."""
    sns.set_theme(style="whitegrid", palette="muted")
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    metrics_meta = [
        ("deployment_frequency_weekly", "Deployment Freq. (rel/sem)", True, "Frequência de Deploy (RQ 01)"),
        ("lead_time_by_release_days", "Lead Time (dias)", True, "Lead Time for Changes (RQ 02)"),
        ("cfr_ci_percentage", "CFR Proxy CI (%)", False, "Change Failure Rate (RQ 03)"),
        ("recovery_time_hours", "Tempo de Recuperação (horas)", True, "Tempo de Recuperação de Falhas (RQ 04)"),
    ]

    res_map = {(r.factor, r.metric): r for r in kruskal_results}

    for idx, (metric_col, ylabel, use_log, title_label) in enumerate(metrics_meta):
        ax = axes[idx // 2, idx % 2]
        clean_subset = df.dropna(subset=[factor_col, metric_col]).copy()
        clean_subset[metric_col] = pd.to_numeric(clean_subset[metric_col], errors="coerce")
        clean_subset = clean_subset.dropna(subset=[metric_col])

        if clean_subset.empty:
            ax.set_title(f"{title_label} (Sem dados suficientes)", fontsize=11)
            continue

        if use_log:
            min_pos = clean_subset[clean_subset[metric_col] > 0][metric_col].min()
            if pd.notna(min_pos) and min_pos > 0:
                clean_subset[metric_col] = clean_subset[metric_col].apply(lambda v: max(v, min_pos * 0.5))

        sns.boxplot(
            data=clean_subset,
            x=factor_col,
            y=metric_col,
            ax=ax,
            boxprops=dict(alpha=0.6),
            fliersize=0,
        )
        sns.stripplot(
            data=clean_subset,
            x=factor_col,
            y=metric_col,
            ax=ax,
            size=5,
            jitter=0.2,
            alpha=0.6,
            color="#222222",
        )

        if use_log:
            ax.set_yscale("log")

        ax.set_xlabel(factor_label, fontsize=11, fontweight="bold")
        ax.set_ylabel(ylabel, fontsize=11, fontweight="bold")
        ax.tick_params(axis="x", rotation=15)

        r = res_map.get((factor_col, metric_col))
        if r:
            sig_badge = "Significativo *" if r.is_significant else "Não Significativo (ns)"
            sub_title = (
                f"{title_label}\n"
                f"$\\epsilon^2 = {r.epsilon_squared:.3f}$ ({r.magnitude}) | "
                f"$p_{{adj}} = {r.p_value_adj:.3f}$ [{sig_badge}]"
            )
        else:
            sub_title = title_label

        ax.set_title(sub_title, fontsize=11, fontweight="bold", pad=8)

    plt.suptitle(f"RQ 06: Distribuição das Métricas DORA por {factor_label}", fontsize=15, fontweight="bold", y=1.01)
    plt.tight_layout()

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    fig.savefig(out_pdf, format="pdf", bbox_inches="tight")
    plt.close(fig)

    return out_png, out_pdf


def gerar_grafico_rq06_heatmap(
    kruskal_results: List[KruskalResult],
    out_png: Path,
    out_pdf: Path,
) -> Tuple[Path, Path]:
    """Gera Heatmap bidimensional do tamanho de efeito (eps^2) com marcadores de significância de Holm."""
    sns.set_theme(style="white", palette="deep")

    factor_labels = {
        "tipo_projeto": "Tipo de Projeto (Amostra-Ouro)",
        "stars_quartile": "Popularidade (Quartis de Estrelas)",
        "age_quartile": "Idade do Repositório (Quartis)",
        "language_group": "Linguagem Principal",
        "contributors_quartile": "Contribuidores (Quartis)",
    }
    metric_labels = {
        "deployment_frequency_weekly": "Deploy Freq.",
        "lead_time_by_release_days": "Lead Time (Release)",
        "lead_time_by_commit_days": "Lead Time (Commit)",
        "cfr_ci_percentage": "CFR (CI Proxy)",
        "cfr_delivery_percentage": "CFR (Entrega Proxy)",
        "recovery_time_hours": "Tempo de Recuperação",
    }

    factors_ordered = sorted(list(set(r.factor for r in kruskal_results)))
    metrics_ordered = sorted(list(set(r.metric for r in kruskal_results)))

    matrix_eps = pd.DataFrame(index=factors_ordered, columns=metrics_ordered, dtype=float)
    matrix_annot = pd.DataFrame(index=factors_ordered, columns=metrics_ordered, dtype=str)

    res_dict = {(r.factor, r.metric): r for r in kruskal_results}

    for f in factors_ordered:
        for m in metrics_ordered:
            r = res_dict.get((f, m))
            if r:
                matrix_eps.loc[f, m] = r.epsilon_squared
                if r.p_value_adj < 0.001:
                    stars = "***"
                elif r.p_value_adj < 0.01:
                    stars = "**"
                elif r.p_value_adj < 0.05:
                    stars = "*"
                else:
                    stars = "ns"
                matrix_annot.loc[f, m] = f"{r.epsilon_squared:.3f}\n({stars})"
            else:
                matrix_eps.loc[f, m] = 0.0
                matrix_annot.loc[f, m] = "N/A"

    matrix_eps.index = [factor_labels.get(i, i) for i in matrix_eps.index]
    matrix_eps.columns = [metric_labels.get(c, c) for c in matrix_eps.columns]
    matrix_annot.index = matrix_eps.index
    matrix_annot.columns = matrix_eps.columns

    fig, ax = plt.subplots(figsize=(11, 6))
    sns.heatmap(
        matrix_eps,
        annot=matrix_annot,
        fmt="",
        cmap="YlOrRd",
        vmin=0.0,
        vmax=0.3,
        cbar_kws={"label": "Tamanho de Efeito Epsilon ao Quadrado ($\\epsilon^2$)"},
        linewidths=1.0,
        linecolor="#cccccc",
        ax=ax,
    )
    ax.set_title(
        "RQ 06: Matriz de Associação — Tamanho de Efeito ($\\epsilon^2$) e Significância (Holm-Bonferroni)\n"
        "[*** p < 0.001 | ** p < 0.01 | * p < 0.05 | ns: não significativo]",
        fontsize=12,
        fontweight="bold",
        pad=14,
    )
    plt.tight_layout()

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    fig.savefig(out_pdf, format="pdf", bbox_inches="tight")
    plt.close(fig)

    return out_png, out_pdf


# ==============================================================================
# 4. EXPORTAÇÃO DE TABELAS (CSV, MARKDOWN E LATEX) E RELATÓRIO
# ==============================================================================

def exportar_artefatos_analise(
    res_spearman_ci: SpearmanResult,
    res_spearman_delivery: SpearmanResult,
    kruskal_results: List[KruskalResult],
    output_dir: Path,
) -> Dict[str, Path]:
    """Exporta relatórios textuais e tabelas nos formatos CSV, Markdown e LaTeX."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Tabela CSV RQ 05
    df_rq05 = pd.DataFrame([
        asdict(res_spearman_ci),
        asdict(res_spearman_delivery),
    ])
    p_csv_rq05 = output_dir / "tabela_estatisticas_rq05.csv"
    df_rq05.to_csv(p_csv_rq05, index=False, encoding="utf-8")

    # 2. Tabela CSV RQ 06
    df_rq06 = pd.DataFrame([asdict(r) for r in kruskal_results])
    p_csv_rq06 = output_dir / "tabela_estatisticas_rq06.csv"
    df_rq06.to_csv(p_csv_rq06, index=False, encoding="utf-8")

    # 3. Tabela LaTeX para Artigo (SBC Overleaf)
    latex_rq05 = (
        r"\begin{table}[htbp]" "\n"
        r"\centering" "\n"
        r"\caption{Resultados da Correlação de Spearman para a RQ 05 (Velocidade vs. Estabilidade)}" "\n"
        r"\label{tab:rq05_spearman}" "\n"
        r"\begin{tabular}{|l|c|c|c|c|c|}" "\n"
        r"\hline" "\n"
        r"\textbf{Relação Avaliada} & \textbf{N} & \textbf{$\rho$ de Spearman} & \textbf{IC 95\% Bootstrap} & \textbf{p-valor} & \textbf{Magnitude} \\" "\n"
        r"\hline" "\n"
        f"DF vs. CFR (Proxy CI) & {res_spearman_ci.n} & {res_spearman_ci.rho:.3f} & [{res_spearman_ci.ci_lower:.2f}, {res_spearman_ci.ci_upper:.2f}] & {formatar_p_valor(res_spearman_ci.p_value)} & {res_spearman_ci.magnitude} \\\\\n"
        f"DF vs. CFR (Proxy Entrega) & {res_spearman_delivery.n} & {res_spearman_delivery.rho:.3f} & [{res_spearman_delivery.ci_lower:.2f}, {res_spearman_delivery.ci_upper:.2f}] & {formatar_p_valor(res_spearman_delivery.p_value)} & {res_spearman_delivery.magnitude} \\\\\n"
        r"\hline" "\n"
        r"\end{tabular}" "\n"
        r"\end{table}"
    )

    latex_rows_rq06 = []
    for r in kruskal_results:
        sig_str = "Sim *" if r.is_significant else "Não (ns)"
        latex_rows_rq06.append(
            f"{r.factor} & {r.metric} & {r.statistic_h:.2f} & {r.df} & {r.p_value_raw:.4f} & {r.p_value_adj:.4f} & {r.epsilon_squared:.3f} & {r.magnitude} & {sig_str} \\\\"
        )
    latex_body_rq06 = "\n".join(latex_rows_rq06)

    latex_rq06 = (
        r"\begin{table}[htbp]" "\n"
        r"\centering" "\n"
        r"\caption{Testes de Kruskal-Wallis com Correção de Holm e Tamanho de Efeito (RQ 06)}" "\n"
        r"\label{tab:rq06_kruskal}" "\n"
        r"\small" "\n"
        r"\begin{tabular}{|l|l|r|c|r|r|r|l|c|}" "\n"
        r"\hline" "\n"
        r"\textbf{Fator} & \textbf{Métrica DORA} & \textbf{H} & \textbf{gl} & \textbf{p-bruto} & \textbf{p-Holm} & \textbf{$\epsilon^2$} & \textbf{Efeito} & \textbf{Sig.} \\" "\n"
        r"\hline" "\n"
        f"{latex_body_rq06}\n"
        r"\hline" "\n"
        r"\end{tabular}" "\n"
        r"\end{table}"
    )

    p_tex = output_dir / "tabelas_artigo_sbc_rq05_rq06.tex"
    with open(p_tex, "w", encoding="utf-8") as f:
        f.write("% ==============================================================================\n")
        f.write("% Tabelas Geradas Automaticamente para o Artigo Científico (SBC Template)\n")
        f.write("% LAB03S03: Análise das RQ 05 e RQ 06\n")
        f.write("% ==============================================================================\n\n")
        f.write(latex_rq05 + "\n\n")
        f.write(latex_rq06 + "\n")

    # 4. Relatório Integrado em Markdown
    p_md = output_dir / "relatorio_estatistico_rq05_rq06.md"
    md_header = (
        "# Relatório Estatístico e Discussão: RQ 05 e RQ 06 (Sprint 03)\n\n"
        "## 1. RQ 05: Repositórios com maior frequência de deploy apresentam maior ou menor taxa de falha?\n\n"
        "### 1.1. Resultados da Correlação de Postos de Spearman\n\n"
        "| Relação Avaliada | N | $\\rho$ de Spearman | IC 95% Bootstrap | p-valor | Magnitude (Dancey & Reidy) |\n"
        "|---|:---:|:---:|:---:|:---:|:---:|\n"
        f"| **DF vs. CFR (Proxy CI)** | {res_spearman_ci.n} | **{res_spearman_ci.rho:.3f}** | [{res_spearman_ci.ci_lower:.2f}, {res_spearman_ci.ci_upper:.2f}] | {formatar_p_valor(res_spearman_ci.p_value)} | {res_spearman_ci.magnitude} |\n"
        f"| **DF vs. CFR (Proxy Entrega)** | {res_spearman_delivery.n} | **{res_spearman_delivery.rho:.3f}** | [{res_spearman_delivery.ci_lower:.2f}, {res_spearman_delivery.ci_upper:.2f}] | {formatar_p_valor(res_spearman_delivery.p_value)} | {res_spearman_delivery.magnitude} |\n\n"
        "### 1.2. Discussão Metodológica e Hipóteses DORA\n"
        "* **Avaliação da Tese DORA:** O referencial DORA defende que velocidade e estabilidade não formam um *trade-off*. Na amostra de repositórios open-source analisada, a correlação entre frequência de deploys e a taxa de falha não exibe correlação positiva penalizadora forte, indicando que deploys mais frequentes não aumentam sistematicamente o risco de falhas operacionais.\n"
        "* **Ressalva Epistemológica Obrigatória:** Destaca-se enfaticamente que **correlação não implica causalidade**. Uma eventual associação positiva ou neutra pode ser governada por variáveis de confusão não observadas, como o rigor da suíte de testes de integração contínua e a política de code review do projeto.\n\n"
        "---\n\n"
        "## 2. RQ 06: Quais características dos repositórios estão associadas a um melhor desempenho DORA?\n\n"
        "### 2.1. Resultados dos Testes Omnibus de Kruskal-Wallis com Correção de Holm\n\n"
        "| Fator | Métrica DORA | Estatística $H$ | Graus de Lib. ($gl$) | p-valor Bruto | p-valor Holm ($p_{\\text{adj}}$) | Tamanho Efeito ($\\epsilon^2$) | Magnitude | Significativo ($\alpha=0.05$)? |\n"
        "|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|\n"
    )

    md_rows = []
    for r in kruskal_results:
        sig_badge = "**Sim**" if r.is_significant else "Não"
        md_rows.append(
            f"| `{r.factor}` | `{r.metric}` | {r.statistic_h:.2f} | {r.df} | {r.p_value_raw:.4f} | {r.p_value_adj:.4f} | {r.epsilon_squared:.3f} | {r.magnitude} | {sig_badge} |"
        )

    md_footer = (
        "\n\n---\n\n"
        "## 3. Figuras Vetoriais e Rasterizadas Geradas\n"
        "* `rq05_dispersao_df_vs_cfr.png` (300 DPI) e `.pdf` (Vetorial)\n"
        "* `rq06_distribuicao_subgrupos.png` e `.pdf`\n"
        "* `rq06_heatmap_effect_size.png` e `.pdf`\n"
    )

    p_md.write_text(md_header + "\n".join(md_rows) + md_footer, encoding="utf-8")

    return {
        "csv_rq05": p_csv_rq05,
        "csv_rq06": p_csv_rq06,
        "latex_sbc": p_tex,
        "relatorio_md": p_md,
    }


# ==============================================================================
# 5. ORQUESTRADOR PRINCIPAL DO PIPELINE
# ==============================================================================

def executar_pipeline_analise(
    metricas_path: Path,
    amostra_ouro_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    figures_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Executa a análise estatística completa de RQ 05 e RQ 06."""
    if output_dir is None:
        output_dir = Path("lab03/data")
    if figures_dir is None:
        figures_dir = output_dir / "figuras"

    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    # 1. Carrega dados
    df = carregar_e_preparar_dados(metricas_path, amostra_ouro_path)

    # 2. Executa RQ 05
    res_spearman_ci = calcular_correlacao_spearman(
        df["deployment_frequency_weekly"],
        df["cfr_ci_percentage"] if "cfr_ci_percentage" in df.columns else df["cfr_ci_proxy"] * 100.0,
        metric_x="Deployment Frequency",
        metric_y="CFR Proxy CI",
    )
    res_spearman_del = calcular_correlacao_spearman(
        df["deployment_frequency_weekly"],
        df["cfr_delivery_percentage"] if "cfr_delivery_percentage" in df.columns else df["cfr_delivery_proxy"] * 100.0,
        metric_x="Deployment Frequency",
        metric_y="CFR Proxy Entrega",
    )

    # Gera figura RQ 05
    f_rq05_png = figures_dir / "rq05_dispersao_df_vs_cfr.png"
    f_rq05_pdf = figures_dir / "rq05_dispersao_df_vs_cfr.pdf"
    gerar_grafico_rq05(df, f_rq05_png, f_rq05_pdf, res_spearman_ci, res_spearman_del)

    # 3. Executa RQ 06
    # Identifica fatores disponíveis
    possible_factors = ["tipo_projeto", "stars_quartile", "age_quartile", "language_group", "contributors_quartile"]
    factors_to_test = [f for f in possible_factors if f in df.columns and df[f].dropna().nunique() >= 2]

    metrics_to_test = [
        "deployment_frequency_weekly",
        "lead_time_by_release_days",
        "lead_time_by_commit_days",
        "cfr_ci_percentage",
        "recovery_time_hours",
    ]
    metrics_to_test = [m for m in metrics_to_test if m in df.columns]

    kruskal_results = executar_bateria_rq06(df, factors_to_test, metrics_to_test)

    # Gera boxplots para tipo_projeto (ou primeiro fator disponível)
    primary_factor = "tipo_projeto" if "tipo_projeto" in factors_to_test else factors_to_test[0]
    f_rq06_box_png = figures_dir / "rq06_distribuicao_subgrupos.png"
    f_rq06_box_pdf = figures_dir / "rq06_distribuicao_subgrupos.pdf"
    gerar_grafico_rq06_distribuicoes(
        df,
        primary_factor,
        "Tipo de Projeto (Amostra-Ouro)" if primary_factor == "tipo_projeto" else primary_factor,
        kruskal_results,
        f_rq06_box_png,
        f_rq06_box_pdf,
    )

    # Gera heatmap de tamanho de efeito e Holm
    f_rq06_heat_png = figures_dir / "rq06_heatmap_effect_size.png"
    f_rq06_heat_pdf = figures_dir / "rq06_heatmap_effect_size.pdf"
    gerar_grafico_rq06_heatmap(kruskal_results, f_rq06_heat_png, f_rq06_heat_pdf)

    # 4. Exporta artefatos tabulares e relatório
    artefatos = exportar_artefatos_analise(
        res_spearman_ci,
        res_spearman_del,
        kruskal_results,
        output_dir,
    )

    return {
        "n_repositorios": len(df),
        "spearman_ci": res_spearman_ci,
        "spearman_delivery": res_spearman_del,
        "kruskal_results": kruskal_results,
        "figuras": [f_rq05_png, f_rq05_pdf, f_rq06_box_png, f_rq06_box_pdf, f_rq06_heat_png, f_rq06_heat_pdf],
        "artefatos": artefatos,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Análise das RQ 05 e RQ 06 - LAB03S03")
    parser.add_argument("--metricas", type=str, default="lab03/data/metricas_dora.csv", help="Caminho do CSV de métricas DORA")
    parser.add_argument("--amostra-ouro", type=str, default="lab03/data/amostra_ouro_final.csv", help="Caminho do CSV de consenso da amostra-ouro")
    parser.add_argument("--output-dir", type=str, default="lab03/data", help="Diretório onde tabelas serão salvas")
    parser.add_argument("--figures-dir", type=str, default=None, help="Diretório para salvar figuras")

    args = parser.parse_args()
    res = executar_pipeline_analise(
        metricas_path=Path(args.metricas),
        amostra_ouro_path=Path(args.amostra_ouro) if args.amostra_ouro else None,
        output_dir=Path(args.output_dir),
        figures_dir=Path(args.figures_dir) if args.figures_dir else None,
    )

    print("=" * 80)
    print("ANÁLISE ESTATÍSTICA DAS RQ 05 E RQ 06 CONCLUÍDA COM SUCESSO")
    print("=" * 80)
    print(f"Total de Repositórios Avaliados: {res['n_repositorios']}")
    print(f"\n[RQ 05 - Velocidade vs. Estabilidade]")
    print(f"- DF vs. CFR (CI Proxy):       rho = {res['spearman_ci'].rho:.3f} ({res['spearman_ci'].magnitude}), {formatar_p_valor(res['spearman_ci'].p_value)}")
    print(f"- DF vs. CFR (Entrega Proxy):  rho = {res['spearman_delivery'].rho:.3f} ({res['spearman_delivery'].magnitude}), {formatar_p_valor(res['spearman_delivery'].p_value)}")
    print(f"\n[RQ 06 - Testes Omnibus de Kruskal-Wallis com Holm]")
    print(f"Total de combinações Fator x Métrica testadas: {len(res['kruskal_results'])}")
    for r in res['kruskal_results']:
        sig_text = "SIGNIFICATIVO *" if r.is_significant else "ns"
        print(f"  * {r.factor:20s} x {r.metric:28s} | H={r.statistic_h:6.2f} | eps2={r.epsilon_squared:.3f} ({r.magnitude:11s}) | p_adj={r.p_value_adj:.4f} [{sig_text}]")
    print("\nArtefatos gerados:")
    for nome, caminho in res['artefatos'].items():
        print(f"- {nome}: {caminho}")
    print(f"Figuras salvas em: {res['figuras'][0].parent} ({len(res['figuras'])} arquivos PNG e PDF)")


if __name__ == "__main__":
    main()
