"""Cliente HTTP para a API REST do GitHub construído com requests.

Em estrito atendimento às restrições do laboratório:
- NÃO utiliza bibliotecas prontas de terceiros (como PyGithub).
- Gerencia cabeçalhos de autenticação e User-Agent.
- Monitora X-RateLimit-Remaining e X-RateLimit-Reset com pausa automática.
- Implementa retry com backoff exponencial para erros temporários (5xx, 429, 403).
- Integra-se à camada de cache em disco para evitar requisições redundantes.
"""

from __future__ import annotations

import logging
import re
import time
from typing import Any, Dict, List, Optional, Tuple
import requests

from .cache_manager import CacheManager

logger = logging.getLogger(__name__)


def parse_link_header(link_header: Optional[str]) -> Dict[str, str]:
    """Extrai os links de paginação do cabeçalho HTTP Link do GitHub.

    Exemplo: '<https://api.github.com/...page=2>; rel="next", <...page=50>; rel="last"'
    Retorna: {'next': 'https://api.github.com/...page=2', 'last': '...page=50'}
    """
    links: Dict[str, str] = {}
    if not link_header:
        return links

    # Padrão: <URL>; rel="REL"
    pattern = r'<([^>]+)>;\s*rel="([^"]+)"'
    for match in re.finditer(pattern, link_header):
        url, rel = match.groups()
        links[rel] = url

    return links


def extract_page_number_from_url(url: str) -> Optional[int]:
    """Extrai o número da página (parâmetro ?page=X) a partir de uma URL."""
    match = re.search(r'[?&]page=(\d+)', url)
    if match:
        return int(match.group(1))
    return None


