"""Análise estatística descritiva, inferencial e visualizações do LAB05 (Issue #68).

Consome exclusivamente os datasets validados em ``lab05/data/processed/`` e segue
integralmente o protocolo definido em ``lab05/planejamento_analise_estatistica.md``:
- Verificação prévia de integridade dos dados validados;
- Estatística descritiva (média, mediana, DP, CV%, mín, máx, IQR, P25/P50/P75/P95);
- Checagem de pressupostos (Shapiro-Wilk para normalidade, Levene para variâncias);
- Seleção automática entre Teste t de Student, Teste t de Welch e Mann-Whitney U;
- Correção de Bonferroni para múltiplas comparações (4 métricas, alpha_adj = 0,0125);
- Cálculo de tamanho do efeito (d de Cohen ou r rank-biserial) e diferença %;
- Análise de sensibilidade (sem outliers IQR + testes pareados por random_seed);
- Matriz de correlações (Spearman) entre métricas;
- Geração de 6 gráficos comparativos e temporais em ``lab05/results/graficos/``.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from lab05.src.validar_dados import PROCESSED_DIR  # noqa: E402

LAB05_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = LAB05_DIR / "results"
CHARTS_DIR = RESULTS_DIR / "graficos"

# Paleta acessível (Okabe-Ito: azul vs laranja, evitando vermelho x verde)
COLOR_PG17 = "#0072B2"
COLOR_PG18 = "#D55E00"


@dataclass(frozen=True)
class MetricSpec:
    """Especificação de uma métrica dependente analisada no estudo."""

    col: str
    label: str
    short_label: str
    unit: str
    rq: str
    outlier_col: str
    higher_is_better: bool | None


METRICS: list[MetricSpec] = [
    MetricSpec(
        col="latencia_media_ms",
        label="Latência média por transação (ms)",
        short_label="Latência média",
        unit="ms",
        rq="RQ1",
        outlier_col="outlier_latencia",
        higher_is_better=False,
    ),
    MetricSpec(
        col="tps",
        label="Vazão — Transações por segundo (TPS)",
        short_label="TPS",
        unit="tx/s",
        rq="RQ2",
        outlier_col="outlier_tps",
        higher_is_better=True,
    ),
    MetricSpec(
        col="cpu_media_pct",
        label="Consumo médio de CPU multi-core (%)",
        short_label="CPU média",
        unit="%",
        rq="RQ3",
        outlier_col="outlier_cpu",
        higher_is_better=False,
    ),
    MetricSpec(
        col="memoria_media_mib",
        label="Consumo médio de memória RSS (MiB)",
        short_label="Memória média",
        unit="MiB",
        rq="RQ4",
        outlier_col="outlier_memoria",
        higher_is_better=False,
    ),
]


def verify_validated_inputs(processed_dir: Path = PROCESSED_DIR) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Carrega e verifica a integridade dos dados validados da Sprint 2."""
    bench_path = processed_dir / "benchmark_validado.csv"
    ts_path = processed_dir / "resource_timeseries_validado.csv"
    report_path = processed_dir / "relatorio_validacao.json"

    for path in (bench_path, ts_path, report_path):
        if not path.exists():
            raise FileNotFoundError(f"Artefato validado ausente: {path}")

    report = json.loads(report_path.read_text(encoding="utf-8"))
    if not report.get("aprovado", False):
        raise ValueError(
            f"relatorio_validacao.json não está aprovado: {report.get('erros')}"
        )

    df = pd.read_csv(bench_path)
    df_ts = pd.read_csv(ts_path)

    if set(df["versao"].unique()) != {"PG17", "PG18"}:
        raise ValueError(f"Versões inesperadas no dataset: {df['versao'].unique().tolist()}")
    if (df["status"] != "OK").any():
        raise ValueError("Dataset validado contém registros com status != OK.")

    return df, df_ts, report


