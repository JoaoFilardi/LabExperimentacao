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


def make_workflow_run(
    run_id: int,
    created_at: str,
    conclusion: Optional[str] = "success",
    *,
    workflow_id: int = 1,
    event: str = "push",
    head_branch: str = "main",
    run_started_at: Optional[str] = None,
    updated_at: Optional[str] = None,
    status: str = "completed",
    name: str = "CI",
) -> Dict[str, Any]:
    """Workflow run no formato da API REST do GitHub."""
    started = run_started_at or created_at
    return {
        "id": run_id,
        "workflow_id": workflow_id,
        "name": name,
        "event": event,
        "head_branch": head_branch,
        "status": status,
        "conclusion": conclusion,
        "created_at": created_at,
        "run_started_at": started,
        "updated_at": updated_at or started,
    }


class FakeWorkflowClient:
    """Imita GitHubClient.request para coleta de workflow runs (sem rede).

    Replica o teto de 1.000 resultados por consulta `created`, a paginação
    por `page`/`per_page` e o cache em disco quando `cache` é informado.
    """

    def __init__(
        self,
        runs: Optional[List[Dict[str, Any]]] = None,
        default_branch: str = "main",
        cache: Any = None,
        fail_on_created: Optional[str] = None,
        fail_repo: bool = False,
        cap_at: int = 1000,
    ) -> None:
        from lab03.src.config import parse_iso_datetime

        self._parse = parse_iso_datetime
        self.runs = list(runs or [])
        self.default_branch = default_branch
        self.cache = cache
        self.fail_on_created = fail_on_created
        self.fail_repo = fail_repo
        self.cap_at = cap_at
        self.calls: List[Dict[str, Any]] = []

    def request(self, endpoint, params=None, cache_category=None, cache_key=None):
        params = dict(params or {})
        
        if self.cache and cache_category and cache_key:
            cached = self.cache.get(cache_category, cache_key)
            if cached is not None:
                return cached, {}

        self.calls.append(
            {
                "endpoint": endpoint,
                "params": params,
                "cache_category": cache_category,
                "cache_key": cache_key,
            }
        )

        if self.fail_repo and endpoint.count("/") == 2:
            raise RuntimeError("falha persistente ao consultar repositório")

        if endpoint.startswith("repos/") and "/actions/" not in endpoint:
            data = {"default_branch": self.default_branch}
            self._store_cache(cache_category, cache_key, data)
            return data, {}

        if endpoint.endswith("/actions/runs"):
            created = str(params.get("created") or "")
            if self.fail_on_created and self.fail_on_created in created:
                raise RuntimeError("falha persistente na API de workflow runs")

            branch = params.get("branch")
            event = params.get("event")
            filtered = []
            for run in self.runs:
                if branch and run.get("head_branch") != branch:
                    continue
                if event and run.get("event") != event:
                    continue
                if created and not self._in_created_range(run.get("created_at") or "", created):
                    continue
                filtered.append(run)

            total_count = len(filtered)
            capped = filtered[: self.cap_at]
            page = int(params.get("page") or 1)
            per_page = int(params.get("per_page") or 100)
            start = (page - 1) * per_page
            chunk = capped[start : start + per_page]
            data = {"total_count": total_count, "workflow_runs": chunk}
            self._store_cache(cache_category, cache_key, data)
            return data, {}

        raise AssertionError(f"endpoint inesperado: {endpoint}")

    def _store_cache(self, category, key, data) -> None:
        if self.cache and category and key:
            self.cache.set(category, key, data)

    def _in_created_range(self, created_at: str, created_range: str) -> bool:
        if ".." not in created_range or not created_at:
            return True
        start_s, end_s = created_range.split("..", 1)
        start = self._parse(start_s)
        end = self._parse(end_s)
        dt = self._parse(created_at)
        return start <= dt <= end
