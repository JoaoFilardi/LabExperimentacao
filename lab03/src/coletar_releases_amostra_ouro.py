"""Coleta 5 releases REAIS por repositório da amostra-ouro (LAB03S02).

Substitui a geração sintética de `gerar_amostra_ouro.py`: as tags, títulos, datas e
notas vêm da API do GitHub, para que a rotulagem manual possa ser feita lendo as
release notes de verdade. Usa a lista de 60 repositórios já definida no projeto e a
semente fixa (42). O CSV gerado deve ser versionado e usado por TODOS os avaliadores,
pois as releases mudam com o tempo.

Uso (na raiz do repositório, com GITHUB_TOKEN no ambiente ou no .env):
    python -m lab03.src.coletar_releases_amostra_ouro
"""

from __future__ import annotations

import argparse
import os
import random
import time
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import requests

from .gerar_amostra_ouro import REPOSITORIOS_AMOSTRA_OURO, SEED

API = "https://api.github.com"
RELEASES_POR_REPO = 5
TRECHO_NOTAS = 1500


def _headers() -> Dict[str, str]:
    h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def listar_releases(full_name: str, max_paginas: int = 5) -> List[Dict[str, Any]]:
    """Lista releases publicadas (sem rascunhos nem pré-releases) de um repositório."""
    todas: List[Dict[str, Any]] = []
    for pagina in range(1, max_paginas + 1):
        resp = requests.get(
            f"{API}/repos/{full_name}/releases",
            headers=_headers(),
            params={"per_page": 100, "page": pagina},
            timeout=30,
        )
        resp.raise_for_status()
        lote = resp.json()
        if not lote:
            break
        todas.extend(r for r in lote if not r["draft"] and not r["prerelease"])
        time.sleep(0.3)
    return todas


def sortear_releases(releases: List[Dict[str, Any]], seed: int, full_name: str) -> List[Dict[str, Any]]:
    """Sorteia 5 releases de forma determinística (semente + nome do repo)."""
    if len(releases) < RELEASES_POR_REPO:
        raise ValueError(
            f"{full_name}: apenas {len(releases)} releases elegíveis (mínimo {RELEASES_POR_REPO}). "
            "Troque o repositório de forma documentada, igual para todo o grupo."
        )
    rng = random.Random(f"{seed}:{full_name}")
    escolhidas = rng.sample(releases, RELEASES_POR_REPO)
    return sorted(escolhidas, key=lambda r: r["published_at"])


def montar_base(seed: int = SEED) -> pd.DataFrame:
    linhas: List[Dict[str, Any]] = []
    for repo_id, repo in enumerate(REPOSITORIOS_AMOSTRA_OURO, start=1):
        nome = repo["full_name"]
        escolhidas = sortear_releases(listar_releases(nome), seed, nome)
        for num, rel in enumerate(escolhidas, start=1):
            linhas.append({
                "repo_id": repo_id,
                "full_name": nome,
                "repo_url": f"https://github.com/{nome}",
                "primary_language": repo["language"],
                "release_num": num,
                "tag_name": rel["tag_name"],
                "release_name": rel["name"] or rel["tag_name"],
                "published_at": rel["published_at"],
                "release_url": rel["html_url"],
                "release_body": (rel["body"] or "")[:TRECHO_NOTAS],
                "tipo_projeto": "",
                "entrega_real": "",
                "is_corretiva": "",
                "justificativa": "",
            })
        print(f"[{repo_id:02d}/60] {nome}: ok")
    return pd.DataFrame(linhas)


def main() -> None:
    parser = argparse.ArgumentParser(description="Coleta releases reais da amostra-ouro")
    parser.add_argument("--output", default="lab03/data/amostra_ouro_base.csv")
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    df = montar_base(args.seed)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False, encoding="utf-8")
    print(f"Base gerada: {out} ({len(df)} linhas)")


if __name__ == "__main__":
    main()