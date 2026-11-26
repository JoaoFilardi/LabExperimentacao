# Análise Estatística dos Dados Coletados

**Experimento:** Comparação de desempenho e consumo de recursos entre PostgreSQL 17 e PostgreSQL 18  
**Issue:** `#68` — `[ LAB05S02 ] Realizar análise estatística dos dados coletados`  
**Responsável:** Integrante C — Análise e Impacto (`kayqueallan`)  
**Sprint:** 2 (`LAB05S02`)  
**Data:** 25/11/2026  

---

## 1. Verificação dos Dados Validados Recebidos

A análise foi conduzida integralmente sobre os artefatos validados produzidos na Issue `#66` ([execucao_validacao_coleta.md](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/execucao_validacao_coleta.md)), respeitando o fluxo definido em [planejamento_analise_estatistica.md](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/planejamento_analise_estatistica.md):

- **Fonte tabular principal:** [benchmark_validado.csv](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/data/processed/benchmark_validado.csv) — `60` execuções válidas (`30` no **PostgreSQL 17.12** e `30` no **PostgreSQL 18.7**), com `0` valores ausentes, `0` transações falhas e balanceamento temporal exato de blocos ABBA (`índice médio = 6,5` em ambas as versões).
- **Série temporal de recursos:** [resource_timeseries_validado.csv](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/data/processed/resource_timeseries_validado.csv) — `459` amostras de ~`1 s` vinculadas às `60` rodadas válidas.
- **Auditoria prévia confirmada:** [relatorio_validacao.json](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/data/processed/relatorio_validacao.json) (`"aprovado": true`, `0` erros).
- **Script reproduzível:** [analise_estatistica.py](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/src/analise_estatistica.py), com saída estruturada em [resumo_analise_estatistica.json](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/results/resumo_analise_estatistica.json).

---

## 2. Análise Estatística Descritiva

Todas as quatro métricas dependentes estão em **escala de razão** (possuem zero absoluto e permitem razões proporcionais). A tabela abaixo sintetiza as medidas descritivas para $n = 30$ repetições por versão ([estatisticas_descritivas.csv](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/results/estatisticas_descritivas.csv)):

| RQ | Métrica | Versão | $n$ | Média | Mediana | DP | CV (%) | Mín | Máx | IQR | P95 |
| :-: | :--- | :---: | :-: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **RQ1** | **Latência média (`ms`)** | `PG17` | 30 | `2,8355` | `2,8245` | `0,0701` | `2,47%` | `2,7290` | `3,0020` | `0,0935` | `2,9625` |
| **RQ1** | **Latência média (`ms`)** | `PG18` | 30 | `2,8848` | `2,8715` | `0,0760` | `2,64%` | `2,7730` | `3,0960` | `0,0850` | `3,0250` |
| **RQ2** | **TPS (`tx/s`)** | `PG17` | 30 | `2820,48` | `2830,30` | `68,94` | `2,44%` | `2661,96` | `2928,42` | `93,38` | `2914,50` |
| **RQ2** | **TPS (`tx/s`)** | `PG18` | 30 | `2772,61` | `2783,93` | `71,34` | `2,57%` | `2581,64` | `2882,20` | `82,20` | `2863,00` |
| **RQ3** | **CPU média (`%` multi-core)** | `PG17` | 30 | `489,18` | `488,27` | `15,38` | `3,14%` | `441,80` | `512,42` | `13,23` | `508,84` |
| **RQ3** | **CPU média (`%` multi-core)** | `PG18` | 30 | `493,97` | `496,78` | `16,02` | `3,24%` | `439,49` | `521,81` | `14,45` | `513,06` |
| **RQ4** | **Memória RSS média (`MiB`)** | `PG17` | 30 | `496,58` | `500,33` | `15,86` | `3,19%` | `443,83` | `512,47` | `9,79` | `511,81` |
| **RQ4** | **Memória RSS média (`MiB`)** | `PG18` | 30 | `536,93` | `541,64` | `15,88` | `2,96%` | `490,75` | `551,18` | `14,05` | `550,49` |

**Observações descritivas iniciais:**
- A estabilidade entre repetições foi alta em todas as métricas (**CV entre `2,44%` e `3,24%`**).
- Em **Latência (`RQ1`)** e **TPS (`RQ2`)**, média e mediana são muito próximas em ambas as versões, sugerindo simetria aproximada.
- Em **CPU (`RQ3`)** e **Memória (`RQ4`)**, a mediana supera a média em ambos os grupos por causa de poucas execuções na cauda inferior (outliers sinalizados na validação em `RUN_014`, `RUN_018`, `RUN_051`, `RUN_052` e `RUN_065`).

---

## 3. Verificação de Pressupostos e Testes de Hipótese

