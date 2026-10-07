"""Coleta de releases e de commits entre releases (LAB03S01 - Lead Time for Changes).

Responsabilidades deste módulo (somente coleta, sem cálculo de métricas):
1. Listar as releases de um repositório pela API do GitHub e manter apenas as
   releases válidas (publicadas, draft=false, prerelease=false).
2. Montar os pares (release atual, release anterior) das releases que caem
   dentro da janela de observação.
3. Obter os commits entre duas releases via endpoint de comparação
   (GET /repos/{owner}/{repo}/compare/{base}...{head}), tratando 404,
   paginação e o limite de 250 commits da API.

Todas as requisições passam pelo GitHubClient compartilhado, que já fornece
cache em disco, retry e controle de rate limit.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

from .config import WindowConfig, parse_iso_datetime
from .github_client import GitHubClient

logger = logging.getLogger(__name__)

# A API de comparação devolve no máximo 250 commits por comparação (3 páginas de 100).
MAX_COMPARE_COMMITS = 250
COMPARE_PER_PAGE = 100
COMPARE_MAX_PAGES = 3
# 10 páginas x 100 = 1000 releases mais recentes: suficiente para achar a release
# anterior da primeira release da janela.
MAX_RELEASE_PAGES = 10


@dataclass(frozen=True)
class Release:
    """Release publicada, com os campos necessários para relacionar releases e commits."""

    release_id: int
    name: str
    tag_name: str
    published_at: datetime
    html_url: str = ""
    target_commitish: str = ""
    created_at: str = ""


ReleasePair = Tuple[Release, Optional[Release]]


@dataclass
class CompareResult:
    """Resultado da comparação entre duas releases.

    available=False indica comparação inexistente (404) ou falha na requisição.
    truncated=True indica que a API informou mais commits (total_commits) do que
    os efetivamente retornados (limite de 250).
    """

    available: bool
    commits: List[Dict[str, Any]] = field(default_factory=list)
    total_commits: int = 0
    truncated: bool = False
    error: str = ""


def parse_release(raw: Any) -> Optional[Release]:
    """Converte o JSON de uma release em Release, ou None se ela não for válida.

    Critérios: dict, draft=false, prerelease=false, com tag_name e published_at
    parseável. Releases sem published_at (não publicadas) são descartadas.
    """
    if not isinstance(raw, dict):
        return None
    if raw.get("draft", False) or raw.get("prerelease", False):
        return None

    tag_name = raw.get("tag_name")
    published_raw = raw.get("published_at")
    if not tag_name or not published_raw:
        return None

    try:
        published_at = parse_iso_datetime(published_raw)
    except (ValueError, TypeError, AttributeError):
        return None

    return Release(
        release_id=raw.get("id") or 0,
        name=raw.get("name") or tag_name,
        tag_name=tag_name,
        published_at=published_at,
        html_url=raw.get("html_url") or "",
        target_commitish=raw.get("target_commitish") or "",
        created_at=raw.get("created_at") or "",
    )


def fetch_valid_releases(client: GitHubClient, owner: str, repo: str) -> List[Release]:
    """Lista todas as releases válidas do repositório, ordenadas da mais antiga para a mais nova.

    Não aplica a janela de observação: a release imediatamente anterior à
    primeira release da janela pode estar fora dela e é necessária como base
    da comparação. A janela é aplicada em build_release_pairs.

    Usa o mesmo cache_category/prefixo da etapa de seleção, reaproveitando as
    páginas já baixadas.
    """
    raw_releases = client.paginate(
        endpoint=f"repos/{owner}/{repo}/releases",
        params={"per_page": 100},
        max_pages=MAX_RELEASE_PAGES,
        cache_category="releases",
        cache_key_prefix=f"releases_{owner}_{repo}",
    )

    releases: List[Release] = []
    seen_ids = set()
    for raw in raw_releases:
        release = parse_release(raw)
        if release is None:
            continue
        if release.release_id and release.release_id in seen_ids:
            continue
        seen_ids.add(release.release_id)
        releases.append(release)

    releases.sort(key=lambda r: (r.published_at, r.release_id))
    return releases


def build_release_pairs(releases: List[Release], window: WindowConfig) -> List[ReleasePair]:
    """Retorna (release, release_anterior) para cada release dentro da janela.

    `releases` deve estar ordenada por published_at crescente. A release anterior
    é a release válida imediatamente anterior, mesmo que esteja fora da janela;
    é None apenas quando não existe nenhuma release válida anterior.
    """
    pairs: List[ReleasePair] = []
    for idx, release in enumerate(releases):
        if not window.is_in_window(release.published_at):
            continue
        previous = releases[idx - 1] if idx > 0 else None
        pairs.append((release, previous))
    return pairs


def _compare_endpoint(owner: str, repo: str, base_tag: str, head_tag: str) -> str:
    base = quote(base_tag, safe="/")
    head = quote(head_tag, safe="/")
    return f"repos/{owner}/{repo}/compare/{base}...{head}"


def fetch_commits_between(
    client: GitHubClient,
    owner: str,
    repo: str,
    base_tag: str,
    head_tag: str,
) -> CompareResult:
    """Obtém os commits entre duas releases (base_tag...head_tag).

    - 404 / comparação inexistente -> CompareResult(available=False).
    - Falha persistente do client -> available=False com a mensagem em `error`
      (o repositório continua sendo processado).
    - Paginação: cada página da comparação é um dict com a lista "commits";
      as páginas são concatenadas e commits repetidos (mesmo sha) são ignorados.
    - Mais de 250 commits: a API limita a resposta; quando total_commits é maior
      que o número de commits retornados, truncated=True.
    """
    endpoint = _compare_endpoint(owner, repo, base_tag, head_tag)
    try:
        pages = client.paginate(
            endpoint=endpoint,
            params={"per_page": COMPARE_PER_PAGE},
            max_pages=COMPARE_MAX_PAGES,
            cache_category="compare",
            cache_key_prefix=f"compare_{owner}_{repo}_{base_tag}_{head_tag}",
        )
    except Exception as err:  # noqa: BLE001 - o repositório deve seguir no pipeline
        logger.warning("Falha ao comparar %s...%s em %s/%s: %s", base_tag, head_tag, owner, repo, err)
        return CompareResult(available=False, error=str(err))

    pages = [page for page in pages if isinstance(page, dict)]
    if not pages:
        logger.debug("Comparação indisponível (404) %s...%s em %s/%s", base_tag, head_tag, owner, repo)
        return CompareResult(available=False, error="comparacao_inexistente_404")

    commits: List[Dict[str, Any]] = []
    seen_shas = set()
    for page in pages:
        for commit in page.get("commits") or []:
            if not isinstance(commit, dict):
                continue
            sha = commit.get("sha")
            if sha:
                if sha in seen_shas:
                    continue
                seen_shas.add(sha)
            commits.append(commit)

    reported_total = pages[0].get("total_commits")
    total_commits = reported_total if isinstance(reported_total, int) else len(commits)
    total_commits = max(total_commits, len(commits))

    return CompareResult(
        available=True,
        commits=commits,
        total_commits=total_commits,
        truncated=total_commits > len(commits),
    )
