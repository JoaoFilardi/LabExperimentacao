"""Fakes e builders de fixtures para os testes de Lead Time (sem rede)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import unquote


def make_release(
    release_id: int,
    tag: str,
    published_at: Optional[str],
    draft: bool = False,
    prerelease: bool = False,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "id": release_id,
        "tag_name": tag,
        "name": name if name is not None else f"Release {tag}",
        "draft": draft,
        "prerelease": prerelease,
        "published_at": published_at,
        "created_at": published_at,
        "html_url": f"https://github.com/o/r/releases/tag/{tag}",
        "target_commitish": "main",
    }


def make_commit(
    sha: str,
    author_date: Optional[str],
    committer_date: Optional[str] = None,
) -> Dict[str, Any]:
    """Commit no formato da API. committer_date existe para provar que ele é ignorado."""
    author: Dict[str, Any] = {"name": "dev"}
    if author_date is not None:
        author["date"] = author_date
    return {
        "sha": sha,
        "commit": {
            "author": author,
            "committer": {"name": "dev", "date": committer_date or author_date},
        },
    }


def make_compare_page(
    commits: List[Dict[str, Any]],
    total_commits: Optional[int] = None,
) -> Dict[str, Any]:
    """Uma página da resposta de /compare (o client.paginate devolve uma lista destas)."""
    total = len(commits) if total_commits is None else total_commits
    return {"status": "ahead", "ahead_by": total, "total_commits": total, "commits": commits}


class FakeClient:
    """Imita o contrato de GitHubClient.paginate usado pelos módulos de lead time.

    - /releases    -> lista de releases (dicts brutos)
    - /compare/b...h -> lista de páginas (dicts); [] simula 404
    """

    def __init__(
        self,
        releases: Optional[List[Dict[str, Any]]] = None,
        compares: Optional[Dict[Tuple[str, str], List[Dict[str, Any]]]] = None,
        fail_releases: bool = False,
        fail_compares: Tuple[Tuple[str, str], ...] = (),
    ) -> None:
        self.releases = releases or []
        self.compares = compares or {}
        self.fail_releases = fail_releases
        self.fail_compares = fail_compares
        self.calls: List[Dict[str, Any]] = []

    def paginate(self, endpoint, params=None, max_pages=None, cache_category=None, cache_key_prefix=None):
        self.calls.append(
            {
                "endpoint": endpoint,
                "params": params,
                "max_pages": max_pages,
                "cache_category": cache_category,
                "cache_key_prefix": cache_key_prefix,
            }
        )
        if endpoint.endswith("/releases"):
            if self.fail_releases:
                raise RuntimeError("falha persistente em releases")
            return list(self.releases)
        if "/compare/" in endpoint:
            spec = endpoint.split("/compare/", 1)[1]
            base, head = spec.split("...")
            key = (unquote(base), unquote(head))
            if key in self.fail_compares:
                raise RuntimeError("falha persistente em compare")
            return list(self.compares.get(key, []))
        raise AssertionError(f"endpoint inesperado: {endpoint}")
