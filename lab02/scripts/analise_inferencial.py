#!/usr/bin/env python3
"""Analise Estatistica Inferencial (Teste de Wilcoxon) - RQ1 e RQ2.

Issue: [Lab02S03] Analise Estatistica Inferencial (Teste de Wilcoxon) : RQ1 e RQ2 #21

Le o log consolidado de trials (CSV) e aplica o Teste de Postos com Sinais de
Wilcoxon (Wilcoxon Signed-Rank Test) para amostras pareadas, comparando o
Tratamento A (Manual) contra o Tratamento B (Com IA).

Pareamento: os trials sao pareados POR KATA (K1, K2, K3, K4), nao por
participante, pois o desenho e crossover between-subjects por kata (cada kata
e resolvido por sujeitos diferentes em cada tratamento). Quando ha mais de um
registro do mesmo kata e tratamento, usa-se a MEDIANA desses registros como o
valor representativo daquele kata-tratamento antes do pareamento (evita que um
kata com 3 replicas em B pese mais que um kata com 1 replica em A).

RQ1 - Time-to-green (T_TTG):
    H0: Mediana(T_TTG_B) >= Mediana(T_TTG_A)
    H1: Mediana(T_TTG_B) <  Mediana(T_TTG_A)   (teste unilateral a esquerda)
    Trials censurados (censurado=1) entram com T_TTG = 35.0 (nao sao descartados).

RQ2 - Taxa de sucesso nos testes (SR_test = N_pass / N_total * 100):
    H0: Mediana(SR_B) <= Mediana(SR_A)
    H1: Mediana(SR_B) >  Mediana(SR_A)   (teste unilateral a direita)

Tamanho de efeito: r de Rosenthal, r = |Z| / sqrt(N), onde N e o numero de
pares (excluindo empates, conforme a convencao do teste de Wilcoxon).

Uso:
    python analise_inferencial.py --log data/log_trials_consolidado.csv

O CSV de entrada precisa das colunas:
    participante,kata,tratamento,T_TTG_min,censurado,N_total,N_pass

Onde:
    tratamento  -> "A" (manual) ou "B" (com IA)
    censurado   -> 0 ou 1 (1 = atingiu o time-box de 35 min sem terminar)
    T_TTG_min   -> tempo em minutos decimais (se censurado=1, deve ja vir como 35.0)
"""

from __future__ import annotations

import argparse
import sys

import numpy as np
import pandas as pd
from scipy import stats

TIME_BOX_MIN = 35.0
COLUNAS_OBRIGATORIAS = [
    "participante", "kata", "tratamento", "T_TTG_min", "censurado",
    "N_total", "N_pass",
]


def carregar_dados(caminho_csv: str) -> pd.DataFrame:
    df = pd.read_csv(caminho_csv)

    faltantes = [c for c in COLUNAS_OBRIGATORIAS if c not in df.columns]
    if faltantes:
        raise ValueError(f"Colunas obrigatorias ausentes no CSV: {faltantes}")

    df["tratamento"] = df["tratamento"].str.upper().str.strip()
    if not set(df["tratamento"].unique()).issubset({"A", "B"}):
        raise ValueError("Coluna 'tratamento' deve conter apenas 'A' ou 'B'")

    # Sanidade: linhas marcadas como censuradas mas sem T_TTG=35.0 sao um erro
    # de preenchimento do log, nao um valor valido - aborta em vez de mascarar.
    inconsistentes = df[(df["censurado"] == 1) & (df["T_TTG_min"] != TIME_BOX_MIN)]
    if not inconsistentes.empty:
        raise ValueError(
            "Ha linhas com censurado=1 mas T_TTG_min != 35.0. Corrija o log:\n"
            f"{inconsistentes[['participante', 'kata', 'tratamento', 'T_TTG_min']]}"
        )

    df["SR_test_pct"] = (df["N_pass"] / df["N_total"]) * 100.0
    return df


def preparar_pares_por_kata(df: pd.DataFrame, coluna_metrica: str) -> pd.Series:
    """Agrega por (kata, tratamento) usando a mediana e pivota A vs B."""
    agregado = df.groupby(["kata", "tratamento"])[coluna_metrica].median()
    pivot = agregado.unstack("tratamento")

    if "A" not in pivot.columns or "B" not in pivot.columns:
        raise ValueError(
            "Dataset nao tem os dois tratamentos representados; "
            "impossivel formar pares A-B."
        )

    pares = pivot.dropna(subset=["A", "B"])
    return pares


def rosenthal_r(estatistica_z: float, n_pares: int) -> float:
    if n_pares == 0:
        return float("nan")
    return abs(estatistica_z) / np.sqrt(n_pares)


