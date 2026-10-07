# Guia de Execução e Arquitetura - Seleção de Repositórios (LAB03)

Este guia documenta o módulo de **Seleção de Repositórios e Funil de Coleta** (Issue #26 / Lab03S01), detalhando requisitos, execução padronizada, arquitetura de cache e integração com os demais módulos do grupo.

---

## 1. Requisitos e Configuração do Ambiente

O projeto requer **Python 3.10+**.

### 1.1. Instalação das Dependências

A partir da raiz do repositório:
```powershell
pip install -r lab03/requirements.txt
```

### 1.2. Configuração do `GITHUB_TOKEN`

Por exigência de segurança e integridade do laboratório, **nenhuma credencial pode ser commitada**. O módulo busca o token nas seguintes origens (em ordem de prioridade):
1. Variável de ambiente `GITHUB_TOKEN`.
2. Arquivo `lab03/.env`.
3. Arquivo `.env` na raiz do repositório.
4. Arquivo `lab01/.env` (legado).

Para configurar via variável de ambiente no PowerShell:
```powershell
$env:GITHUB_TOKEN = "seu_token_aqui"
```
Ou criando um arquivo `.env` a partir do template:
```powershell
Copy-Item lab03/.env.example lab03/.env
# Edite lab03/.env inserindo seu token
```

---

## 2. Execução do Pipeline de Seleção

O módulo é executável diretamente via linha de comando através de um único comando:

```powershell
python -m lab03.src.selecao_repositorios
```

### 2.1. Parâmetros Opcionais (CLI)

| Parâmetro | Descrição | Padrão |
|---|---|---|
| `--target <int>` | Quantidade desejada de repositórios qualificados a selecionar. | 100 (S01) / 300 (S02) |
| `--candidate-limit <int>` | Limite máximo de candidatos minerados na busca prévia por estrelas. | 500 |
| `--config <path>` | Caminho para arquivo de configuração alternativo. | `lab03/config.yaml` |
| `--no-cache` | Desativa o uso do cache em disco, forçando requisições à API. | Falso (cache ativado) |

**Exemplo de teste rápido com 10 repositórios:**
```powershell
python -m lab03.src.selecao_repositorios --target 10 --candidate-limit 100
```

---

## 3. Funcionamento do Cache e Retomada (*Resume*)

Para economizar a cota horária da API do GitHub e viabilizar coletas longas sem risco de perda por falha de rede ou interrupção voluntária (`Ctrl+C`):

- Toda resposta HTTP com status 200 é serializada em formato JSON na pasta `lab03/data/cache/`.
- O diretório de cache é segmentado por categoria:
  - `cache/search/`: Listas de repositórios retornadas pela busca de estrelas.
  - `cache/workflows/`: Definições de workflows de CI/CD por repositório.
  - `cache/releases/`: Páginas de releases paginadas.
  - `cache/workflow_runs/`: Execuções de CI na branch padrão.
  - `cache/contributors_count/`: Total estimado de contribuidores.
- Ao reexecutar o pipeline, requisições cujo resultado já se encontra em disco são lidas instantaneamente sem qualquer consumo de requisições da cota da API.

---

## 4. Execução dos Testes Automatizados e Cobertura

Os testes unitários utilizam `pytest` e *fixtures* mockadas, garantindo execução ultrarrápida sem depender de conexão de rede ou consumo de cota:

```powershell
pytest lab03/tests -v --cov=lab03/src --cov-report=term-missing --cov-fail-under=80
```

Critérios verificados:
- Tratamento de cabeçalhos de Rate Limit (`X-RateLimit-Remaining` e `X-RateLimit-Reset`).
- Backoff exponencial em falhas transitórias (códigos 429, 403 e 5xx).
- Paginação baseada no cabeçalho HTTP `Link: rel="next"`.
- Contagem inteligente de contribuidores via `Link: rel="last"`.
- Validação das regras de inclusão e descarte do funil (Releases $\ge 5$, Runs $\ge 50$, GitHub Actions $\ge 1$).
- Cobertura de testes superior a 80%.

---

## 5. Interface com os Demais Integrantes (Sprints S01 e S02)

O módulo de seleção atua como **ponto de partida e fornecedor oficial dos dados amostrais** para as demais frentes:

1. **Integrante B (Issue #28 - Releases e Lead Time):**
   - Lê a lista de repositórios qualificados em `lab03/data/repositorios_selecionados.csv` (`owner`, `name`, `default_branch`).
   - Para cada repositório já aprovado, coleta o histórico aprofundado de commits entre releases consecutivas para calcular o *Lead Time for Changes*.
2. **Integrante C (Issue #27 - Workflow Runs, CFR e Tempo de Recuperação):**
   - Utiliza a mesma lista de repositórios aprovados em `lab03/data/repositorios_selecionados.csv`.
   - Utiliza a infraestrutura compartilhada de `CacheManager` e `GitHubClient` para coletar os workflow runs detalhados e computar o CFR (variante CI) e o *Failed Deployment Recovery Time*.
