#!/usr/bin/env python3
"""Consolidacao e Analise Estatistica das Metricas Estaticas (RQ3).

Issue: [Lab02S03] Consolidacao das Metricas Estaticas: RQ3

Analisa a qualidade estrutural do codigo gerado no experimento (Tratamento A vs B):
  - Complexidade Ciclomatica de McCabe (cc)
  - Linhas de codigo (SLOC e LOC) como metrica de controle/normalizacao
  - Indice de Manutenibilidade (MI)

Executa:
  1. Estatistica descritiva robusta (Mediana, IQR, Q1, Q3, Media, DP, Min, Max)
  2. Deteccao de outliers pelo metodo de Tukey (1.5 * IQR)
  3. Razao e densidade de complexidade (CC / SLOC)
  4. Teste inferencial de Wilcoxon Signed-Rank pareado por kata (bilateral)
  5. Tamanho de efeito (r de Rosenthal e Cliff's Delta)

Uso:
  python scripts/analise_rq3_metricas_estaticas.py
  python scripts/analise_rq3_metricas_estaticas.py --dados data/metricas_estaticas.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


METRICAS_ALVO = [
    ("complexidade_media", "Complexidade Ciclomatica Media (McCabe)"),
    ("sloc", "Linhas de Codigo Fonte Executavel (SLOC)"),
    ("loc", "Linhas de Codigo Totais (LOC)"),
    ("indice_manutenibilidade", "Indice de Manutenibilidade (MI)"),
]


def calcular_estatisticas_descritivas(df: pd.DataFrame, coluna: str) -> dict:
    """Calcula estatisticas descritivas e identifica outliers via IQR."""
    serie = df[coluna].dropna()
    q1 = float(serie.quantile(0.25))
    q3 = float(serie.quantile(0.75))
    iqr = q3 - q1
    mediana = float(serie.median())
    media = float(serie.mean())
    std = float(serie.std(ddof=1)) if len(serie) > 1 else 0.0
    v_min = float(serie.min())
    v_max = float(serie.max())

    limite_inf = q1 - 1.5 * iqr
    limite_sup = q3 + 1.5 * iqr
    outliers = serie[(serie < limite_inf) | (serie > limite_sup)].tolist()

    return {
        "n": len(serie),
        "mediana": round(mediana, 2),
        "q1": round(q1, 2),
        "q3": round(q3, 2),
        "iqr": round(iqr, 2),
        "media": round(media, 2),
        "desvio_padrao": round(std, 2),
        "minimo": round(v_min, 2),
        "maximo": round(v_max, 2),
        "limite_inf_iqr": round(limite_inf, 2),
        "limite_sup_iqr": round(limite_sup, 2),
        "outliers_count": len(outliers),
        "outliers": outliers,
    }


def calcular_cliffs_delta(x: list[float] | np.ndarray, y: list[float] | np.ndarray) -> float:
    """Calcula o tamanho de efeito Cliff's Delta para comparacao de duas amostras."""
    n_x = len(x)
    n_y = len(y)
    if n_x == 0 or n_y == 0:
        return float("nan")

    maiores = 0
    menores = 0
    for val_x in x:
        for val_y in y:
            if val_x > val_y:
                maiores += 1
            elif val_x < val_y:
                menores += 1

    return (maiores - menores) / (n_x * n_y)