def interpret_cohens_d(d: float) -> str:
    """Classifica magnitude do d de Cohen segundo limiares do planejamento."""
    mag = abs(d)
    if mag < 0.2:
        return "negligenciável"
    if mag < 0.5:
        return "pequeno"
    if mag < 0.8:
        return "médio"
    return "grande"


def interpret_rank_biserial(r: float) -> str:
    """Classifica magnitude da correlação rank-biserial r segundo o planejamento."""
    mag = abs(r)
    if mag < 0.1:
        return "negligenciável"
    if mag < 0.3:
        return "pequeno"
    if mag < 0.5:
        return "médio"
    return "grande"


def compute_cohens_d(g18: np.ndarray, g17: np.ndarray) -> float:
    """Calcula d de Cohen = (média_PG18 - média_PG17) / DP_pooled."""
    n18, n17 = len(g18), len(g17)
    s18 = float(np.std(g18, ddof=1))
    s17 = float(np.std(g17, ddof=1))
    pooled_var = (((n18 - 1) * (s18**2)) + ((n17 - 1) * (s17**2))) / (n18 + n17 - 2)
    pooled_sd = math.sqrt(pooled_var)
    if pooled_sd == 0.0:
        return 0.0
    return (float(np.mean(g18)) - float(np.mean(g17))) / pooled_sd


def compute_rank_biserial(u_18: float, n18: int, n17: int) -> float:
    """Calcula r rank-biserial com sinal positivo quando PG18 > PG17."""
    return ((2.0 * u_18) / (n18 * n17)) - 1.0


