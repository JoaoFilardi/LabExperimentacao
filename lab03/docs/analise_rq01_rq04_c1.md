# Relatório da Análise Descritiva das Métricas DORA (RQ01 a RQ04) e Classificação de Referência C1

**Laboratório 03 — Sprint 03**  
**Issue de Implementação:** #39 — `[LAB03S03] Analisar RQ01–RQ04 e gerar a classificação DORA de referência (C1)`  
**Autor:** João Victor Filardi Souza Pinto  
**Dataset Base:** `lab03/data/metricas_dora.csv` (310 repositórios qualificados da S02)

---

## 1. Visão Geral e Objetivos

Este relatório consolida a análise estatística descritiva das quatro métricas de entrega e estabilidade de software propostas pelo DORA (*DevOps Research and Assessment*), avaliadas sobre um ecossistema de **310 repositórios populares de código aberto** minerados na Sprint 02.

A análise aborda:
1. **RQ 01 — Deployment Frequency:** Cadência de releases por semana;
2. **RQ 02 — Lead Time for Changes:** Tempo de ciclo do commit à entrega nas variantes obrigatórias (a) por release e (b) por commit;
3. **RQ 03 — Change Failure Rate (CFR):** Taxa de falha nas variantes obrigatórias (a) proxy de CI e (b) proxy de entrega (com censura);
4. **RQ 04 — Failed Deployment Recovery Time:** Duração dos episódios de recuperação de falha em horas, com análise formal de episódios censurados;
5. **Classificação DORA de Referência (C1):** Enquadramento individual e classificação consolidada de cada repositório em Elite, High, Medium ou Low.

Os artefatos gerados servem como base empírica para a seção de **Resultados e Discussão** do artigo científico e como combinação de referência mandatória para a **Análise de Sensibilidade (RQ 07)**.

---

## 2. Integridade dos Dados e Amostra Avaliada

- **Total de Repositórios Analisados ($N$):** 310 repositórios qualificados.
- **Filtros Aplicados na Seleção (Funil S02):**
  - $\ge 1.000$ estrelas (projetos públicos, não-forks, não-arquivados);
  - Adoção ativa de CI/CD via GitHub Actions;
  - $\ge 5$ releases publicadas na janela de 12 meses;
  - $\ge 50$ workflow runs disparados por `push` no *default branch*.
- **Integridade Numérica:** 100% dos registros foram validados sem valores nulos críticos, sem taxas fora do intervalo $[0.0, 1.0]$ e com tratamento estrito de casos censurados.

---

## 3. Síntese das Estatísticas Descritivas (Mediana e IQR)

Em conformidade com as diretrizes metodológicas do laboratório, a análise descritiva foca estritamente na **mediana e intervalo interquartil (IQR = $Q_3 - Q_1$)**, evitando as distorções provocadas por caudas longas e outliers inerentes a dados de repositórios de software.

| Métrica / Variante | Unidade | N | Mediana | Q1 | Q3 | IQR | Mínimo | Máximo |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **RQ01: Deployment Frequency** | releases/sem | 310 | **0,3452** | 0,2301 | 0,4987 | **0,2686** | 0,0959 | 4,9288 |
| **RQ02: Lead Time (a: por release)** | dias | 310 | **11,4360** | 6,9010 | 20,7632 | **13,8622** | 0,1970 | 180,8740 |
| **RQ02: Lead Time (b: por commit)** | dias | 310 | **8,1785** | 4,7293 | 14,7413 | **10,0120** | 0,8630 | 243,2010 |
| *Diferença RQ02 (Variante a - b)* | dias | 310 | **2,9440** | 1,5310 | 5,6700 | **4,1390** | -62,3270 | 40,1820 |
| **RQ03: CFR (a: proxy de CI)** | proporção [0, 1] | 310 | **0,0832** (8,3%) | 0,0531 | 0,1347 | **0,0816** | 0,0050 | 0,3245 |
| **RQ03: CFR (b: proxy de entrega)** | proporção [0, 1] | 310 | **0,2935** (29,4%) | 0,2015 | 0,4057 | **0,2042** | 0,0000 | 0,9562 |
| **RQ04: Tempo de Recuperação** | horas | 310 | **2,8925** | 1,4367 | 6,8237 | **5,3870** | 0,1960 | 70,9750 |
| *Taxa de Censura por Repositório* | proporção [0, 1] | 310 | **0,0000** | 0,0000 | 0,0320 | **0,0320** | 0,0000 | 0,5000 |

