#!/usr/bin/env python3
"""Gera os boxplots do dashboard de resultados do Lab02S03.

Entradas:
    data/log_trials_consolidado.csv
    data/metricas_estaticas.csv

Saidas:
    graficos_dashboard/boxplot_rq1_tempo.png
    graficos_dashboard/boxplot_rq2_taxa_sucesso.png
    graficos_dashboard/boxplots_rq3_metricas_estaticas.png
    graficos_dashboard/resumo_dashboard.csv

Uso:
    python scripts/dashboard_resultados.py
    python scripts/dashboard_resultados.py --saida graficos_dashboard
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


TRATAMENTOS = ["Manual", "Com IA"]
CORES = {"Manual": "#386641", "Com IA": "#bc4749"}
COLUNAS_LOG = {"kata", "tratamento", "T_TTG_min", "N_total", "N_pass"}
COLUNAS_ESTATICAS = {
    "tratamento",
    "complexidade_media",
    "sloc",
    "indice_manutenibilidade",
}


def validar_colunas(df: pd.DataFrame, obrigatorias: set[str], nome: str) -> None:
    faltantes = sorted(obrigatorias.difference(df.columns))
    if faltantes:
        raise ValueError(f"Colunas ausentes em {nome}: {', '.join(faltantes)}")


def normalizar_tratamento(df: pd.DataFrame) -> pd.DataFrame:
    resultado = df.copy()
    valores = resultado["tratamento"].astype(str).str.upper().str.strip()
    desconhecidos = sorted(set(valores) - {"A", "B"})
    if desconhecidos:
        raise ValueError(
            "Coluna 'tratamento' deve conter apenas A ou B; "
            f"valores encontrados: {desconhecidos}"
        )
    resultado["tratamento"] = valores.map({"A": "Manual", "B": "Com IA"})
    return resultado


def carregar_dados(caminho_log: Path, caminho_estaticas: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    log = pd.read_csv(caminho_log)
    estaticas = pd.read_csv(caminho_estaticas)
    validar_colunas(log, COLUNAS_LOG, caminho_log.name)
    validar_colunas(estaticas, COLUNAS_ESTATICAS, caminho_estaticas.name)

    log = normalizar_tratamento(log)
    estaticas = normalizar_tratamento(estaticas)
    for coluna in ["T_TTG_min", "N_total", "N_pass"]:
        log[coluna] = pd.to_numeric(log[coluna], errors="coerce")
    for coluna in ["complexidade_media", "sloc", "indice_manutenibilidade"]:
        estaticas[coluna] = pd.to_numeric(estaticas[coluna], errors="coerce")

    if (log["N_total"] <= 0).any():
        raise ValueError("N_total deve ser maior que zero em todos os trials.")
    log["SR_test_pct"] = log["N_pass"] / log["N_total"] * 100
    log["N_fail"] = log["N_total"] - log["N_pass"]
    return log, estaticas


def configurar_grafico(titulo: str, eixo_y: str) -> None:
    plt.title(titulo, loc="left", fontweight="bold")
    plt.xlabel("")
    plt.ylabel(eixo_y)
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    sns.despine()


def gerar_boxplot(
    dados: pd.DataFrame,
    coluna: str,
    titulo: str,
    eixo_y: str,
    caminho: Path,
    limite_y: tuple[float, float] | None = None,
) -> None:
    plt.figure(figsize=(8, 5))
    sns.boxplot(
        data=dados,
        x="tratamento",
        y=coluna,
        order=TRATAMENTOS,
        hue="tratamento",
        palette=CORES,
        legend=False,
        width=0.5,
    )
    sns.stripplot(
        data=dados,
        x="tratamento",
        y=coluna,
        order=TRATAMENTOS,
        color="#202020",
        size=5,
        jitter=0.12,
    )
    configurar_grafico(titulo, eixo_y)
    if limite_y is not None:
        plt.ylim(*limite_y)
    plt.tight_layout()
    plt.savefig(caminho, dpi=180)
    plt.close()


def gerar_rq3(estaticas: pd.DataFrame, caminho: Path) -> None:
    metricas = {
        "complexidade_media": "Complexidade ciclom. media",
        "sloc": "SLOC",
        "indice_manutenibilidade": "Indice de manutenibilidade",
    }
    dados = estaticas.melt(
        id_vars=["tratamento"],
        value_vars=list(metricas),
        var_name="metrica",
        value_name="valor",
    )
    dados["metrica"] = dados["metrica"].map(metricas)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for eixo, nome in zip(axes, metricas.values()):
        subset = dados[dados["metrica"] == nome].dropna(subset=["valor"])
        sns.boxplot(
            data=subset,
            x="tratamento",
            y="valor",
            order=TRATAMENTOS,
            hue="tratamento",
            palette=CORES,
            legend=False,
            width=0.5,
            ax=eixo,
        )
        sns.stripplot(
            data=subset,
            x="tratamento",
            y="valor",
            order=TRATAMENTOS,
            color="#202020",
            size=4,
            jitter=0.12,
            ax=eixo,
        )
        eixo.set_title(nome, loc="left", fontweight="bold")
        eixo.set_xlabel("")
        eixo.set_ylabel("Valor")
        eixo.grid(axis="y", linestyle="--", alpha=0.3)
        sns.despine(ax=eixo)

    fig.suptitle("RQ3 - Metricas estaticas por tratamento", x=0.03, ha="left", fontweight="bold")
    fig.tight_layout()
    fig.savefig(caminho, dpi=180)
    plt.close(fig)


def criar_resumo(log: pd.DataFrame, estaticas: pd.DataFrame) -> pd.DataFrame:
    partes = []
    for dados, metricas in [
        (log, {"T_TTG_min": "RQ1 - Tempo (min)", "SR_test_pct": "RQ2 - Taxa de sucesso (%)"}),
        (
            estaticas,
            {
                "complexidade_media": "RQ3 - Complexidade ciclom. media",
                "sloc": "RQ3 - SLOC",
                "indice_manutenibilidade": "RQ3 - Indice de manutenibilidade",
            },
        ),
    ]:
        for coluna, nome in metricas.items():
            validos = dados.dropna(subset=[coluna])
            resumo = validos.groupby("tratamento")[coluna].agg(
                n="count",
                mediana="median",
                q1=lambda serie: serie.quantile(0.25),
                q3=lambda serie: serie.quantile(0.75),
            ).reset_index()
            resumo["metrica"] = nome
            resumo["iqr"] = resumo["q3"] - resumo["q1"]
            partes.append(resumo[["metrica", "tratamento", "n", "mediana", "q1", "q3", "iqr"]])
    return pd.concat(partes, ignore_index=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    raiz = Path(__file__).resolve().parents[1]
    parser.add_argument("--log", type=Path, default=raiz / "data/log_trials_consolidado.csv")
    parser.add_argument("--estaticas", type=Path, default=raiz / "data/metricas_estaticas.csv")
    parser.add_argument("--saida", type=Path, default=raiz / "graficos_dashboard")
    args = parser.parse_args()

    sns.set_theme(style="whitegrid", context="notebook")
    log, estaticas = carregar_dados(args.log, args.estaticas)
    args.saida.mkdir(parents=True, exist_ok=True)

    tempo = log.dropna(subset=["T_TTG_min"])
    ausentes = len(log) - len(tempo)
    if ausentes:
        print(f"AVISO: {ausentes} trial(s) sem T_TTG_min; excluido(s) apenas do boxplot de RQ1.")
    if tempo.empty:
        print("AVISO: nenhum tempo disponivel; boxplot de RQ1 nao sera gerado.")
    else:
        gerar_boxplot(
            tempo,
            "T_TTG_min",
            "RQ1 - Time-to-green por tratamento",
            "Tempo (minutos)",
            args.saida / "boxplot_rq1_tempo.png",
            limite_y=(0, 35),
        )

    gerar_boxplot(
        log,
        "SR_test_pct",
        "RQ2 - Taxa de sucesso nos testes",
        "Testes aprovados (%)",
        args.saida / "boxplot_rq2_taxa_sucesso.png",
        limite_y=(0, 100),
    )
    gerar_rq3(estaticas, args.saida / "boxplots_rq3_metricas_estaticas.png")
    criar_resumo(log, estaticas).to_csv(args.saida / "resumo_dashboard.csv", index=False)
    print(f"Dashboard gerado em: {args.saida}")


if __name__ == "__main__":
    main()