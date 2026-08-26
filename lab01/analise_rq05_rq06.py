"""Gera estatisticas e graficos da amostra para RQ05 e RQ06.

Os dados sao lidos exclusivamente de repositorios_1000.csv.

Uso (a partir da raiz do repositorio):
    python lab01/analise_rq05_rq06.py
"""

from __future__ import annotations

import csv
import math
import statistics
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
from validacao_rq05_rq06 import calcular_quartis

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "repositorios_1000.csv"
OUTPUT_DIR = BASE_DIR / "graficos_rq05_rq06"


def resumir_razoes(razoes: list[float]) -> dict[str, float]:
    ordenadas = sorted(razoes)
    q1, mediana, q3 = calcular_quartis(ordenadas)
    iqr = q3 - q1
    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr
    outliers = [valor for valor in ordenadas if valor < limite_inferior or valor > limite_superior]
    return {
        "n": len(ordenadas),
        "min": ordenadas[0],
        "max": ordenadas[-1],
        "media": statistics.mean(ordenadas),
        "q1": q1,
        "mediana": mediana,
        "q3": q3,
        "iqr": iqr,
        "limite_inferior": limite_inferior,
        "limite_superior": limite_superior,
        "outliers": len(outliers),
        "zeros": sum(valor == 0 for valor in ordenadas),
        "cem": sum(valor == 100 for valor in ordenadas),
    }


def carregar_dados() -> tuple[list[str], list[float], int, int, int]:
    linguagens: list[str] = []
    razoes: list[float] = []
    issues_sem_total = 0
    valores_invalidos = 0
    razoes_inconsistentes = 0

    with CSV_PATH.open(encoding="utf-8", newline="") as arquivo:
        for numero_linha, linha in enumerate(csv.DictReader(arquivo), start=2):
            linguagem = (linha.get("linguagem_primaria") or "").strip()
            valor_total = (linha.get("issues_total") or "").strip()
            valor_fechadas = (linha.get("issues_fechadas") or "").strip()
            valor_razao = (linha.get("razao_issues_fechadas") or "").strip()
            if not linguagem or not valor_total or not valor_fechadas or not valor_razao:
                valores_invalidos += 1
                continue
            try:
                total = int(valor_total)
                fechadas = int(valor_fechadas)
                razao = float(valor_razao)
            except ValueError:
                valores_invalidos += 1
                continue
            if total < 0 or fechadas < 0 or fechadas > total or not 0 <= razao <= 100:
                valores_invalidos += 1
                continue

            razao_calculada = (fechadas / total) * 100 if total else 0.0
            if not math.isclose(razao, razao_calculada, abs_tol=0.005):
                razoes_inconsistentes += 1
            if total == 0:
                issues_sem_total += 1
            linguagens.append(linguagem)
            razoes.append(razao)

    if not razoes:
        raise ValueError("O CSV nao possui registros validos para RQ05/RQ06")
    return linguagens, razoes, issues_sem_total, valores_invalidos, razoes_inconsistentes


def salvar_graficos(linguagens: list[str], razoes: list[float]) -> None:
    contagens = Counter(linguagens)
    principais = contagens.most_common(10)
    nomes = [nome for nome, _ in principais]
    valores = [valor for _, valor in principais]

    figura, eixo = plt.subplots(figsize=(10, 5))
    eixo.bar(nomes, valores, color="#176b87")
    eixo.set_title("RQ05: linguagens primarias mais frequentes")
    eixo.set_xlabel("Linguagem primaria")
    eixo.set_ylabel("Quantidade de repositorios")
    eixo.tick_params(axis="x", rotation=35)
    eixo.grid(axis="y", alpha=0.25)
    figura.tight_layout()
    figura.savefig(OUTPUT_DIR / "frequencia_linguagens_rq05.png", dpi=160)
    plt.close(figura)

    figura, eixo = plt.subplots(figsize=(9, 5))
    eixo.hist(razoes, bins=20, range=(0, 100), color="#d1495b", edgecolor="white")
    eixo.set_title("RQ06: distribuicao da razao de issues fechadas")
    eixo.set_xlabel("Issues fechadas (%)")
    eixo.set_ylabel("Quantidade de repositorios")
    eixo.grid(axis="y", alpha=0.25)
    figura.tight_layout()
    figura.savefig(OUTPUT_DIR / "histograma_rq06.png", dpi=160)
    plt.close(figura)

    figura, eixo = plt.subplots(figsize=(7, 5))
    eixo.boxplot(razoes, patch_artist=True, boxprops={"facecolor": "#74b49b"})
    eixo.set_title("RQ06: boxplot da razao de issues fechadas")
    eixo.set_ylabel("Issues fechadas (%)")
    eixo.set_ylim(0, 100)
    eixo.grid(axis="y", alpha=0.25)
    figura.tight_layout()
    figura.savefig(OUTPUT_DIR / "boxplot_rq06.png", dpi=160)
    plt.close(figura)

    limites = [0, 25, 50, 75, 100.01]
    rotulos = ["0-24%", "25-49%", "50-74%", "75-100%"]
    faixas = [sum(inicio <= valor < fim for valor in razoes) for inicio, fim in zip(limites, limites[1:])]
    figura, eixo = plt.subplots(figsize=(8, 5))
    eixo.bar(rotulos, faixas, color="#f2a65a")
    eixo.set_title("RQ06: repositorios por faixa de issues fechadas")
    eixo.set_xlabel("Razao de issues fechadas")
    eixo.set_ylabel("Quantidade de repositorios")
    eixo.grid(axis="y", alpha=0.25)
    for indice, quantidade in enumerate(faixas):
        eixo.text(indice, quantidade + 8, str(quantidade), ha="center")
    figura.tight_layout()
    figura.savefig(OUTPUT_DIR / "faixas_rq06.png", dpi=160)
    plt.close(figura)


def main() -> int:
    if not CSV_PATH.exists():
        print(f"[ERRO] CSV nao encontrado: {CSV_PATH}")
        return 1

    try:
        linguagens, razoes, issues_sem_total, invalidos, inconsistentes = carregar_dados()
    except ValueError as erro:
        print(f"[ERRO] {erro}")
        return 1

    resumo = resumir_razoes(razoes)
    contagens = Counter(linguagens)
    sem_linguagem = contagens.get("N/A", 0)
    distintas = len(contagens) - (1 if sem_linguagem else 0)

    print(f"Registros validos: {len(razoes)}")
    print(f"Valores invalidos: {invalidos}")
    print(f"RQ05 - linguagens distintas (sem N/A): {distintas}")
    print(f"RQ05 - N/A: {sem_linguagem} ({100 * sem_linguagem / len(razoes):.2f}%)")
    print("RQ05 - top 10:")
    for linguagem, quantidade in contagens.most_common(10):
        print(f"  {linguagem}: {quantidade} ({100 * quantidade / len(razoes):.2f}%)")
    print("RQ06 - " + "  ".join(f"{chave}={valor:.2f}" for chave, valor in resumo.items()))
    print(f"RQ06 - issues_total igual a zero: {issues_sem_total}")
    print(f"RQ06 - razoes incompatíveis com os totais: {inconsistentes}")

    OUTPUT_DIR.mkdir(exist_ok=True)
    salvar_graficos(linguagens, razoes)
    print(f"Graficos salvos em: {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
