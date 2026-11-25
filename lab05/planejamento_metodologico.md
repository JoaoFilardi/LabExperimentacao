# Planejamento Metodológico da Pesquisa

**Experimento:** Comparação de desempenho e consumo de recursos entre PostgreSQL 17 e PostgreSQL 18  
**Issue:** `#63` — `[ LAB05S01 ] Definir o planejamento e método da pesquisa`  
**Responsável:** Integrante A — Planejamento e Método (João Victor Filardi Souza Pinto)  
**Sprint:** 1 (`LAB05S01`)  
**Data:** 25/11/2026  

---

## 1. Software Escolhido e Justificativa

### 1.1 Objeto de estudo

O software selecionado pela equipe é o **PostgreSQL**, um Sistema Gerenciador de Banco de Dados (SGBD) objeto-relacional de código aberto, amplamente adotado em sistemas críticos de produção.

O estudo compara o comportamento em execução de duas versões principais (*major versions*) oficialmente mantidas do software:

- **Tratamento A (Linha de base):** **PostgreSQL 17** (série atual `17.12`).
- **Tratamento B (Comparação):** **PostgreSQL 18** (série atual `18.7`).

> **Aderência às regras do LAB05:** o objeto de pesquisa **não** é o repositório público do PostgreSQL no GitHub (não há mineração de commits, issues, pull requests ou análise estática de código-fonte). O objeto de estudo é o **software real em funcionamento**, executando transações de banco de dados em ambiente controlado via containers Docker com imagens oficiais.

### 1.2 Por que escolher o PostgreSQL e comparar as versões 17 e 18?

1. **Relevância prática e aderência ao enunciado:** o PostgreSQL é um dos SGBDs mais utilizados no mundo em ambientes corporativos e de nuvem, atendendo integralmente aos critérios de software **real**, **em operação** e de **alto impacto**.
2. **Motivação técnica da comparação 17 × 18:** o PostgreSQL 18 introduziu mudanças arquiteturais relevantes voltadas a desempenho, com destaque para o subsistema nativo de **I/O Assíncrono (AIO)** para operações de leitura (configurável via parâmetro `io_method`, com modos `sync`, `worker` e `io_uring`), além de melhorias no planejador e executor de consultas (Documentação oficial de release do PostgreSQL 18). Investigar empiricamente se essas mudanças produzem diferenças mensuráveis de latência, vazão (TPS) e consumo de CPU/memória sob uma mesma carga controlada gera conhecimento diretamente útil para decisões de migração.
3. **Observabilidade e reprodutibilidade:** o próprio PostgreSQL distribui o utilitário oficial `pgbench` para execução de cargas transacionais reproduzíveis e disponibiliza imagens oficiais no Docker Hub com tags explícitas por versão, permitindo isolar variáveis e repetir medições de forma auditável.
4. **Nota sobre o ciclo de versões:** em **19/11/2026** foi lançado o PostgreSQL `19.0`. Ainda assim, a comparação **PostgreSQL 17 × PostgreSQL 18** permanece metodologicamente recomendada e alinhada às decisões registradas pela equipe (`contextualizacao_lab05_postgresql.md` e `planejamento_analise_estatistica.md`), pois ambas são versões maduras, com múltiplos ciclos de correções menores (`17.12` e `18.7`), suporte ativo garantido até 2029 e 2030 e ampla presença em ambientes de produção atuais.

---

## 2. Comprovação dos Três Critérios (Real, Em Operação e Alto Impacto)

Todas as fontes abaixo foram verificadas em **25/11/2026**.

