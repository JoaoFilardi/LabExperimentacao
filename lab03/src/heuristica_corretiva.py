"""Heurística de releases corretivas e sua avaliação contra o consenso (LAB03S02, issue #34).

Cada versão da heurística fica registrada em HEURISTICAS. A avaliação calcula precisão,
recall e F1 da classe positiva ("sim") e, se o F1 ficar abaixo do limiar (0,70), avalia a
próxima versão, registrando todas.

ATENÇÃO: se a base da amostra-ouro for sintética (títulos "Maintenance & Bugfixes"
fabricados), qualquer heurística baseada em título tende a F1 ~ 1,0 por circularidade.
Isso não valida a heurística em releases reais.
"""

from __future__ import annotations

import re
from typing import Callable, Dict, List

import pandas as pd

LIMIAR_F1 = 0.70
POSITIVO = "sim"

_CORRECAO = re.compile(r"\b(fix(es|ed)?|bug(s|fix(es)?)?|patch(es)?|hotfix|cve-\d+|security|regression|crash)\b", re.I)
_EVOLUCAO = re.compile(r"\b(feature(s)?|new|improvement(s)?|breaking|add(s|ed)?|introduc\w+|support)\b", re.I)
_SEMVER = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


def _texto(row: pd.Series) -> str:
    return f"{row.get('release_name', '')} {row.get('release_body', '')}"


def v1_palavras_chave(row: pd.Series) -> str:
    """v1: qualquer termo de correção no título/notas."""
    return "sim" if _CORRECAO.search(_texto(row)) else "não"


def v2_palavras_e_semver(row: pd.Series) -> str:
    """v2: refina a v1. Termo de correção sem sinal de evolução => sim; sinal de evolução
    sem termo de correção => não; sem texto conclusivo, usa bump de patch (x.y.Z, Z>0)."""
    texto = _texto(row)
    corrige, evolui = bool(_CORRECAO.search(texto)), bool(_EVOLUCAO.search(texto))
    if corrige and not evolui:
        return "sim"
    if evolui and not corrige:
        return "não"
    m = _SEMVER.match(str(row.get("tag_name", "")))
    if m and int(m.group(3)) > 0:
        return "sim"
    return "sim" if corrige else "não"


HEURISTICAS: Dict[str, Callable[[pd.Series], str]] = {
    "v1_palavras_chave": v1_palavras_chave,
    "v2_palavras_e_semver": v2_palavras_e_semver,
}


def metricas(y_true: List[str], y_pred: List[str], positivo: str = POSITIVO) -> Dict[str, float]:
    tp = sum(t == positivo and p == positivo for t, p in zip(y_true, y_pred))
    fp = sum(t != positivo and p == positivo for t, p in zip(y_true, y_pred))
    fn = sum(t == positivo and p != positivo for t, p in zip(y_true, y_pred))
    tn = len(y_true) - tp - fp - fn
    precisao = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precisao * recall / (precisao + recall) if precisao + recall else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precisao": round(precisao, 4), "recall": round(recall, 4), "f1": round(f1, 4)}


def avaliar(consenso: pd.DataFrame, versao: str) -> Dict[str, float]:
    previsoes = consenso.apply(HEURISTICAS[versao], axis=1).tolist()
    return {"versao": versao, "n": len(consenso), **metricas(consenso["is_corretiva"].tolist(), previsoes)}


def avaliar_versoes(consenso: pd.DataFrame, limiar: float = LIMIAR_F1) -> pd.DataFrame:
    """Avalia as versões em ordem; para quando uma atinge o limiar. Registra todas as avaliadas."""
    resultados = []
    for versao in HEURISTICAS:
        r = avaliar(consenso, versao)
        r["atingiu_limiar"] = r["f1"] >= limiar
        resultados.append(r)
        if r["atingiu_limiar"]:
            break
    return pd.DataFrame(resultados)