def compute_descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula todas as estatísticas descritivas definidas na Seção 4 do planejamento."""
    rows: list[dict[str, Any]] = []
    for spec in METRICS:
        for versao in ("PG17", "PG18"):
            vals = df.loc[df["versao"] == versao, spec.col].dropna().to_numpy(dtype=float)
            mean_v = float(np.mean(vals))
            sd_v = float(np.std(vals, ddof=1))
            q25, q50, q75, q95 = np.percentile(vals, [25, 50, 75, 95])
            rows.append(
                {
                    "rq": spec.rq,
                    "metrica": spec.col,
                    "metrica_label": spec.short_label,
                    "unidade": spec.unit,
                    "versao": versao,
                    "n": int(len(vals)),
                    "media": round(mean_v, 4),
                    "mediana": round(float(q50), 4),
                    "dp": round(sd_v, 4),
                    "cv_pct": round((sd_v / mean_v) * 100.0 if mean_v != 0 else 0.0, 4),
                    "min": round(float(np.min(vals)), 4),
                    "max": round(float(np.max(vals)), 4),
                    "iqr": round(float(q75 - q25), 4),
                    "p25": round(float(q25), 4),
                    "p50": round(float(q50), 4),
                    "p75": round(float(q75), 4),
                    "p95": round(float(q95), 4),
                }
            )
    return pd.DataFrame(rows)


def run_hypothesis_test_for_metric(
    vals_17: np.ndarray,
    vals_18: np.ndarray,
    spec: MetricSpec,
    alpha: float = 0.05,
    num_comparisons: int = 4,
) -> dict[str, Any]:
    """Aplica fluxo Shapiro-Wilk -> Levene -> (t Student / Welch / Mann-Whitney U)."""
    n17, n18 = len(vals_17), len(vals_18)
    mean17, mean18 = float(np.mean(vals_17)), float(np.mean(vals_18))
    med17, med18 = float(np.median(vals_17)), float(np.median(vals_18))

    shapiro_17 = stats.shapiro(vals_17)
    shapiro_18 = stats.shapiro(vals_18)
    normal_17 = bool(shapiro_17.pvalue >= alpha)
    normal_18 = bool(shapiro_18.pvalue >= alpha)
    both_normal = normal_17 and normal_18

    levene_res = stats.levene(vals_17, vals_18)
    equal_var = bool(levene_res.pvalue >= alpha)

    if both_normal:
        if equal_var:
            test_name = "Teste t de Student (independente)"
            res = stats.ttest_ind(vals_18, vals_17, equal_var=True, alternative="two-sided")
        else:
            test_name = "Teste t de Welch (variâncias desiguais)"
            res = stats.ttest_ind(vals_18, vals_17, equal_var=False, alternative="two-sided")
        effect_name = "d de Cohen"
        effect_val = compute_cohens_d(vals_18, vals_17)
        effect_mag = interpret_cohens_d(effect_val)
    else:
        test_name = "Mann-Whitney U (bilateral)"
        res = stats.mannwhitneyu(vals_18, vals_17, alternative="two-sided")
        effect_name = "r rank-biserial"
        effect_val = compute_rank_biserial(float(res.statistic), n18, n17)
        effect_mag = interpret_rank_biserial(effect_val)

    p_val = float(res.pvalue)
    alpha_bonf = alpha / num_comparisons
    p_bonf = min(p_val * num_comparisons, 1.0)

    diff_mean_abs = mean18 - mean17
    diff_mean_pct = ((mean18 - mean17) / mean17) * 100.0 if mean17 != 0 else 0.0
    diff_med_abs = med18 - med17
    diff_med_pct = ((med18 - med17) / med17) * 100.0 if med17 != 0 else 0.0

    # Intervalo de confiança de 95% (Welch) para diferença entre médias como referência
    se_diff = math.sqrt((np.var(vals_18, ddof=1) / n18) + (np.var(vals_17, ddof=1) / n17))
    if se_diff > 0:
        num_df = ((np.var(vals_18, ddof=1) / n18) + (np.var(vals_17, ddof=1) / n17)) ** 2
        den_df = (((np.var(vals_18, ddof=1) / n18) ** 2) / (n18 - 1)) + (
            ((np.var(vals_17, ddof=1) / n17) ** 2) / (n17 - 1)
        )
        df_welch = num_df / den_df
        t_crit = float(stats.t.ppf(1.0 - alpha / 2.0, df_welch))
        ci_low = diff_mean_abs - t_crit * se_diff
        ci_high = diff_mean_abs + t_crit * se_diff
    else:
        ci_low, ci_high = diff_mean_abs, diff_mean_abs

    return {
        "rq": spec.rq,
        "metrica": spec.col,
        "metrica_label": spec.short_label,
        "unidade": spec.unit,
        "n_pg17": n17,
        "n_pg18": n18,
        "media_pg17": round(mean17, 4),
        "media_pg18": round(mean18, 4),
        "mediana_pg17": round(med17, 4),
        "mediana_pg18": round(med18, 4),
        "diff_media_pg18_minus_pg17": round(diff_mean_abs, 4),
        "diff_media_pct": round(diff_mean_pct, 4),
        "diff_mediana_pg18_minus_pg17": round(diff_med_abs, 4),
        "diff_mediana_pct": round(diff_med_pct, 4),
        "ic95_diff_media_inf": round(ci_low, 4),
        "ic95_diff_media_sup": round(ci_high, 4),
        "shapiro_pg17_w": round(float(shapiro_17.statistic), 4),
        "shapiro_pg17_p": float(shapiro_17.pvalue),
        "shapiro_pg18_w": round(float(shapiro_18.statistic), 4),
        "shapiro_pg18_p": float(shapiro_18.pvalue),
        "normalidade_ambos": both_normal,
        "levene_stat": round(float(levene_res.statistic), 4),
        "levene_p": float(levene_res.pvalue),
        "variancias_homogeneas": equal_var,
        "teste_selecionado": test_name,
        "estatistica_teste": round(float(res.statistic), 4),
        "p_valor": p_val,
        "rejeita_h0_alpha_0_05": bool(p_val < alpha),
        "alpha_bonferroni": alpha_bonf,
        "p_valor_bonferroni": p_bonf,
        "rejeita_h0_bonferroni": bool(p_val < alpha_bonf),
        "medida_tamanho_efeito": effect_name,
        "tamanho_efeito": round(float(effect_val), 4),
        "magnitude_efeito": effect_mag,
    }


def run_sensitivity_checks(df: pd.DataFrame) -> pd.DataFrame:
    """Executa análise de sensibilidade: (1) sem outliers IQR; (2) teste pareado por seed."""
    rows: list[dict[str, Any]] = []
    # Pareamento por random_seed (mesma semente para PG17 e PG18 em cada repeticao)
    df17_sorted = df[df["versao"] == "PG17"].sort_values("repeticao").reset_index(drop=True)
    df18_sorted = df[df["versao"] == "PG18"].sort_values("repeticao").reset_index(drop=True)
    paired_ok = (
        len(df17_sorted) == len(df18_sorted)
        and (df17_sorted["random_seed"] == df18_sorted["random_seed"]).all()
    )

    for spec in METRICS:
        # 1. Remoção de outliers sinalizados (apenas para sensibilidade)
        clean_df = df[~df[spec.outlier_col].astype(bool)]
        c17 = clean_df.loc[clean_df["versao"] == "PG17", spec.col].to_numpy(dtype=float)
        c18 = clean_df.loc[clean_df["versao"] == "PG18", spec.col].to_numpy(dtype=float)
        no_out = run_hypothesis_test_for_metric(c17, c18, spec)

        # 2. Teste pareado complementar por random_seed
        paired_test_name = "N/A"
        paired_p = float("nan")
        if paired_ok:
            p17 = df17_sorted[spec.col].to_numpy(dtype=float)
            p18 = df18_sorted[spec.col].to_numpy(dtype=float)
            diffs = p18 - p17
            if stats.shapiro(diffs).pvalue >= 0.05:
                paired_test_name = "t pareado"
                paired_p = float(stats.ttest_rel(p18, p17).pvalue)
            else:
                paired_test_name = "Wilcoxon pareado"
                paired_p = float(stats.wilcoxon(p18, p17).pvalue)

        rows.append(
            {
                "rq": spec.rq,
                "metrica": spec.col,
                "outliers_removidos_n": int(len(df) - len(clean_df)),
                "n_pg17_sem_outliers": len(c17),
                "n_pg18_sem_outliers": len(c18),
                "diff_media_pct_sem_outliers": no_out["diff_media_pct"],
                "teste_sem_outliers": no_out["teste_selecionado"],
                "p_valor_sem_outliers": no_out["p_valor"],
                "rejeita_h0_0_05_sem_outliers": no_out["rejeita_h0_alpha_0_05"],
                "rejeita_h0_bonferroni_sem_outliers": no_out["rejeita_h0_bonferroni"],
                "tamanho_efeito_sem_outliers": no_out["tamanho_efeito"],
                "magnitude_sem_outliers": no_out["magnitude_efeito"],
                "teste_pareado_complementar": paired_test_name,
                "p_valor_pareado": paired_p,
                "rejeita_h0_0_05_pareado": bool(paired_p < 0.05) if not math.isnan(paired_p) else False,
            }
        )
    return pd.DataFrame(rows)


def compute_metric_correlations(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula matriz de correlação de Spearman entre as 4 métricas principais."""
    cols = [m.col for m in METRICS]
    corr = df[cols].corr(method="spearman").round(4)
    corr.index.name = "metrica"
    return corr.reset_index()


