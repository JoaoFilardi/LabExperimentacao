#!/usr/bin/env python3
"""Script de coleta de metricas estaticas (RQ3) do Lab02.

Issue: [Lab02S01] Scripts de Analise Estatica (Radon/CK) #14

Coleta, para cada arquivo de kata resolvido em um trial:
  - Complexidade ciclomatica media por funcao (Radon `cc`)
  - Linhas de codigo: LOC total e SLOC (Radon `raw`) - metrica de controle
  - Indice de Manutenibilidade (Radon `mi`) - metrica opcional/aprofundamento

E acrescenta uma linha por trial em um CSV consolidado
(`data/metricas_estaticas.csv`), que depois alimenta o dashboard (Lab02S03).

Requisitos:
    pip install radon

Uso individual (um trial):
    python scripts/analise_estatica.py single \
        --arquivo katas/kata_01_intervalos.py \
        --participante joao \
        --kata K1 \
        --tratamento A

Uso em lote (todos os arquivos finais de uma pasta de trials):
    python scripts/analise_estatica.py lote --pasta trials/ \
        --manifest trials/manifest.csv

    O manifest.csv deve ter as colunas:
        arquivo,participante,kata,tratamento
    com o caminho (relativo a --pasta) de cada arquivo final resolvido.

Duplicacao de codigo (RQ3, opcional): como cada kata e um arquivo unico e
pequeno, a duplicacao *intra-arquivo* tende a ser pouco informativa. Se o
grupo quiser essa metrica mesmo assim, ver a nota e o script auxiliar
`duplicacao_jscpd.md` (comentarios no final deste arquivo).
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path

try:
    from radon.complexity import cc_visit
    from radon.raw import analyze as raw_analyze
    from radon.metrics import mi_visit
except ImportError:  # pragma: no cover
    print(
        "ERRO: o pacote 'radon' nao esta instalado.\n"
        "Instale com: pip install radon",
        file=sys.stderr,
    )
    sys.exit(1)


CSV_COLUNAS = [
    "timestamp_utc",
    "participante",
    "kata",
    "tratamento",
    "arquivo",
    "num_funcoes",
    "complexidade_media",
    "complexidade_maxima",
    "loc",
    "sloc",
    "linhas_em_branco",
    "indice_manutenibilidade",
]


@dataclass
class MetricasArquivo:
    num_funcoes: int
    complexidade_media: float
    complexidade_maxima: int
    loc: int
    sloc: int
    linhas_em_branco: int
    indice_manutenibilidade: float


def calcular_metricas(caminho_arquivo: Path) -> MetricasArquivo:
    """Calcula complexidade ciclomatica, LOC/SLOC e MI de um arquivo .py."""
    codigo = caminho_arquivo.read_text(encoding="utf-8")

    blocos = cc_visit(codigo)
    complexidades = [b.complexity for b in blocos]
    num_funcoes = len(complexidades)
    complexidade_media = (
        sum(complexidades) / num_funcoes if num_funcoes else 0.0
    )
    complexidade_maxima = max(complexidades) if complexidades else 0

    bruto = raw_analyze(codigo)

    mi = mi_visit(codigo, multi=True)

    return MetricasArquivo(
        num_funcoes=num_funcoes,
        complexidade_media=round(complexidade_media, 2),
        complexidade_maxima=complexidade_maxima,
        loc=bruto.loc,
        sloc=bruto.sloc,
        linhas_em_branco=bruto.blank,
        indice_manutenibilidade=round(mi, 2),
    )


def garantir_csv(caminho_csv: Path) -> None:
    caminho_csv.parent.mkdir(parents=True, exist_ok=True)
    if not caminho_csv.exists():
        with caminho_csv.open("w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=CSV_COLUNAS).writeheader()


def registrar_trial(
    caminho_csv: Path,
    arquivo: Path,
    participante: str,
    kata: str,
    tratamento: str,
) -> dict:
    if tratamento.upper() not in {"A", "B"}:
        raise ValueError("tratamento deve ser 'A' (manual) ou 'B' (com IA)")

    metricas = calcular_metricas(arquivo)
    linha = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "participante": participante,
        "kata": kata,
        "tratamento": tratamento.upper(),
        "arquivo": str(arquivo),
        **asdict(metricas),
    }

    garantir_csv(caminho_csv)
    with caminho_csv.open("a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=CSV_COLUNAS).writerow(linha)

    return linha


def comando_single(args: argparse.Namespace) -> None:
    linha = registrar_trial(
        caminho_csv=Path(args.saida),
        arquivo=Path(args.arquivo),
        participante=args.participante,
        kata=args.kata,
        tratamento=args.tratamento,
    )
    print("Registrado em", args.saida)
    for chave, valor in linha.items():
        print(f"  {chave}: {valor}")


def comando_lote(args: argparse.Namespace) -> None:
    pasta = Path(args.pasta)
    manifest = Path(args.manifest)
    caminho_csv = Path(args.saida)

    with manifest.open(newline="", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        total = 0
        for row in leitor:
            arquivo = pasta / row["arquivo"]
            if not arquivo.exists():
                print(f"AVISO: arquivo nao encontrado, pulando: {arquivo}", file=sys.stderr)
                continue
            registrar_trial(
                caminho_csv=caminho_csv,
                arquivo=arquivo,
                participante=row["participante"],
                kata=row["kata"],
                tratamento=row["tratamento"],
            )
            total += 1
    print(f"{total} trial(s) registrados em {caminho_csv}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="comando", required=True)

    p_single = subparsers.add_parser("single", help="analisa um unico arquivo/trial")
    p_single.add_argument("--arquivo", required=True, help="caminho do .py do trial")
    p_single.add_argument("--participante", required=True)
    p_single.add_argument("--kata", required=True, help="ex.: K1, K2, K3, K4")
    p_single.add_argument("--tratamento", required=True, choices=["A", "B", "a", "b"])
    p_single.add_argument("--saida", default="data/metricas_estaticas.csv")
    p_single.set_defaults(func=comando_single)

    p_lote = subparsers.add_parser("lote", help="analisa varios trials via manifest.csv")
    p_lote.add_argument("--pasta", required=True, help="pasta base contendo os arquivos dos trials")
    p_lote.add_argument("--manifest", required=True, help="csv com colunas: arquivo,participante,kata,tratamento")
    p_lote.add_argument("--saida", default="data/metricas_estaticas.csv")
    p_lote.set_defaults(func=comando_lote)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
