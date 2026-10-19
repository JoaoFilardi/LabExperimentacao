"""Módulo e pipeline de análise das RQ01 a RQ04 e classificação DORA C1 (LAB03S03 - Issue #39).

Executa:
1. Verificação da integridade do dataset de métricas DORA da S02.
2. Análise descritiva da RQ01 (Deployment Frequency, releases/semana).
3. Análise descritiva da RQ02 (Lead Time for Changes, variantes a: release e b: commit).
4. Análise descritiva da RQ03 (Change Failure Rate, variantes a: CI e b: entrega com censura).
5. Análise descritiva da RQ04 (Recovery Time, horas e proporção de censura).
6. Classificação individual e classificação DORA geral de referência C1 (Elite, High, Medium, Low).
7. Geração de tabelas descritivas (Markdown, CSV e LaTeX) e gráficos de alta resolução.
8. Exportação do dataset consolidado de referência C1 para a RQ07 e para o artigo.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")  # Backend headless para execução sem interface gráfica
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .metricas import classify_dora_reference, calculate_iqr


# Definição das categorias DORA e ordem canônica
DORA_CATEGORIES = ["Elite", "High", "Medium", "Low"]
DORA_PALETTE = {
    "Elite": "#2ecc71",   # Verde Esmeralda
    "High": "#3498db",    # Azul
    "Medium": "#f39c12",  # Âmbar / Laranja
    "Low": "#e74c3c",     # Vermelho Coral
}

# Limiares de classificação DORA conforme Seção 5 e Tabela de Referência
THRESHOLDS = {
    "df": {
        "elite": 7.0,     # >= 7 releases/semana
        "high": 1.0,      # >= 1 e < 7 releases/semana
        "medium": 0.23,   # >= 0.23 (1 por mês) e < 1 release/semana
    },
    "lt": {
        "elite": 1.0,     # < 1 dia
        "high": 7.0,      # 1 a < 7 dias
        "medium": 30.0,   # 7 a < 30 dias
    },
    "cfr": {
        "elite": 0.15,    # <= 15% (0.15)
        "high": 0.30,     # > 15% e <= 30%
        "medium": 0.45,   # > 30% e <= 45%
    },
    "rt": {
        "elite": 1.0,     # < 1 hora
        "high": 24.0,     # 1 hora a < 24 horas (1 dia)
        "medium": 168.0,  # 24 horas a < 168 horas (1 semana)
    },
}


# ==============================================================================
# 1. Verificação de Integridade dos Dados
# ==============================================================================

REQUIRED_COLUMNS = [
    "full_name",
    "stars",
    "primary_language",
    "age_years",
    "contributors_count",
    "deployment_frequency_weekly",
    "valid_releases_count",
    "lead_time_by_release_days",
    "lead_time_by_release_iqr_days",
    "lead_time_by_commit_days",
    "lead_time_by_commit_iqr_days",
    "cfr_ci_proxy",
    "cfr_delivery_proxy",
    "cfr_delivery_censored_count",
    "recovery_time_hours",
    "recovery_time_iqr_hours",
    "recovery_total_episodes",
    "recovery_censored_episodes",
    "recovery_censored_ratio",
]


def verificar_integridade_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """Verifica a integridade formal do dataset carregado.

    Valida presença das colunas obrigatórias, ausência de valores nulos críticos,
    consistência de intervalos e regras de censura.
    """
    erros: List[str] = []
    avisos: List[str] = []

    # 1. Presença de colunas
    colunas_faltantes = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if colunas_faltantes:
        erros.append(f"Colunas obrigatórias ausentes no dataset: {colunas_faltantes}")

    n_total = len(df)
    if n_total == 0:
        erros.append("O dataset está completamente vazio (0 repositórios).")
        return {"valido": False, "erros": erros, "avisos": avisos, "n_total": 0}

    # 2. Valores nulos ou ausentes
    nulos_por_coluna = {col: int(df[col].isna().sum()) for col in df.columns if df[col].isna().sum() > 0}
    if nulos_por_coluna:
        avisos.append(f"Colunas com valores ausentes/NaN detectados: {nulos_por_coluna}")

    # 3. Consistência de tipos e intervalos numéricos
    if "deployment_frequency_weekly" in df.columns:
        if (df["deployment_frequency_weekly"] < 0).any():
            erros.append("Valores negativos encontrados em 'deployment_frequency_weekly'.")

    if "lead_time_by_release_days" in df.columns:
        if (df["lead_time_by_release_days"] < 0).any():
            erros.append("Valores negativos encontrados em 'lead_time_by_release_days'.")

    if "lead_time_by_commit_days" in df.columns:
        if (df["lead_time_by_commit_days"] < 0).any():
            erros.append("Valores negativos encontrados em 'lead_time_by_commit_days'.")

    if "cfr_ci_proxy" in df.columns:
        if (df["cfr_ci_proxy"] < 0.0).any() or (df["cfr_ci_proxy"] > 1.0).any():
            erros.append("Valores de 'cfr_ci_proxy' fora do intervalo [0.0, 1.0].")

    if "cfr_delivery_proxy" in df.columns:
        if (df["cfr_delivery_proxy"] < 0.0).any() or (df["cfr_delivery_proxy"] > 1.0).any():
            erros.append("Valores de 'cfr_delivery_proxy' fora do intervalo [0.0, 1.0].")

    if "recovery_time_hours" in df.columns:
        if (df["recovery_time_hours"] < 0).any():
            erros.append("Valores negativos encontrados em 'recovery_time_hours'.")

    if "recovery_censored_ratio" in df.columns:
        if (df["recovery_censored_ratio"] < 0.0).any() or (df["recovery_censored_ratio"] > 1.0).any():
            erros.append("Valores de 'recovery_censored_ratio' fora do intervalo [0.0, 1.0].")

    return {
        "valido": len(erros) == 0,
        "n_total": n_total,
        "erros": erros,
        "avisos": avisos,
        "nulos_por_coluna": nulos_por_coluna,
    }


# ==============================================================================
# 2. Funções de Estatística Descritiva (Mediana e IQR)
# ==============================================================================

def calcular_resumo_estatistico(series: pd.Series, nome_metrica: str, unidade: str) -> Dict[str, Any]:
    """Calcula estatísticas descritivas exigidas com foco estrito em mediana e IQR."""
    val = series.dropna().astype(float)
    if len(val) == 0:
        return {
            "metrica": nome_metrica,
            "unidade": unidade,
            "n": 0,
            "mediana": 0.0,
            "q1": 0.0,
            "q3": 0.0,
            "iqr": 0.0,
            "min": 0.0,
            "max": 0.0,
            "media": 0.0,
            "desvio_padrao": 0.0,
        }

    med, q1, q3 = calculate_iqr(val.tolist())
    return {
        "metrica": nome_metrica,
        "unidade": unidade,
        "n": int(len(val)),
        "mediana": round(med, 4),
        "q1": round(q1, 4),
        "q3": round(q3, 4),
        "iqr": round(q3 - q1, 4),
        "min": round(float(val.min()), 4),
        "max": round(float(val.max()), 4),
        "media": round(float(val.mean()), 4),
        "desvio_padrao": round(float(val.std()), 4),
    }


# ==============================================================================
# 3. Classificação DORA Individual e Geral (C1)
# ==============================================================================

def classificar_df(val: float) -> str:
    """Classifica Deployment Frequency (releases/semana)."""
    if val >= THRESHOLDS["df"]["elite"]:
        return "Elite"
    if val >= THRESHOLDS["df"]["high"]:
        return "High"
    if val >= THRESHOLDS["df"]["medium"]:
        return "Medium"
    return "Low"


def classificar_lt(val: float) -> str:
    """Classifica Lead Time (dias)."""
    if val < THRESHOLDS["lt"]["elite"]:
        return "Elite"
    if val < THRESHOLDS["lt"]["high"]:
        return "High"
    if val < THRESHOLDS["lt"]["medium"]:
        return "Medium"
    return "Low"


def classificar_cfr(val: float) -> str:
    """Classifica Change Failure Rate (proporção 0.0 a 1.0)."""
    if val <= THRESHOLDS["cfr"]["elite"]:
        return "Elite"
    if val <= THRESHOLDS["cfr"]["high"]:
        return "High"
    if val <= THRESHOLDS["cfr"]["medium"]:
        return "Medium"
    return "Low"


def classificar_rt(val: float) -> str:
    """Classifica Recovery Time (horas)."""
    if val < THRESHOLDS["rt"]["elite"]:
        return "Elite"
    if val < THRESHOLDS["rt"]["high"]:
        return "High"
    if val < THRESHOLDS["rt"]["medium"]:
        return "Medium"
    return "Low"


def classificar_dora_c1_df(df: pd.DataFrame) -> pd.DataFrame:
    """Gera classificações individuais e classificação DORA de referência C1.

    Pontuação: Elite=4, High=3, Medium=2, Low=1.
    C1 = mediana dos scores das 4 métricas, arredondada para baixo (math.floor).
    """
    df_res = df.copy()

    # RQ 01: Deployment Frequency
    df_res["c1_df_category"] = df_res["deployment_frequency_weekly"].apply(classificar_df)

    # RQ 02: Lead Time - Variante (a) por release é a variante de referência em C1
    df_res["c1_lt_category"] = df_res["lead_time_by_release_days"].apply(classificar_lt)
    # Também calcula variante (b) para análise comparativa da RQ02
    df_res["lt_commit_category"] = df_res["lead_time_by_commit_days"].apply(classificar_lt)

    # RQ 03: CFR - Variante (a) Proxy de CI é a variante de referência em C1
    df_res["c1_cfr_category"] = df_res["cfr_ci_proxy"].apply(classificar_cfr)
    # Também calcula variante (b) para análise comparativa da RQ03
    df_res["cfr_delivery_category"] = df_res["cfr_delivery_proxy"].apply(classificar_cfr)

    # RQ 04: Recovery Time
    df_res["c1_rt_category"] = df_res["recovery_time_hours"].apply(classificar_rt)

    score_map = {"Elite": 4, "High": 3, "Medium": 2, "Low": 1}
    inv_map = {4: "Elite", 3: "High", 2: "Medium", 1: "Low"}

    overall_scores: List[int] = []
    overall_cats: List[str] = []

    for _, row in df_res.iterrows():
        scores = [
            score_map[row["c1_df_category"]],
            score_map[row["c1_lt_category"]],
            score_map[row["c1_cfr_category"]],
            score_map[row["c1_rt_category"]],
        ]
        med_score = math.floor(float(np.median(scores)))
        overall_scores.append(med_score)
        overall_cats.append(inv_map.get(med_score, "Low"))

    df_res["c1_overall_score"] = overall_scores
    df_res["c1_overall_category"] = overall_cats

    return df_res


# ==============================================================================
# 4. Análise Estatística Individual das RQs (RQ01 a RQ04)
# ==============================================================================

def analisar_rq01_df(df: pd.DataFrame) -> Dict[str, Any]:
    """Análise descritiva da RQ 01: Deployment Frequency (releases/semana)."""
    stats = calcular_resumo_estatistico(
        df["deployment_frequency_weekly"], "RQ01 - Deployment Frequency", "releases/semana"
    )
    freq_cat = df["c1_df_category"].value_counts().reindex(DORA_CATEGORIES, fill_value=0)
    pct_cat = (freq_cat / len(df) * 100.0).round(2)

    return {
        "estatisticas": stats,
        "distribuicao_contagem": freq_cat.to_dict(),
        "distribuicao_percentual": pct_cat.to_dict(),
    }


def analisar_rq02_lt(df: pd.DataFrame) -> Dict[str, Any]:
    """Análise descritiva da RQ 02: Lead Time for Changes (Variantes a e b)."""
    stats_a = calcular_resumo_estatistico(
        df["lead_time_by_release_days"], "RQ02 - Lead Time (Variante a: por release)", "dias"
    )
    stats_b = calcular_resumo_estatistico(
        df["lead_time_by_commit_days"], "RQ02 - Lead Time (Variante b: por commit)", "dias"
    )

    # Comparação direta entre variantes
    diff = df["lead_time_by_release_days"] - df["lead_time_by_commit_days"]
    stats_diff = calcular_resumo_estatistico(
        diff, "RQ02 - Diferença (Variante a - Variante b)", "dias"
    )

    freq_a = df["c1_lt_category"].value_counts().reindex(DORA_CATEGORIES, fill_value=0)
    pct_a = (freq_a / len(df) * 100.0).round(2)

    freq_b = df["lt_commit_category"].value_counts().reindex(DORA_CATEGORIES, fill_value=0)
    pct_b = (freq_b / len(df) * 100.0).round(2)

    return {
        "variante_a": stats_a,
        "variante_b": stats_b,
        "diferenca": stats_diff,
        "distribuicao_a_contagem": freq_a.to_dict(),
        "distribuicao_a_percentual": pct_a.to_dict(),
        "distribuicao_b_contagem": freq_b.to_dict(),
        "distribuicao_b_percentual": pct_b.to_dict(),
    }


def analisar_rq03_cfr(df: pd.DataFrame) -> Dict[str, Any]:
    """Análise descritiva da RQ 03: Change Failure Rate (Variantes a e b)."""
    stats_a = calcular_resumo_estatistico(
        df["cfr_ci_proxy"], "RQ03 - CFR (Variante a: proxy de CI)", "proporção [0, 1]"
    )
    stats_b = calcular_resumo_estatistico(
        df["cfr_delivery_proxy"], "RQ03 - CFR (Variante b: proxy de entrega)", "proporção [0, 1]"
    )

    # Análise de censura da Variante (b)
    censored_releases_total = int(df["cfr_delivery_censored_count"].sum())
    repos_com_censura = int((df["cfr_delivery_censored_count"] > 0).sum())

    freq_a = df["c1_cfr_category"].value_counts().reindex(DORA_CATEGORIES, fill_value=0)
    pct_a = (freq_a / len(df) * 100.0).round(2)

    freq_b = df["cfr_delivery_category"].value_counts().reindex(DORA_CATEGORIES, fill_value=0)
    pct_b = (freq_b / len(df) * 100.0).round(2)

    return {
        "variante_a": stats_a,
        "variante_b": stats_b,
        "censura_entrega": {
            "total_releases_censuradas": censored_releases_total,
            "repositorios_com_releases_censuradas": repos_com_censura,
            "pct_repositorios_com_censura": round(repos_com_censura / len(df) * 100.0, 2),
        },
        "distribuicao_a_contagem": freq_a.to_dict(),
        "distribuicao_a_percentual": pct_a.to_dict(),
        "distribuicao_b_contagem": freq_b.to_dict(),
        "distribuicao_b_percentual": pct_b.to_dict(),
    }


def analisar_rq04_rt(df: pd.DataFrame) -> Dict[str, Any]:
    """Análise descritiva da RQ 04: Recovery Time e censura de episódios."""
    stats_rt = calcular_resumo_estatistico(
        df["recovery_time_hours"], "RQ04 - Tempo de Recuperação", "horas"
    )
    stats_cens_ratio = calcular_resumo_estatistico(
        df["recovery_censored_ratio"], "RQ04 - Taxa de Censura de Episódios", "proporção [0, 1]"
    )

    total_episodes = int(df["recovery_total_episodes"].sum())
    censored_episodes = int(df["recovery_censored_episodes"].sum())
    overall_censored_ratio = round(censored_episodes / max(1, total_episodes), 4)
    repos_com_censura = int((df["recovery_censored_episodes"] > 0).sum())

    freq_rt = df["c1_rt_category"].value_counts().reindex(DORA_CATEGORIES, fill_value=0)
    pct_rt = (freq_rt / len(df) * 100.0).round(2)

    return {
        "tempo_recuperacao": stats_rt,
        "taxa_censura_repositorio": stats_cens_ratio,
        "censura_agregada": {
            "total_episodios": total_episodes,
            "episodios_recuperados": total_episodes - censored_episodes,
            "episodios_censurados": censored_episodes,
            "taxa_global_censura": overall_censored_ratio,
            "pct_global_censura": round(overall_censored_ratio * 100.0, 2),
            "repositorios_com_episodios_censurados": repos_com_censura,
            "pct_repos_com_censura": round(repos_com_censura / len(df) * 100.0, 2),
        },
        "distribuicao_contagem": freq_rt.to_dict(),
        "distribuicao_percentual": pct_rt.to_dict(),
    }


def analisar_c1_geral(df: pd.DataFrame) -> Dict[str, Any]:
    """Análise da classificação DORA de referência C1 agregada."""
    freq_c1 = df["c1_overall_category"].value_counts().reindex(DORA_CATEGORIES, fill_value=0)
    pct_c1 = (freq_c1 / len(df) * 100.0).round(2)

    # Matriz comparativa das 4 dimensões
    comparativo = pd.DataFrame({
        "RQ01_DF": df["c1_df_category"].value_counts().reindex(DORA_CATEGORIES, fill_value=0),
        "RQ02_LT": df["c1_lt_category"].value_counts().reindex(DORA_CATEGORIES, fill_value=0),
        "RQ03_CFR": df["c1_cfr_category"].value_counts().reindex(DORA_CATEGORIES, fill_value=0),
        "RQ04_RT": df["c1_rt_category"].value_counts().reindex(DORA_CATEGORIES, fill_value=0),
        "C1_Overall": freq_c1,
    })

    return {
        "distribuicao_contagem": freq_c1.to_dict(),
        "distribuicao_percentual": pct_c1.to_dict(),
        "tabela_comparativa": comparativo,
    }


# ==============================================================================
# 5. Geração de Gráficos de Alta Resolução (Figuras para o Artigo)
# ==============================================================================

def gerar_graficos_analise(
    df: pd.DataFrame,
    output_dir: Path,
) -> List[Path]:
    """Gera gráficos estatísticos de alta qualidade para as RQ01 a RQ04 e C1."""
    output_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", font="sans-serif")
    saved_paths: List[Path] = []

    # --------------------------------------------------------------------------
    # Figura 1: RQ 01 - Deployment Frequency
    # --------------------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    
    # Histograma com KDE em escala logarítmica
    sns.histplot(
        df["deployment_frequency_weekly"],
        bins=25,
        kde=True,
        color="#3498db",
        ax=ax1,
    )
    med_df = df["deployment_frequency_weekly"].median()
    q1_df = df["deployment_frequency_weekly"].quantile(0.25)
    q3_df = df["deployment_frequency_weekly"].quantile(0.75)
    ax1.axvline(med_df, color="#e74c3c", linestyle="--", linewidth=2, label=f"Mediana: {med_df:.3f}")
    ax1.axvline(q1_df, color="#95a5a6", linestyle=":", linewidth=1.5, label=f"Q1: {q1_df:.3f}")
    ax1.axvline(q3_df, color="#95a5a6", linestyle=":", linewidth=1.5, label=f"Q3: {q3_df:.3f}")
    ax1.set_title("Distribuição Contínua de Deployment Frequency", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Releases por Semana", fontsize=11)
    ax1.set_ylabel("Quantidade de Repositórios", fontsize=11)
    ax1.legend(loc="upper right")

    # Gráfico de barras da categorização DORA
    counts_df = df["c1_df_category"].value_counts().reindex(DORA_CATEGORIES, fill_value=0)
    bars = ax2.bar(
        DORA_CATEGORIES,
        counts_df.values,
        color=[DORA_PALETTE[c] for c in DORA_CATEGORIES],
        edgecolor="#2c3e50",
        linewidth=1,
    )
    for bar in bars:
        h = bar.get_height()
        pct = (h / len(df)) * 100.0
        ax2.annotate(
            f"{h}\n({pct:.1f}%)",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )
    ax2.set_title("Classificação DORA - Deployment Frequency (RQ 01)", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Categoria DORA", fontsize=11)
    ax2.set_ylabel("Repositórios", fontsize=11)
    ax2.set_ylim(0, max(counts_df.values) * 1.25)

    fig.tight_layout()
    p1 = output_dir / "distribuicao_rq01_deployment_frequency.png"
    fig.savefig(p1, dpi=300)
    plt.close(fig)
    saved_paths.append(p1)

    # --------------------------------------------------------------------------
    # Figura 2: RQ 02 - Lead Time Comparativo (Variante a vs Variante b)
    # --------------------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    # Boxplot comparativo em escala logarítmica
    df_lt_melted = pd.melt(
        df[["lead_time_by_release_days", "lead_time_by_commit_days"]],
        value_vars=["lead_time_by_release_days", "lead_time_by_commit_days"],
        var_name="Variante",
        value_name="Dias",
    )
    df_lt_melted["Variante"] = df_lt_melted["Variante"].map({
        "lead_time_by_release_days": "(a) Por Release",
        "lead_time_by_commit_days": "(b) Por Commit",
    })

    sns.boxplot(
        x="Variante",
        y="Dias",
        hue="Variante",
        data=df_lt_melted,
        palette=["#9b59b6", "#1abc9c"],
        ax=ax1,
        legend=False,
        showmeans=True,
        meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black"},
    )
    ax1.set_yscale("log")
    ax1.set_title("Comparação de Lead Time (Escala Logarítmica)", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Lead Time (Dias)", fontsize=11)
    ax1.set_xlabel("Variante Operacional", fontsize=11)

    # Barras de categorização comparando Variante A e Variante B
    cats_a = df["c1_lt_category"].value_counts().reindex(DORA_CATEGORIES, fill_value=0)
    cats_b = df["lt_commit_category"].value_counts().reindex(DORA_CATEGORIES, fill_value=0)
    x = np.arange(len(DORA_CATEGORIES))
    width = 0.35

    ax2.bar(x - width / 2, cats_a.values, width, label="(a) Por Release", color="#9b59b6", edgecolor="#2c3e50")
    ax2.bar(x + width / 2, cats_b.values, width, label="(b) Por Commit", color="#1abc9c", edgecolor="#2c3e50")
    ax2.set_xticks(x)
    ax2.set_xticklabels(DORA_CATEGORIES, fontsize=10)
    ax2.set_title("Categorias DORA de Lead Time por Variante (RQ 02)", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Categoria DORA", fontsize=11)
    ax2.set_ylabel("Repositórios", fontsize=11)
    ax2.legend()

    fig.tight_layout()
    p2 = output_dir / "distribuicao_rq02_lead_time_comparativo.png"
    fig.savefig(p2, dpi=300)
    plt.close(fig)
    saved_paths.append(p2)

    # --------------------------------------------------------------------------
    # Figura 3: RQ 03 - Change Failure Rate Comparativo
    # --------------------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    # Scatter plot / Dispersão entre as duas variantes
    sns.scatterplot(
        x=df["cfr_ci_proxy"] * 100.0,
        y=df["cfr_delivery_proxy"] * 100.0,
        hue=df["c1_cfr_category"],
        palette=DORA_PALETTE,
        alpha=0.8,
        s=60,
        ax=ax1,
    )
    ax1.axline((0, 0), slope=1, color="gray", linestyle="--", alpha=0.6, label="Identidade (y=x)")
    ax1.set_title("Proxy de CI vs. Proxy de Entrega (CFR)", fontsize=12, fontweight="bold")
    ax1.set_xlabel("CFR CI Proxy (%)", fontsize=11)
    ax1.set_ylabel("CFR Entrega Proxy (%)", fontsize=11)
    ax1.legend(loc="upper left")

    # Comparativo de distribuição categórica
    cfr_a = df["c1_cfr_category"].value_counts().reindex(DORA_CATEGORIES, fill_value=0)
    cfr_b = df["cfr_delivery_category"].value_counts().reindex(DORA_CATEGORIES, fill_value=0)
    ax2.bar(x - width / 2, cfr_a.values, width, label="(a) CI Proxy (C1)", color="#3498db", edgecolor="#2c3e50")
    ax2.bar(x + width / 2, cfr_b.values, width, label="(b) Entrega Proxy", color="#e67e22", edgecolor="#2c3e50")
    ax2.set_xticks(x)
    ax2.set_xticklabels(DORA_CATEGORIES, fontsize=10)
    ax2.set_title("Categorias DORA de CFR por Variante (RQ 03)", fontsize=12, fontweight="bold")
    ax2.set_xlabel("Categoria DORA", fontsize=11)
    ax2.set_ylabel("Repositórios", fontsize=11)
    ax2.legend()

    fig.tight_layout()
    p3 = output_dir / "distribuicao_rq03_cfr_comparativo.png"
    fig.savefig(p3, dpi=300)
    plt.close(fig)
    saved_paths.append(p3)

    # --------------------------------------------------------------------------
    # Figura 4: RQ 04 - Recovery Time e Censura
    # --------------------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    sns.histplot(
        df["recovery_time_hours"],
        bins=25,
        kde=True,
        color="#e74c3c",
        ax=ax1,
    )
    med_rt = df["recovery_time_hours"].median()
    ax1.axvline(med_rt, color="#2c3e50", linestyle="--", linewidth=2, label=f"Mediana: {med_rt:.2f}h")
    ax1.axvline(24.0, color="#f39c12", linestyle=":", linewidth=1.5, label="Limite High/Medium (24h)")
    ax1.set_title("Distribuição do Tempo de Recuperação (Horas)", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Tempo de Recuperação (Horas)", fontsize=11)
    ax1.set_ylabel("Repositórios", fontsize=11)
    ax1.legend(loc="upper right")

    # Censura de episódios
    total_episodes = int(df["recovery_total_episodes"].sum())
    censored_episodes = int(df["recovery_censored_episodes"].sum())
    recovered_episodes = total_episodes - censored_episodes

    ax2.pie(
        [recovered_episodes, censored_episodes],
        labels=["Recuperados", "Censurados (Janela Fechada)"],
        autopct="%1.1f%%",
        startangle=140,
        colors=["#2ecc71", "#e74c3c"],
        explode=(0, 0.1),
        textprops={"fontsize": 11, "fontweight": "bold"},
    )
    ax2.set_title(
        f"Proporção de Censura em Episódios de Falha (Total: {total_episodes})",
        fontsize=12,
        fontweight="bold",
    )

    fig.tight_layout()
    p4 = output_dir / "distribuicao_rq04_recovery_time.png"
    fig.savefig(p4, dpi=300)
    plt.close(fig)
    saved_paths.append(p4)

    # --------------------------------------------------------------------------
    # Figura 5: Classificação Geral DORA C1
    # --------------------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    c1_counts = df["c1_overall_category"].value_counts().reindex(DORA_CATEGORIES, fill_value=0)
    bars_c1 = ax1.bar(
        DORA_CATEGORIES,
        c1_counts.values,
        color=[DORA_PALETTE[c] for c in DORA_CATEGORIES],
        edgecolor="#2c3e50",
        linewidth=1.2,
    )
    for bar in bars_c1:
        h = bar.get_height()
        pct = (h / len(df)) * 100.0
        ax1.annotate(
            f"{h}\n({pct:.1f}%)",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )
    ax1.set_title("Classificação DORA de Referência (C1) - Geral", fontsize=12, fontweight="bold")
    ax1.set_xlabel("Categoria de Desempenho", fontsize=11)
    ax1.set_ylabel("Quantidade de Repositórios", fontsize=11)
    ax1.set_ylim(0, max(c1_counts.values) * 1.25)

    # Mapa de calor das 4 métricas componentes de C1
    heatmap_data = pd.DataFrame({
        "Deploy Freq (RQ01)": df["c1_df_category"].value_counts().reindex(DORA_CATEGORIES, fill_value=0),
        "Lead Time (RQ02)": df["c1_lt_category"].value_counts().reindex(DORA_CATEGORIES, fill_value=0),
        "CFR CI (RQ03)": df["c1_cfr_category"].value_counts().reindex(DORA_CATEGORIES, fill_value=0),
        "Recovery (RQ04)": df["c1_rt_category"].value_counts().reindex(DORA_CATEGORIES, fill_value=0),
    })
    sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="YlGnBu", cbar=True, ax=ax2)
    ax2.set_title("Distribuição das Métricas Componentes de C1", fontsize=12, fontweight="bold")
    ax2.set_ylabel("Categoria DORA", fontsize=11)

    fig.tight_layout()
    p5 = output_dir / "distribuicao_classificacao_dora_c1.png"
    fig.savefig(p5, dpi=300)
    plt.close(fig)
    saved_paths.append(p5)

    # --------------------------------------------------------------------------
    # Figura 6: Painel Consolidado 2x2 para Artigo
    # --------------------------------------------------------------------------
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    # (0, 0) RQ01
    sns.boxplot(y=df["deployment_frequency_weekly"], color="#3498db", ax=axes[0, 0])
    axes[0, 0].set_title(f"RQ01: Deployment Frequency (Mediana={df['deployment_frequency_weekly'].median():.3f} rel/sem)", fontweight="bold")
    axes[0, 0].set_ylabel("Releases por Semana")

    # (0, 1) RQ02
    sns.boxplot(
        data=df[["lead_time_by_release_days", "lead_time_by_commit_days"]],
        palette=["#9b59b6", "#1abc9c"],
        ax=axes[0, 1],
    )
    axes[0, 1].set_yscale("log")
    axes[0, 1].set_xticks([0, 1])
    axes[0, 1].set_xticklabels(["Por Release (a)", "Por Commit (b)"])
    axes[0, 1].set_title("RQ02: Lead Time for Changes (Dias - Escala Log)", fontweight="bold")
    axes[0, 1].set_ylabel("Dias")

    # (1, 0) RQ03
    sns.boxplot(
        data=df[["cfr_ci_proxy", "cfr_delivery_proxy"]],
        palette=["#3498db", "#e67e22"],
        ax=axes[1, 0],
    )
    axes[1, 0].set_xticks([0, 1])
    axes[1, 0].set_xticklabels(["Proxy CI (a)", "Proxy Entrega (b)"])
    axes[1, 0].set_title("RQ03: Change Failure Rate (Proporção)", fontweight="bold")
    axes[1, 0].set_ylabel("Taxa de Falha")

    # (1, 1) C1 Geral
    bars = axes[1, 1].bar(
        DORA_CATEGORIES,
        c1_counts.values,
        color=[DORA_PALETTE[c] for c in DORA_CATEGORIES],
        edgecolor="#2c3e50",
    )
    for bar in bars:
        h = bar.get_height()
        pct = (h / len(df)) * 100.0
        axes[1, 1].annotate(
            f"{h} ({pct:.1f}%)",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )
    axes[1, 1].set_title("Classificação DORA de Referência (C1)", fontweight="bold")
    axes[1, 1].set_ylabel("Repositórios")
    axes[1, 1].set_ylim(0, max(c1_counts.values) * 1.25)

    fig.tight_layout()
    p6 = output_dir / "painel_resumo_dora_c1.png"
    fig.savefig(p6, dpi=300)
    plt.close(fig)
    saved_paths.append(p6)

    return saved_paths


# ==============================================================================
# 6. Exportação de Tabelas e Resultados
# ==============================================================================

def _df_para_markdown(df: pd.DataFrame) -> str:
    """Converte DataFrame em tabela Markdown sem depender do pacote tabulate."""
    headers = [str(c) for c in df.columns]
    linhas = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join([":---" if i == 0 else ":---:" for i in range(len(headers))]) + " |",
    ]
    for _, row in df.iterrows():
        vals = [str(row[c]) for c in df.columns]
        linhas.append("| " + " | ".join(vals) + " |")
    return "\n".join(linhas)


def exportar_tabelas_estatisticas(
    analise_rq01: Dict[str, Any],
    analise_rq02: Dict[str, Any],
    analise_rq03: Dict[str, Any],
    analise_rq04: Dict[str, Any],
    analise_c1: Dict[str, Any],
    output_dir: Path,
) -> Dict[str, Path]:
    """Exporta tabelas estatísticas em formatos CSV, Markdown e LaTeX."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Tabela Consolidada de Estatísticas Descritivas (RQ01 a RQ04)
    rows_desc = [
        analise_rq01["estatisticas"],
        analise_rq02["variante_a"],
        analise_rq02["variante_b"],
        analise_rq02["diferenca"],
        analise_rq03["variante_a"],
        analise_rq03["variante_b"],
        analise_rq04["tempo_recuperacao"],
        analise_rq04["taxa_censura_repositorio"],
    ]
    df_desc = pd.DataFrame(rows_desc)
    p_csv_desc = output_dir / "tabela_estatisticas_rq01_rq04.csv"
    df_desc.to_csv(p_csv_desc, index=False, encoding="utf-8")

    p_md_desc = output_dir / "tabela_estatisticas_rq01_rq04.md"
    with open(p_md_desc, "w", encoding="utf-8") as f:
        f.write("# Estatísticas Descritivas das Métricas DORA (RQ01 a RQ04)\n\n")
        f.write(_df_para_markdown(df_desc))
        f.write("\n")

    # 2. Tabela de Distribuição das Categorias DORA
    rows_cat = [
        {"Métrica": "RQ01 - Deployment Frequency", **{c: f"{analise_rq01['distribuicao_contagem'][c]} ({analise_rq01['distribuicao_percentual'][c]}%)" for c in DORA_CATEGORIES}},
        {"Métrica": "RQ02 - Lead Time (Variante a: release)", **{c: f"{analise_rq02['distribuicao_a_contagem'][c]} ({analise_rq02['distribuicao_a_percentual'][c]}%)" for c in DORA_CATEGORIES}},
        {"Métrica": "RQ02 - Lead Time (Variante b: commit)", **{c: f"{analise_rq02['distribuicao_b_contagem'][c]} ({analise_rq02['distribuicao_b_percentual'][c]}%)" for c in DORA_CATEGORIES}},
        {"Métrica": "RQ03 - CFR (Variante a: CI proxy)", **{c: f"{analise_rq03['distribuicao_a_contagem'][c]} ({analise_rq03['distribuicao_a_percentual'][c]}%)" for c in DORA_CATEGORIES}},
        {"Métrica": "RQ03 - CFR (Variante b: entrega proxy)", **{c: f"{analise_rq03['distribuicao_b_contagem'][c]} ({analise_rq03['distribuicao_b_percentual'][c]}%)" for c in DORA_CATEGORIES}},
        {"Métrica": "RQ04 - Tempo de Recuperação", **{c: f"{analise_rq04['distribuicao_contagem'][c]} ({analise_rq04['distribuicao_percentual'][c]}%)" for c in DORA_CATEGORIES}},
        {"Métrica": "DORA Geral de Referência (C1)", **{c: f"{analise_c1['distribuicao_contagem'][c]} ({analise_c1['distribuicao_percentual'][c]}%)" for c in DORA_CATEGORIES}},
    ]
    df_cat = pd.DataFrame(rows_cat)
    p_csv_cat = output_dir / "tabela_distribuicao_categorias.csv"
    df_cat.to_csv(p_csv_cat, index=False, encoding="utf-8")

    p_md_cat = output_dir / "tabela_distribuicao_categorias.md"
    with open(p_md_cat, "w", encoding="utf-8") as f:
        f.write("# Distribuição de Repositórios por Categoria DORA\n\n")
        f.write(_df_para_markdown(df_cat))
        f.write("\n")

    # 3. Tabela LaTeX para Artigo (Template SBC)
    p_tex = output_dir / "tabelas_artigo_sbc.tex"
    with open(p_tex, "w", encoding="utf-8") as f:
        f.write("% ==============================================================================\n")
        f.write("% Tabelas Geradas Automaticamente para o Artigo Científico (SBC Template)\n")
        f.write("% Issue #39: Análise RQ01-RQ04 e Classificação DORA C1\n")
        f.write("% ==============================================================================\n\n")
        
        f.write("\\begin{table}[htbp]\n\\centering\n")
        f.write("\\caption{Estatísticas Descritivas das Métricas DORA (Mediana e IQR)}\n")
        f.write("\\label{tab:metricas_descritivas_rq01_rq04}\n")
        f.write("\\begin{tabular}{|l|l|r|r|r|r|r|}\n\\hline\n")
        f.write("\\textbf{Métrica / Variante} & \\textbf{Unidade} & \\textbf{Mediana} & \\textbf{Q1} & \\textbf{Q3} & \\textbf{IQR} & \\textbf{N} \\\\\n\\hline\n")
        for r in rows_desc:
            f.write(f"{r['metrica']} & {r['unidade']} & {r['mediana']} & {r['q1']} & {r['q3']} & {r['iqr']} & {r['n']} \\\\\n")
        f.write("\\hline\n\\end{tabular}\n\\end{table}\n\n")

        f.write("\\begin{table}[htbp]\n\\centering\n")
        f.write("\\caption{Classificação DORA dos Repositórios (Referência C1)}\n")
        f.write("\\label{tab:classificacao_dora_c1}\n")
        f.write("\\begin{tabular}{|l|r|r|r|r|}\n\\hline\n")
        f.write("\\textbf{Métrica} & \\textbf{Elite} & \\textbf{High} & \\textbf{Medium} & \\textbf{Low} \\\\\n\\hline\n")
        for r in rows_cat:
            f.write(f"{r['Métrica']} & {r['Elite']} & {r['High']} & {r['Medium']} & {r['Low']} \\\\\n")
        f.write("\\hline\n\\end{tabular}\n\\end{table}\n")

    return {
        "csv_desc": p_csv_desc,
        "md_desc": p_md_desc,
        "csv_cat": p_csv_cat,
        "md_cat": p_md_cat,
        "latex": p_tex,
    }


