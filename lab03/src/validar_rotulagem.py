"""Validador de arquivos de rotulagem da amostra-ouro (LAB03S02).

Confere estrutura, completude e vocabulário controlado, para que o arquivo possa
entrar direto no cálculo do Fleiss' kappa.

Uso:
    python -m lab03.src.validar_rotulagem lab03/data/rotulagem_amostra_ouro_kayque.csv \
        --base lab03/data/amostra_ouro_base.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

import pandas as pd

COLUNAS_BASE = [
    "repo_id", "full_name", "repo_url", "primary_language", "release_num",
    "tag_name", "release_name", "published_at", "release_url",
]
COLUNAS_ROTULO = ["tipo_projeto", "entrega_real", "is_corretiva", "justificativa"]

TIPOS = {"biblioteca/framework", "aplicação/serviço", "CLI", "outro"}
ENTREGAS = {"sim", "não", "incerto"}
CORRETIVAS = {"sim", "não"}

N_REPOS = 60
N_RELEASES = 5


def validar(df: pd.DataFrame, base: Optional[pd.DataFrame] = None) -> List[str]:
    """Retorna a lista de erros encontrados (vazia se o arquivo está válido)."""
    erros: List[str] = []

    faltando = [c for c in COLUNAS_BASE + COLUNAS_ROTULO if c not in df.columns]
    if faltando:
        return [f"Colunas ausentes: {faltando}"]

    if len(df) != N_REPOS * N_RELEASES:
        erros.append(f"Esperadas {N_REPOS * N_RELEASES} linhas, encontradas {len(df)}")
    if df["repo_id"].nunique() != N_REPOS:
        erros.append(f"Esperados {N_REPOS} repositórios, encontrados {df['repo_id'].nunique()}")
    if df.duplicated(["repo_id", "release_num"]).any():
        erros.append("Há pares (repo_id, release_num) duplicados")
    por_repo = df.groupby("repo_id")["release_num"].apply(lambda s: sorted(s.tolist()))
    for repo_id, nums in por_repo.items():
        if nums != list(range(1, N_RELEASES + 1)):
            erros.append(f"repo_id {repo_id}: release_num deveria ser 1..{N_RELEASES}, veio {nums}")

    for col, validos in (("tipo_projeto", TIPOS), ("entrega_real", ENTREGAS), ("is_corretiva", CORRETIVAS)):
        serie = df[col].astype("string").str.strip()
        vazias = serie.isna() | (serie == "")
        if vazias.any():
            erros.append(f"{col}: {int(vazias.sum())} linhas vazias (repo_id {sorted(df.loc[vazias, 'repo_id'].unique().tolist())})")
        invalidos = sorted(set(serie[~vazias]) - validos)
        if invalidos:
            erros.append(f"{col}: valores fora do vocabulário {invalidos}; aceitos: {sorted(validos)}")

    # tipo e entrega são atributos do repositório: constantes nas 5 releases
    for col in ("tipo_projeto", "entrega_real"):
        variam = df.groupby("repo_id")[col].nunique()
        variam = variam[variam > 1]
        if len(variam):
            erros.append(f"{col}: valores diferentes dentro do mesmo repositório (repo_id {variam.index.tolist()})")

    # justificativa obrigatória nos casos incertos
    incertos = df[(df["entrega_real"] == "incerto") & (df["justificativa"].astype("string").fillna("").str.strip() == "")]
    if len(incertos):
        erros.append(f"{len(incertos)} linhas com entrega_real='incerto' sem justificativa")

    if base is not None:
        chave = ["repo_id", "release_num", "tag_name", "release_url"]
        a = df[chave].sort_values(chave).reset_index(drop=True)
        b = base[chave].sort_values(chave).reset_index(drop=True)
        if not a.equals(b):
            erros.append("O arquivo não corresponde à mesma amostra da base (repo_id, release_num, tag, URL)")

    return erros


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida um arquivo de rotulagem da amostra-ouro")
    parser.add_argument("arquivo")
    parser.add_argument("--base", default=None, help="CSV base para conferir se a amostra é a mesma")
    args = parser.parse_args()

    df = pd.read_csv(args.arquivo, encoding="utf-8")
    base = pd.read_csv(args.base, encoding="utf-8") if args.base and Path(args.base).exists() else None
    erros = validar(df, base)
    if erros:
        print(f"INVÁLIDO ({len(erros)} problemas):")
        for e in erros:
            print(f" - {e}")
        return 1
    print("OK: rotulagem completa e válida (60 repositórios, 300 releases).")
    return 0


if __name__ == "__main__":
    sys.exit(main())