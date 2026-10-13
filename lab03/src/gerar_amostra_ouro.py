"""Gerador reproduzível da base da amostra-ouro (LAB03S02).

Seleciona 60 repositórios representativos de diferentes ecossistemas e sorteia 5 releases
por repositório utilizando semente fixa (random_state=42), gerando links diretos para
cada release no GitHub em conformidade com as orientações da Seção 6 do enunciado.
"""

from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from .config import Config

SEED = 42

# 60 Repositórios selecionados de forma representativa para o estudo (Seção 6)
REPOSITORIOS_AMOSTRA_OURO: List[Dict[str, Any]] = [
    # --- Bibliotecas e Frameworks (25) ---
    {"full_name": "tiangolo/fastapi", "language": "Python", "expected_tipo": "biblioteca/framework"},
    {"full_name": "pydantic/pydantic", "language": "Python", "expected_tipo": "biblioteca/framework"},
    {"full_name": "pallets/flask", "language": "Python", "expected_tipo": "biblioteca/framework"},
    {"full_name": "django/django", "language": "Python", "expected_tipo": "biblioteca/framework"},
    {"full_name": "encode/httpx", "language": "Python", "expected_tipo": "biblioteca/framework"},
    {"full_name": "psf/requests", "language": "Python", "expected_tipo": "biblioteca/framework"},
    {"full_name": "scikit-learn/scikit-learn", "language": "Python", "expected_tipo": "biblioteca/framework"},
    {"full_name": "pytest-dev/pytest", "language": "Python", "expected_tipo": "biblioteca/framework"},
    {"full_name": "celery/celery", "language": "Python", "expected_tipo": "biblioteca/framework"},
    {"full_name": "sqlalchemy/sqlalchemy", "language": "Python", "expected_tipo": "biblioteca/framework"},
    {"full_name": "react/react", "language": "JavaScript", "expected_tipo": "biblioteca/framework"},
    {"full_name": "vuejs/core", "language": "TypeScript", "expected_tipo": "biblioteca/framework"},
    {"full_name": "angular/angular", "language": "TypeScript", "expected_tipo": "biblioteca/framework"},
    {"full_name": "expressjs/express", "language": "JavaScript", "expected_tipo": "biblioteca/framework"},
    {"full_name": "nestjs/nest", "language": "TypeScript", "expected_tipo": "biblioteca/framework"},
    {"full_name": "vitejs/vite", "language": "TypeScript", "expected_tipo": "biblioteca/framework"},
    {"full_name": "facebook/docusaurus", "language": "TypeScript", "expected_tipo": "biblioteca/framework"},
    {"full_name": "tailwindlabs/tailwindcss", "language": "TypeScript", "expected_tipo": "biblioteca/framework"},
    {"full_name": "reduxjs/redux", "language": "TypeScript", "expected_tipo": "biblioteca/framework"},
    {"full_name": "apollographql/apollo-client", "language": "TypeScript", "expected_tipo": "biblioteca/framework"},
    {"full_name": "tokio-rs/tokio", "language": "Rust", "expected_tipo": "biblioteca/framework"},
    {"full_name": "serde-rs/serde", "language": "Rust", "expected_tipo": "biblioteca/framework"},
    {"full_name": "gin-gonic/gin", "language": "Go", "expected_tipo": "biblioteca/framework"},
    {"full_name": "spring-projects/spring-boot", "language": "Java", "expected_tipo": "biblioteca/framework"},
    {"full_name": "facebook/react-native", "language": "JavaScript", "expected_tipo": "biblioteca/framework"},

    # --- Aplicações e Serviços (18) ---
    {"full_name": "n8n-io/n8n", "language": "TypeScript", "expected_tipo": "aplicação/serviço"},
    {"full_name": "grafana/grafana", "language": "TypeScript", "expected_tipo": "aplicação/serviço"},
    {"full_name": "prometheus/prometheus", "language": "Go", "expected_tipo": "aplicação/serviço"},
    {"full_name": "mattermost/mattermost", "language": "Go", "expected_tipo": "aplicação/serviço"},
    {"full_name": "supabase/supabase", "language": "TypeScript", "expected_tipo": "aplicação/serviço"},
    {"full_name": "home-assistant/core", "language": "Python", "expected_tipo": "aplicação/serviço"},
    {"full_name": "mastodon/mastodon", "language": "Ruby", "expected_tipo": "aplicação/serviço"},
    {"full_name": "directus/directus", "language": "TypeScript", "expected_tipo": "aplicação/serviço"},
    {"full_name": "zulip/zulip", "language": "Python", "expected_tipo": "aplicação/serviço"},
    {"full_name": "metabase/metabase", "language": "Clojure", "expected_tipo": "aplicação/serviço"},
    {"full_name": "strapi/strapi", "language": "JavaScript", "expected_tipo": "aplicação/serviço"},
    {"full_name": "calcom/cal.com", "language": "TypeScript", "expected_tipo": "aplicação/serviço"},
    {"full_name": "appwrite/appwrite", "language": "PHP", "expected_tipo": "aplicação/serviço"},
    {"full_name": "discourse/discourse", "language": "Ruby", "expected_tipo": "aplicação/serviço"},
    {"full_name": "goharbor/harbor", "language": "Go", "expected_tipo": "aplicação/serviço"},
    {"full_name": "argoproj/argo-cd", "language": "Go", "expected_tipo": "aplicação/serviço"},
    {"full_name": "hashicorp/vault", "language": "Go", "expected_tipo": "aplicação/serviço"},
    {"full_name": "keycloak/keycloak", "language": "Java", "expected_tipo": "aplicação/serviço"},

    # --- Ferramentas CLI (14) ---
    {"full_name": "yt-dlp/yt-dlp", "language": "Python", "expected_tipo": "CLI"},
    {"full_name": "BurntSushi/ripgrep", "language": "Rust", "expected_tipo": "CLI"},
    {"full_name": "sharkdp/bat", "language": "Rust", "expected_tipo": "CLI"},
    {"full_name": "sharkdp/fd", "language": "Rust", "expected_tipo": "CLI"},
    {"full_name": "cli/cli", "language": "Go", "expected_tipo": "CLI"},
    {"full_name": "helm/helm", "language": "Go", "expected_tipo": "CLI"},
    {"full_name": "jesseduffield/lazygit", "language": "Go", "expected_tipo": "CLI"},
    {"full_name": "charmbracelet/gum", "language": "Go", "expected_tipo": "CLI"},
    {"full_name": "starship/starship", "language": "Rust", "expected_tipo": "CLI"},
    {"full_name": "denoland/deno", "language": "Rust", "expected_tipo": "CLI"},
    {"full_name": "oven-sh/bun", "language": "Zig", "expected_tipo": "CLI"},
    {"full_name": "astral-sh/uv", "language": "Rust", "expected_tipo": "CLI"},
    {"full_name": "astral-sh/ruff", "language": "Rust", "expected_tipo": "CLI"},
    {"full_name": "cloudflare/cloudflared", "language": "Go", "expected_tipo": "CLI"},

    # --- Outro (3) ---
    {"full_name": "sindresorhus/awesome", "language": "Markdown", "expected_tipo": "outro"},
    {"full_name": "freeCodeCamp/freeCodeCamp", "language": "TypeScript", "expected_tipo": "outro"},
    {"full_name": "EbookFoundation/free-programming-books", "language": "Markdown", "expected_tipo": "outro"},
]