Seguindo exatamente a árvore de decisão da Seção 5.2 de [planejamento_analise_estatistica.md](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/planejamento_analise_estatistica.md), testou-se a normalidade com **Shapiro-Wilk** ($\alpha = 0{,}05$) e a homogeneidade de variâncias com **Levene** ($\alpha = 0{,}05$) antes da escolha de cada teste inferencial:

### 3.1 Pressupostos por métrica

| Métrica | Shapiro-Wilk PG17 ($W$, $p$) | Shapiro-Wilk PG18 ($W$, $p$) | Levene ($F$, $p$) | Teste Selecionado |
| :--- | :---: | :---: | :---: | :--- |
| **Latência média (`ms`)** | `0,9518` (`p = 0,1887`) | `0,9323` (`p = 0,0565`) | `0,0191` (`p = 0,8907`) | **Teste t de Student** *(normalidade e homocedasticidade atendidas)* |
| **TPS (`tx/s`)** | `0,9576` (`p = 0,2693`) | `0,9458` (`p = 0,1307`) | `0,1178` (`p = 0,7327`) | **Teste t de Student** *(normalidade e homocedasticidade atendidas)* |
| **CPU média (`%`)** | `0,8148` (`p = 0,00012`) | `0,9025` (`p = 0,00968`) | `0,1743` (`p = 0,6778`) | **Mann-Whitney U** *(violação de normalidade nos dois grupos)* |
| **Memória RSS média (`MiB`)** | `0,6989` (`p = 1,50e-6`) | `0,7366` (`p = 5,57e-6`) | `0,0919` (`p = 0,7628`) | **Mann-Whitney U** *(violação severa de normalidade)* |

### 3.2 Correlação entre métricas e decisão sobre múltiplas comparações

A matriz de correlação de **Spearman** ([correlacoes_metricas.csv](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/results/correlacoes_metricas.csv)) revelou:
- `latencia_media_ms` × `tps`: **$\rho = -0{,}9997$** (correlação negativa quase perfeita, esperada pela relação inversa entre tempo de transação e vazão sob concorrência fixa).
- `cpu_media_pct` × `memoria_media_mib`: **$\rho = +0{,}4155$** (correlação moderada positiva).
- `memoria_media_mib` × `latencia_media_ms`: **$\rho = +0{,}2754$** / × `tps`: **$\rho = -0{,}2744$**.

Como as métricas não são independentes entre si, aplicou-se a **correção conservadora de Bonferroni** para 4 testes ($\alpha_{\text{ajustado}} = 0{,}05 / 4 = 0{,}0125$; $p_{\text{bonf}} = \min(4p,\, 1{,}0)$), reportando ambos os critérios para total transparência.

### 3.3 Resultados dos testes de hipótese e tamanho do efeito ([testes_hipotese_efeito.csv](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/results/testes_hipotese_efeito.csv))

| RQ | Hipótese Testada | Teste Bilateral | Estatística | $p$-valor bruto | $p$-valor Bonferroni | Rejeita $H_0$ ($\alpha_{\text{adj}} = 0{,}0125$)? | Dif. PG18 vs PG17 (Média / Mediana) | Tamanho do Efeito |
| :-: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **RQ1** | $H_{0,\text{lat}}$: Latência igual | Teste t Student | `t = 2,6091` | `0,0115` | `0,0461` | **Sim** *(p < 0,0125)* | `+0,0493 ms` (`+1,74%`) / `+1,66%` | `d = +0,6737` (**médio**) |
| **RQ2** | $H_{0,\text{tps}}$: TPS igual | Teste t Student | `t = -2,6427` | `0,0106` | `0,0422` | **Sim** *(p < 0,0125)* | `-47,87 tx/s` (`-1,70%`) / `-1,64%` | `d = -0,6823` (**médio**) |
| **RQ3** | $H_{0,\text{cpu}}$: CPU igual | Mann-Whitney U | `U = 559,0` | `0,1087` | `0,4348` | **Não** | `+4,79 pp` (`+0,98%`) / `+1,74%` | `r = +0,2422` (**pequeno**) |
| **RQ4** | $H_{0,\text{mem}}$: Memória igual | Mann-Whitney U | `U = 837,0` | `1,10e-8` | `4,41e-8` | **Sim** *(p < 0,0125)* | `+40,35 MiB` (`+8,13%`) / `+8,26%` | `r = +0,8600` (**grande**) |

*(IC 95% da diferença de médias PG18 − PG17: Latência `[+0,0115, +0,0871] ms`; TPS `[-84,13, -11,61] tx/s`; CPU `[-3,33, +12,91] pp`; Memória `[+32,15, +48,55] MiB`.)*

---

