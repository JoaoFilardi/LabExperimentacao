"""Construção dos rótulos de consenso da amostra-ouro (LAB03S02, issue #34).

Procedimento (documentado em docs/consenso_e_heuristica_s02.md):
  1. Unanimidade (3 de 3): o rótulo é adotado.
  2. Maioria (2 de 3): o rótulo da maioria é adotado.
  3. Sem maioria (3 rótulos distintos, só possível em tipo_projeto e entrega_real):
     o caso é marcado como PENDENTE e decidido em sessão do grupo. A decisão e o motivo
     são registrados em um CSV de desempates (dimensao, repo_id, release_num, valor_final,
     motivo) e reaplicados de forma reproduzível.
Todo rótulo final registra o método usado (unanimidade, maioria, desempate_grupo, pendente).
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

import pandas as pd

from .concordancia import DIMENSOES, DIMENSOES_POR_REPO, matriz_avaliacoes

PENDENTE = "PENDENTE"


def _decidir(valores: list) -> Tuple[str, str]:
    contagem = pd.Series(valores).value_counts()
    topo = contagem.iloc[0]
    if topo == len(valores):
        return contagem.index[0], "unanimidade"
    if topo > len(valores) / 2:
        return contagem.index[0], "maioria"
    return PENDENTE, "pendente"


def carregar_desempates(caminho: Optional[str]) -> pd.DataFrame:
    colunas = ["dimensao", "repo_id", "release_num", "valor_final", "motivo"]
    if not caminho:
        return pd.DataFrame(columns=colunas)
    return pd.read_csv(caminho, encoding="utf-8")


def construir_consenso(
    dfs: Dict[str, pd.DataFrame], desempates: Optional[pd.DataFrame] = None
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Retorna (amostra_ouro_final, pendencias)."""
    desempates = desempates if desempates is not None else carregar_desempates(None)
    ref = next(iter(dfs.values()))
    colunas_info = [c for c in ref.columns if c not in DIMENSOES + ["justificativa"]]
    final = ref[colunas_info].copy().sort_values(["repo_id", "release_num"]).reset_index(drop=True)
    pendencias = []

    for dim in DIMENSOES:
        r = matriz_avaliacoes(dfs, dim)
        resultado = {}
        for chave, linha in r.iterrows():
            valor, metodo = _decidir(linha.tolist())
            repo_id, release_num = (chave, 0) if dim in DIMENSOES_POR_REPO else chave
            if metodo == "pendente":
                achou = desempates[
                    (desempates["dimensao"] == dim)
                    & (desempates["repo_id"] == repo_id)
                    & (desempates["release_num"] == release_num)
                ]
                if len(achou):
                    valor, metodo = achou.iloc[0]["valor_final"], "desempate_grupo"
                else:
                    pendencias.append({"dimensao": dim, "repo_id": repo_id, "release_num": release_num,
                                       **linha.to_dict()})
            resultado[chave] = (valor, metodo)

        def pegar(row):
            chave = row["repo_id"] if dim in DIMENSOES_POR_REPO else (row["repo_id"], row["release_num"])
            return resultado[chave]

        pares = final.apply(pegar, axis=1)
        final[dim] = [p[0] for p in pares]
        final[f"metodo_{dim}"] = [p[1] for p in pares]

    return final, pd.DataFrame(pendencias)