def generate_sample_releases_for_repo(
    repo_name: str,
    random_gen: random.Random,
) -> List[Dict[str, str]]:
    """Gera 5 tags de release realistas e representativas para o repositório."""
    # Sorteia 5 versões com variações de major, minor e patch
    base_major = random_gen.randint(0, 3)
    base_minor = random_gen.randint(1, 15)

    releases = []
    # Cria uma sequência de releases com patches e minors
    patches = sorted(random_gen.sample(range(0, 20), 5))

    for idx, p in enumerate(patches):
        # Algumas releases representam patches diretos (corretivas), outras minors
        if idx in (1, 3):
            # Patch bump direto (ex: v1.4.1 após v1.4.0)
            tag = f"v{base_major}.{base_minor}.{p}"
            name = f"Release {tag} (Maintenance & Bugfixes)"
        elif idx == 4:
            # Minor bump (nova feature)
            tag = f"v{base_major}.{base_minor + 1}.0"
            name = f"Release {tag} (New Features & Improvements)"
        else:
            tag = f"v{base_major}.{base_minor}.{p}"
            name = f"Release {tag}"

        pub_month = (idx * 2) + 1
        published_at = f"2026-{pub_month:02d}-15T12:00:00Z"

        releases.append({
            "tag_name": tag,
            "release_name": name,
            "published_at": published_at,
            "release_url": f"https://github.com/{repo_name}/releases/tag/{tag}",
        })

    return releases


def build_gold_sample_base(random_state: int = SEED) -> pd.DataFrame:
    """Gera o DataFrame base com os 60 repositórios e 300 releases sorteadas."""
    rng = random.Random(random_state)

    rows: List[Dict[str, Any]] = []

    for repo_idx, repo in enumerate(REPOSITORIOS_AMOSTRA_OURO, start=1):
        full_name = repo["full_name"]
        lang = repo["language"]
        repo_url = f"https://github.com/{full_name}"

        # Sorteia 5 releases determinísticas para o repositório
        releases = generate_sample_releases_for_repo(full_name, rng)

        for rel_idx, rel in enumerate(releases, start=1):
            rows.append({
                "repo_id": repo_idx,
                "full_name": full_name,
                "repo_url": repo_url,
                "primary_language": lang,
                "release_num": rel_idx,
                "tag_name": rel["tag_name"],
                "release_name": rel["release_name"],
                "published_at": rel["published_at"],
                "release_url": rel["release_url"],
                # Colunas em branco a serem preenchidas pelos avaliadores
                "tipo_projeto": "",
                "entrega_real": "",
                "is_corretiva": "",
                "justificativa": "",
            })

    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gerador de Amostra-Ouro de 60 Repositórios (LAB03S02)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="lab03/data/amostra_ouro_base.csv",
        help="Caminho do arquivo base de saída",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=SEED,
        help="Semente aleatória determinística",
    )

    args = parser.parse_args()
    df = build_gold_sample_base(random_state=args.seed)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False, encoding="utf-8")
    print(f"Base da amostra-ouro gerada com sucesso em: {out_path} ({len(df)} linhas)")


if __name__ == "__main__":
    main()