## 4. Análise de Sensibilidade (Sem Outliers e Pareamento por Semente)

Conforme previsto na validação não destrutiva da Issue `#66`, verificou-se se a exclusão temporária dos outliers IQR ou a consideração do pareamento por `random_seed` (`4201..4230`) alteraria as conclusões ([analise_sensibilidade_outliers.csv](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/results/analise_sensibilidade_outliers.csv)):

| Métrica | Outliers IQR removidos | Resultado sem outliers (independente) | Teste pareado por `random_seed` (todos os dados) | Estabilidade da conclusão |
| :--- | :---: | :--- | :--- | :--- |
| **Latência (`RQ1`)** | `2` (`RUN_032`, `RUN_056`) | Dif. `+1,26%`, `p = 0,0392`, `d = 0,5548` *(médio)* — significativo a `0,05`, mas `> 0,0125` | `t pareado`, `p = 0,00091` | **Sensível a Bonferroni** sem os 2 outliers; porém **muito robusto** no teste pareado |
| **TPS (`RQ2`)** | `1` (`RUN_056`) | Dif. `-1,46%`, `p = 0,0195`, `d = -0,6262` *(médio)* — significativo a `0,05`, mas `> 0,0125` | `t pareado`, `p = 0,00075` | Idem: diferença moderada e consistente quando pareada por semente |
| **CPU (`RQ3`)** | `3` (`RUN_014`, `RUN_051`, `RUN_052`) | Dif. `+0,68%`, Mann-Whitney `p = 0,1314`, `r = 0,2340` | `Wilcoxon pareado`, `p = 0,1909` | **Totalmente estável**: sem diferença significativa em nenhum cenário |
| **Memória (`RQ4`)** | `5` (`RUN_014`, `RUN_018`, `RUN_051`, `RUN_052`, `RUN_065`) | Passa na normalidade! Teste t `p = 1,50e-27`, `d = 5,7178` *(grande)*, dif. `+8,26%` | `Wilcoxon pareado`, `p = 9,31e-9` | **Altamente robusto**: separação clara entre versões em todos os cenários |

---

## 5. Visualizações Revisadas

Todos os gráficos seguem o checklist da Seção 7.4 de [planejamento_analise_estatistica.md](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/planejamento_analise_estatistica.md) (eixos rotulados com unidades, paleta acessível azul `#0072B2` × laranja `#D55E00`, indicação de $n = 30$ e eixo vertical partindo de zero nos gráficos de barras e séries temporais):

1. **[01_boxplots_strip_metricas.png](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/results/graficos/01_boxplots_strip_metricas.png)** — Boxplots com pontos individuais: evidencia a sobreposição moderada entre PG17 e PG18 em Latência, TPS e CPU, e a **separação nítida de ~40 MiB em Memória RSS**.
2. **[02_histogramas_metricas.png](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/results/graficos/02_histogramas_metricas.png)** — Histogramas sobrepostos: mostram distribuições unimodais próximas à normal em Latência/TPS e assimetria à esquerda em CPU/Memória devido a poucos pontos na cauda inferior.
3. **[03_qqplots_metricas.png](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/results/graficos/03_qqplots_metricas.png)** — Q-Q plots: confirmam boa aderência linear para Latência ($R^2 = 0{,}957$ e $0{,}930$) e TPS ($R^2 = 0{,}964$ e $0{,}945$), enquanto CPU ($R^2 = 0{,}801$ e $0{,}885$) e Memória ($R^2 = 0{,}686$ e $0{,}733$) desviam na cauda inferior, justificando Mann-Whitney U.
4. **[04_barras_medias_dp.png](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/results/graficos/04_barras_medias_dp.png)** — Barras de média ± DP com eixo iniciado em zero: mostra visualmente que, em escala absoluta, as diferenças de Latência, TPS e CPU são sutis, ao passo que a elevação de Memória no PG18 se destaca.
5. **[05_diferenca_percentual.png](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/results/graficos/05_diferenca_percentual.png)** — Síntese das diferenças percentuais de PG18 sobre PG17 com indicação da significância estatística.
6. **[06_serie_temporal_recursos.png](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/results/graficos/06_serie_temporal_recursos.png)** — Série temporal agregada (`1` a `10 s`, mediana + faixa Q25–Q75): revela que a CPU acompanha trajetória praticamente indistinguível entre versões (~`450%`–`525%`), enquanto o **consumo de memória RSS do PG18 permanece ~`35–45 MiB` acima do PG17 do segundo `1` ao segundo `10`**, com crescimento paralelo de preenchimento de *buffers*.

---

## 6. Interpretação Integrada e Relação com as Hipóteses

### 6.1 Respostas às subperguntas e hipóteses

