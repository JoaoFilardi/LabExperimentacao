"""Coleta reproduzível de Pull Requests reais via API REST do GitHub (LAB04S01).

Critérios de seleção (ver docs/fonte_e_coleta.md):
  - somente PRs com merge (merged_at != null) criados na janela [inicio, fim];
  - autor humano (user.type == "User"): PRs abertos por bots (ex.: dependabot) ficam de fora,
    para não confundir "bot revisando" com "bot como autor";
  - com_bot: PR com pelo menos 1 comentário/review/comentário de review feito por uma conta
    Bot (user.type == "Bot" ou login terminado em "[bot]");
  - sem_bot: PR sem nenhuma interação de conta Bot;
  - tempo_horas = merged_at - created_at (horas decimais, UTC); PRs com tempo <= 0 são descartados;
  - amostragem aleatória simples com semente fixa, N_POR_GRUPO por grupo.

Uso (a partir da raiz do repositório):
    export GITHUB_TOKEN=...   # recomendado: evita o limite de 60 requisições/h
    python -m lab04.src.coleta_dados_reais --repo tiangolo/fastapi \
        --inicio 2024-06-01 --fim 2024-06-30 --n 30 --seed 42
"""

from __future__ import annotations

import argparse
import json
import os
import random
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import pandas as pd

API = "https://api.github.com"
N_POR_GRUPO = 30
SEMENTE_PADRAO = 42
COLUNAS_CSV = [
    "pr_id", "repositorio", "grupo", "bot_presente", "nome_bot",
    "created_at", "merged_at", "tempo_horas",
]
SAIDA_PADRAO = Path(__file__).resolve().parent.parent / "data" / "amostra_dados_reais.csv"


# ----------------------------------------------------------------------------
# Funções puras (testáveis sem rede)
# ----------------------------------------------------------------------------
def eh_bot(usuario: Optional[Dict[str, Any]]) -> bool:
    """True se a conta é de bot (type == 'Bot' ou login terminado em '[bot]')."""
    if not usuario:
        return False
    return usuario.get("type") == "Bot" or str(usuario.get("login", "")).endswith("[bot]")


def parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc)


def calcular_tempo_horas(created_at: str, merged_at: str) -> float:
    """Diferença em horas decimais (arredondada a 2 casas)."""
    delta = parse_iso(merged_at) - parse_iso(created_at)
    return round(delta.total_seconds() / 3600, 2)


def nomes_de_bots(interacoes: Iterable[Dict[str, Any]]) -> List[str]:
    """Logins distintos de bots, na ordem em que aparecem."""
    vistos: List[str] = []
    for item in interacoes:
        usuario = item.get("user")
        if eh_bot(usuario) and usuario["login"] not in vistos:
            vistos.append(usuario["login"])
    return vistos


