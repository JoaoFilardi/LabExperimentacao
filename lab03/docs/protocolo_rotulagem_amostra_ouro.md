# Protocolo de Rotulagem Independente da Amostra-Ouro (Avaliador: João)

## 1. Visão Geral e Objetivos

No âmbito do **Laboratório 03 — Mineração de Métricas DORA em Repositórios Open-Source** (Sprint 02, Seção 6), este documento formaliza o protocolo operacional e os critérios de julgamento adotados de forma independente pelo integrante **João** para a rotulagem da amostra-ouro (*gold standard*).

O objetivo da amostra-ouro é validar empiricamente as heurísticas automatizadas de classificação — em particular a heurística de identificação de releases corretivas (RQ 03b) e a categorização de tipologia de sistemas (RQ 06). Para garantir a integridade metodológica e mitigar viés de confirmação:
1. A rotulagem foi realizada de modo **independente**, sem comunicação prévia com os demais avaliadores sobre casos específicos antes da consolidação;
2. A rotulagem foi realizada **às cegas** em relação à classificação da heurística automatizada;
3. O conjunto de dados resultante (`lab03/data/rotulagem_amostra_ouro_joao.csv`) servirá de entrada direta para o cálculo do coeficiente **Kappa de Fleiss** de concordância interobservadores e para a construção da matriz de consenso.

---

## 2. Metodologia de Amostragem

Conforme estipulado no enunciado do laboratório:
* **Tamanho da amostra:** 60 repositórios sorteados da amostra de repositórios do laboratório;
* **Semente pseudoaleatória:** Semente determinística fixa `random_state = 42` (utilizando `pandas.DataFrame.sample(n=60, random_state=42)` ou amostragem balanceada por linguagem e domínio quando aplicável);
* **Amostragem de releases:** Exatamente 5 releases sorteadas por repositório, totalizando **300 releases avaliadas**;
* **Rastreabilidade:** Cada release na amostra possui sua URL direta canônica para a página de releases do GitHub (`release_url`), viabilizando auditoria direta e consulta às *release notes* e commits.

O script reprodutível de geração da base encontra-se em `lab03/src/gerar_amostra_ouro.py`, gerando a base neutra em `lab03/data/amostra_ouro_base.csv`.

---

## 3. Critérios Operacionais de Rotulagem

Para cada uma das 300 releases (60 repositórios), foram avaliadas três dimensões obrigatórias, com vocabulário estritamente controlado para permitir agregação matemática.

### 3.1. Dimensão 1: Tipo do Projeto (`tipo_projeto`)
Classificação do repositório quanto à sua natureza primária de uso no ecossistema de software:

* **`biblioteca/framework`**: Componentes reutilizáveis, SDKs, APIs de código, frameworks de desenvolvimento web/dados e bibliotecas utilitárias destinados a serem importados e consumidos como dependência em outros projetos.
  * *Exemplos:* `tiangolo/fastapi`, `pydantic/pydantic`, `pallets/flask`, `numpy/numpy`, `facebook/react`, `pandas-dev/pandas`.
* **`aplicação/serviço`**: Softwares completos de usuário final ou serviços de infraestrutura/backend prontos para execução autônoma (servidores web, brokers de mensageria, bancos de dados, plataformas web, painéis analíticos, etc.).
  * *Exemplos:* `home-assistant/core`, `discourse/discourse`, `grafana/grafana`, `supabase/supabase`, `mattermost/mattermost-server`.
* **`CLI`**: Ferramentas de linha de comando cujo principal canal de interação é o terminal/shell, fornecendo comandos executáveis, linters, empacotadores ou utilitários de sistema.
  * *Exemplos:* `cli/cli` (GitHub CLI), `httpie/cli`, `denoland/deno`, `sharkdp/bat`, `junegunn/fzf`.
* **`outro`**: Repositórios educacionais, curadorias de conteúdo ("awesome lists"), livros abertos, boilerplates ou especificações técnicas que não se encaixam prioritariamente como biblioteca, aplicação ou CLI.
  * *Exemplos:* `freeCodeCamp/freeCodeCamp`, `EbookFoundation/free-programming-books`.