def executar_analise_rq3(caminho_dados: Path, pasta_saida: Path) -> None:
    pasta_saida.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(caminho_dados)

    df["tratamento"] = df["tratamento"].astype(str).str.upper().str.strip()

    print("=" * 80)
    print("CONSOLIDACAO E ANALISE ESTATISTICA DE QUALIDADE ESTRUTURAL — RQ3")
    print(f"Dataset de entrada: {caminho_dados} (Total de observacoes: {len(df)})")
    print("=" * 80)

    # 1. Tabela Descritiva Consolidada
    linhas_descritivas = []
    print("\n--- 1. ESTATISTICA DESCRITIVA (TRATAMENTO A vs B) ---")
    for coluna, rotulo in METRICAS_ALVO:
        for trat, trat_nome in [("A", "Manual (A)"), ("B", "Com IA (B)")]:
            sub = df[df["tratamento"] == trat]
            est = calcular_estatisticas_descritivas(sub, coluna)
            linhas_descritivas.append({
                "metrica": rotulo,
                "coluna_codigo": coluna,
                "tratamento": trat,
                "tratamento_nome": trat_nome,
                **est,
            })

    df_desc = pd.DataFrame(linhas_descritivas)
    tabela_resumo = df_desc[[
        "metrica", "tratamento_nome", "n", "mediana", "iqr", "media", "desvio_padrao", "minimo", "maximo", "outliers_count"
    ]]
    print(tabela_resumo.to_string(index=False))

    # 2. Densidade de Complexidade (Normalizacao CC / SLOC)
    df["densidade_cc_sloc"] = df["complexidade_media"] / df["sloc"]
    print("\n--- 2. NORMALIZACAO DE COMPLEXIDADE POR LINHA (CC / SLOC) ---")
    for trat, nome in [("A", "Manual (A)"), ("B", "Com IA (B)")]:
        sub = df[df["tratamento"] == trat]
        est_dens = calcular_estatisticas_descritivas(sub, "densidade_cc_sloc")
        print(f"{nome:15s} | Mediana: {est_dens['mediana']:.3f} | IQR: {est_dens['iqr']:.3f} | Media: {est_dens['media']:.3f} (+/- {est_dens['desvio_padrao']:.3f})")

    # 3. Analise Inferencial Pareada por Kata (Wilcoxon Signed-Rank Test)
    print("\n--- 3. ANALISE INFERENCIAL PAREADA POR KATA (TESTE DE WILCOXON) ---")
    linhas_inferenciais = []
    pares_dict = {"kata": ["K1", "K2", "K3", "K4"]}

    for coluna, rotulo in METRICAS_ALVO:
        piv = df.groupby(["kata", "tratamento"])[coluna].median().unstack("tratamento")
        if "A" not in piv.columns or "B" not in piv.columns:
            continue

        pares = piv.dropna(subset=["A", "B"])
        a_vals = pares["A"].values
        b_vals = pares["B"].values
        diffs = b_vals - a_vals

        pares_dict[f"{coluna}_Manual_A"] = a_vals
        pares_dict[f"{coluna}_ComIA_B"] = b_vals
        pares_dict[f"{coluna}_Diff_B_menos_A"] = diffs

        # Wilcoxon bicaudal
        diffs_nao_nulas = diffs[diffs != 0]
        n_pares_efetivos = len(diffs_nao_nulas)

        if n_pares_efetivos > 0:
            res_w = stats.wilcoxon(b_vals, a_vals, alternative="two-sided")
            stat_w = float(res_w.statistic)
            p_val = float(res_w.pvalue)

            # Calculo do Z e r de Rosenthal
            # Para N pequeno, stats.wilcoxon pode nao expor Z assintotico diretamente
            # r = |Z| / sqrt(N_pares)
            z_score = stats.norm.ppf(1.0 - p_val / 2.0) if p_val < 1.0 else 0.0
            r_rosenthal = abs(z_score) / np.sqrt(len(b_vals)) if len(b_vals) > 0 else 0.0
        else:
            stat_w = float("nan")
            p_val = 1.0
            r_rosenthal = 0.0

        # Cliff's Delta entre as amostras completas do tratamento
        vals_a_totais = df[df["tratamento"] == "A"][coluna].values
        vals_b_totais = df[df["tratamento"] == "B"][coluna].values
        cliffs_d = calcular_cliffs_delta(vals_b_totais, vals_a_totais)

        linhas_inferenciais.append({
            "metrica": rotulo,
            "coluna": coluna,
            "n_pares_katas": len(b_vals),
            "mediana_manual_A": round(float(np.median(a_vals)), 2),
            "mediana_com_ia_B": round(float(np.median(b_vals)), 2),
            "diferenca_medianas (B - A)": round(float(np.median(b_vals) - np.median(a_vals)), 2),
            "estatistica_W": stat_w,
            "p_valor_bicaudal": round(p_val, 4),
            "r_rosenthal": round(r_rosenthal, 4),
            "cliffs_delta": round(cliffs_d, 4),
            "conclusao_h0 (alpha=0.05)": "Nao rejeita H0" if p_val >= 0.05 else "Rejeita H0",
        })

    df_inf = pd.DataFrame(linhas_inferenciais)
    print(df_inf[[
        "metrica", "mediana_manual_A", "mediana_com_ia_B", "diferenca_medianas (B - A)",
        "estatistica_W", "p_valor_bicaudal", "cliffs_delta", "conclusao_h0 (alpha=0.05)"
    ]].to_string(index=False))

    # Exportar relatorios em CSV
    caminho_resumo = pasta_saida / "resumo_estatistico_rq3.csv"
    caminho_pares = pasta_saida / "pares_rq3_katas.csv"

    df_desc.to_csv(caminho_resumo, index=False, encoding="utf-8")
    pd.DataFrame(pares_dict).to_csv(caminho_pares, index=False, encoding="utf-8")

    print(f"\n[OK] Arquivo com resumo descritivo salvo em: {caminho_resumo}")
    print(f"[OK] Arquivo com pares por kata salvo em: {caminho_pares}")
    print("=" * 80)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analise Estatistica RQ3 - Qualidade Estrutural")
    parser.add_argument("--dados", default="data/metricas_estaticas.csv", help="Caminho do CSV de metricas estaticas")
    parser.add_argument("--saida", default="data", help="Pasta de saida para os CSVs consolidados")
    args = parser.parse_args()

    executar_analise_rq3(Path(args.dados), Path(args.saida))


if __name__ == "__main__":
    main()