class GitHubClient:
    """Cliente HTTP com controle de cota, retry exponencial e cache local."""

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = "https://api.github.com",
        timeout: int = 30,
        max_retries: int = 5,
        backoff_factor: float = 2.0,
        safety_margin: int = 20,
        cache_manager: Optional[CacheManager] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.safety_margin = safety_margin
        self.cache = cache_manager

        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "LabExperimentacao-DORA-Metrics-Client/1.0",
        })
        if self.token:
            self.session.headers["Authorization"] = f"Bearer {self.token}"

        self.last_rate_limit: Dict[str, int] = {
            "limit": 5000 if self.token else 60,
            "remaining": 5000 if self.token else 60,
            "reset": 0,
        }

    def _update_rate_limit_from_headers(self, headers: requests.structures.CaseInsensitiveDict) -> None:
        """Atualiza estado interno da cota a partir dos cabeçalhos da resposta."""
        if "X-RateLimit-Limit" in headers:
            try:
                self.last_rate_limit["limit"] = int(headers["X-RateLimit-Limit"])
                self.last_rate_limit["remaining"] = int(headers["X-RateLimit-Remaining"])
                self.last_rate_limit["reset"] = int(headers["X-RateLimit-Reset"])
            except ValueError:
                pass

    def _handle_rate_limit_pause_if_needed(self) -> None:
        """Pausa automaticamente a execução se a cota restante atingir a margem de segurança."""
        remaining = self.last_rate_limit.get("remaining", 5000)
        reset_epoch = self.last_rate_limit.get("reset", 0)

        if remaining <= self.safety_margin and reset_epoch > 0:
            now = time.time()
            sleep_duration = max(1.0, (reset_epoch - now) + 3.0)
            logger.warning(
                "Cota da API do GitHub quase esgotada (restam %d). Pausando por %.1f segundos até o reset...",
                remaining,
                sleep_duration,
            )
            time.sleep(sleep_duration)

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Consulta o status da cota via GET /rate_limit sem consumir chamadas."""
        url = f"{self.base_url}/rate_limit"
        resp = self.session.get(url, timeout=self.timeout)
        if resp.status_code == 200:
            data = resp.json()
            core = data.get("resources", {}).get("core", {})
            self.last_rate_limit["limit"] = core.get("limit", self.last_rate_limit["limit"])
            self.last_rate_limit["remaining"] = core.get("remaining", self.last_rate_limit["remaining"])
            self.last_rate_limit["reset"] = core.get("reset", self.last_rate_limit["reset"])
            return core
        return self.last_rate_limit

    def request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        cache_category: Optional[str] = None,
        cache_key: Optional[str] = None,
    ) -> Tuple[Optional[Any], requests.structures.CaseInsensitiveDict]:
        """Executa uma requisição GET com cache, retry exponencial e controle de rate limit.

        Retorna:
            Tupla (json_data, response_headers).
        """
        # 1. Verifica cache se habilitado
        if self.cache and cache_category and cache_key:
            cached_data = self.cache.get(cache_category, cache_key)
            if cached_data is not None:
                # Retorna com headers vazios para indicar hit no cache
                return cached_data, requests.structures.CaseInsensitiveDict()

        # 2. Verifica proximidade do limite de cota antes da chamada
        self._handle_rate_limit_pause_if_needed()

        url = endpoint if endpoint.startswith("http") else f"{self.base_url}/{endpoint.lstrip('/')}"
        attempt = 0

        while attempt <= self.max_retries:
            attempt += 1
            try:
                resp = self.session.get(url, params=params, timeout=self.timeout)
                self._update_rate_limit_from_headers(resp.headers)

                # Sucesso
                if resp.status_code == 200:
                    data = resp.json()
                    if self.cache and cache_category and cache_key:
                        self.cache.set(cache_category, cache_key, data)
                    return data, resp.headers

                # Recursos não encontrados ou vazios (ex: compare inválido ou workflows inexistentes)
                if resp.status_code == 404:
                    logger.debug("Recurso não encontrado (404): %s", url)
                    return None, resp.headers

                # Respostas de Rate Limit ou Abuso (429 ou 403 de rate limit)
                is_rate_limited = resp.status_code == 429 or (
                    resp.status_code == 403 and "rate limit" in resp.text.lower()
                )

                if is_rate_limited:
                    reset_epoch = self.last_rate_limit.get("reset", 0)
                    now = time.time()
                    sleep_time = (reset_epoch - now + 2.0) if reset_epoch > now else (self.backoff_factor ** attempt)
                    logger.warning(
                        "Rate limit atingido (HTTP %d). Aguardando %.1f segundos antes da tentativa %d/%d...",
                        resp.status_code,
                        sleep_time,
                        attempt,
                        self.max_retries,
                    )
                    time.sleep(max(1.0, sleep_time))
                    continue

                # Erros transitórios do servidor (5xx)
                if resp.status_code in {500, 502, 503, 504}:
                    wait_time = self.backoff_factor ** attempt
                    logger.warning(
                        "Erro de servidor HTTP %d em %s. Tentativa %d/%d após %.1fs...",
                        resp.status_code,
                        url,
                        attempt,
                        self.max_retries,
                        wait_time,
                    )
                    time.sleep(wait_time)
                    continue

                # Outros erros definitivos do cliente (ex: 401, 422)
                resp.raise_for_status()

            except (requests.ConnectionError, requests.Timeout) as err:
                wait_time = self.backoff_factor ** attempt
                logger.warning(
                    "Falha de conexão/timeout em %s (%s). Tentativa %d/%d após %.1fs...",
                    url,
                    err,
                    attempt,
                    self.max_retries,
                    wait_time,
                )
                time.sleep(wait_time)

        raise RuntimeError(
            f"Falha persistente ao consultar {url} após {self.max_retries} tentativas."
        )

    def paginate(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        max_pages: Optional[int] = None,
        cache_category: Optional[str] = None,
        cache_key_prefix: Optional[str] = None,
    ) -> List[Any]:
        """Itera sobre todas as páginas de uma listagem seguindo o cabeçalho Link rel='next'."""
        results: List[Any] = []
        page = 1
        current_endpoint = endpoint
        current_params = dict(params or {})
        if "per_page" not in current_params:
            current_params["per_page"] = 100

        while True:
            cache_key = f"{cache_key_prefix}_p{page}" if cache_key_prefix else None
            data, headers = self.request(
                endpoint=current_endpoint,
                params=current_params if page == 1 else None,
                cache_category=cache_category,
                cache_key=cache_key,
            )

            if not data:
                break

            if isinstance(data, list):
                results.extend(data)
            elif isinstance(data, dict):
                # Alguns endpoints retornam dict com lista interna (ex: search com 'items', workflow_runs)
                for key in ["items", "workflow_runs", "workflows"]:
                    if key in data and isinstance(data[key], list):
                        results.extend(data[key])
                        break
                else:
                    results.append(data)

            if max_pages and page >= max_pages:
                break

            links = parse_link_header(headers.get("Link"))
            if "next" in links:
                current_endpoint = links["next"]
                current_params = {}
                page += 1
            else:
                break

        return results

    def count_contributors(self, owner: str, repo: str) -> Optional[int]:
        """Conta contribuidores com eficiência máxima via header Link da última página.

        Conforme recomendação na Seção 4 do enunciado:
        GET /repos/{owner}/{repo}/contributors?per_page=1&anon=true
        e lê o número da última página no cabeçalho Link, economizando centenas de chamadas.
        """
        cache_category = "contributors_count"
        cache_key = f"{owner}_{repo}"

        if self.cache:
            cached = self.cache.get(cache_category, cache_key)
            if cached is not None:
                return int(cached)

        endpoint = f"repos/{owner}/{repo}/contributors"
        params = {"per_page": 1, "anon": "true"}

        try:
            data, headers = self.request(endpoint, params=params)
            if data is None:
                return None

            link_header = headers.get("Link")
            if not link_header:
                # Se não tem link header, há 0 ou 1 contribuidor
                count = len(data) if isinstance(data, list) else 1
            else:
                links = parse_link_header(link_header)
                last_url = links.get("last")
                if last_url:
                    last_page = extract_page_number_from_url(last_url)
                    count = last_page if last_page is not None else len(data)
                else:
                    count = len(data)

            if self.cache:
                self.cache.set(cache_category, cache_key, count)
            return count

        except Exception as err:
            logger.debug("Não foi possível contar contribuidores para %s/%s: %s", owner, repo, err)
            return None