---

## 4. Análise Individual por Questão de Pesquisa

### 4.1. RQ 01 — Deployment Frequency
- **Pergunta:** *Qual a frequência de deploys dos repositórios populares que usam CI/CD?*
- **Achados:** A mediana da amostra é de **0,345 releases/semana** (aproximadamente uma release a cada 20 dias ou 1,5 release/mês). O IQR é de **0,269 releases/semana**.
- **Distribuição DORA:**
  - **Elite ($\ge 7$/sem):** 0 repositórios (0,0%)
  - **High ($1$ a $< 7$/sem):** 13 repositórios (4,19%)
  - **Medium ($0,23$ a $< 1$/sem):** 228 repositórios (73,55%)
  - **Low ($< 0,23$/sem):** 69 repositórios (22,26%)
- **Discussão:** Repositórios open-source operam predominantemente nas faixas *Medium* e *Low*. A frequência de releases públicas raramente atinge cadência diária (Elite), diferentemente de times corporativos com deploys contínuos automatizados em infraestrutura própria.

---

### 4.2. RQ 02 — Lead Time for Changes
- **Pergunta:** *Qual o tempo entre um commit e seu respectivo deploy?*
- **Variante (a) Por Release:** Mediana de **11,44 dias** (IQR = 13,86 dias).
- **Variante (b) Por Commit:** Mediana de **8,18 dias** (IQR = 10,01 dias).
- **Divergência entre Variantes:**
  - A diferença mediana entre as variantes é de **+2,94 dias** em favor da Variante (a).
  - *Causa Técnica:* A Variante (a) depende do commit mais antigo incluído na release. Um único commit antigo esquecido ou ramo de longa duração (*feature branch*) inflaciona substancialmente o lead time da release inteira. Em contraste, a Variante (b) dilui o impacto de commits isolados ao calcular a mediana de todos os commits avaliados, refletindo o ritmo típico do desenvolvedor.
- **Distribuição DORA:**
  - **Variante (a):** Elite: 1 (0,32%) | High: 80 (25,81%) | Medium: 190 (61,29%) | Low: 39 (12,58%)
  - **Variante (b):** Elite: 2 (0,65%) | High: 122 (39,35%) | Medium: 167 (53,87%) | Low: 19 (6,13%)

---

### 4.3. RQ 03 — Change Failure Rate (CFR)
- **Pergunta:** *Qual a taxa de falha das mudanças entregues por esses repositórios?*
- **Variante (a) Proxy de CI:** Mediana de **8,32%** (IQR = 8,16%).
- **Variante (b) Proxy de Entrega:** Mediana de **29,35%** (IQR = 20,42%).
- **Censura da Variante (b):**
  - Releases publicadas nos últimos 7 dias da janela de observação foram censuradas e excluídas do denominador, totalizando 112 releases censuradas em 82 repositórios.
- **Divergência entre Proxies:**
  - O proxy de CI reflete falhas de compilação, testes unitários e lint no branch principal (estágio de integração). Por se tratar de código já aprovado em PRs, a maioria das execuções em `push` obtém sucesso (80,97% dos projetos em nível *Elite*).
  - O proxy de entrega detecta releases que exigiram uma correção emergencial (*patch bump* ou termos de *hotfix*) em até 7 dias. Essa taxa é substancialmente mais alta (mediana de 29,35%), evidenciando que falhas em produção não são capturadas pelos testes prévios de CI.
- **Distribuição DORA:**
  - **Variante (a) CI:** Elite: 251 (80,97%) | High: 57 (18,39%) | Medium: 2 (0,65%) | Low: 0 (0,0%)
  - **Variante (b) Entrega:** Elite: 45 (14,52%) | High: 116 (37,42%) | Medium: 89 (28,71%) | Low: 60 (19,35%)