| Critério | Evidência objetiva | Fonte verificada | Data de acesso |
| :--- | :--- | :--- | :---: |
| **Real** | SGBD objeto-relacional open source com mais de **40 anos de desenvolvimento ativo** (origem em 1986 no projeto POSTGRES, UC Berkeley), compatível com propriedades **ACID** desde 2001, mantido pelo *PostgreSQL Global Development Group* com governança pública, documentação extensa e ferramenta oficial de benchmark (`pgbench`). | [PostgreSQL — About](https://www.postgresql.org/about/), [Documentação oficial](https://www.postgresql.org/docs/), [Documentação do pgbench](https://www.postgresql.org/docs/current/pgbench.html) e [Patrocinadores oficiais](https://www.postgresql.org/about/sponsors/) | 25/11/2026 |
| **Em operação** | Política formal de suporte de **5 anos** por versão principal com lançamentos menores regulares de correção e segurança. **PostgreSQL 17:** lançado em `26/09/2024`, versão menor atual **`17.12`** (`12/11/2026`), suportado até `08/11/2029`. **PostgreSQL 18:** lançado em `25/09/2025`, versão menor atual **`18.7`** (`12/11/2026`), suportado até `14/11/2030`. **PostgreSQL 19:** lançado em `19/11/2026` (`19.0`). Imagem oficial no Docker Hub (`library/postgres`) atualizada em **`24/11/2026`**. | [PostgreSQL — Versioning Policy](https://www.postgresql.org/support/versioning/) e [Docker Hub — Official Postgres Image](https://hub.docker.com/_/postgres) | 25/11/2026 |
| **Alto impacto** | **#1 banco de dados mais utilizado** no *Stack Overflow Developer Survey 2026* (**57,9%**; `6.984` respondentes, à frente de SQLite com `42,1%` e MySQL com `35,1%`), mantendo a liderança registrada em 2025 (**55,6%** geral / **58,2%** entre desenvolvedores profissionais). **4º lugar global** no *DB-Engines Ranking* (score **689,69**, crescimento de **+38,32 pontos** em 12 meses, próximo ao 3º colocado SQL Server com `693,53`) e eleito **DBMS of the Year** cinco vezes (2017, 2018, 2020, 2023 e 2024). Mais de **12,7 bilhões de pulls** (`12.728.966.579` pulls e `15.060` estrelas) na imagem oficial `postgres` do Docker Hub. | [Stack Overflow Developer Survey 2026](https://survey.stackoverflow.co/2026/technology/), [Stack Overflow Developer Survey 2025](https://survey.stackoverflow.co/2025/technology/), [DB-Engines Ranking](https://db-engines.com/en/ranking) e [Docker Hub API — library/postgres](https://hub.docker.com/v2/repositories/library/postgres/) | 25/11/2026 |

### Síntese das versões oficiais mantidas (PostgreSQL Versioning Policy)

| Versão Principal | Versão Menor Atual | Suportada | Lançamento Inicial | Fim de Suporte (EOL) | Papel no Estudo |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **19** | `19.0` | Sim | 19/11/2026 | 19/11/2031 | Fora do escopo (lançamento muito recente) |
| **18** | `18.7` | Sim | 25/09/2025 | 14/11/2030 | **Tratamento B** |
| **17** | `17.12` | Sim | 26/09/2024 | 08/11/2029 | **Tratamento A (Linha de base)** |
| **16** | `16.16` | Sim | 14/09/2023 | 09/11/2028 | Fora do escopo |
| **15** | `15.20` | Sim | 13/10/2022 | 11/11/2027 | Fora do escopo |

*Fonte: [https://www.postgresql.org/support/versioning/](https://www.postgresql.org/support/versioning/) (acesso em 25/11/2026).*

---

## 3. Pergunta de Pesquisa

### 3.1 Pergunta principal (RQ)

> **RQ:** *A versão 18 do PostgreSQL apresenta diferenças de desempenho e eficiência no uso de recursos computacionais em comparação com a versão 17, sob uma carga de trabalho controlada?*

A formulação é **intencionalmente neutra e bilateral**: o estudo não pressupõe que o PostgreSQL 18 seja superior ao PostgreSQL 17. Uma resposta cientificamente válida pode indicar melhora em determinadas métricas, piora em outras, ausência de diferença estatisticamente detectável ou diferença estatisticamente significativa porém de magnitude prática irrelevante.

### 3.2 Subperguntas operacionais

Para operacionalizar a RQ em dimensões mensuráveis — mantendo total alinhamento com `planejamento_analise_estatistica.md` — a pergunta principal desdobra-se em quatro subperguntas:

- **RQ1 (Latência):** Há diferença na latência das transações (em ms) entre o PostgreSQL 17 e o PostgreSQL 18 sob carga controlada?
- **RQ2 (Vazão / TPS):** Há diferença na vazão medida em transações por segundo (TPS) entre o PostgreSQL 17 e o PostgreSQL 18 sob carga controlada?
- **RQ3 (Eficiência de CPU):** Há diferença no percentual de consumo de CPU do container entre o PostgreSQL 17 e o PostgreSQL 18 durante a execução da carga?
- **RQ4 (Eficiência de Memória):** Há diferença no consumo de memória RAM (em MiB) do container entre o PostgreSQL 17 e o PostgreSQL 18 durante a execução da carga?

---

## 4. Caminho Metodológico Escolhido e Justificativa

Dentre os caminhos propostos na Seção 2b do enunciado (`README.md`), o estudo adota o caminho:

> **Rodar o software no ambiente do grupo** — executar localmente as mesmas versões oficiais utilizadas em produção (PostgreSQL 17 e PostgreSQL 18) em containers Docker isolados, variando apenas a versão do SGBD sob uma carga de trabalho padronizada via `pgbench`.

### 4.1 Justificativa da escolha

1. **Controle causal superior:** ao executar o SGBD localmente em containers isolados, a equipe controla hardware, sistema operacional, esquema do banco, volume de dados, número de clientes simultâneos e duração da carga — o que não seria viável medindo serviços de terceiros externamente.
2. **Conformidade ética integral:** o enunciado proíbe testes de carga ou estresse em serviços de terceiros. Executar o benchmark em containers locais com dados sintéticos gerados pelo `pgbench` e credenciais fictícias elimina qualquer risco operacional, legal ou de privacidade.
3. **Reprodutibilidade:** o uso de imagens oficiais com tags explícitas (sem `latest`), scripts automatizados e registros brutos em CSV permite que terceiros recriem o ambiente e verifiquem os resultados.
4. **Reaproveitamento dos laboratórios anteriores (Seção 4 do README):**
   - **Lab01 / Lab03:** organização do fluxo de trabalho em sprints e issues no GitHub Projects e separação entre dados brutos e tratados.
   - **Lab02:** estruturação formal de desenho experimental com tratamentos, variáveis de controle, protocolo de execução e ameaças à validade.
   - **Lab04:** critérios rigorosos para seleção de testes de hipótese (verificação de normalidade e homogeneidade de variâncias), controle de Erro Tipo I, poder estatístico e tamanho do efeito.

---

## 5. Primeira Versão das Sete Categorias de Pesquisa

Conforme a taxonomia da Aula 8 de **Medição e Experimentação** (Seção 3 do `README.md`), apresenta-se abaixo a **1ª versão** da classificação do estudo. Esta classificação será revisada na Sprint 2/3 após a execução efetiva da coleta, garantindo fidelidade ao método realmente praticado.

| # | Categoria | Classificação (1ª versão) | Justificativa metodológica |
| :-: | :--- | :--- | :--- |
| **1** | **Natureza** | **Aplicada** | O estudo investiga um problema concreto da Engenharia de Software: compreender se a atualização de versão principal de um SGBD amplamente usado em produção (PostgreSQL 17 → 18) altera desempenho e consumo de recursos, gerando subsídios práticos para equipes técnicas e decisões de infraestrutura. |
| **2** | **Objetivos** | **Explicativa** *(com base descritiva)* | Além de descrever quantitativamente o comportamento das duas versões (estatística descritiva), o estudo busca testar relações de causa e efeito entre o fator manipulado (versão do PostgreSQL) e as variáveis de resposta (latência, TPS, CPU e memória) sob condições controladas. |
| **3** | **Abordagem** | **Quantitativa** | Todos os fenômenos investigados são representados por medições numéricas objetivas em escala de razão (ms, transações/s, % de CPU e MiB), analisadas por estatística descritiva, testes de hipótese inferenciais e medidas de tamanho do efeito. |
| **4** | **Procedimentos** | **Experimento controlado** *(benchmark laboratorial)* | Há manipulação deliberada da variável independente (Tratamento A: PG17 × Tratamento B: PG18), padronização das variáveis de controle, múltiplas repetições independentes e controle de ordem/aquecimento (*warm-up*) para reduzir vieses sistemáticos. |
| **5** | **Tempo** | **Transversal** *(pontual / cross-sectional)* | As medições comparam duas versões congeladas em tags específicas durante uma janela delimitada de execução, capturando um retrato comparativo sob carga definida — sem acompanhamento longitudinal de sistemas reais em produção ao longo de meses. |
| **6** | **Controle** | **Alto controle** *(ambiente laboratorial / in vitro)* | A execução ocorre em máquina dedicada sob controle da equipe, com containers Docker isolados, volumes independentes, limites equivalentes de CPU/memória, mesma estrutura e volume de dados e mesma carga `pgbench`. Permanece apenas ruído residual inevitável do hospedeiro (Windows + Docker Desktop), tratado por protocolo de mitigação. |
| **7** | **Nível de evidência** | **Moderado a alto para validade interna; limitado para validade externa** | Por ser um experimento controlado com repetições e comparação direta entre tratamentos, fornece evidência causal forte dentro das condições testadas (superior a estudos puramente observacionais ou opiniões técnicas). Contudo, por ocorrer em uma única máquina local com carga sintética, possui menor poder de generalização do que experimentos replicados em múltiplos ambientes de produção ou revisões sistemáticas. |

---

## 6. Modelo GQM (*Goal-Question-Metric*)

### 6.1 Objetivo no template de Basili et al. (1994)

> **Analisar** o SGBD PostgreSQL em execução (versões 17 e 18),  
> **com o propósito de** comparar e caracterizar,  
> **com respeito a** desempenho transacional (latência e vazão) e eficiência no consumo de recursos computacionais (CPU e memória RAM),  
> **do ponto de vista de** engenheiros de software, administradores de banco de dados (DBAs) e equipes técnicas de infraestrutura,  
> **no contexto de** execuções controladas em ambiente local containerizado (Docker Desktop em Windows) submetido a uma carga de trabalho reproduzível via `pgbench`.

### 6.2 Mapeamento Perguntas → Métricas, Entidades, Atributos e Escalas

A tabela abaixo consolida a estrutura GQM em consistência direta com `planejamento_analise_estatistica.md`:

| Pergunta (GQM) | Métrica | Entidade | Atributo | Tipo de Medida | Unidade | Escala | Instrumento |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **Q1 (RQ1):** Qual é a latência por transação em cada versão? | **M1:** Latência média e desvio padrão por transação (`latency average`, `latency stddev`; percentis quando disponíveis) | Produto (SGBD PostgreSQL) | Externo (comportamento observável) | Direta | ms | Razão | `pgbench` |
| **Q2 (RQ2):** Qual é a vazão transacional alcançada por cada versão? | **M2:** Transações por segundo (`tps`, excluindo/incluindo estabelecimento de conexão — padronizar critério na Issue #64) | Produto (SGBD PostgreSQL) | Externo (comportamento observável) | Direta | TPS (tx/s) | Razão | `pgbench` |
| **Q3 (RQ3):** Quanto de CPU cada versão consome para executar a carga? | **M3:** Percentual de uso de CPU do container durante o benchmark | Recurso (Container Docker) | Externo | Direta | % | Razão | `docker stats` (via script Python) |
| **Q4 (RQ4):** Quanta memória RAM cada versão consome durante a carga? | **M4:** Memória RAM utilizada pelo container (`MEM USAGE`) durante o benchmark | Recurso (Container Docker) | Externo | Direta | MiB | Razão | `docker stats` (via script Python) |

### 6.3 Armadilhas de medição consideradas (Goodhart, Campbell e McNamara)

- **Lei de Goodhart e visão multidimensional:** se uma equipe otimizasse ou avaliasse apenas **TPS** isoladamente, poderia considerar superior uma versão que entrega ligeiramente mais transações às custas de picos severos de latência (cauda longa) ou consumo desproporcional de CPU/RAM. Por isso, o GQM combina **velocidade** (latência e TPS) e **custo computacional** (CPU e memória), exigindo interpretação integrada.
- **Falácia de McNamara:** reconhece-se que métricas quantitativas de benchmark sintético não esgotam o conceito amplo de "qualidade de um SGBD em produção" (que também envolve estabilidade, compatibilidade de extensões, facilidade de upgrade e segurança). O estudo delimita explicitamente que mede apenas desempenho e uso de recursos sob a carga testada.
- **Lei de Campbell:** para evitar distorção intencional do indicador, nenhuma configuração será ajustada exclusivamente para favorecer uma das versões, e todos os parâmetros equivalentes e resultados brutos (inclusive execuções anômalas) serão preservados e auditáveis.

---

## 7. Hipóteses da Pesquisa

Todas as hipóteses são formuladas *a priori* (antes da coleta definitiva) com caráter **bilateral** ($\alpha = 0{,}05$), em coerência com a neutralidade da RQ e com a estratégia de análise definida em `planejamento_analise_estatistica.md`:

### 7.1 Latência (RQ1)
- **$H_{0,\text{lat}}$:** Não há diferença estatisticamente significativa na latência por transação entre o PostgreSQL 17 e o PostgreSQL 18 sob a carga controlada.
- **$H_{1,\text{lat}}$:** Há diferença estatisticamente significativa na latência por transação entre o PostgreSQL 17 e o PostgreSQL 18 sob a carga controlada.

### 7.2 Transações por Segundo — TPS (RQ2)
- **$H_{0,\text{tps}}$:** Não há diferença estatisticamente significativa na vazão (TPS) entre o PostgreSQL 17 e o PostgreSQL 18 sob a carga controlada.
- **$H_{1,\text{tps}}$:** Há diferença estatisticamente significativa na vazão (TPS) entre o PostgreSQL 17 e o PostgreSQL 18 sob a carga controlada.

### 7.3 Consumo de CPU (RQ3)
- **$H_{0,\text{cpu}}$:** Não há diferença estatisticamente significativa no percentual de consumo de CPU entre o PostgreSQL 17 e o PostgreSQL 18 sob a carga controlada.
- **$H_{1,\text{cpu}}$:** Há diferença estatisticamente significativa no percentual de consumo de CPU entre o PostgreSQL 17 e o PostgreSQL 18 sob a carga controlada.

### 7.4 Consumo de Memória RAM (RQ4)
- **$H_{0,\text{mem}}$:** Não há diferença estatisticamente significativa no consumo de memória RAM (MiB) entre o PostgreSQL 17 e o PostgreSQL 18 sob a carga controlada.
- **$H_{1,\text{mem}}$:** Há diferença estatisticamente significativa no consumo de memória RAM (MiB) entre o PostgreSQL 17 e o PostgreSQL 18 sob a carga controlada.

> **Alinhamento com a estratégia estatística (Issue #65):** a escolha entre teste paramétrico (*t* de Student / Welch) e não paramétrico (Mann-Whitney U), bem como a avaliação de correção para múltiplas comparações (Bonferroni, $\alpha_{\text{ajustado}} = 0{,}0125$) e cálculo de tamanho do efeito (*d* de Cohen ou *r* rank-biserial), seguirá o fluxo especificado em `planejamento_analise_estatistica.md` após verificação empírica dos pressupostos na Sprint 2.

---

## 8. Variáveis e Desenho Experimental

### 8.1 Unidade experimental

Uma **execução completa e independente de benchmark (`pgbench`)** sobre uma instância containerizada de uma versão do PostgreSQL (17 ou 18), sob parâmetros de carga, duração e coleta padronizados.

### 8.2 Classificação das variáveis

| Tipo de Variável | Variável | Especificação / Papel no Experimento |
| :--- | :--- | :--- |
| **Independente (Fator)** | Versão do PostgreSQL | Categórica com 2 níveis (tratamentos): **Tratamento A** (`PostgreSQL 17`) e **Tratamento B** (`PostgreSQL 18`), usando imagens oficiais com tags explícitas a serem fixadas na Issue #64 (sugestão: `postgres:17.12` e `postgres:18.7`). |
| **Dependentes (Resposta)** | Latência (ms), TPS, CPU (%), Memória RAM (MiB) | Variáveis quantitativas contínuas em escala de razão que capturam desempenho transacional e custo computacional. |
| **De Controle (Fixas)** | Hardware e SO hospedeiro | Mesma máquina física, mesma versão do Windows e mesma versão do Docker Desktop em todas as execuções. |
| **De Controle (Fixas)** | Isolamento e recursos do container | Limites equivalentes de CPU e memória (`--cpus`, `--memory`), volumes de dados separados e portas distintas (ex.: `5432` e `5433`), mantendo **apenas um container de banco sob benchmark ativo por vez** durante a medição. |
| **De Controle (Fixas)** | Configuração do SGBD | Parâmetros equivalentes entre as duas versões; eventuais diferenças de padrões nativos da arquitetura (ex.: `io_method` introduzido no PG18) devem ser explicitamente inspecionadas e documentadas sem ajustes ad hoc. |
| **De Controle (Fixas)** | Banco de dados e carga de trabalho | Mesmo esquema e fator de escala (`scale factor`) inicializados via `pgbench -i`, mesmo número de clientes (`-c`) e threads (`-j`), mesma duração por execução (`-T`) e mesmo protocolo de *warm-up* e *cooldown*. |
| **De Controle (Fixas)** | Instrumentação de coleta | Mesmo script de automação, mesma ferramenta de monitoramento (`docker stats`) e mesma frequência de amostragem nas duas versões. |
| **De Confusão / Ruído (Extrínsecas)** | Processos concorrentes no hospedeiro, cache do SO/banco, aquecimento térmico (*thermal throttling*) e ordem de execução | Fatores não desejados que podem distorcer medições; mitigados pelo protocolo operacional e monitorados via registro de metadados e logs. |

### 8.3 Desenho experimental (visão metodológica)

- **Estrutura:** experimento comparativo de **um fator com dois níveis (Tratamento A × Tratamento B)** e **múltiplas repetições independentes** por tratamento.
- **Ordem de execução (controle de efeito de ordem):** adotar execução **alternada ou aleatorizada em blocos** entre PG17 e PG18 (por exemplo, pares alternados A→B / B→A ou sequência pseudoaleatória com semente registrada), evitando executar todas as repetições de uma versão em bloco único antes da outra.
- **Isolamento temporal:** executar apenas o container da versão sob teste durante cada rodada, incluindo fase padronizada de **aquecimento (*warm-up*)** (descartada dos dados analisados) e breve intervalo de estabilização (**cooldown**) entre rodadas.
- **Parâmetros a calibrar na coleta piloto (escopo da Issue #64):** o número final de repetições ($n$ por versão — sugestão inicial de 20 a 30 conforme `planejamento_analise_estatistica.md`), o *scale factor* do `pgbench`, o número de clientes/threads, a duração de cada rodada e a resolução temporal do `docker stats` serão definidos e justificados empiricamente na coleta piloto, sem antecipar essa etapa nesta issue.

---

## 9. Ameaças à Validade e Estratégias de Mitigação

Seguindo a classificação de Wohlin et al. (2012), foram mapeadas as principais ameaças à validade nos quatro domínios clássicos, com ações preventivas já incorporadas ao planejamento (a serem revisadas após a coleta na Issue #67):

### 9.1 Validade de Conclusão

| Ameaça | Risco ao estudo | Mitigação planejada |
| :--- | :--- | :--- |
| **Número insuficiente de repetições / baixo poder estatístico** | Não detectar diferenças reais (Erro Tipo II) ou produzir estimativas instáveis. | Usar a variabilidade observada na coleta piloto (Issue #64) para dimensionar $n$ adequado (meta inicial: 20–30 repetições por versão). |
| **Violação de pressupostos dos testes estatísticos** | Aplicar teste *t* em dados assimétricos ou com variâncias desiguais pode gerar valores-*p* inválidos. | Verificar normalidade (Shapiro-Wilk + Q-Q plot/histograma) e homogeneidade de variâncias (Levene), recorrendo a Welch ou Mann-Whitney U conforme fluxo de `planejamento_analise_estatistica.md`. |
| **Múltiplas comparações (4 métricas)** | Aumento da probabilidade acumulada de falso positivo (Erro Tipo I). | Avaliar correlação entre métricas e aplicar/reportar correção de Bonferroni ($\alpha_{\text{ajustado}} = 0{,}0125$) junto ao resultado sem ajuste para transparência. |
| **Alta variabilidade entre execuções** | Ruído excessivo mascarando o efeito real do tratamento. | Padronizar ambiente, encerrar aplicativos pesados durante a coleta, aplicar *warm-up* e reportar medidas robustas (mediana e IQR) junto à média e desvio padrão. |

### 9.2 Validade Interna

| Ameaça | Risco ao estudo | Mitigação planejada |
| :--- | :--- | :--- |
| **Concorrência de processos no Windows hospedeiro** | Antivírus, atualizações do SO, sincronização em nuvem (ex.: OneDrive) ou navegadores alterarem CPU, disco ou memória durante apenas uma das versões. | Fechar programas não essenciais durante a execução definitiva, pausar sincronizações pesadas, manter o computador ligado à energia e registrar logs/horários de cada rodada. |
| **Efeito de ordem e deriva temporal (ex.: aquecimento da CPU / *thermal throttling*)** | Se todas as execuções do PG18 ocorrerem após o PG17, a máquina mais quente ou com caches aquecidos pode enviesar o segundo grupo. | Alternar ou aleatorizar a ordem das rodadas entre PG17 e PG18 e aplicar intervalos de *cooldown* padronizados. |
| **Efeitos de cache e aquecimento (*warm-up*)** | Primeiras execuções sofrerem leitura fria em disco enquanto posteriores aproveitam dados em memória. | Aplicar fase fixa e idêntica de *warm-up* antes das medições válidas e documentar o estado inicial do banco/container em cada rodada. |
| **Diferenças de configuração padrão entre versões** | Alterações de parâmetros *default* entre PG17 e PG18 (como o novo subsistema de AIO `io_method` no PG18) influenciarem o resultado sem visibilidade. | Exportar e comparar as configurações efetivas (`SHOW ALL;` / `pg_settings`) de ambos os containers; distinguir explicitamente o que é evolução padrão da versão (parte legítima do tratamento) de divergências acidentais de ambiente. |
| **Competição simultânea entre os dois containers** | Rodar PG17 e PG18 sob carga simultânea gera disputa de CPU, memória e I/O. | Executar benchmarks de forma estritamente sequencial, mantendo ativo somente o container alvo durante cada medição. |

### 9.3 Validade de Construto

| Ameaça | Risco ao estudo | Mitigação planejada |
| :--- | :--- | :--- |
| **Sub-representação do construto "desempenho" (Lei de Goodhart)** | Uma métrica isolada (ex.: TPS) não captura latência nem eficiência computacional. | Medir quatro variáveis complementares (latência, TPS, CPU e memória) derivadas formalmente pelo GQM e interpretá-las conjuntamente. |
| **Carga sintética limitada (`pgbench`)** | O perfil padrão do `pgbench` (semelhante a TPC-B) representa transações OLTP curtas e simples, não cobrindo consultas analíticas (OLAP), joins complexos ou cargas pesadas de texto/JSON/vetores. | Declarar explicitamente o escopo da carga escolhida na pergunta e nas conclusões, evitando generalizar os achados para perfis de consulta não testados. |
| **Granularidade das métricas de container (`docker stats`)** | `MEM USAGE` inclui memória gerenciada no nível do container (inclusive caches de página do sistema de arquivos dentro do cgroup), podendo diferir da memória privada estrita dos processos do PostgreSQL. | Registrar a definição exata da métrica, a unidade e o intervalo de coleta, garantindo exatamente o mesmo método de medição nas duas versões. |

### 9.4 Validade Externa

| Ameaça | Risco ao estudo | Mitigação planejada |
| :--- | :--- | :--- |
| **Hardware único e virtualização local (Windows + Docker Desktop / WSL2)** | O overhead de virtualização e o subsistema de disco local diferem de servidores Linux *bare-metal* ou instâncias em nuvem (ex.: AWS RDS, Google Cloud SQL), podendo inclusive afetar o comportamento de I/O assíncrono (`io_uring` vs `worker`). | Registrar integralmente especificações de hardware, SO, versão do Docker e modo `io_method` ativo no PG18; restringir as conclusões ao ambiente testado. |
| **Generalização indevida para produção** | Extrapolar ganhos ou perdas percentuais diretamente para qualquer empresa ou sistema real. | Explicitar claramente o que **não é possível afirmar** com o estudo; apresentar projeções de impacto (Sprint 3) sempre como estimativas condicionadas a premissas transparentes. |

---

## 10. Verificação dos Critérios de Aceitação (Issue #63)

| Critério de aceitação da Issue #63 | Status | Onde está documentado |
| :--- | :---: | :--- |
| Software selecionado e justificado | ✅ | Seção 1 (PostgreSQL 17 × PostgreSQL 18, com justificativa técnica e aderência à regra contra mineração de repositório) |
| Evidências dos três critérios documentadas | ✅ | Seção 2 (Real, Em operação e Alto impacto, com números verificados, links oficiais e data de acesso `25/11/2026`) |
| Pergunta de pesquisa definida | ✅ | Seção 3 (RQ principal neutra/bilateral + subperguntas operacionais RQ1–RQ4) |
| Primeira versão das sete categorias elaborada | ✅ | Seção 5 (Natureza, Objetivos, Abordagem, Procedimentos, Tempo, Controle e Nível de evidência, todas justificadas) |
| GQM estruturado | ✅ | Seção 6 (Template de Basili + mapeamento Q1–Q4 → M1–M4 + entidades, atributos, escalas e armadilhas de medição) |
| Hipóteses e variáveis identificadas | ✅ | Seções 7 e 8 ($H_0$/$H_1$ bilaterais por métrica + unidade experimental, VI, VDs, variáveis de controle, ruído e desenho experimental) |
| Ameaças à validade definidas *(atividade da issue)* | ✅ | Seção 9 (Conclusão, Interna, Construto e Externa com estratégias de mitigação) |

---

## 11. Decisões em Aberto e Próximos Passos (Integração com Issue #64 e Sprint 2)

Os itens abaixo ficam registrados como pontos de alinhamento para a equipe e para as próximas issues, preservando estritamente a divisão de escopo das sprints:

1. **Confirmação de escopo de versões (alinhamento rápido da equipe):** confirmar formalmente a permanência da comparação **PostgreSQL 17 × PostgreSQL 18** diante do lançamento recente do PostgreSQL `19.0` (19/11/2026). *Recomendação deste planejamento:* manter **17 × 18**, já adotado em `contextualizacao_lab05_postgresql.md` e `planejamento_analise_estatistica.md`, pela maturidade em produção e foco nas mudanças arquiteturais do PG18.
2. **Fixação das tags Docker e parâmetros operacionais (escopo da Issue #64 — Integrante B):**
   - Definir e travar tags explícitas equivalentes das imagens oficiais (ex.: `postgres:17.12` e `postgres:18.7`, mesma base de sistema operacional como Debian *bookworm* ou *alpine*).
   - Verificar e registrar os parâmetros efetivos (`pg_settings`), especialmente o valor padrão de `io_method` no container PostgreSQL 18 sob Docker Desktop/WSL2.
   - Calibrar na coleta piloto: *scale factor* (`-s`), número de clientes (`-c`), threads (`-j`), duração (`-T`), tempo de *warm-up*, intervalo de amostragem do `docker stats` e número definitivo de repetições ($n$).
   - Confirmar se a métrica de TPS usará `excluding connections establishing` ou `including connections establishing` do `pgbench` de forma padronizada.
3. **Revisão metodológica pós-coleta (escopo da Issue #67 — Sprint 2):** revisar a 1ª versão das sete categorias de pesquisa e atualizar o mapeamento de ameaças à validade à luz dos desvios ou eventos realmente observados na execução.

---

*Documento elaborado na Sprint 1 (`LAB05S01`) como entregável da Issue `#63`. Alinhado a `README.md`, `contextualizacao_lab05_postgresql.md` e `planejamento_analise_estatistica.md`.*