def _apply_clean_axes_style(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.35)


def plot_boxplots_and_strips(df: pd.DataFrame, out_path: Path) -> None:
    """Figura 1: Boxplots lado a lado com strip plot (pontos individuais)."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.5), dpi=160)
    rng = np.random.default_rng(42)

    for ax, spec in zip(axes.flat, METRICS):
        v17 = df.loc[df["versao"] == "PG17", spec.col].to_numpy(dtype=float)
        v18 = df.loc[df["versao"] == "PG18", spec.col].to_numpy(dtype=float)

        bp = ax.boxplot(
            [v17, v18],
            positions=[1, 2],
            widths=0.42,
            patch_artist=True,
            showfliers=False,
            medianprops={"color": "#111111", "linewidth": 2.0},
            whiskerprops={"linewidth": 1.2},
            capprops={"linewidth": 1.2},
        )
        for patch, color in zip(bp["boxes"], (COLOR_PG17, COLOR_PG18)):
            patch.set_facecolor(color)
            patch.set_alpha(0.35)
            patch.set_edgecolor(color)
            patch.set_linewidth(1.5)

        for pos, vals, color, marker in (
            (1, v17, COLOR_PG17, "o"),
            (2, v18, COLOR_PG18, "s"),
        ):
            jitter = rng.normal(0.0, 0.055, size=len(vals))
            ax.scatter(
                np.full(len(vals), pos) + jitter,
                vals,
                color=color,
                marker=marker,
                s=26,
                alpha=0.85,
                edgecolors="white",
                linewidths=0.4,
                zorder=3,
            )

        ax.set_xticks([1, 2])
        ax.set_xticklabels(["PG 17.12", "PG 18.7"], fontsize=10, fontweight="bold")
        ax.set_title(f"{spec.rq}: {spec.short_label}", fontsize=11, fontweight="bold")
        ax.set_ylabel(f"{spec.short_label} ({spec.unit})", fontsize=10)
        _apply_clean_axes_style(ax)

    fig.suptitle(
        "Comparação PostgreSQL 17 vs PostgreSQL 18 — Distribuição por Métrica (Boxplot + Pontos)",
        fontsize=13,
        fontweight="bold",
        y=0.98,
    )
    fig.text(
        0.5,
        0.01,
        "Fonte: pgbench + psutil (n = 30 repetições válidas por versão; blocos contrabalanceados ABBA).",
        ha="center",
        fontsize=9,
        color="#444444",
    )
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_histograms(df: pd.DataFrame, out_path: Path) -> None:
    """Figura 2: Histogramas sobrepostos por versão para avaliação visual de forma."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 8.5), dpi=160)

    for ax, spec in zip(axes.flat, METRICS):
        v17 = df.loc[df["versao"] == "PG17", spec.col].to_numpy(dtype=float)
        v18 = df.loc[df["versao"] == "PG18", spec.col].to_numpy(dtype=float)
        bins = np.histogram_bin_edges(np.concatenate([v17, v18]), bins=10)

        ax.hist(
            v17,
            bins=bins,
            color=COLOR_PG17,
            alpha=0.50,
            edgecolor=COLOR_PG17,
            linewidth=1.1,
            label="PG 17.12",
        )
        ax.hist(
            v18,
            bins=bins,
            color=COLOR_PG18,
            alpha=0.50,
            edgecolor=COLOR_PG18,
            linewidth=1.1,
            hatch="//",
            label="PG 18.7",
        )
        ax.set_title(f"{spec.rq}: Histograma — {spec.short_label}", fontsize=11, fontweight="bold")
        ax.set_xlabel(f"{spec.short_label} ({spec.unit})", fontsize=10)
        ax.set_ylabel("Frequência (execuções)", fontsize=10)
        ax.legend(frameon=False, fontsize=9)
        _apply_clean_axes_style(ax)

    fig.suptitle(
        "Distribuição de Frequências — PostgreSQL 17 vs PostgreSQL 18",
        fontsize=13,
        fontweight="bold",
        y=0.98,
    )
    fig.text(
        0.5,
        0.01,
        "Fonte: pgbench + psutil (n = 30 repetições válidas por versão).",
        ha="center",
        fontsize=9,
        color="#444444",
    )
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_qqplots(df: pd.DataFrame, out_path: Path) -> None:
    """Figura 3: Q-Q plots para verificação visual de aderência à normalidade."""
    fig, axes = plt.subplots(4, 2, figsize=(10.5, 13), dpi=160)

    for row_idx, spec in enumerate(METRICS):
        for col_idx, (versao, color, vlabel) in enumerate(
            (("PG17", COLOR_PG17, "PG 17.12"), ("PG18", COLOR_PG18, "PG 18.7"))
        ):
            ax = axes[row_idx, col_idx]
            vals = df.loc[df["versao"] == versao, spec.col].to_numpy(dtype=float)
            (osm, osr), (slope, intercept, r) = stats.probplot(vals, dist="norm")
            ax.scatter(osm, osr, color=color, s=24, alpha=0.85)
            x_line = np.array([osm.min(), osm.max()])
            ax.plot(x_line, slope * x_line + intercept, color="#222222", linestyle="--", linewidth=1.3)
            ax.set_title(f"{spec.short_label} — {vlabel} (R²={r**2:.3f})", fontsize=10, fontweight="bold")
            ax.set_xlabel("Quantis teóricos", fontsize=9)
            ax.set_ylabel(f"Quantis observados ({spec.unit})", fontsize=9)
            _apply_clean_axes_style(ax)

    fig.suptitle(
        "Q-Q Plots de Normalidade por Métrica e Versão",
        fontsize=13,
        fontweight="bold",
        y=0.99,
    )
    fig.text(
        0.5,
        0.006,
        "Fonte: pgbench + psutil (n = 30 repetições válidas por versão).",
        ha="center",
        fontsize=9,
        color="#444444",
    )
    fig.tight_layout(rect=[0, 0.02, 1, 0.97])
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_bars_mean_sd(df: pd.DataFrame, out_path: Path) -> None:
    """Figura 4: Gráfico de barras com barras de erro (média ± DP), eixo Y partindo do zero."""
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 8.2), dpi=160)

    for ax, spec in zip(axes.flat, METRICS):
        v17 = df.loc[df["versao"] == "PG17", spec.col].to_numpy(dtype=float)
        v18 = df.loc[df["versao"] == "PG18", spec.col].to_numpy(dtype=float)
        means = [float(np.mean(v17)), float(np.mean(v18))]
        sds = [float(np.std(v17, ddof=1)), float(np.std(v18, ddof=1))]

        bars = ax.bar(
            [0, 1],
            means,
            yerr=sds,
            capsize=6,
            width=0.5,
            color=[COLOR_PG17, COLOR_PG18],
            alpha=0.85,
            edgecolor="#222222",
            linewidth=0.8,
        )
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["PG 17.12", "PG 18.7"], fontsize=10, fontweight="bold")
        ax.set_ylim(0, max(m + s for m, s in zip(means, sds)) * 1.18)
        ax.set_title(f"{spec.rq}: {spec.short_label} (Média ± DP)", fontsize=11, fontweight="bold")
        ax.set_ylabel(f"{spec.short_label} ({spec.unit})", fontsize=10)
        for bar, mean_v in zip(bars, means):
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                mean_v * 0.5,
                f"{mean_v:.2f}",
                ha="center",
                va="center",
                color="white",
                fontweight="bold",
                fontsize=10,
            )
        _apply_clean_axes_style(ax)

    fig.suptitle(
        "Comparação Direta de Médias (± Desvio Padrão) — PG17 vs PG18",
        fontsize=13,
        fontweight="bold",
        y=0.98,
    )
    fig.text(
        0.5,
        0.01,
        "Fonte: pgbench + psutil (n = 30 por versão; eixo vertical iniciado em zero).",
        ha="center",
        fontsize=9,
        color="#444444",
    )
    fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_pct_difference(tests_df: pd.DataFrame, out_path: Path) -> None:
    """Figura 5: Diferença percentual de PG18 em relação a PG17 por métrica."""
    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=160)

    labels = [f"{r['rq']}: {r['metrica_label']}" for _, r in tests_df.iterrows()]
    pct_vals = tests_df["diff_media_pct"].to_numpy(dtype=float)
    y_pos = np.arange(len(labels))

    colors = [COLOR_PG18 if v >= 0 else COLOR_PG17 for v in pct_vals]
    bars = ax.barh(y_pos, pct_vals, height=0.55, color=colors, alpha=0.88, edgecolor="#222222")
    ax.axvline(0.0, color="#111111", linewidth=1.2)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10, fontweight="bold")
    ax.invert_yaxis()
    ax.set_xlabel("Diferença relativa de PG18 em relação a PG17 (%)", fontsize=10)
    ax.set_title(
        "Variação Percentual de PG 18.7 sobre PG 17.12 (Linha de Base)",
        fontsize=12,
        fontweight="bold",
    )

    pad_right = max(abs(pct_vals).max() * 0.45, 3.8)
    pad_left = max(abs(pct_vals).max() * 0.65, 5.2)
    ax.set_xlim(min(pct_vals.min() - pad_left, -6.5), max(pct_vals.max() + pad_right, 11.8))

    for bar, (_, row) in zip(bars, tests_df.iterrows()):
        v = float(row["diff_media_pct"])
        sig = "p_bonf < 0,0125" if row["rejeita_h0_bonferroni"] else (
            "p < 0,05" if row["rejeita_h0_alpha_0_05"] else "não signif."
        )
        offset = 0.25 if v >= 0 else -0.25
        ha = "left" if v >= 0 else "right"
        ax.text(
            v + offset,
            bar.get_y() + bar.get_height() / 2.0,
            f"{v:+.2f}% ({sig})",
            va="center",
            ha=ha,
            fontsize=9.5,
            fontweight="bold",
        )

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle="--", alpha=0.35)
    fig.text(
        0.5,
        0.01,
        "Fonte: pgbench + psutil (n = 30 por versão). Fórmula: (média_PG18 - média_PG17) / média_PG17 × 100%.",
        ha="center",
        fontsize=8.5,
        color="#444444",
    )
    fig.tight_layout(rect=[0, 0.04, 1, 0.96])
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def plot_resource_timeseries(df_ts: pd.DataFrame, out_path: Path) -> None:
    """Figura 6: Evolução temporal média (± IQR) de CPU e Memória por segundo relativo."""
    ts = df_ts.copy()
    # Agrupa segundo_relativo em bins inteiros de 1s (1..10s) para curva agregada por versão
    ts["sec_bin"] = ts["segundo_relativo"].round().astype(int).clip(lower=1, upper=10)

    fig, (ax_cpu, ax_mem) = plt.subplots(1, 2, figsize=(12.5, 5.0), dpi=160)

    for ax, col, title, ylabel in (
        (ax_cpu, "cpu_pct", "Evolução Temporal de CPU (%)", "CPU multi-core (%)"),
        (ax_mem, "memoria_mib", "Evolução Temporal de Memória RSS (MiB)", "Memória RSS (MiB)"),
    ):
        for versao, color, ls, label in (
            ("PG17", COLOR_PG17, "-", "PG 17.12 (mediana + IQR)"),
            ("PG18", COLOR_PG18, "--", "PG 18.7 (mediana + IQR)"),
        ):
            sub = ts[ts["versao"] == versao]
            grouped = sub.groupby("sec_bin")[col]
            secs = grouped.median().index.to_numpy()
            med = grouped.median().to_numpy()
            q25 = grouped.quantile(0.25).to_numpy()
            q75 = grouped.quantile(0.75).to_numpy()

            ax.plot(secs, med, color=color, linestyle=ls, linewidth=2.2, marker="o", markersize=4, label=label)
            ax.fill_between(secs, q25, q75, color=color, alpha=0.18)

        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_xlabel("Segundo relativo da execução (s)", fontsize=10)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_xticks(range(1, 11))
        ax.set_ylim(bottom=0)
        ax.legend(frameon=False, fontsize=9)
        _apply_clean_axes_style(ax)

    fig.suptitle(
        "Série Temporal Agregada de Recursos Durante o Benchmark (30 repetições por versão)",
        fontsize=12.5,
        fontweight="bold",
        y=0.98,
    )
    fig.text(
        0.5,
        0.01,
        "Fonte: psutil (459 amostras em intervalos de ~1 s nas 60 execuções válidas). Faixa sombreada = Q25–Q75.",
        ha="center",
        fontsize=9,
        color="#444444",
    )
    fig.tight_layout(rect=[0, 0.04, 1, 0.94])
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def run_analysis(
    processed_dir: Path = PROCESSED_DIR,
    results_dir: Path = RESULTS_DIR,
) -> dict[str, Any]:
    """Executa todo o pipeline de análise estatística e grava artefatos e gráficos."""
    charts_dir = results_dir / "graficos"
    results_dir.mkdir(parents=True, exist_ok=True)
    charts_dir.mkdir(parents=True, exist_ok=True)

    df, df_ts, val_report = verify_validated_inputs(processed_dir)

    desc_df = compute_descriptive_stats(df)
    test_rows = [
        run_hypothesis_test_for_metric(
            df.loc[df["versao"] == "PG17", spec.col].to_numpy(dtype=float),
            df.loc[df["versao"] == "PG18", spec.col].to_numpy(dtype=float),
            spec,
        )
        for spec in METRICS
    ]
    tests_df = pd.DataFrame(test_rows)
    sens_df = run_sensitivity_checks(df)
    corr_df = compute_metric_correlations(df)

    # Salva tabelas CSV
    desc_df.to_csv(results_dir / "estatisticas_descritivas.csv", index=False, encoding="utf-8")
    tests_df.to_csv(results_dir / "testes_hipotese_efeito.csv", index=False, encoding="utf-8")
    sens_df.to_csv(results_dir / "analise_sensibilidade_outliers.csv", index=False, encoding="utf-8")
    corr_df.to_csv(results_dir / "correlacoes_metricas.csv", index=False, encoding="utf-8")

    # Gera os 6 gráficos
    chart_files = {
        "boxplots_strip": charts_dir / "01_boxplots_strip_metricas.png",
        "histogramas": charts_dir / "02_histogramas_metricas.png",
        "qqplots": charts_dir / "03_qqplots_metricas.png",
        "barras_medias_dp": charts_dir / "04_barras_medias_dp.png",
        "diferenca_percentual": charts_dir / "05_diferenca_percentual.png",
        "serie_temporal_recursos": charts_dir / "06_serie_temporal_recursos.png",
    }
    plot_boxplots_and_strips(df, chart_files["boxplots_strip"])
    plot_histograms(df, chart_files["histogramas"])
    plot_qqplots(df, chart_files["qqplots"])
    plot_bars_mean_sd(df, chart_files["barras_medias_dp"])
    plot_pct_difference(tests_df, chart_files["diferenca_percentual"])
    plot_resource_timeseries(df_ts, chart_files["serie_temporal_recursos"])

    summary: dict[str, Any] = {
        "n_execucoes_validadas": int(len(df)),
        "n_por_versao": {k: int(v) for k, v in df["versao"].value_counts().items()},
        "amostras_serie_temporal": int(len(df_ts)),
        "validacao_origem_aprovada": bool(val_report.get("aprovado")),
        "estatisticas_descritivas": desc_df.to_dict(orient="records"),
        "testes_hipotese_efeito": tests_df.to_dict(orient="records"),
        "analise_sensibilidade": sens_df.to_dict(orient="records"),
        "correlacoes_spearman": corr_df.to_dict(orient="records"),
        "graficos_gerados": {
            k: str(v.relative_to(LAB05_DIR) if v.is_relative_to(LAB05_DIR) else v.relative_to(results_dir))
            for k, v in chart_files.items()
        },
    }

    (results_dir / "resumo_analise_estatistica.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return summary


def parse_args() -> argparse.Namespace:
    """Argumentos CLI da análise estatística."""
    parser = argparse.ArgumentParser(
        description="Executa análise estatística e gera visualizações do LAB05 (Issue #68)."
    )
    parser.add_argument("--processed-dir", type=Path, default=PROCESSED_DIR)
    parser.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    return parser.parse_args()


def main() -> None:
    """Ponto de entrada CLI."""
    args = parse_args()
    summary = run_analysis(args.processed_dir, args.results_dir)
    print(json.dumps(summary["testes_hipotese_efeito"], indent=2, ensure_ascii=False))
    print(f"[LAB05 Análise] Resultados e gráficos gravados em {args.results_dir}")


if __name__ == "__main__":
    main()