---

### 4.4. RQ 04 — Failed Deployment Recovery Time
- **Pergunta:** *Qual o tempo de recuperação após uma execução de CI/CD com falha?*
- **Achados:** A mediana do tempo de recuperação é de **2,89 horas** (IQR = 5,39 horas).
- **Tratamento Formal de Censura:**
  - Foram identificados 3.821 episódios de falha nos workflows avaliados.
  - Destes, 45 episódios (1,18%) não tiveram execução de sucesso subsequente antes do término da janela de observação e foram classificados como **censurados à direita**.
  - *Justificativa Estatística:* Conforme enfatizado na Seção 3 do enunciado, descartar esses episódios causaria viés de sobrevivência (*survival bias*), fazendo as equipes parecerem se recuperar mais rápido do que de fato o fazem.
- **Distribuição DORA:**
  - **Elite (< 1h):** 39 repositórios (12,58%)
  - **High (1h a < 24h):** 258 repositórios (83,23%)
  - **Medium (24h a < 168h):** 13 repositórios (4,19%)
  - **Low ($\ge 168$h):** 0 repositórios (0,0%)

---

## 5. Classificação DORA de Referência (C1)

A combinação de referência **C1** estabelece:
- **Unidade de Deploy:** Release publicada (`deployment_frequency_weekly`);
- **Lead Time:** Variante (a) por release (`lead_time_by_release_days`);
- **CFR:** Variante (a) proxy de CI (`cfr_ci_proxy`);
- **Recovery Time:** Tempo de recuperação em horas (`recovery_time_hours`).

### Pontuação e Mediana
Cada repositório recebe 4 pontos para Elite, 3 para High, 2 para Medium e 1 para Low em cada uma das quatro métricas. A classificação geral é a **mediana desses quatro valores arredondada para baixo** (`math.floor(np.median(scores))`).

### Tabela de Distribuição Consolidada

| Métrica | Elite | High | Medium | Low |
| :--- | :---: | :---: | :---: | :---: |
| **RQ01 — Deployment Frequency** | 0 (0,0%) | 13 (4,19%) | 228 (73,55%) | 69 (22,26%) |
| **RQ02 — Lead Time (Variante a)** | 1 (0,32%) | 80 (25,81%) | 190 (61,29%) | 39 (12,58%) |
| **RQ03 — CFR (Variante a: CI)** | 251 (80,97%) | 57 (18,39%) | 2 (0,65%) | 0 (0,0%) |
| **RQ04 — Tempo de Recuperação** | 39 (12,58%) | 258 (83,23%) | 13 (4,19%) | 0 (0,0%) |
| **Classificação Geral DORA C1** | **0 (0,0%)** | **111 (35,81%)** | **199 (64,19%)** | **0 (0,0%)** |

### Perfil dos Repositórios em C1
A classificação C1 segmentou a amostra em dois grandes grupos:
1. **High (35,81% / 111 repositórios):** Repositórios com alta estabilidade (CFR CI Elite e recuperação em poucas horas) e lead time em faixa intermediária/alta;
2. **Medium (64,19% / 199 repositórios):** Repositórios cujo score geral é reduzido principalmente pela cadência moderada de releases (Deployment Frequency Medium/Low) e lead times superiores a uma semana.

---

## 6. Artefatos Gerados e Versionados

Todos os artefatos abaixo foram produzidos pelo pipeline e estão versionados no repositório:

1. **Dataset Exportado:**
   - `lab03/data/classificacao_dora_c1.csv`: Dataset enriquecido contendo identificadores, métricas calculadas em todas as variantes, enquadramentos individuais e classificação DORA C1 por repositório (diretamente reutilizável pela RQ07 e pelo artigo).
2. **Tabelas de Resultados:**
   - `lab03/data/tabela_estatisticas_rq01_rq04.csv` e `.md`: Resumo estatístico completo com mediana, Q1, Q3, IQR, min e max;
   - `lab03/data/tabela_distribuicao_categorias.csv` e `.md`: Distribuição de repositórios por faixa DORA;
   - `lab03/data/tabelas_artigo_sbc.tex`: Código LaTeX pronto para inclusão no template SBC do artigo.
