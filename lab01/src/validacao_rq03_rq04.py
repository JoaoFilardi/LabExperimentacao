"""
Validação de consistência do CSV para RQ03 e RQ04 (Lab01S02 / Issue #7).

RQ03 — total de releases (coluna total_releases)
RQ04 — tempo até a última atualização (coluna dias_ultimo_push)

Uso (a partir da raiz do repositório):
    python lab01/validacao_rq03_rq04.py
"""

from __future__ import annotations

import csv
import math
import statistics
from collections import Counter
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent / "repositorios_1000.csv"
COL_RQ03 = "total_releases"
COL_RQ04 = "dias_ultimo_push"


def _parse_int(valor: str | None):
    if valor is None:
        return None
    texto = valor.strip()
    if texto == "":
        return None
    try:
        return int(texto)
    except ValueError:
        return f"INVALID:{texto!r}"


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
    cerca_inf = q1 - 1.5 * iqr
    cerca_sup = q3 + 1.5 * iqr
    outliers = [v for v in ordenado if v < cerca_inf or v > cerca_sup]
    zeros = sum(1 for v in ordenado if v == 0)
    return {
        "nome": nome,
        "n": n,
        "min": ordenado[0],
        "max": ordenado[-1],
        "media": statistics.mean(ordenado),
        "mediana": mediana,
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "cerca_inf": cerca_inf,
        "cerca_sup": cerca_sup,
        "n_outliers": len(outliers),
        "pct_outliers": 100.0 * len(outliers) / n,
        "n_zeros": zeros,
        "pct_zeros": 100.0 * zeros / n,
        "mais_comuns": Counter(ordenado).most_common(8),
    }


def _imprimir_resumo(resumo: dict) -> None:
    print(f"\n=== {resumo['nome']} ===")
    print(f"n={resumo['n']}  min={resumo['min']}  max={resumo['max']}")
    print(
        f"media={resumo['media']:.2f}  mediana={resumo['mediana']:.1f}  "
        f"Q1={resumo['q1']:.1f}  Q3={resumo['q3']:.1f}  IQR={resumo['iqr']:.1f}"
    )
    print(
        f"cerca IQR: [{resumo['cerca_inf']:.2f}, {resumo['cerca_sup']:.2f}]  "
        f"outliers={resumo['n_outliers']} ({resumo['pct_outliers']:.1f}%)"
    )
    print(f"zeros={resumo['n_zeros']} ({resumo['pct_zeros']:.1f}%)")
    print(f"valores mais frequentes: {resumo['mais_comuns']}")


def validar() -> int:
    if not CSV_PATH.exists():
        print(f"[ERRO] CSV nao encontrado: {CSV_PATH}")
        return 1

    with CSV_PATH.open(encoding="utf-8", newline="") as arquivo:
        linhas = list(csv.DictReader(arquivo))

    print(f"Arquivo: {CSV_PATH.name}")
    print(f"Linhas (repositorios): {len(linhas)}")

    if len(linhas) != 1000:
        print(f"[ALERTA] Esperado 1000 repositorios; obtido {len(linhas)}.")

    nomes = [linha.get("nome", "").strip() for linha in linhas]
    nulos_nome = sum(1 for nome in nomes if not nome)
    duplicados = [nome for nome, qtd in Counter(nomes).items() if nome and qtd > 1]
    print(f"nomes vazios: {nulos_nome}  nomes duplicados: {len(duplicados)}")

    releases: list[tuple[int, str]] = []
    pushes: list[tuple[int, str]] = []
    nulos_rq03 = invalidos_rq03 = negativos_rq03 = 0
    nulos_rq04 = invalidos_rq04 = negativos_rq04 = 0

    for linha in linhas:
        nome = linha.get("nome", "").strip() or "(sem nome)"
        total_releases = _parse_int(linha.get(COL_RQ03))
        dias_push = _parse_int(linha.get(COL_RQ04))

        if total_releases is None:
            nulos_rq03 += 1
        elif isinstance(total_releases, str):
            invalidos_rq03 += 1
        else:
            if total_releases < 0:
                negativos_rq03 += 1
            releases.append((total_releases, nome))

        if dias_push is None:
            nulos_rq04 += 1
        elif isinstance(dias_push, str):
            invalidos_rq04 += 1
        else:
            if dias_push < 0:
                negativos_rq04 += 1
            pushes.append((dias_push, nome))

    print("\n--- Valores ausentes / invalidos ---")
    print(
        f"RQ03 ({COL_RQ03}): nulos={nulos_rq03}  nao-inteiros={invalidos_rq03}  "
        f"negativos={negativos_rq03}"
    )
    print(
        f"RQ04 ({COL_RQ04}): nulos={nulos_rq04}  nao-inteiros={invalidos_rq04}  "
        f"negativos={negativos_rq04}"
    )

    if not releases or not pushes:
        print("[ERRO] Nao ha valores numericos suficientes para resumir.")
        return 1

    resumo_rq03 = _resumir("RQ03 total_releases", [v for v, _ in releases])
    resumo_rq04 = _resumir("RQ04 dias_ultimo_push", [v for v, _ in pushes])
    _imprimir_resumo(resumo_rq03)
    _imprimir_resumo(resumo_rq04)

    teto_1000 = [(v, nome) for v, nome in releases if v == 1000]
    print(f"\n--- Possivel teto da API em total_releases == 1000 ---")
    print(f"repositorios com exatamente 1000 releases: {len(teto_1000)}")
    if teto_1000:
        print("exemplos:", ", ".join(nome for _, nome in teto_1000[:8]))

    print("\n--- Maiores totais de releases ---")
    for valor, nome in sorted(releases, reverse=True)[:10]:
        print(f"  {valor:5d}  {nome}")

    print("\n--- Repositorios com atualizacao mais antiga (dias_ultimo_push) ---")
    for valor, nome in sorted(pushes, reverse=True)[:10]:
        print(f"  {valor:5d}  {nome}")

    print("\nValidacao concluida.")
    return 0


if __name__ == "__main__":
    raise SystemExit(validar())
