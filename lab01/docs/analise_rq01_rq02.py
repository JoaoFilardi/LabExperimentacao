"""Gera estatisticas e graficos da amostra para RQ01 e RQ02.

Os dados sao lidos exclusivamente de repositorios_1000.csv.

Uso (a partir da raiz do repositorio):
    python lab01/analise_rq01_rq02.py
"""

from __future__ import annotations

import csv
import math
import statistics
from pathlib import Path

import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "repositorios_1000.csv"
OUTPUT_DIR = BASE_DIR / "graficos_rq01_rq02"


def _percentil(ordenado: list[int], p: float) -> float:
    if not ordenado:
        return float("nan")
    k = (len(ordenado) - 1) * (p / 100.0)
    baixo = math.floor(k)
    alto = math.ceil(k)
    if baixo == alto:
        return float(ordenado[int(k)])
    return ordenado[baixo] * (alto - k) + ordenado[alto] * (k - baixo)


def _resumir(nome: str, valores: list[int]) -> dict:
    ordenado = sorted(valores)
    n = len(ordenado)
    q1 = _percentil(ordenado, 25)
    mediana = _percentil(ordenado, 50)
    q3 = _percentil(ordenado, 75)
    iqr = q3 - q1
    return {
        "nome": nome,
        "n": n,
        "media": statistics.mean(ordenado),
        "mediana": mediana,
        "q1": q1,
        "q3": q3,
        "iqr": iqr
    }


def carregar_metricas() -> tuple[list[int], list[int]]:
    idades: list[int] = []
    prs: list[int] = []

    with CSV_PATH.open(encoding="utf-8", newline="") as arquivo:
        for numero_linha, linha in enumerate(csv.DictReader(arquivo), start=2):
            try:
                idade = int(linha["idade_total_dias"])
                pr = int(linha["prs_merged"])
            except (KeyError, TypeError, ValueError) as erro:
                raise ValueError(
                    f"Dados invalidos na linha {numero_linha} do CSV"
                ) from erro
            if idade < 0 or pr < 0:
                raise ValueError(f"Valor negativo na linha {numero_linha} do CSV")
            idades.append(idade)
            prs.append(pr)

    if not idades:
        raise ValueError("O CSV nao possui repositorios")
    return idades, prs


def salvar_histograma(valores: list[int], titulo: str, eixo_x: str, nome: str) -> None:
    figura, eixo = plt.subplots(figsize=(9, 5))
    eixo.hist(valores, bins=30, color="#176b87", edgecolor="white")
    eixo.set_title(titulo)
    eixo.set_xlabel(eixo_x)
    eixo.set_ylabel("Quantidade de repositorios")
    eixo.grid(axis="y", alpha=0.25)
    figura.tight_layout()
    figura.savefig(OUTPUT_DIR / nome, dpi=160)
    plt.close(figura)


def salvar_boxplot(idades: list[int], prs: list[int]) -> None:
    figura, eixos = plt.subplots(1, 2, figsize=(10, 5))
    
    eixos[0].boxplot(idades, orientation="vertical", patch_artist=True,
                     boxprops={"facecolor": "#f2a65a"})
    eixos[0].set_title("RQ01: Idade do Repositorio (Dias)")
    eixos[0].set_ylabel("Dias de idade")
    
    eixos[1].boxplot(prs, orientation="vertical", patch_artist=True,
                     boxprops={"facecolor": "#74b49b"})
    eixos[1].set_title("RQ02: PRs Merged")
    eixos[1].set_ylabel("Total de PRs Merged")
    
    for eixo in eixos:
        eixo.grid(axis="y", alpha=0.25)
        
    figura.suptitle("Boxplots das metricas")
    figura.tight_layout()
    figura.savefig(OUTPUT_DIR / "boxplots_rq01_rq02.png", dpi=160)
    plt.close(figura)


def salvar_faixas_rq01(idades: list[int]) -> None:
    idades_anos = [d // 365 for d in idades]
    faixas = [0, 1, 3, 6, 9, 12, 15, float("inf")]
    rotulos = ["<1 ano", "1-2 anos", "3-5 anos", "6-8 anos", "9-11 anos", "12-14 anos", ">=15 anos"]
    quantidades = [
        sum(inicio <= valor < fim for valor in idades_anos)
        for inicio, fim in zip(faixas, faixas[1:])
    ]

    figura, eixo = plt.subplots(figsize=(9, 5))
    eixo.bar(rotulos, quantidades, color="#d1495b")
    eixo.set_title("RQ01: Repositorios por faixa de idade em anos")
    eixo.set_xlabel("Faixa de Idade")
    eixo.set_ylabel("Quantidade de repositorios")
    eixo.grid(axis="y", alpha=0.25)
    for indice, quantidade in enumerate(quantidades):
        eixo.text(indice, quantidade + 8, str(quantidade), ha="center")
    figura.tight_layout()
    figura.savefig(OUTPUT_DIR / "faixas_rq01.png", dpi=160)
    plt.close(figura)


def main() -> int:
    if not CSV_PATH.exists():
        print(f"[ERRO] CSV nao encontrado: {CSV_PATH}")
        return 1

    try:
        idades, prs = carregar_metricas()
    except ValueError as erro:
        print(f"[ERRO] {erro}")
        return 1

    OUTPUT_DIR.mkdir(exist_ok=True)
    resumo_rq01 = _resumir("RQ01 idade_total_dias", idades)
    resumo_rq02 = _resumir("RQ02 prs_merged", prs)

    for resumo in (resumo_rq01, resumo_rq02):
        print(
            f"{resumo['nome']}: n={resumo['n']}, media={resumo['media']:.2f}, "
            f"mediana={resumo['mediana']:.1f}, Q1={resumo['q1']:.1f}, "
            f"Q3={resumo['q3']:.1f}, IQR={resumo['iqr']:.1f}"
        )

    salvar_histograma(idades, "RQ01: distribuicao da idade do repositorio",
                      "Idade (dias)", "histograma_rq01.png")
    salvar_histograma(prs, "RQ02: distribuicao do total de PRs Merged",
                      "Total de PRs Merged", "histograma_rq02.png")
    salvar_boxplot(idades, prs)
    salvar_faixas_rq01(idades)
    print(f"Graficos salvos em: {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