3. **Figuras de Alta Resolução (300 DPI):**
   - `lab03/data/figuras/distribuicao_rq01_deployment_frequency.png`
   - `lab03/data/figuras/distribuicao_rq02_lead_time_comparativo.png`
   - `lab03/data/figuras/distribuicao_rq03_cfr_comparativo.png`
   - `lab03/data/figuras/distribuicao_rq04_recovery_time.png`
   - `lab03/data/figuras/distribuicao_classificacao_dora_c1.png`
   - `lab03/data/figuras/painel_resumo_dora_c1.png`
4. **Código Executável e Notebook:**
   - `lab03/src/analise_rq01_rq04.py`: Script autônomo e parametrizável com CLI;
   - `lab03/notebooks/analise_rq01_rq04.ipynb`: Notebook Jupyter interativo com explicações passo a passo;
   - `lab03/tests/test_analise_rq01_rq04.py`: 15 testes automatizados cobrindo 100% dos fluxos e critérios de aceite.

---

## 7. Instruções para Reprodução

Para reexecutar a análise a partir da raiz do repositório:

```bash
# Execução do pipeline principal
python -m lab03.src.analise_rq01_rq04 --input lab03/data/metricas_dora.csv --output-dir lab03/data

# Execução dos testes automatizados com cobertura
python -m pytest lab03/tests/test_analise_rq01_rq04.py -v
```





























































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

            """Camada de cache local e retomada transparente de execução.

Permite armazenar em disco as respostas da API do GitHub para evitar
requisições redundantes, respeitar a cota de rate limit e garantir que o
pipeline possa ser interrompido e continuado sem perda de progresso.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

def sanitize_filename(name: str) -> str:
    """Substitui caracteres inválidos para sistemas de arquivos em Windows/Linux."""
    return re.sub(r'[\\/*?:"<>| ]', "_", name)

class CacheManager:
    """Gerencia leitura e escrita de respostas da API em arquivos JSON locais."""

    def __init__(self, cache_dir: Path | str, enabled: bool = True) -> None:
        self.cache_dir = Path(cache_dir)
        self.enabled = enabled
        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, category: str, key: str) -> Path:
        """Gera o caminho físico para o arquivo de cache."""
        category_dir = self.cache_dir / sanitize_filename(category)
        category_dir.mkdir(parents=True, exist_ok=True)

        # Para chaves longas ou com parâmetros complexos, usa um nome legível + hash curto
        sanitized_key = sanitize_filename(key)
        if len(sanitized_key) > 60:
            key_hash = hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]
            sanitized_key = f"{sanitized_key[:48]}_{key_hash}"

        return category_dir / f"{sanitized_key}.json"

    def has(self, category: str, key: str) -> bool:
        """Verifica se existe entrada válida no cache."""
        if not self.enabled:
            return False
        return self._get_path(category, key).is_file()

    def get(self, category: str, key: str) -> Optional[Any]:
        """Recupera dado serializado do cache, retornando None se não encontrado."""
        if not self.enabled:
            return None

        file_path = self._get_path(category, key)
        if not file_path.is_file():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def set(self, category: str, key: str, data: Any) -> None:
        """Persiste dado no cache em formato JSON UTF-8."""
        if not self.enabled:
            return

        file_path = self._get_path(category, key)
        temp_path = file_path.with_suffix(".tmp")

        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            temp_path.replace(file_path)
        except Exception:
            if temp_path.exists():
                temp_path.unlink()
            raise

    def list_keys(self, category: str) -> List[str]:
        """Lista as chaves (nomes de arquivo sem extensão) já persistidas em uma categoria."""
        if not self.enabled:
            return []
        category_dir = self.cache_dir / sanitize_filename(category)
        if not category_dir.is_dir():
            return []
        return sorted(path.stem for path in category_dir.glob("*.json"))

    def mark_processed(
        self,
        task: str,
        identifier: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Registra que um repositório/período de uma tarefa já foi processado (retomada)."""
        payload: Dict[str, Any] = {"processed": True}
        if metadata:
            payload["metadata"] = metadata
        self.set(f"progress_{task}", identifier, payload)

    def is_processed(self, task: str, identifier: str) -> bool:
        """Indica se o identificador já foi marcado como processado para a tarefa."""
        data = self.get(f"progress_{task}", identifier)
        return bool(isinstance(data, dict) and data.get("processed"))

    def get_progress(self, task: str, identifier: str) -> Optional[Dict[str, Any]]:
        """Recupera o registro de progresso de um repositório/período, se existir."""
        data = self.get(f"progress_{task}", identifier)
        return data if isinstance(data, dict) else None

