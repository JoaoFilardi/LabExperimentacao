"""Concordância entre avaliadores (Fleiss' kappa) da amostra-ouro (LAB03S02, issue #34).

Usa `aggregate_raters` e `fleiss_kappa` do `statsmodels`, conforme a atividade.
Unidade de análise:
  - tipo_projeto e entrega_real: atributos do repositório -> 60 sujeitos (repo_id)
  - is_corretiva: atributo da release -> 300 sujeitos (repo_id, release_num)
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from statsmodels.stats.inter_rater import aggregate_raters, fleiss_kappa

from .validar_rotulagem import validar

DIMENSOES = ["tipo_projeto", "entrega_real", "is_corretiva"]
DIMENSOES_POR_REPO = {"tipo_projeto", "entrega_real"}
CHAVE_RELEASE = ["repo_id", "release_num"]
CHAVE_AMOSTRA = ["repo_id", "release_num", "tag_name", "release_url"]


def carregar(caminhos: Dict[str, str]) -> Dict[str, pd.DataFrame]:
    """Lê os CSVs dos avaliadores: {'kayque': caminho, 'joao': caminho, 'tiago': caminho}."""
    return {nome: pd.read_csv(c, encoding="utf-8") for nome, c in caminhos.items()}


def verificar_amostra(dfs: Dict[str, pd.DataFrame]) -> List[str]:
    """Confere se os arquivos são válidos, da mesma amostra e com a mesma estrutura."""
    erros: List[str] = []
    for nome, df in dfs.items():
        erros += [f"{nome}: {e}" for e in validar(df)]
    nomes = list(dfs)
    ref = dfs[nomes[0]]
    base_ref = ref[CHAVE_AMOSTRA].sort_values(CHAVE_AMOSTRA).reset_index(drop=True)
    for nome in nomes[1:]:
        if set(dfs[nome].columns) != set(ref.columns):
            erros.append(f"{nome}: colunas diferentes de {nomes[0]}")
        outra = dfs[nome][CHAVE_AMOSTRA].sort_values(CHAVE_AMOSTRA).reset_index(drop=True)
        if not base_ref.equals(outra):
            erros.append(f"{nome}: não corresponde à mesma amostra de {nomes[0]}")
    return erros


def matriz_avaliacoes(dfs: Dict[str, pd.DataFrame], dimensao: str) -> pd.DataFrame:
    """Tabela sujeitos x avaliadores com os rótulos de uma dimensão."""
    colunas = {}
    for nome, df in dfs.items():
        if dimensao in DIMENSOES_POR_REPO:
            s = df.sort_values(CHAVE_RELEASE).groupby("repo_id")[dimensao].first()
        else:
            s = df.set_index(CHAVE_RELEASE)[dimensao]
        colunas[nome] = s
    return pd.DataFrame(colunas).sort_index()


def fleiss(ratings: pd.DataFrame) -> Tuple[float, int]:
    """Fleiss' kappa de uma tabela sujeitos x avaliadores. Retorna (kappa, n_categorias).

    Se todos os avaliadores usaram uma única categoria em toda a amostra, o kappa é
    indefinido (variância zero) e retorna NaN.
    """
    categorias = sorted(set(ratings.to_numpy().ravel()))
    codigo = {c: i for i, c in enumerate(categorias)}
    dados = ratings.apply(lambda col: col.map(codigo)).to_numpy()
    if len(categorias) < 2:
        return float("nan"), len(categorias)
    tabela, _ = aggregate_raters(dados)
    return float(fleiss_kappa(tabela, method="fleiss")), len(categorias)


def interpretar_kappa(k: float) -> str:
    """Faixas de Landis & Koch (1977)."""
    if k is None or (isinstance(k, float) and math.isnan(k)):
        return "indefinido"
    if k < 0:
        return "pior que o acaso"
    for limite, nome in ((0.20, "leve"), (0.40, "razoável"), (0.60, "moderada"), (0.80, "substancial")):
        if k <= limite:
            return nome
    return "quase perfeita"


def calcular_concordancia(dfs: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    linhas = []
    for dim in DIMENSOES:
        r = matriz_avaliacoes(dfs, dim)
        k, n_cat = fleiss(r)
        unanimes = (r.nunique(axis=1) == 1).mean()
        linhas.append({
            "dimensao": dim,
            "n_sujeitos": len(r),
            "n_categorias": n_cat,
            "fleiss_kappa": None if math.isnan(k) else round(k, 4),
            "interpretacao": interpretar_kappa(k),
            "concordancia_total_pct": round(100 * float(unanimes), 1),
        })
    return pd.DataFrame(linhas)


def divergencias(dfs: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Lista os sujeitos em que os avaliadores não concordam totalmente."""
    partes = []
    for dim in DIMENSOES:
        r = matriz_avaliacoes(dfs, dim)
        div = r[r.nunique(axis=1) > 1].reset_index()
        if div.empty:
            continue
        div.insert(0, "dimensao", dim)
        partes.append(div)
    if not partes:
        return pd.DataFrame(columns=["dimensao"] + list(dfs))
    return pd.concat(partes, ignore_index=True)