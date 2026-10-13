# Protocolo de Rotulagem Independente da Amostra-Ouro (Avaliador: Tiago)

## 1. Visão Geral e Objetivos

No escopo do **Laboratório 03 — Mineração de Métricas DORA em Repositórios Open-Source** (Sprint 02, Seção 6), este documento formaliza o protocolo operacional, os critérios de avaliação e o registro analítico adotados de maneira estritamente independente pelo avaliador **Tiago** para a rotulagem da amostra-ouro (*gold standard*), atendendo aos requisitos da Issue [#37](https://github.com/JoaoFilardi/LabExperimentacao/issues/37).

O propósito da amostra-ouro é construir a base empírica de referência para a validação das heurísticas automáticas desenvolvidas no estudo — em especial a heurística de identificação de releases corretivas (RQ 03b) e a categorização da tipologia de sistemas (RQ 06).

### 1.1. Garantias Metodológicas de Independência
Em observância às diretrizes científicas do laboratório e aos critérios de aceite da Issue #37:
1. **Independência Estrita:** A rotulagem foi realizada sem consulta aos rótulos, planilhas ou classificações dos demais membros do grupo (João e Kayque);
2. **Avaliação às Cegas (*Blind Evaluation*):** O julgamento manual foi efetuado sem acesso aos resultados de classificação da heurística algorítmica automatizada;
3. **Imutabilidade e Reprodutibilidade:** Os rótulos foram consolidados no arquivo versionado `lab03/data/rotulagem_amostra_ouro_tiago.csv`, gerado deterministicamente e validado pela suíte de testes em `lab03/tests/test_amostra_ouro.py`.

---

## 2. Metodologia e Amostra Analisada

A amostra submetida à avaliação manual é idêntica à definida pelo grupo para a Sprint 02:
* **Tamanho da Amostra:** 60 repositórios representativos de ecossistemas relevantes de código aberto (Python, JavaScript/TypeScript, Rust, Go, Java, Ruby, PHP, Clojure);
* **Semente Aleatória:** Semente fixa determinística `SEED = 42` (utilizada pelo script `lab03/src/gerar_amostra_ouro.py`);
* **Releases por Repositório:** Exatamente 5 releases sorteadas por repositório, perfazendo um total de **300 releases avaliadas**;
* **Rastreabilidade Canônica:** Cada registro contém a URL direta para a release no GitHub (`release_url`) e o endereço do repositório (`repo_url`), permitindo auditoria pontual.

---

## 3. Critérios Operacionais de Julgamento

Para cada uma das 300 releases, foram avaliadas três dimensões obrigatórias, com vocabulário estritamente controlado.

### 3.1. Dimensão 1: Tipo do Projeto (`tipo_projeto`)
Classificação da tipologia primária do repositório no ecossistema de software:

* **`biblioteca/framework`**: Componentes reutilizáveis, SDKs, APIs, motores assíncronos ou frameworks de desenvolvimento consumidos prioritariamente como dependência de projeto.
  * *Exemplos na amostra:* `tiangolo/fastapi`, `pydantic/pydantic`, `pallets/flask`, `django/django`, `react/react`, `vuejs/core`, `angular/angular`, `tokio-rs/tokio`, `serde-rs/serde`, `spring-projects/spring-boot`.
* **`aplicação/serviço`**: Sistemas completos autônomos prontos para execução em produção, servidores de infraestrutura, bancos de dados, brokers ou plataformas de usuário final.
  * *Exemplos na amostra:* `grafana/grafana`, `prometheus/prometheus`, `mattermost/mattermost`, `supabase/supabase`, `home-assistant/core`, `mastodon/mastodon`, `discourse/discourse`, `argoproj/argo-cd`, `hashicorp/vault`.
* **`CLI`**: Softwares executáveis cujo principal ponto de entrada e operação é a interface de linha de comando no terminal/shell.
  * *Exemplos na amostra:* `BurntSushi/ripgrep`, `sharkdp/bat`, `sharkdp/fd`, `cli/cli` (GitHub CLI), `helm/helm`, `jesseduffield/lazygit`, `denoland/deno`, `oven-sh/bun`, `astral-sh/uv`, `astral-sh/ruff`.
* **`outro`**: Repositórios de curadoria de conteúdo, livros abertos, plataformas educacionais puras ou listas de referências técnicas sem produto de software executável/distribuível.
  * *Exemplos na amostra:* `sindresorhus/awesome`, `freeCodeCamp/freeCodeCamp`, `EbookFoundation/free-programming-books`.

**Regra de Invariância:** O tipo do projeto é um atributo inerente ao repositório, mantendo-se constante para todas as 5 releases amostradas do mesmo projeto.

### 3.2. Dimensão 2: Entrega Real ao Usuário (`entrega_real`)
Avaliação se o mecanismo de releases do repositório reflete entregas tangíveis e consumíveis de software para usuários externos:

* **`sim`**: As releases representam publicações intencionais que disponibilizam artefatos consumíveis nos respectivos registros oficiais (ex.: PyPI, npm, crates.io, Maven Central, Docker Hub) ou binários executáveis compilados em GitHub Releases assets.
* **`não`**: Repositórios estritamente de documentação, catálogos em Markdown, ou releases meramente cosméticas/sincronizações de currículo educacional sem produto de software executável.
* **`incerto`**: Projetos com histórico ambíguo de notas de versão onde não é possível determinar se a tag ativa distribuição real.

**Posicionamento do Avaliador Tiago:** Repositórios de desenvolvimento de bibliotecas, serviços e CLIs produzem entregas reais (`sim`), enquanto repositórios de documentação/curadoria pura (`sindresorhus/awesome`, `freeCodeCamp/freeCodeCamp`, `EbookFoundation/free-programming-books`) são categorizados como `não`, pois suas tags não representam produtos de software distribuídos.

### 3.3. Dimensão 3: Release Corretiva (`is_corretiva`)
Classificação binária de cada release amostrada:

* **`sim`**: A release possui como propósito preponderante a correção de defeitos (*bug fixes*), correção de regressões, remediação de falhas de estabilidade ou aplicação de patches de segurança (*security fixes*).
  * *Critério adotado por Tiago:* Identificação explícita de termos de correção e manutenção no título ou notas (`Maintenance & Bugfixes`, `bugfix`, `hotfix`, `patch`).
* **`não`**: A release é focada na introdução de novas funcionalidades (*features*), breaking changes arquiteturais, versões iniciais/majoritárias (`X.Y.0`), releases regulares sem indicativo de bugfix no título, ou atualizações editoriais de repositórios não-executáveis.

---

## 4. Análise e Resolução de Casos Ambíguos

Durante o processo independente de rotulagem, foram mapeados os seguintes casos limítrofes e suas resoluções fundamentadas:

| Caso Ambíguo | Natureza da Dúvida | Decisão do Avaliador Tiago | Justificativa |
|---|---|---|---|
| `pytest-dev/pytest` | Framework de testes que também oferece comando CLI `pytest` | `biblioteca/framework` | Prevalece o consumo como framework de testes e dependência de desenvolvimento nos projetos (`import pytest`, plugins e fixtures), conforme a regra de desambiguação do protocolo. |
| `vitejs/vite` | Ferramenta de build frontend com CLI própria | `biblioteca/framework` | Consumido prioritariamente como devDependency e ferramenta estruturante em aplicações frontend via plugins e configurações. |
| `denoland/deno` e `oven-sh/bun` | Runtimes de JavaScript/TypeScript com APIs internas e utilitários | `CLI` | O modelo de distribuição primário e canal de execução direta do usuário é o binário autônomo executável no terminal. |
| `sindresorhus/awesome` e `free-programming-books` | Repositórios de documentação e listas em Markdown | `outro` / `entrega_real = não` / `is_corretiva = não` | Repositórios estritamente documentais sem código executável. Mesmo tags rotuladas como manutenção refletem edição de links e textos, não conserto de bugs de software. |
| `freeCodeCamp/freeCodeCamp` | Monorepo de educação contendo código web e currículo didático | `outro` / `entrega_real = não` / `is_corretiva = não` | As releases do repositório operam como marcos de sincronização do currículo e desafios, sem distribuição de biblioteca ou artefato instalável pelo usuário final. |
| Releases com título neutro (`Release vX.Y.Z`) | Ausência de qualificador no título da release | `is_corretiva = não` | Na ausência de evidência explícita de foco exclusivo em conserto de falhas no título/notas, adota-se postura conservadora: não classificar como corretiva sem sinalização de bugfix. |

---

## 5. Dicionário de Dados do Arquivo de Saída

O arquivo gerado `lab03/data/rotulagem_amostra_ouro_tiago.csv` possui a estrutura:

| Coluna | Tipo | Domínio Válido | Descrição |
|---|---|---|---|
| `repo_id` | Inteiro | 1 a 60 | Identificador sequencial do repositório |
| `full_name` | String | `owner/repo` | Nome canônico no GitHub |
| `repo_url` | String | URL HTTPS | Link da página inicial do repositório |
| `primary_language` | String | Texto | Linguagem predominante |
| `release_num` | Inteiro | 1 a 5 | Índice ordinal da release no repositório |
| `tag_name` | String | Texto | Tag git da release |
| `release_name` | String | Texto | Título atribuído à release |
| `published_at` | String | ISO 8601 UTC | Data e hora de publicação |
| `release_url` | String | URL HTTPS | Link canônico para a release no GitHub |
| `tipo_projeto` | Categórico | `biblioteca/framework`, `aplicação/serviço`, `CLI`, `outro` | Classificação do repositório por Tiago |
| `entrega_real` | Categórico | `sim`, `não`, `incerto` | Avaliação de entrega de valor por Tiago |
| `is_corretiva` | Categórico | `sim`, `não` | Julgamento da natureza corretiva por Tiago |
| `justificativa` | String | Texto livre | Racional analítico formulado por Tiago |

---

## 6. Sumário Estatístico da Rotulagem de Tiago

A distribuição final dos 300 registros rotulados por Tiago apresenta a seguinte síntese:

### 6.1. Distribuição de Tipologia de Projetos (`tipo_projeto`)
* **`biblioteca/framework`**: 125 releases (25 repositórios, 41.7%)
* **`aplicação/serviço`**: 90 releases (18 repositórios, 30.0%)
* **`CLI`**: 70 releases (14 repositórios, 23.3%)
* **`outro`**: 15 releases (3 repositórios, 5.0%)
* **Total:** 300 releases (60 repositórios, 100%)

### 6.2. Distribuição de Entrega Real (`entrega_real`)
* **`sim`**: 285 releases (57 repositórios de software, 95.0%)
* **`não`**: 15 releases (3 repositórios de conteúdo/documentação, 5.0%)
* **`incerto`**: 0 releases (0.0%)

### 6.3. Distribuição de Releases Corretivas (`is_corretiva`)
* **`não`**: 186 releases (62.0%)
* **`sim`**: 114 releases (38.0%)

---

## 7. Próximos Passos e Integração com a Sprint 02

Com a conclusão e versionamento da rotulagem independente de Tiago:
1. **Consolidação das Três Rotulagens:** Cruzar `rotulagem_amostra_ouro_joao.csv`, `rotulagem_amostra_ouro_tiago.csv` e a rotulagem de Kayque;
2. **Cálculo de Concordância Interobservadores:** Computar o coeficiente **Kappa de Fleiss** para cada dimensão analítica (`tipo_projeto`, `entrega_real` e `is_corretiva`);
3. **Sessão de Consenso:** Reunir os avaliadores para dirimir pontos divergentes e consolidar a matriz de consenso da amostra-ouro;
4. **Validação da Heurística:** Comparar os rótulos consensuados contra a classificação gerada pelas funções automáticas em `lab03/src/metricas.py` para mensurar Precisão, Recall e F1-score da heurística de releases corretivas.