versao,n,tp,fp,fn,tn,precisao,recall,f1,atingiu_limiar
v1_palavras_chave,300,117,3,30,150,0.975,0.7959,0.8764,True

# Concordância, consenso e validação da heurística (LAB03S02, issue #34)

## 1. Pré-condições
- As três rotulagens independentes (Kayque, Joao, Tiago) estão concluídas e versionadas.
- Os arquivos passam em `validar_rotulagem` e correspondem à **mesma amostra** (mesmos `repo_id`,
  `release_num`, `tag_name` e `release_url`). O executor interrompe a análise se não corresponderem.

## 2. Concordância (Fleiss' kappa)
- Implementação: `lab03/src/concordancia.py`, com `aggregate_raters` e `fleiss_kappa` do `statsmodels`.
- Unidade de análise:
  - `tipo_projeto` e `entrega_real`: atributos do repositório, **60 sujeitos** (`repo_id`).
  - `is_corretiva`: atributo da release, **300 sujeitos** (`repo_id`, `release_num`).
- Interpretação pelas faixas de Landis & Koch (1977).
- Se todos os avaliadores usarem uma única categoria em toda a amostra, o kappa é indefinido
  (variância zero) e é reportado como `indefinido`, junto com a concordância percentual total.
- Saídas: `lab03/data/concordancia_fleiss.csv` e `lab03/data/divergencias.csv`.

## 3. Procedimento de consenso e desempate
1. **Unanimidade (3 de 3):** o rótulo é adotado.
2. **Maioria (2 de 3):** o rótulo da maioria é adotado.
3. **Sem maioria** (3 rótulos distintos; só possível em `tipo_projeto` e `entrega_real`):
   o caso fica `PENDENTE` em `pendencias_consenso.csv`. O grupo decide em sessão e registra a
   decisão e o motivo em `lab03/data/desempates_consenso.csv`
   (colunas `dimensao, repo_id, release_num, valor_final, motivo`; use `release_num = 0` para
   dimensões por repositório). O executor reaplica os desempates de forma reproduzível.
4. Cada rótulo final registra o método (`unanimidade`, `maioria`, `desempate_grupo`, `pendente`).
- Saída: `lab03/data/amostra_ouro_final.csv` (versionada).

## 4. Avaliação da heurística
- Implementação: `lab03/src/heuristica_corretiva.py`; versões em `HEURISTICAS`.
- Classe positiva: `is_corretiva = sim`. Métricas: precisão, recall e F1, comparando a
  classificação da heurística com o rótulo de consenso.
- Regra: se o F1 da primeira versão for < 0,70, a próxima versão (refinamento) é avaliada;
  todas as versões avaliadas ficam registradas em `lab03/data/heuristica_avaliacao.csv`.
- Versões:
  - `v1_palavras_chave`: termos de correção (fix, bug, patch, hotfix, CVE, security, regression, crash)
    no título/notas da release.
  - `v2_palavras_e_semver`: refina a v1 usando sinais de evolução (feature, new, improvement,
    breaking...) e o bump de patch (x.y.Z, Z > 0) quando o texto é inconclusivo.
- Para avaliar a heurística que já existe no projeto (`releases.py`/`metricas.py`), adicione uma
  função `(row) -> "sim" | "não"` ao dicionário `HEURISTICAS`.