def exportar_dataset_c1(df_c1: pd.DataFrame, output_path: Path) -> Path:
    """Exporta o dataset consolidado com a classificação DORA C1 e métricas.

    Formato diretamente compatível para reutilização na RQ07 e no artigo.
    """
    colunas_export = [
        "full_name",
        "stars",
        "primary_language",
        "age_years",
        "contributors_count",
        "deployment_frequency_weekly",
        "c1_df_category",
        "lead_time_by_release_days",
        "c1_lt_category",
        "lead_time_by_commit_days",
        "lt_commit_category",
        "cfr_ci_proxy",
        "cfr_ci_percentage",
        "c1_cfr_category",
        "cfr_delivery_proxy",
        "cfr_delivery_percentage",
        "cfr_delivery_category",
        "cfr_delivery_censored_count",
        "recovery_time_hours",
        "recovery_time_iqr_hours",
        "c1_rt_category",
        "recovery_total_episodes",
        "recovery_censored_episodes",
        "recovery_censored_ratio",
        "c1_overall_score",
        "c1_overall_category",
    ]
    df_export = df_c1[colunas_export].copy()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_export.to_csv(output_path, index=False, encoding="utf-8")
    return output_path


# ==============================================================================
# 7. Pipeline Completo de Execução
# ==============================================================================