def rodar_wilcoxon(pares: pd.DataFrame, alternativa: str) -> dict:
    """alternativa: 'less' (B < A, para RQ1) ou 'greater' (B > A, para RQ2)."""
    diffs = pares["B"] - pares["A"]
    n_pares_validos = int((diffs != 0).sum())

    if len(pares) < 5:
        aviso = (
            f"AVISO: apenas {len(pares)} par(es) kata disponivel(is). "
            "Wilcoxon exige N>=5 minimamente para gerar p-valor exato/aproximado "
            "e a literatura recomenda N>=6-8 para ter poder estatistico minimo. "
            "O resultado abaixo e reportavel apenas como exploratorio."
        )
        print(aviso, file=sys.stderr)

    if n_pares_validos == 0:
        return {
            "n_pares": len(pares),
            "n_pares_sem_empate": 0,
            "estatistica_w": float("nan"),
            "p_valor": float("nan"),
            "r_rosenthal": float("nan"),
            "mediana_A": pares["A"].median(),
            "mediana_B": pares["B"].median(),
            "erro": "Todas as diferencas pareadas sao zero (empate total); "
                    "Wilcoxon nao pode ser calculado.",
        }

    try:
        resultado = stats.wilcoxon(
            pares["B"], pares["A"], alternative=alternativa, zero_method="wilcox"
        )
        estatistica_w = resultado.statistic
        p_valor = resultado.pvalue
    except ValueError as exc:
        return {
            "n_pares": len(pares),
            "n_pares_sem_empate": n_pares_validos,
            "estatistica_w": float("nan"),
            "p_valor": float("nan"),
            "r_rosenthal": float("nan"),
            "mediana_A": pares["A"].median(),
            "mediana_B": pares["B"].median(),
            "erro": str(exc),
        }

    # scipy nao retorna Z diretamente; aproxima via distribuicao normal para o r de Rosenthal
    z_aprox = stats.norm.ppf(1 - p_valor) if alternativa != "two-sided" else stats.norm.ppf(1 - p_valor / 2)

    return {
        "n_pares": len(pares),
        "n_pares_sem_empate": n_pares_validos,
        "estatistica_w": float(estatistica_w),
        "p_valor": float(p_valor),
        "r_rosenthal": rosenthal_r(z_aprox, n_pares_validos),
        "mediana_A": float(pares["A"].median()),
        "mediana_B": float(pares["B"].median()),
        "iqr_A": float(pares["A"].quantile(0.75) - pares["A"].quantile(0.25)),
        "iqr_B": float(pares["B"].quantile(0.75) - pares["B"].quantile(0.25)),
    }


def imprimir_resultado(titulo: str, hipoteses: tuple[str, str], resultado: dict) -> None:
    print(f"\n{'=' * 70}")
    print(titulo)
    print("=" * 70)
    print(f"H0: {hipoteses[0]}")
    print(f"H1: {hipoteses[1]}")
    print(f"N pares (katas): {resultado['n_pares']}")
    if "erro" in resultado:
        print(f"ERRO: {resultado['erro']}")
        return
    print(f"Mediana Manual (A): {resultado['mediana_A']:.2f}  (IQR={resultado.get('iqr_A', float('nan')):.2f})")
    print(f"Mediana Com IA (B): {resultado['mediana_B']:.2f}  (IQR={resultado.get('iqr_B', float('nan')):.2f})")
    print(f"Estatistica W: {resultado['estatistica_w']:.4f}")
    print(f"p-valor: {resultado['p_valor']:.4f}")
    print(f"r de Rosenthal (tamanho de efeito): {resultado['r_rosenthal']:.4f}")
    alfa = 0.05
    if resultado["p_valor"] < alfa:
        print(f"=> p < {alfa}: rejeita H0 (diferenca estatisticamente significativa)")
    else:
        print(f"=> p >= {alfa}: nao rejeita H0 (sem evidencia estatistica suficiente)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--log", required=True, help="CSV consolidado dos trials")
    args = parser.parse_args()

    df = carregar_dados(args.log)

    print("Trials carregados:")
    print(df[["participante", "kata", "tratamento", "T_TTG_min", "censurado", "N_total", "N_pass", "SR_test_pct"]].to_string(index=False))

    pares_ttg = preparar_pares_por_kata(df, "T_TTG_min")
    resultado_rq1 = rodar_wilcoxon(pares_ttg, alternativa="less")
    imprimir_resultado(
        "RQ1 - Produtividade Temporal (Time-to-Green)",
        (
            "Mediana(T_TTG, IA) >= Mediana(T_TTG, Manual)",
            "Mediana(T_TTG, IA) <  Mediana(T_TTG, Manual)",
        ),
        resultado_rq1,
    )

    pares_sr = preparar_pares_por_kata(df, "SR_test_pct")
    resultado_rq2 = rodar_wilcoxon(pares_sr, alternativa="greater")
    imprimir_resultado(
        "RQ2 - Qualidade Funcional (Taxa de Sucesso nos Testes)",
        (
            "Mediana(SR, IA) <= Mediana(SR, Manual)",
            "Mediana(SR, IA) >  Mediana(SR, Manual)",
        ),
        resultado_rq2,
    )


if __name__ == "__main__":
    main()