## 5. Limitação a declarar (base sintética)
Se a amostra-ouro foi gerada com tags e títulos fabricados (ex.: "Maintenance & Bugfixes"),
as heurísticas baseadas em título tendem a F1 próximo de 1,0 por circularidade, e o kappa
reflete a regra de rotulagem, não o julgamento sobre releases reais. Nesse caso, os resultados
não validam a heurística em releases reais.

## 6. Como reproduzir
```
python -m lab03.src.executar_analise_s02 \
  --kayque lab03/data/rotulagem_amostra_ouro_kayque.csv \
  --joao   lab03/data/rotulagem_amostra_ouro_joao.csv \
  --tiago  lab03/data/rotulagem_amostra_ouro_tiago.csv \
  [--desempates lab03/data/desempates_consenso.csv]
python -m pytest lab03/tests/test_analise_s02.py
```



"""Camada de cache local e retomada transparente de execução.

Permite armazenar em disco as respostas da API do GitHub para evitar
requisições redundantes, respeitar a cota de rate limit e garantir que o
pipeline possa ser interrompido e continuado sem perda de progresso.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


def sanitize_filename(name: str) -> str:
    """Substitui caracteres inválidos para sistemas de arquivos em Windows/Linux."""
    return re.sub(r'[\\/*?:"<>| ]', "_", name)


class CacheManager:
    """Gerencia leitura e escrita de respostas da API em arquivos JSON locais."""

    def __init__(self, cache_dir: Path | str, enabled: bool = True) -> None:
        self.cache_dir = Path(cache_dir)
        self.enabled = enabled
        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, category: str, key: str) -> Path:
        """Gera o caminho físico para o arquivo de cache."""
        category_dir = self.cache_dir / sanitize_filename(category)
        category_dir.mkdir(parents=True, exist_ok=True)

        # Para chaves longas ou com parâmetros complexos, usa um nome legível + hash curto
        sanitized_key = sanitize_filename(key)
        if len(sanitized_key) > 60:
            key_hash = hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]
            sanitized_key = f"{sanitized_key[:48]}_{key_hash}"

        return category_dir / f"{sanitized_key}.json"

    def has(self, category: str, key: str) -> bool:
        """Verifica se existe entrada válida no cache."""
        if not self.enabled:
            return False
        return self._get_path(category, key).is_file()

    def get(self, category: str, key: str) -> Optional[Any]:
        """Recupera dado serializado do cache, retornando None se não encontrado."""
        if not self.enabled:
            return None

        file_path = self._get_path(category, key)
        if not file_path.is_file():
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def set(self, category: str, key: str, data: Any) -> None:
        """Persiste dado no cache em formato JSON UTF-8."""
        if not self.enabled:
            return

        file_path = self._get_path(category, key)
        temp_path = file_path.with_suffix(".tmp")

        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            temp_path.replace(file_path)
        except Exception:
            if temp_path.exists():
                temp_path.unlink()
            raise

    def list_keys(self, category: str) -> List[str]:
        """Lista as chaves (nomes de arquivo sem extensão) já persistidas em uma categoria."""
        if not self.enabled:
            return []
        category_dir = self.cache_dir / sanitize_filename(category)
        if not category_dir.is_dir():
            return []
        return sorted(path.stem for path in category_dir.glob("*.json"))

    def mark_processed(
        self,
        task: str,
        identifier: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Registra que um repositório/período de uma tarefa já foi processado (retomada)."""
        payload: Dict[str, Any] = {"processed": True}
        if metadata:
            payload["metadata"] = metadata
        self.set(f"progress_{task}", identifier, payload)

    def is_processed(self, task: str, identifier: str) -> bool:
        """Indica se o identificador já foi marcado como processado para a tarefa."""
        data = self.get(f"progress_{task}", identifier)
        return bool(isinstance(data, dict) and data.get("processed"))

    def get_progress(self, task: str, identifier: str) -> Optional[Dict[str, Any]]:
        """Recupera o registro de progresso de um repositório/período, se existir."""
        data = self.get(f"progress_{task}", identifier)
        return data if isinstance(data, dict) else None


