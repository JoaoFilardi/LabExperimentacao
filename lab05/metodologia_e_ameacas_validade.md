# Metodologia Revisada e Ameaças à Validade

**Experimento:** Comparação de desempenho e consumo de recursos entre PostgreSQL 17 e PostgreSQL 18  
**Issue:** `#67` — `[ LAB05S02 ] Revisar metodologia e ameaças à validade do estudo`  
**Responsável:** Integrante C — Análise e Impacto  
**Sprint:** 2 (`LAB05S02`)  
**Data de revisão:** 25/11/2026  
**Documentos de referência:** `planejamento_metodologico.md` (Issue #63) · `execucao_validacao_coleta.md` (Issue #66) · `analise_estatistica.md` (Issue #68) · `planejamento_analise_estatistica.md` (Issue #65)

---

## 1. Revisão da Pergunta de Pesquisa e dos Objetivos

### 1.1 Pergunta principal (RQ) — status após a execução

> **RQ:** *A versão 18 do PostgreSQL apresenta diferenças de desempenho e eficiência no uso de recursos computacionais em comparação com a versão 17, sob uma carga de trabalho controlada?*

**Avaliação:** a pergunta permanece **válida e operacionalizável** após a execução. Os dados coletados permitem respondê-la diretamente pelas quatro subperguntas definidas em `planejamento_metodologico.md`. Não houve necessidade de reformulação.

A neutralidade bilateral da RQ foi confirmada pelos resultados: o PG18 apresentou diferença em três das quatro métricas, em **direções distintas** (latência maior, TPS menor e memória maior), o que corrobora a decisão de não pressupor superioridade de nenhuma versão.

### 1.2 Subperguntas e sua correspondência com os resultados

| Subpergunta | Métrica | Hipótese testada | Resultado obtido |
|:------------|:--------|:-----------------|:-----------------|
| **RQ1** — Há diferença na latência? | Latência média (ms) | $H_{0,\text{lat}}$ | Rejeitada — PG18 apresentou latência 1,74% maior (d = 0,67, médio) |
| **RQ2** — Há diferença no TPS? | TPS (tx/s) | $H_{0,\text{tps}}$ | Rejeitada — PG18 apresentou TPS 1,70% menor (d = 0,68, médio) |
| **RQ3** — Há diferença no uso de CPU? | CPU média (%) | $H_{0,\text{cpu}}$ | Não rejeitada — diferença de 0,98 pp sem significância estatística (r = 0,24, pequeno) |
| **RQ4** — Há diferença no uso de memória? | Memória RSS (MiB) | $H_{0,\text{mem}}$ | Rejeitada — PG18 utilizou 8,13% mais memória (r = 0,86, grande) |

### 1.3 Objetivo geral — verificação de aderência

O objetivo declarado em `contextualizacao_lab05_postgresql.md` era:

> *Comparar o comportamento do PostgreSQL 17 e do PostgreSQL 18 ao executar uma carga de trabalho equivalente, observando desempenho e consumo de recursos computacionais.*

**Status:** objetivo integralmente cumprido. As quatro métricas previstas foram coletadas, validadas e analisadas com 30 repetições por versão.

---

## 2. Revisão das Escolhas Metodológicas

### 2.1 Adaptação do ambiente de execução

O planejamento original previa o uso de **Docker Desktop** (containers). Por indisponibilidade do Docker na estação utilizada durante a Sprint 2, a coleta foi realizada com **binários portáteis oficiais do PostgreSQL** (EnterpriseDB / postgresql.org), seguindo adaptação documentada em `execucao_validacao_coleta.md`.

| Aspecto | Planejado | Executado | Impacto |
|:--------|:----------|:----------|:--------|
| Ambiente de execução | Docker Desktop (containers) | Binários portáteis nativos (Windows 11) | Elimina o *overhead* de virtualização do WSL2; reduz uma camada de indireção mas afasta do ambiente Docker de produção |
| Instrumento de monitoramento de CPU/RAM | `docker stats` | `psutil` sobre a árvore de processos do PostgreSQL | Métricas equivalentes; diferença na granularidade de reporting (cgroup vs. processo) documentada |
| Portas | 5432 / 5433 | 55432 / 55433 | Sem impacto científico |

> **Avaliação:** a adaptação preserva o rigor da comparação e é **metodologicamente defensável**. Os dados coletados com `psutil` são equivalentes e auditáveis. O impacto para as ameaças à validade está detalhado na Seção 4.

### 2.2 Protocolo de controle de ordem

O delineamento **ABBA em 12 blocos de 5 repetições** foi executado conforme planejado. O índice médio de bloco foi exatamente `6,5` para PG17 e `6,5` para PG18, confirmando o balanceamento temporal perfeito.

### 2.3 Número de repetições e parâmetros do benchmark

| Parâmetro | Meta (planejamento) | Executado | Validação |
|:----------|:-------------------:|:---------:|:---------:|
| Repetições por versão | 20–30 | **30** | ✅ |
| Scale factor (`-s`) | a calibrar | **10** | ✅ |
| Clientes (`-c`) | a calibrar | **8** | ✅ |
| Threads (`-j`) | a calibrar | **4** | ✅ |
| Duração por execução (`-T`) | a calibrar | **10 s** | ✅ |
| Warm-up | sim | **5 s** por bloco | ✅ |
| Cooldown | sim | **2 s** entre rodadas / **3 s** ao trocar versão | ✅ |

### 2.4 Coerência entre planejamento e execução — resumo

| Item verificado | Status |
|:----------------|:------:|
| RQ e subperguntas mantidas sem alteração | ✅ |
| Hipóteses formuladas a priori (antes da coleta) | ✅ |
| Variável independente e variáveis dependentes inalteradas | ✅ |
| Variáveis de controle aplicadas (mesma máquina, mesma configuração base, execução sequencial) | ✅ |
| Número mínimo de repetições atingido (30 ≥ meta de 20–30) | ✅ |
| Dados brutos preservados sem exclusão de observações desfavoráveis | ✅ |
| Adaptação de ambiente documentada e justificada | ✅ |
| Auditoria de `pg_settings` realizada e divergências registradas | ✅ |

---

## 3. As Sete Categorias de Pesquisa — Versão Revisada

A primeira versão foi elaborada em `planejamento_metodologico.md` (Seção 5), antes da execução. Esta seção traz a **versão revisada e definitiva**, ajustada à luz do que realmente ocorreu, conforme exigido pela Issue #67.

| # | Categoria | Classificação definitiva | Justificativa revisada |
|:-:|:----------|:-------------------------|:-----------------------|
| **1** | **Natureza** | **Aplicada** | Mantida. O estudo produz conhecimento diretamente utilizável por equipes de infraestrutura e DBAs que avaliam migração de PG17 para PG18 em ambientes de produção. Os dados coletados e os resultados obtidos têm aplicação prática imediata. |
| **2** | **Objetivos** | **Explicativa** *(com base descritiva)* | Mantida. A análise vai além de descrever as médias: testa se a diferença entre versões é causada pela mudança de versão (Tratamento A vs B) ou pode ser atribuída ao acaso. Os testes de hipótese com rejeição de H₀ para latência, TPS e memória sustentam a dimensão explicativa. |
| **3** | **Abordagem** | **Quantitativa** | Mantida. Todas as variáveis de resposta foram medidas numericamente em escala de razão (ms, tx/s, % de CPU e MiB). A análise combina estatística descritiva (média, mediana, DP, IQR, percentis), testes inferenciais (t de Student e Mann-Whitney U) e medidas de tamanho do efeito (d de Cohen e r de rank-biserial). |
| **4** | **Procedimentos** | **Experimento controlado** *(benchmark laboratorial)* | Mantida e confirmada pela execução. A manipulação deliberada foi a versão do PostgreSQL (único fator com dois níveis). As variáveis de controle foram mantidas: mesma máquina, mesmo hardware, mesmo `postgresql.conf` de base, mesma carga `pgbench`, delineamento ABBA e execução estritamente sequencial. |
| **5** | **Tempo** | **Transversal** *(cross-sectional)* | Mantida. A coleta ocorreu em uma janela única de **15 min 14 s** (21:56:33 UTC a 22:11:47 UTC de 25/11/2026), comparando dois estados congelados (versões 17.12 e 18.7). Não houve acompanhamento longitudinal de sistemas em produção. |
| **6** | **Controle** | **Alto controle** *(ambiente laboratorial)* | **Revisada parcialmente.** O controle sobre hardware, parâmetros e carga foi rigoroso. Contudo, a execução em Windows 11 com binários nativos (em vez de containers Linux) introduz fontes de ruído do hospedeiro (processos do SO, sincronização do OneDrive, eventos de sistema) que são inerentemente menores em servidores Linux dedicados. O grau de controle é classificado como **alto para um ambiente Windows**, com ruído residual documentado. |
| **7** | **Nível de evidência** | **Moderado a alto para validade interna; baixo para validade externa** | **Revisada.** A evidência interna é **moderada a alta**: delineamento ABBA, 30 repetições por versão, CV ≤ 3,24% em todas as métricas, testes formais com pressupostos verificados e tamanho do efeito calculado. A evidência externa é **baixa**: uma única máquina Windows 11 com binários portáteis, carga sintética TPC-B-like e ausência de containers Linux ou ambientes de nuvem limitam a generalização. Mais baixa do que originalmente estimado por conta da não utilização de Docker. |

---

## 4. Hipóteses — Revisão Pós-Execução

As hipóteses foram formuladas *a priori* em `planejamento_metodologico.md` (Seção 7) com caráter bilateral ($\alpha = 0{,}05$, Bonferroni $\alpha_{\text{adj}} = 0{,}0125$). Esta seção revisa sua adequação após a coleta.

### 4.1 Verificação de adequação das hipóteses

| Hipótese | Formulação original | Teste aplicado | Decisão | Adequação da formulação |
|:---------|:--------------------|:---------------|:--------|:------------------------|
| $H_{0,\text{lat}}$ | Sem diferença na latência | Teste t de Student (bilateral) | **Rejeitada** ($p = 0{,}0115 < 0{,}0125$) | ✅ Adequada — bilateral confirmado pelo resultado |
| $H_{0,\text{tps}}$ | Sem diferença no TPS | Teste t de Student (bilateral) | **Rejeitada** ($p = 0{,}0106 < 0{,}0125$) | ✅ Adequada |
| $H_{0,\text{cpu}}$ | Sem diferença no consumo de CPU | Mann-Whitney U (bilateral) | **Não rejeitada** ($p = 0{,}1087$) | ✅ Adequada — resultado plausível dado o `io_method = worker` consumindo CPU mas sem diferença detectável nessa escala |
| $H_{0,\text{mem}}$ | Sem diferença no consumo de memória | Mann-Whitney U (bilateral) | **Rejeitada** ($p = 1{,}10 \times 10^{-8} \ll 0{,}0125$) | ✅ Adequada — efeito muito grande (r = 0,86) |

### 4.2 Decisão sobre teste bilateral ou unilateral

A formulação bilateral foi preservada. Os resultados confirmam sua adequação: o PG18 foi pior em latência e TPS, mas apresentou comportamento neutro em CPU — um teste unilateral (assumindo que "novo é melhor") teria levado a conclusões equivocadas.

### 4.3 Correção para múltiplas comparações

A correção de **Bonferroni** ($\alpha_{\text{adj}} = 0{,}0125$) foi aplicada. Latência e TPS foram aprovadas também pelo critério ajustado. Os resultados foram reportados tanto com $p$ bruto quanto com $p$ Bonferroni, garantindo transparência. A decisão se mostrou **necessária**: a correlação de Spearman $\rho = -0{,}9997$ entre latência e TPS confirmou que as métricas não são independentes, o que reforça o uso da correção conservadora.

---

## 5. Ameaças à Validade — Análise Atualizada

Classificação seguindo **Wohlin et al. (2012)** — quatro domínios. Cada ameaça recebeu status de **confirmada**, **parcialmente confirmada** ou **mitigada** à luz do que realmente ocorreu.

---

### 5.1 Validade de Conclusão

*Diz respeito à capacidade de tirar conclusões corretas a partir dos dados estatísticos.*

| # | Ameaça | Status pós-execução | Mitigação aplicada | Mitigação adicional recomendada |
|:-:|:-------|:-------------------:|:-------------------|:-------------------------------|
| **C1** | **Número insuficiente de repetições / baixo poder estatístico** | ✅ Mitigada | 30 repetições por versão (meta atingida). CV ≤ 3,24% em todas as métricas, indicando ambiente estável. Os três testes que rejeitaram H₀ exibiram tamanhos de efeito médio a grande, sugerindo poder suficiente. | Análise de poder *post hoc* poderia ser calculada para a métrica de CPU (onde H₀ não foi rejeitada) para verificar se 30 repetições eram suficientes para detectar a diferença observada (d ≈ 0,30). |
| **C2** | **Violação de pressupostos dos testes estatísticos** | ✅ Mitigada | Shapiro-Wilk e Levene aplicados por métrica antes da escolha do teste. CPU e memória violaram normalidade → Mann-Whitney U. Latência e TPS aprovaram normalidade → teste t de Student. | — |
| **C3** | **Múltiplas comparações (4 métricas)** | ✅ Mitigada | Bonferroni aplicado ($\alpha_{\text{adj}} = 0{,}0125$). Resultados reportados com e sem ajuste para transparência. | — |
| **C4** | **Alta variabilidade entre execuções** | ✅ Mitigada | CV ≤ 3,24% em todas as métricas. Protocolo de warm-up e cooldown aplicado. Delineamento ABBA equilibrou posição temporal. | — |
| **C5** | **Variáveis de confusão não medidas** | ⚠️ Parcialmente confirmada | A atividade do autovacuum e do autoanálise do PostgreSQL pode ter afetado algumas execuções individualmente (gerando os outliers identificados em RUN_014, RUN_051 e RUN_052). | Desabilitar autovacuum durante o benchmark em experimentos futuros; registrar eventos de checkpoint no log. |

---

### 5.2 Validade Interna

*Diz respeito à relação causal entre tratamento (versão do PostgreSQL) e as variáveis de resposta.*

| # | Ameaça | Status pós-execução | Mitigação aplicada | Observação adicional |
|:-:|:-------|:-------------------:|:-------------------|:---------------------|
| **I1** | **Concorrência de processos no Windows hospedeiro** | ⚠️ Parcialmente confirmada | Programas não essenciais foram encerrados. Mesmo assim, o Windows 11 executa serviços de fundo (Windows Update, Defender, OneDrive) que podem ter sido responsáveis pelos outliers de CPU (RUN_051 e RUN_052 — PG17 — e RUN_014 — PG18). | Os outliers foram preservados sem exclusão e sinalizados com flags. A análise de sensibilidade (sem outliers) confirmou robustez dos resultados: as conclusões não mudam com ou sem esses casos. |
| **I2** | **Efeito de ordem e deriva temporal** | ✅ Mitigada | Delineamento ABBA com 12 blocos garantiu índice médio de bloco idêntico (`6,5`) para PG17 e PG18. Nenhuma versão foi executada inteiramente antes da outra. | — |
| **I3** | **Efeitos de cache e aquecimento (warm-up)** | ✅ Mitigada | Fase de warm-up de 5 s aplicada antes de cada bloco de 5 repetições. Warm-ups registrados em `raw` e excluídos de `processed`. | — |
| **I4** | **Diferenças de configuração padrão entre versões** | ⚠️ Confirmada como parte do tratamento | Auditoria completa de `pg_settings` revelou diferenças nativas do PG18: `data_checksums = on`, `io_method = worker`, `io_workers = 3`, `effective_io_concurrency = 16`, `maintenance_io_concurrency = 16`, `shared_memory_size = 286 MB` (vs. 279 MB no PG17). | **Interpretação crítica:** essas diferenças são *comportamento padrão do PG18 out-of-the-box*, que é exatamente o que se quer medir numa decisão real de migração. Não são divergências acidentais. O maior consumo de memória do PG18 (+8,13%) é coerente com `shared_memory_size` maior e 3 processos `io_workers` adicionais. Essa distinção é fundamental para as conclusões. |
| **I5** | **Competição simultânea entre containers** | ✅ Mitigada | Apenas uma instância PostgreSQL ativa por vez em cada execução. Verificado na implementação do script. | — |

---

### 5.3 Validade de Construto

*Diz respeito à adequação das métricas escolhidas para representar os construtos investigados.*

| # | Ameaça | Status pós-execução | Mitigação aplicada | Observação adicional |
|:-:|:-------|:-------------------:|:-------------------|:---------------------|
| **Co1** | **Sub-representação do construto "desempenho" (Lei de Goodhart)** | ✅ Mitigada | Quatro métricas complementares coletadas (latência, TPS, CPU, memória). Interpretação integrada: PG18 "piorou" em desempenho transacional (latência +1,74%, TPS −1,70%) mas as diferenças são de **efeito médio** e podem ser parcialmente explicadas pelas verificações de checksum adicionais (`data_checksums = on`). | Nenhuma única métrica define "melhor" versão. A memória maior do PG18 (+8,13% — efeito grande) é o achado mais robusto. |
| **Co2** | **Carga sintética limitada (`pgbench` TPC-B-like)** | ⚠️ Confirmada como limitação | Escopo declarado explicitamente na RQ e nas conclusões. O `pgbench` simula transações OLTP curtas (UPDATE em `pgbench_accounts`, INSERT em `pgbench_history`, SELECT em `pgbench_branches/tellers`). | Não representa cargas analíticas (OLAP), consultas complexas com JOINs, operações de texto/JSON/vetores ou padrões de leitura intensiva. Os resultados não são generalizáveis a esses perfis. |
| **Co3** | **Métricas de CPU e memória pelo `psutil`** | ⚠️ Parcialmente confirmada | A memória RSS (`psutil`) captura a memória residente de todos os processos da instância PostgreSQL, incluindo `postmaster`, backends, workers e agora os 3 `io_workers` extras do PG18. Não equivale exatamente ao `MEM USAGE` do `docker stats` (que usa cgroups). | O método foi aplicado **identicamente nas duas versões** e o `psutil` foi escolhido justamente como substituto auditável do `docker stats`. A diferença de 40 MiB no RSS provavelmente inclui o custo dos 3 `io_workers` adicionais do PG18 — o que é parte do construto "consumo de recursos da versão". |
| **Co4** | **TPS como medida incompleta de vazão** | ✅ Mitigada | Optou-se pelo TPS `without initial connection time` para medir a capacidade transacional líquida do banco. A métrica `tempo_conexao_inicial_ms` foi registrada separadamente para auditoria. Critério documentado no dicionário de dados de `execucao_validacao_coleta.md`. | — |

---

### 5.4 Validade Externa

*Diz respeito à capacidade de generalizar os resultados para além do ambiente experimental.*

| # | Ameaça | Status pós-execução | Mitigação aplicada | Observação adicional |
|:-:|:-------|:-------------------:|:-------------------|:---------------------|
| **E1** | **Hardware único e ambiente Windows (não Linux)** | ⚠️ Confirmada como limitação | Hardware registrado integralmente: Intel Core i7 (12ª geração, 6 núcleos físicos / 8 lógicos), 7,71 GiB RAM, Windows 11 (`10.0.26200`), binários portáteis EDB. | Em servidores Linux `bare-metal` com `io_uring`, o impacto do `io_method = worker` pode ser diferente. No Windows, `io_uring` não está disponível e `io_method` fica limitado ao modo `worker`. Esse detalhe **deve constar das conclusões**. |
| **E2** | **Ausência de containers Docker** | ⚠️ Confirmada como limitação | Adaptação documentada e justificada em `execucao_validacao_coleta.md`. | A execução com containers Docker poderia gerar resultados diferentes (overhead de virtualização). Uma reexecução via Docker (`--backend docker`) é possível com o script existente, caso a equipe deseje comparar. |
| **E3** | **Generalização indevida para produção** | ✅ Mitigada pela delimitação | Conclusões limitadas ao hardware, configuração e carga testados. Projeções de impacto (Sprint 3) serão apresentadas como estimativas com premissas explícitas. | O estudo não permite afirmar que PG18 será mais lento ou gastará mais memória em **qualquer** ambiente de produção. Os resultados descrevem o comportamento *out-of-the-box* sob carga OLTP sintética em Windows 11. |
| **E4** | **Carga sintética não representa todos os perfis de uso** | ⚠️ Confirmada como limitação | Declarada explicitamente no escopo do benchmark. | Empresas com cargas analíticas, alta concorrência de leitura ou uso intensivo de FTS/JSONB/pgvector podem observar comportamentos distintos — especialmente se se beneficiarem do `io_method = worker` em cenários de I/O intenso. |

---

## 6. Verificação de Coerência entre Planejamento e Execução

| Aspecto verificado | Planejado | Executado | Coerente? | Observação |
|:-------------------|:----------|:----------|:---------:|:-----------|
| Versões comparadas | PG17 × PG18 | PG17.12 × PG18.7 | ✅ | Tags explícitas usadas |
| Variável independente | Versão do PostgreSQL | Versão do PostgreSQL | ✅ | — |
| Variáveis dependentes | Latência, TPS, CPU, Memória | Latência, TPS, CPU, Memória | ✅ | — |
| Hipóteses bilaterais formuladas antes da coleta | Sim | Sim | ✅ | Registradas em `planejamento_metodologico.md` antes de `execucao_validacao_coleta.md` |
| Nível de significância $\alpha = 0{,}05$ | Sim | Sim | ✅ | — |
| Correção de Bonferroni | Prevista | Aplicada ($\alpha_{\text{adj}} = 0{,}0125$) | ✅ | — |
| Verificação de normalidade antes do teste | Prevista (fluxo de decisão) | Executada (Shapiro-Wilk + Levene) | ✅ | — |
| Tamanho do efeito (d de Cohen / r de rank-biserial) | Previsto | Calculado | ✅ | — |
| Warm-up descartado dos dados analisados | Previsto | 12 warm-ups em `raw`, excluídos de `processed` | ✅ | — |
| Delineamento ABBA (evitar efeito de ordem) | Previsto | Executado (12 blocos, índice médio = 6,5 para ambas) | ✅ | — |
| Dados brutos preservados sem exclusão | Previsto | ✅ Confirmado (flags não destrutivas de outliers) | ✅ | — |
| Ambiente Docker | Previsto | ⚠️ Substituído por binários portáteis | 🔶 Adaptado | Documentado e justificado; impacto nas ameaças E1/E2 registrado |
| Auditoria de `pg_settings` | Prevista | Realizada (380 PG17 × 400 PG18; 20 diferenças documentadas) | ✅ | Achado relevante: `data_checksums`, `io_method`, `io_workers` |

---

## 7. Verificação dos Critérios de Aceitação — Issue #67

| Critério de aceitação | Status | Onde está documentado |
|:----------------------|:------:|:----------------------|
| Metodologia revisada | ✅ | Seções 1, 2 e 6 |
| Sete categorias de pesquisa justificadas | ✅ | Seção 3 (versão definitiva com revisões) |
| Hipóteses revisadas | ✅ | Seção 4 |
| Quatro tipos de ameaças à validade identificados | ✅ | Seção 5 (Conclusão, Interna, Construto e Externa) |
| Estratégias de mitigação documentadas | ✅ | Coluna "Mitigação aplicada" em cada tabela da Seção 5 |
| Coerência entre planejamento e execução verificada | ✅ | Seção 6 (tabela completa) |

---

## 8. Pendências e Recomendações para a Sprint 3

- [ ] Incorporar na **discussão final** a interpretação do achado `data_checksums = on` + `io_method = worker` como causas prováveis do maior consumo de memória do PG18 (+8,13%) e do leve aumento de latência (+1,74%) — com base na auditoria de `pg_settings`.
- [ ] Delimitar claramente nas **conclusões** que os resultados são específicos para: Windows 11, binários portáteis EDB, carga OLTP sintética TPC-B-like, 8 clientes e 10 s de duração.
- [ ] Estimar na Sprint 3 o **impacto prático** das diferenças observadas (ex.: o custo de memória extra de 40 MiB por instância em um ambiente de produção com centenas de instâncias PostgreSQL).
- [ ] Verificar se uma **reexecução com Docker** seria viável para comparar os resultados e fortalecer a validade externa — opcional, se houver tempo.

---

*Documento elaborado na Sprint 2 (`LAB05S02`) como entregável da Issue `#67`. Revisão da metodologia em relação a `planejamento_metodologico.md` (Issue #63), com base na execução registrada em `execucao_validacao_coleta.md` (Issue #66) e nos resultados de `analise_estatistica.md` (Issue #68).*