def executar_pipeline_analise(
    input_csv_path: Path,
    output_dir: Path,
    figures_dir: Optional[Path] = None,
) -> Dict[str, Any]:
    """Executa o pipeline completo da Issue #39."""
    if not input_csv_path.exists():
        raise FileNotFoundError(f"Arquivo CSV de entrada não encontrado: {input_csv_path}")

    fig_dir = figures_dir or (output_dir / "figuras")

    # 1. Carregamento e Verificação de Integridade
    df_raw = pd.read_csv(input_csv_path)
    integridade = verificar_integridade_dataset(df_raw)
    if not integridade["valido"]:
        raise ValueError(f"Falha na verificação de integridade dos dados: {integridade['erros']}")

    # 2. Classificação DORA C1
    df_c1 = classificar_dora_c1_df(df_raw)

    # 3. Análise estatística de cada RQ
    res_rq01 = analisar_rq01_df(df_c1)
    res_rq02 = analisar_rq02_lt(df_c1)
    res_rq03 = analisar_rq03_cfr(df_c1)
    res_rq04 = analisar_rq04_rt(df_c1)
    res_c1 = analisar_c1_geral(df_c1)

    # 4. Exportação das Tabelas
    tabelas_paths = exportar_tabelas_estatisticas(
        analise_rq01=res_rq01,
        analise_rq02=res_rq02,
        analise_rq03=res_rq03,
        analise_rq04=res_rq04,
        analise_c1=res_c1,
        output_dir=output_dir,
    )

    # 5. Exportação do Dataset C1 para RQ07 e Artigo
    dataset_c1_path = exportar_dataset_c1(
        df_c1=df_c1,
        output_path=output_dir / "classificacao_dora_c1.csv",
    )

    # 6. Geração dos Gráficos
    graficos_paths = gerar_graficos_analise(df_c1, fig_dir)

    return {
        "status": "sucesso",
        "n_repositorios": integridade["n_total"],
        "integridade": integridade,
        "rq01": res_rq01,
        "rq02": res_rq02,
        "rq03": res_rq03,
        "rq04": res_rq04,
        "c1": res_c1,
        "tabelas": tabelas_paths,
        "dataset_c1": dataset_c1_path,
        "graficos": graficos_paths,
        "df_c1": df_c1,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Análise das RQ01 a RQ04 e Classificação DORA C1 (LAB03S03 - Issue #39)"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="lab03/data/metricas_dora.csv",
        help="Caminho do CSV de métricas DORA consolidado",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="lab03/data",
        help="Diretório onde tabelas e datasets serão exportados",
    )
    parser.add_argument(
        "--figures-dir",
        type=str,
        default=None,
        help="Diretório de saída para as figuras (padrão: output-dir/figuras)",
    )

    args = parser.parse_args()
    res = executar_pipeline_analise(
        input_csv_path=Path(args.input),
        output_dir=Path(args.output_dir),
        figures_dir=Path(args.figures_dir) if args.figures_dir else None,
    )

    print("=" * 80)
    print("ANÁLISE RQ01-RQ04 E CLASSIFICAÇÃO DORA DE REFERÊNCIA (C1) CONCLUÍDA")
    print("=" * 80)
    print(f"Total de Repositórios Avaliados: {res['n_repositorios']}")
    print(f"- RQ01 Mediana DF: {res['rq01']['estatisticas']['mediana']} rel/sem (IQR: {res['rq01']['estatisticas']['iqr']})")
    print(f"- RQ02 Mediana LT Release: {res['rq02']['variante_a']['mediana']} dias (IQR: {res['rq02']['variante_a']['iqr']})")
    print(f"- RQ02 Mediana LT Commit:  {res['rq02']['variante_b']['mediana']} dias (IQR: {res['rq02']['variante_b']['iqr']})")
    print(f"- RQ03 Mediana CFR CI:     {res['rq03']['variante_a']['mediana']} (IQR: {res['rq03']['variante_a']['iqr']})")
    print(f"- RQ03 Mediana CFR Entrega:{res['rq03']['variante_b']['mediana']} (IQR: {res['rq03']['variante_b']['iqr']})")
    print(f"- RQ04 Mediana Recovery:   {res['rq04']['tempo_recuperacao']['mediana']} horas (IQR: {res['rq04']['tempo_recuperacao']['iqr']})")
    print(f"- RQ04 Censura Global:     {res['rq04']['censura_agregada']['pct_global_censura']}% dos episódios censurados")
    print("\nDistribuição DORA C1 Geral:")
    for cat in DORA_CATEGORIES:
        print(f"  * {cat:6s}: {res['c1']['distribuicao_contagem'][cat]:3d} repositórios ({res['c1']['distribuicao_percentual'][cat]}%)")
    print(f"\nArtefatos salvos em: {args.output_dir}")
    print(f"Dataset C1 exportado para: {res['dataset_c1']}")
    print(f"Figuras salvas em: {res['graficos'][0].parent} ({len(res['graficos'])} figuras)")


if __name__ == "__main__":
    main()