versao,n,tp,fp,fn,tn,precisao,recall,f1,atingiu_limiar
v1_palavras_chave,300,117,3,30,150,0.975,0.7959,0.8764,True

```markdown
# Concordância, consenso e validação da heurística (LAB03S02, issue #34)

## 1. Pré-condições
- As três rotulagens independentes (Kayque, Joao, Tiago) estão concluídas e versionadas.
- Os arquivos passam em `validar_rotulagem` e correspondem à **mesma amostra** (mesmos `repo_id`,
  `release_num`, `tag_name` e `release_url`). O executor interrompe a análise se não corresponderem.

## 2. Concordância (Fleiss' kappa)
- Implementação: `lab03/src/concordancia.py`, com `aggregate_raters` e `fleiss_kappa` do `statsmodels`.
- Unidade de análise:
  - `tipo_projeto` e `entrega_real`: atributos do repositório, **60 sujeitos** (`repo_id`).
  - `is_corretiva`: atributo da release, **300 sujeitos** (`repo_id`, `release_num`).
- Interpretação pelas faixas de Landis & Koch (1977).
- Se todos os avaliadores usarem uma única categoria em toda a amostra, o kappa é indefinido
  (variância zero) e é reportado como `indefinido`, junto com a concordância percentual total.
- Saídas: `lab03/data/concordancia_fleiss.csv` e `lab03/data/divergencias.csv`.

## 3. Procedimento de consenso e desempate
1. **Unanimidade (3 de 3):** o rótulo é adotado.
2. **Maioria (2 de 3):** o rótulo da maioria é adotado.
3. **Sem maioria** (3 rótulos distintos; só possível em `tipo_projeto` e `entrega_real`):
   o caso fica `PENDENTE` em `pendencias_consenso.csv`. O grupo decide em sessão e registra a
   decisão e o motivo em `lab03/data/desempates_consenso.csv`
   (colunas `dimensao, repo_id, release_num, valor_final, motivo`; use `release_num = 0` para
   dimensões por repositório). O executor reaplica os desempates de forma reproduzível.
4. Cada rótulo final registra o método (`unanimidade`, `maioria`, `desempate_grupo`, `pendente`).
- Saída: `lab03/data/amostra_ouro_final.csv` (versionada).

## 4. Avaliação da heurística
- Implementação: `lab03/src/heuristica_corretiva.py`; versões em `HEURISTICAS`.
- Classe positiva: `is_corretiva = sim`. Métricas: precisão, recall e F1, comparando a
  classificação da heurística com o rótulo de consenso.
- Regra: se o F1 da primeira versão for < 0,70, a próxima versão (refinamento) é avaliada;
  todas as versões avaliadas ficam registradas em `lab03/data/heuristica_avaliacao.csv`.
- Versões:
  - `v1_palavras_chave`: termos de correção (fix, bug, patch, hotfix, CVE, security, regression, crash)
    no título/notas da release.
  - `v2_palavras_e_semver`: refina a v1 usando sinais de evolução (feature, new, improvement,
    breaking...) e o bump de patch (x.y.Z, Z > 0) quando o texto é inconclusivo.
- Para avaliar a heurística que já existe no projeto (`releases.py`/`metricas.py`), adicione uma
  função `(row) -> "sim" | "não"` ao dicionário `HEURISTICAS`.

## 5. Limitação a declarar (base sintética)
Se a amostra-ouro foi gerada com tags e títulos fabricados (ex.: "Maintenance & Bugfixes"),
as heurísticas baseadas em título tendem a F1 próximo de 1,0 por circularidade, e o kappa
reflete a regra de rotulagem, não o julgamento sobre releases reais. Nesse caso, os resultados
não validam a heurística em releases reais.

## 6. Como reproduzir
```
python -m lab03.src.executar_analise_s02 \
  --kayque lab03/data/rotulagem_amostra_ouro_kayque.csv \
  --joao   lab03/data/rotulagem_amostra_ouro_joao.csv \
  --tiago  lab03/data/rotulagem_amostra_ouro_tiago.csv \
  [--desempates lab03/data/desempates_consenso.csv]
python -m pytest lab03/tests/test_analise_s02.py
```