def montar_registro(repo: str, pr: Dict[str, Any], interacoes: Iterable[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Converte um PR + suas interações em uma linha do CSV; None se não elegível."""
    if not pr.get("merged_at") or eh_bot(pr.get("user")):
        return None
    tempo = calcular_tempo_horas(pr["created_at"], pr["merged_at"])
    if tempo <= 0:
        return None
    bots = nomes_de_bots(interacoes)
    return {
        "pr_id": pr["number"],
        "repositorio": repo,
        "grupo": "com_bot" if bots else "sem_bot",
        "bot_presente": bool(bots),
        "nome_bot": ";".join(bots) if bots else "nenhum",
        "created_at": parse_iso(pr["created_at"]).strftime("%Y-%m-%d %H:%M:%S"),
        "merged_at": parse_iso(pr["merged_at"]).strftime("%Y-%m-%d %H:%M:%S"),
        "tempo_horas": tempo,
    }


def amostrar_por_grupo(registros: List[Dict[str, Any]], n: int = N_POR_GRUPO, seed: int = SEMENTE_PADRAO) -> pd.DataFrame:
    """Amostra aleatória simples de n registros por grupo (semente fixa)."""
    rng = random.Random(seed)
    partes = []
    for grupo in ("sem_bot", "com_bot"):
        candidatos = sorted((r for r in registros if r["grupo"] == grupo), key=lambda r: r["pr_id"])
        if len(candidatos) < n:
            raise ValueError(f"Grupo '{grupo}' tem só {len(candidatos)} PRs elegíveis (< {n}); amplie a janela.")
        partes.extend(rng.sample(candidatos, n))
    df = pd.DataFrame(partes, columns=COLUNAS_CSV)
    return df.sort_values(["grupo", "pr_id"], ascending=[False, True]).reset_index(drop=True)


# ----------------------------------------------------------------------------
# Acesso à API (requer rede)
# ----------------------------------------------------------------------------
def _get(url: str, token: Optional[str]) -> Any:
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "lab04-coleta"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 - URL fixa da API do GitHub
        return json.load(resp)


def _paginar(url: str, token: Optional[str], max_paginas: int = 10) -> List[Dict[str, Any]]:
    itens: List[Dict[str, Any]] = []
    for pagina in range(1, max_paginas + 1):
        sep = "&" if "?" in url else "?"
        lote = _get(f"{url}{sep}per_page=100&page={pagina}", token)
        itens.extend(lote)
        if len(lote) < 100:
            break
    return itens


def listar_prs_mesclados(repo: str, inicio: str, fim: str, token: Optional[str], max_paginas: int = 30) -> List[Dict[str, Any]]:
    """PRs mesclados cujo created_at está em [inicio, fim] (datas AAAA-MM-DD, UTC)."""
    ini = parse_iso(inicio + "T00:00:00Z")
    fi = parse_iso(fim + "T23:59:59Z")
    prs = _paginar(f"{API}/repos/{repo}/pulls?state=closed&sort=created&direction=desc", token, max_paginas)
    return [p for p in prs if p.get("merged_at") and ini <= parse_iso(p["created_at"]) <= fi]


def interacoes_do_pr(repo: str, numero: int, token: Optional[str]) -> List[Dict[str, Any]]:
    """Comentários da conversa, reviews e comentários de review do PR."""
    base = f"{API}/repos/{repo}"
    return (
        _paginar(f"{base}/issues/{numero}/comments", token)
        + _paginar(f"{base}/pulls/{numero}/reviews", token)
        + _paginar(f"{base}/pulls/{numero}/comments", token)
    )


def coletar(repo: str, inicio: str, fim: str, n: int = N_POR_GRUPO, seed: int = SEMENTE_PADRAO,
            token: Optional[str] = None, saida: Path | str = SAIDA_PADRAO) -> pd.DataFrame:
    token = token or os.environ.get("GITHUB_TOKEN")
    registros = []
    for pr in listar_prs_mesclados(repo, inicio, fim, token):
        if eh_bot(pr.get("user")):
            continue
        reg = montar_registro(repo, pr, interacoes_do_pr(repo, pr["number"], token))
        if reg:
            registros.append(reg)
    df = amostrar_por_grupo(registros, n, seed)
    saida = Path(saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(saida, index=False)
    return df


def main() -> None:  # pragma: no cover
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True, help="owner/nome, ex.: tiangolo/fastapi")
    ap.add_argument("--inicio", required=True, help="AAAA-MM-DD (UTC)")
    ap.add_argument("--fim", required=True, help="AAAA-MM-DD (UTC)")
    ap.add_argument("--n", type=int, default=N_POR_GRUPO)
    ap.add_argument("--seed", type=int, default=SEMENTE_PADRAO)
    ap.add_argument("--saida", default=str(SAIDA_PADRAO))
    a = ap.parse_args()
    df = coletar(a.repo, a.inicio, a.fim, a.n, a.seed, saida=a.saida)
    print(df.groupby("grupo")["tempo_horas"].describe())
    print(f"CSV gravado em {a.saida}")


if __name__ == "__main__":  # pragma: no cover
    main()