- **RQ1 (Latência — rejeita $H_{0,\text{lat}}$):** sob a carga controlada testada, o **PostgreSQL 18.7 apresentou latência média `+1,74%` maior** (`2,8848 ms` vs `2,8355 ms`; diferença de `+0,0493 ms`, `d = 0,67` médio). Na prática, a diferença absoluta de **~50 microssegundos por transação** é muito pequena, e sem os 2 outliers de PG18 cai para `+1,26%` (`p = 0,0392`).
- **RQ2 (TPS — rejeita $H_{0,\text{tps}}$):** de forma espelhada ($\rho = -0{,}9997$ com a latência), o **PostgreSQL 18.7 entregou `-1,70%` menos TPS** (`2772,61` vs `2820,48 tx/s`; `-47,87 tx/s`, `d = -0,68` médio).
- **RQ3 (CPU — não rejeita $H_{0,\text{cpu}}$):** não houve evidência estatisticamente significativa de diferença no consumo de CPU (`493,97%` vs `489,18%`, `+0,98%`, `p = 0,1087`, `r = 0,24` pequeno). As curvas temporais das duas versões se sobrepõem ao longo de toda a janela de 10 s.
- **RQ4 (Memória RSS — rejeita $H_{0,\text{mem}}$):** o **PostgreSQL 18.7 consumiu `+8,13%` mais memória RAM média** (`536,93` vs `496,58 MiB`; `+40,35 MiB`, `p = 1,10e-8`, tamanho do efeito **grande** `r = 0,86`). Esse é o padrão empírico mais consistente e robusto do experimento.

### 6.2 Explicação técnica dos padrões observados (auditoria `pg_settings`)

Cruzando os dados estatísticos com a auditoria de `pg_settings` registrada em [execucao_validacao_coleta.md](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/execucao_validacao_coleta.md), dois fatores arquiteturais padrão *out-of-the-box* do PostgreSQL 18 explicam diretamente os achados:

1. **`data_checksums = on` por padrão no PostgreSQL 18** (`off` no PG17): a verificação e o cálculo de checksums em todas as páginas de dados aumentam a integridade contra corrupção silenciosa, porém introduzem sobrecarga leve e esperada em operações transacionais de leitura/escrita — coerente com a diferença discreta de **~1,7%** em latência e TPS.
2. **Subsistema nativo de I/O Assíncrono (`io_method = worker`, `io_workers = 3`) e maior `shared_memory_size` (`286 MB` vs `279 MB`):** o PG18 inicia **3 processos *background workers* adicionais** para AIO e estruturas compartilhadas extras (também visível na coluna `num_processos_pg` das séries temporais: tipicamente `17–18` processos no PG18 vs `14–15` no PG17). Em uma base pequena (`scale 10`, ~150 MB) que cabe dentro de `shared_buffers = 256MB` e cache do sistema operacional no Windows, o ganho potencial do AIO não se manifesta, restando apenas o custo fixo de memória dos processos adicionais (`+40 MiB`) e a coordenação de workers.

### 6.3 Cuidado com a Lei de Goodhart

Olhar isoladamente para TPS (`-1,70%`) e Memória (`+8,13%`) levaria à conclusão simplista de que "o PG18 piorou". A leitura multidimensional mostra um *trade-off* de engenharia claro: **o PostgreSQL 18 entrega integridade de dados ativada por padrão (`data_checksums = on`) e infraestrutura pronta para AIO (`io_workers = 3`) ao custo de ~40 MiB adicionais de RAM e ~0,05 ms por transação** nesse perfil de carga OLTP em memória no Windows.

---

## 7. Verificação dos Critérios de Aceitação (Issue `#68`)

| Critério da Issue `#68` | Status | Evidência |
| :--- | :---: | :--- |
| Dados validados recebidos e verificados | ✅ | Seção 1 (`60` execuções + `459` amostras verificadas via `verify_validated_inputs()`). |
| Análise estatística descritiva concluída | ✅ | Seção 2 + [estatisticas_descritivas.csv](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/results/estatisticas_descritivas.csv). |
| Testes estatísticos aplicados | ✅ | Seção 3 (Shapiro-Wilk, Levene, Teste t de Student, Mann-Whitney U, Bonferroni e sensibilidade). |
| Tamanho do efeito calculado | ✅ | Seção 3.3 (`d de Cohen` em Latência/TPS; `r rank-biserial` em CPU/Memória; diferença %). |
| Gráficos e visualizações revisados | ✅ | Seção 5 (6 gráficos em `lab05/results/graficos/`). |
| Resultados relacionados às hipóteses e interpretações documentadas | ✅ | Seções 3.3 e 6 (decisão explícita sobre $H_0$/$H_1$ para RQ1–RQ4 e explicação técnica). |