**Regra de Desambiguação:** Caso um projeto ofereça tanto uma biblioteca quanto um executável CLI secundário (ex.: um parser que tem CLI de conveniência), prevalece o modo primário de consumo pretendido pelos desenvolvedores.

### 3.2. Dimensão 2: Entrega Real ao Usuário (`entrega_real`)
Avaliação se o mecanismo de releases do repositório reflete entregas tangíveis de valor para usuários externos:

* **`sim`**: As releases representam publicações intencionais contendo changelog/release notes, binários compilados, empacotamento distribuível (ex.: PyPI, npm, Docker hub) ou tags que ativam pipelines de entrega em produção.
* **`não`**: Releases meramente cosméticas, criadas exclusivamente para bumps de versão automatizados sem mudanças funcionais relevantes, tags internas de CI/CD que não resultam em artefato consumível, ou repositórios estritamente de documentação sem produto executável.
* **`incerto`**: Casos em que não há histórico suficiente de notas de release, repositórios sem descrição de entrega ou com comportamento de publicação ambíguo entre branches de desenvolvimento e branches de entrega.

### 3.3. Dimensão 3: Release Corretiva (`is_corretiva`)
Classificação binária da release amostrada:

* **`sim`**: A release tem como propósito preponderante a correção de defeitos (*bug fixes*), regressões, vulnerabilidades de segurança (*security patches*) ou falhas de estabilidade operacional.
  * *Sinais investigados:* Menção explícita a termos como `fix`, `bug`, `patch`, `hotfix`, `CVE`, `security`, `regression`, ou notas de versão concentradas em consertos de defeitos reportados por usuários/issues fechadas.
* **`não`**: A release é focada na introdução de novas funcionalidades (*features*), breaking changes arquiteturais, refatorações amplas, atualizações de documentação ou versões iniciais/majoritárias (`v1.0.0`, `v2.0.0`, etc.) sem foco primário em mitigação de falhas prévias.

---

## 4. Dicionário de Dados do Arquivo de Saída

O arquivo `lab03/data/rotulagem_amostra_ouro_joao.csv` contém as seguintes colunas padronizadas:

| Coluna | Tipo | Domínio / Formato | Descrição |
|---|---|---|---|
| `repo_id` | Inteiro | 1 a 60 | Identificador sequencial do repositório na amostra |
| `full_name` | String | `owner/repo` | Nome completo do repositório no GitHub |
| `repo_url` | String | URL HTTP(S) | Link para a página principal do repositório |
| `primary_language` | String | Texto | Linguagem primária do repositório |
| `release_num` | Inteiro | 1 a 5 | Índice ordinal da release sorteada no repositório |
| `tag_name` | String | Texto | Tag git correspondente à release sorteada |
| `release_name` | String | Texto | Título atribuído à release |
| `published_at` | String | ISO 8601 UTC | Carimbo de data/hora de publicação da release |
| `release_url` | String | URL HTTP(S) | Link direto para a página da release no GitHub |
| `tipo_projeto` | Categórico | `biblioteca/framework`, `aplicação/serviço`, `CLI`, `outro` | Julgamento manual do tipo de software |
| `entrega_real` | Categórico | `sim`, `não`, `incerto` | Julgamento sobre representatividade da entrega |
| `is_corretiva` | Categórico | `sim`, `não` | Julgamento se a release é corretiva |
| `justificativa` | String | Texto livre | Racional detalhado adotado pelo avaliador |

---

## 5. Próximos Passos na Sprint 02

Com a conclusão da rotulagem independente de João:
1. **Recepção dos rótulos dos pares:** Aguardar a disponibilização das rotulagens independentes dos colegas (`rotulagem_amostra_ouro_<colega1>.csv` e `rotulagem_amostra_ouro_<colega2>.csv`);
2. **Cálculo do Kappa de Fleiss:** Executar a análise de concordância interobservadores para as três dimensões (`aggregate_raters` e `fleiss_kappa` do `statsmodels`);
3. **Consolidação do Consenso:** Em reunião do grupo, discutir casos divergentes e aplicar o protocolo de consenso;
4. **Avaliação da Heurística:** Calcular Precisão, Recall e F1-score da heurística automatizada de releases corretivas frente ao padrão-ouro consensuado.
