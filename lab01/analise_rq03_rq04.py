"""Gera estatisticas e graficos da amostra para RQ03 e RQ04.

Os dados sao lidos exclusivamente de repositorios_1000.csv. O script nao
faz novas requisicoes ao GitHub.

Uso (a partir da raiz do repositorio):
    python lab01/analise_rq03_rq04.py
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

from validacao_rq03_rq04 import _resumir


BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "repositorios_1000.csv"
OUTPUT_DIR = BASE_DIR / "graficos_rq03_rq04"


def carregar_metricas() -> tuple[list[int], list[int]]:
    """Carrega as duas colunas da analise e rejeita dados invalidos."""
    releases: list[int] = []
    dias_push: list[int] = []

    with CSV_PATH.open(encoding="utf-8", newline="") as arquivo:
        for numero_linha, linha in enumerate(csv.DictReader(arquivo), start=2):
            try:
                release = int(linha["total_releases"])
                dias = int(linha["dias_ultimo_push"])
            except (KeyError, TypeError, ValueError) as erro:
                raise ValueError(
                    f"Dados invalidos na linha {numero_linha} do CSV"
                ) from erro
            if release < 0 or dias < 0:
                raise ValueError(f"Valor negativo na linha {numero_linha} do CSV")
            releases.append(release)
            dias_push.append(dias)

    if not releases:
        raise ValueError("O CSV nao possui repositorios")
    return releases, dias_push


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


def salvar_boxplot(releases: list[int], dias_push: list[int]) -> None:
    figura, eixos = plt.subplots(1, 2, figsize=(10, 5))
    eixos[0].boxplot(releases, orientation="vertical", patch_artist=True,
                     boxprops={"facecolor": "#f2a65a"})
    eixos[0].set_title("RQ03")
    eixos[0].set_ylabel("Total de releases")
    eixos[1].boxplot(dias_push, orientation="vertical", patch_artist=True,
                     boxprops={"facecolor": "#74b49b"})
    eixos[1].set_title("RQ04")
    eixos[1].set_ylabel("Dias desde o ultimo push")
    for eixo in eixos:
        eixo.grid(axis="y", alpha=0.25)
    figura.suptitle("Boxplots das metricas")
    figura.tight_layout()
    figura.savefig(OUTPUT_DIR / "boxplots_rq03_rq04.png", dpi=160)
    plt.close(figura)


def salvar_faixas_rq04(dias_push: list[int]) -> None:
    faixas = [0, 1, 8, 31, 91, 366, 731, float("inf")]
    rotulos = ["0", "1-7", "8-30", "31-90", "91-365", "1-2 anos", ">2 anos"]
    quantidades = [
        sum(inicio <= valor < fim for valor in dias_push)
        for inicio, fim in zip(faixas, faixas[1:])
    ]

    figura, eixo = plt.subplots(figsize=(9, 5))
    eixo.bar(rotulos, quantidades, color="#d1495b")
    eixo.set_title("RQ04: repositorios por faixa de tempo desde o ultimo push")
    eixo.set_xlabel("Dias desde o ultimo push")
    eixo.set_ylabel("Quantidade de repositorios")
    eixo.grid(axis="y", alpha=0.25)
    for indice, quantidade in enumerate(quantidades):
        eixo.text(indice, quantidade + 8, str(quantidade), ha="center")
    figura.tight_layout()
    figura.savefig(OUTPUT_DIR / "faixas_rq04.png", dpi=160)
    plt.close(figura)


def main() -> int:
    if not CSV_PATH.exists():
        print(f"[ERRO] CSV nao encontrado: {CSV_PATH}")
        return 1

    try:
        releases, dias_push = carregar_metricas()
    except ValueError as erro:
        print(f"[ERRO] {erro}")
        return 1

    OUTPUT_DIR.mkdir(exist_ok=True)
    resumo_rq03 = _resumir("RQ03 total_releases", releases)
    resumo_rq04 = _resumir("RQ04 dias_ultimo_push", dias_push)

    for resumo in (resumo_rq03, resumo_rq04):
        print(
            f"{resumo['nome']}: n={resumo['n']}, media={resumo['media']:.2f}, "
            f"mediana={resumo['mediana']:.1f}, Q1={resumo['q1']:.1f}, "
            f"Q3={resumo['q3']:.1f}, IQR={resumo['iqr']:.1f}"
        )

    salvar_histograma(releases, "RQ03: distribuicao do total de releases",
                      "Total de releases", "histograma_rq03.png")
    salvar_histograma(dias_push, "RQ04: distribuicao dos dias desde o ultimo push",
                      "Dias desde o ultimo push", "histograma_rq04.png")
    salvar_boxplot(releases, dias_push)
    salvar_faixas_rq04(dias_push)
    print(f"Graficos salvos em: {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())