# Planejamento da Análise Estatística e das Visualizações

**Experimento:** Comparação de desempenho entre PostgreSQL 17 e PostgreSQL 18  
**Issue:** LAB05S01 — Definir métricas e estratégia de análise dos resultados  
**Responsável:** Integrante C (Análise e Impacto)  
**Sprint:** 1

---

## 1. Revisão da pergunta de pesquisa e das métricas propostas

### Pergunta principal de pesquisa (RQ)

> **A versão 18 do PostgreSQL apresenta diferenças de desempenho e eficiência no uso de recursos computacionais em comparação com a versão 17, sob uma carga de trabalho controlada?**

A pergunta é **neutra e bilateral**: não pressupõe superioridade de nenhuma versão. O estudo deve detectar melhorias, pioras ou ausência de diferença relevante em cada métrica avaliada.

### Métricas propostas pelo grupo (revisadas)

As métricas listadas no arquivo de contextualização (`contextualizacao_lab05_postgresql.md`, seção 8) são:

| Métrica | Descrição resumida |
|:--------|:-------------------|
| **Latência** | Tempo médio por transação (ms) |
| **TPS** | Transações por segundo — vazão do banco |
| **Consumo de CPU** | Percentual de CPU utilizado durante o benchmark |
| **Consumo de memória** | Memória RAM utilizada pelo container durante o benchmark |

Essas quatro métricas respondem diretamente à RQ e cobrem as dimensões de **velocidade** (latência, TPS) e **eficiência de recursos** (CPU, memória).

> **Nota de qualidade:** otimizar isoladamente uma única métrica pode levar a interpretações incompletas (Lei de Goodhart). Por isso todas as quatro métricas são avaliadas em conjunto e os resultados são interpretados de forma integrada.

---

## 2. Métricas e suas definições

### 2.1 Latência

| Campo | Definição |
|:------|:----------|
| **O que mede** | Tempo decorrido entre o início e o fim de uma transação |
| **Instrumento** | `pgbench` — campo `latency average` e `latency stddev` |
| **Unidade** | Milissegundos (ms) |
| **Entidade** | Produto — PostgreSQL como SGBD em execução |
| **Atributo** | Externo, medido pelo comportamento observável |
| **Tipo de medida** | Direta (cronometrada pelo `pgbench`) |

### 2.2 Transações por segundo (TPS)

| Campo | Definição |
|:------|:----------|
| **O que mede** | Quantidade de transações completas por segundo |
| **Instrumento** | `pgbench` — campo `tps` (incluindo e excluindo estabelecimento de conexão) |
| **Unidade** | Transações/segundo |
| **Entidade** | Produto — PostgreSQL como SGBD |
| **Atributo** | Externo |
| **Tipo de medida** | Direta |

### 2.3 Consumo de CPU

| Campo | Definição |
|:------|:----------|
| **O que mede** | Percentual de CPU consumido pelo container durante o benchmark |
| **Instrumento** | `docker stats` (coletado por script Python em paralelo ao `pgbench`) |
| **Unidade** | Percentual (%) |
| **Entidade** | Recurso — container Docker da versão PostgreSQL testada |
| **Atributo** | Externo |
| **Tipo de medida** | Direta |

### 2.4 Consumo de memória

| Campo | Definição |
|:------|:----------|
| **O que mede** | Memória RAM utilizada pelo container durante o benchmark |
| **Instrumento** | `docker stats` (campo `MEM USAGE`) |
| **Unidade** | Mebibytes (MiB) |
| **Entidade** | Recurso — container Docker da versão PostgreSQL testada |
| **Atributo** | Externo |
| **Tipo de medida** | Direta |

---

## 3. Escalas de medição

A escala de cada métrica determina quais estatísticas e testes são apropriados.

| Métrica | Escala | Justificativa |
|:--------|:-------|:--------------|
| **Latência (ms)** | **Razão** | Zero absoluto existe (0 ms = sem tempo); razões entre valores têm sentido ("dobrou o tempo") |
| **TPS** | **Razão** | Zero absoluto existe; proporções são interpretáveis |
| **CPU (%)** | **Razão** | Zero absoluto existe (0% = nenhum uso); escala contínua com zero real |
| **Memória (MiB)** | **Razão** | Zero absoluto existe; proporções são interpretáveis |

Todas as métricas estão em **escala de razão**, o que permite:
- Calcular média, desvio padrão, coeficiente de variação.
- Calcular razões entre versões (ex.: "PG18 foi 12% mais rápido").
- Aplicar testes paramétricos **se os pressupostos forem verificados**.

---

## 4. Estatísticas descritivas

Para cada métrica, por versão (PostgreSQL 17 e PostgreSQL 18), serão calculadas:

| Estatística | Finalidade |
|:------------|:-----------|
| **Média** | Referência central; usada com cautela se a distribuição for assimétrica |
| **Mediana** | Referência robusta a outliers e assimetria |
| **Desvio padrão (DP)** | Variabilidade absoluta das repetições |
| **Coeficiente de variação (CV = DP/Média)** | Variabilidade relativa; útil para comparar métricas em unidades diferentes |
| **Mínimo e máximo** | Identificar valores extremos e verificar se o ambiente estava estável |
| **Intervalo interquartil (IQR = Q3 − Q1)** | Dispersão robusta; complementa o boxplot |
| **Percentis (P25, P50, P75, P95)** | Especialmente relevantes para latência (P95 captura o pior caso) |

> **Atenção à distribuição:** se a distribuição das repetições for assimétrica (verificar com histograma e boxplot), a interpretação deve priorizar mediana e IQR, não apenas média e DP.

Exemplo de tabela descritiva esperada (a ser preenchida após a coleta):

| Versão | Métrica | Média | Mediana | DP | CV (%) | Mín | Máx | IQR |
|:-------|:--------|------:|--------:|---:|-------:|----:|----:|----:|
| PG17 | Latência (ms) | — | — | — | — | — | — | — |
| PG18 | Latência (ms) | — | — | — | — | — | — | — |
| PG17 | TPS | — | — | — | — | — | — | — |
| PG18 | TPS | — | — | — | — | — | — | — |
| PG17 | CPU (%) | — | — | — | — | — | — | — |
| PG18 | CPU (%) | — | — | — | — | — | — | — |
| PG17 | Memória (MiB) | — | — | — | — | — | — | — |
| PG18 | Memória (MiB) | — | — | — | — | — | — | — |

---

## 5. Hipóteses e testes de hipótese

### 5.1 Formulação das hipóteses

As hipóteses são formuladas **antes da coleta dos dados** e são bilaterais, pois a RQ é neutra.

Para cada métrica *m* ∈ {Latência, TPS, CPU, Memória}:

> **H₀:** Não há diferença entre PG17 e PG18 na métrica *m* sob a carga testada.  
> **H₁:** Há diferença entre PG17 e PG18 na métrica *m* sob a carga testada.

### 5.2 Decisão sobre qual teste aplicar

O teste será escolhido **após verificar os pressupostos** sobre os dados coletados, seguindo o fluxo abaixo:

```
Para cada métrica:
   |
   ├── As observações são independentes entre repetições? (esperado: sim)
   |
   ├── Verificar normalidade:
   |      Shapiro-Wilk (amostras pequenas, n < 50)
   |      OU histograma + Q-Q plot
   |
   ├── SE dados seguem distribuição normal em ambas as versões:
   |      └── Teste t de Student para amostras independentes
   |             (verificar homogeneidade de variâncias com Levene;
   |              usar variante de Welch se variâncias forem desiguais)
   |
   └── SE dados NÃO seguem normalidade (ou n for pequeno e assimétrico):
          └── Mann-Whitney U (alternativa não paramétrica ao teste t)
                 (compara medianas / distribuições)
```

> **Justificativa:** o teste t exige normalidade e homogeneidade de variâncias. Benchmarks de banco de dados frequentemente apresentam distribuições levemente assimétricas (outliers por variação do SO). Verificar antes de assumir parametricidade é essencial para não invalidar as conclusões (ameaça à validade de conclusão).

### 5.3 Nível de significância

- **α = 0,05** (5%) para todos os testes.
- O valor-p reportado será o valor calculado; a decisão de rejeitar H₀ será tomada comparando p ao α.

### 5.4 Correção para múltiplas comparações

Serão realizados testes para **4 métricas**. Realizar múltiplos testes aumenta a chance de falso positivo (erro tipo I). A equipe avaliará a necessidade de ajuste:

| Situação | Abordagem |
|:---------|:----------|
| Métricas são independentes entre si | Reportar sem ajuste, discutindo o risco |
| Métricas são correlacionadas | Aplicar correção de Bonferroni (α ajustado = 0,05 / 4 = 0,0125) |

A decisão será documentada junto aos resultados na Sprint 2.

---

## 6. Tamanho do efeito

Significância estatística não implica relevância prática. O tamanho do efeito quantifica **o quanto** as versões diferem.

| Métrica | Medida de tamanho do efeito | Interpretação convencional |
|:--------|:----------------------------|:--------------------------|
| **Latência e TPS** (se paramétrico — teste t) | **d de Cohen** = (μ₁ − μ₂) / s_pooled | \|d\| < 0,2 → negligenciável · 0,2–0,5 → pequeno · 0,5–0,8 → médio · > 0,8 → grande |
| **CPU e Memória** (se paramétrico — teste t) | **d de Cohen** | Idem |
| **Qualquer métrica** (se não paramétrico — Mann-Whitney) | **r de rank-biserial** = 1 − (2U / n₁n₂) | \|r\| < 0,1 → negligenciável · 0,1–0,3 → pequeno · 0,3–0,5 → médio · > 0,5 → grande |
| **Diferença percentual** (complementar) | (μ_PG18 − μ_PG17) / μ_PG17 × 100% | Interpretação de negócio: quanto % melhorou/piorou |

A diferença percentual é calculada para **todos os casos** como forma de comunicar o resultado para audiências não técnicas.

---

## 7. Visualizações planejadas

### 7.1 Por métrica — análise exploratória e comparativa

| Gráfico | O que mostra | Ferramenta |
|:--------|:-------------|:-----------|
| **Boxplot lado a lado** (PG17 × PG18) | Mediana, IQR, outliers de cada versão | Matplotlib / Seaborn |
| **Histograma** (por versão) | Distribuição das repetições; verificar normalidade visualmente | Matplotlib |
| **Q-Q plot** | Verificar aderência à normal (suporte à decisão do teste) | SciPy / Matplotlib |
| **Strip plot** (pontos individuais) | Mostrar cada repetição, sobreposto ao boxplot | Seaborn |

### 7.2 Comparação entre versões — síntese dos resultados

| Gráfico | O que mostra |
|:--------|:-------------|
| **Gráfico de barras com barras de erro** (média ± DP) | Comparação direta das médias; barras de erro mostram variabilidade |
| **Tabela de resultados descritivos** | Síntese compacta de todas as métricas |
| **Gráfico de diferença percentual** | Quanto (%) PG18 difere de PG17 em cada métrica |

### 7.3 Métricas de recursos ao longo do tempo (se coletado por série temporal)

| Gráfico | O que mostra |
|:--------|:-------------|
| **Linha temporal de CPU (%)** | Evolução do consumo de CPU durante cada execução |
| **Linha temporal de memória (MiB)** | Evolução do consumo de memória durante cada execução |

> **Nota:** a série temporal de CPU e memória depende da resolução de coleta do script `docker stats`. Será confirmado na coleta piloto.

### 7.4 Checklist de boas práticas para os gráficos

- [ ] Todos os eixos têm rótulos com unidade.
- [ ] Legendas identificam claramente PG17 e PG18.
- [ ] Título descreve o que está sendo comparado.
- [ ] Fonte de dados indicada (ex.: "pgbench, n=30 repetições").
- [ ] Escala dos eixos não trunca o zero sem motivo justificado.
- [ ] Cores acessíveis (evitar vermelho × verde sem textura/marcador alternativo).

---

## 8. Indicadores de impacto para empresas e usuários

O objetivo desta seção é traduzir os resultados do experimento em termos práticos para quem usa ou considera usar o PostgreSQL em produção.

### 8.1 Indicadores que serão calculados (após a coleta)

| Indicador | Como calcular | Fonte dos dados de escala |
|:----------|:--------------|:--------------------------|
| **Ganho/perda de TPS (%)** | (TPS_PG18 − TPS_PG17) / TPS_PG17 × 100 | Resultados do experimento |
| **Redução/aumento de latência (ms e %)** | Diferença absoluta e relativa entre medianas | Resultados do experimento |
| **Economia de CPU (pp)** | Diferença em pontos percentuais de CPU | Resultados do experimento |
| **Transações adicionais por hora** | Δ_TPS × 3600 | Derivado dos resultados |
| **Horas de CPU economizadas** (estimativa) | Δ_CPU% × usuários adotantes × tempo | Número de empresas/instâncias com fonte pública |

### 8.2 Fontes públicas identificadas para estimar impacto

As fontes abaixo serão consultadas para contextualizar os resultados. Data de acesso será registrada na Sprint 3.

| Dado de impacto | Fonte sugerida |
|:----------------|:---------------|
| Popularidade e adoção do PostgreSQL | Stack Overflow Developer Survey (anual) |
| Ranking de SGBDs | DB-Engines Ranking — https://db-engines.com/en/ranking |
| Downloads da imagem oficial Docker | Docker Hub — https://hub.docker.com/_/postgres |
| Empresas que usam PostgreSQL | Página oficial: https://www.postgresql.org/about/users/ |
| Versões disponíveis e datas de release | https://www.postgresql.org/support/versioning/ |

> **Aviso metodológico:** qualquer extrapolação dos resultados do experimento (ex.: "se todos os usuários migrarem para PG18…") deve ser explicitamente identificada como **estimativa**, apresentar suas premissas e delimitar claramente o que o experimento **não permite afirmar**. Os resultados são válidos apenas para o hardware, configuração e carga utilizados.

---

## 9. Conexão com os conteúdos da disciplina

| Conceito | Como aparece neste planejamento |
|:---------|:-------------------------------|
| **GQM** | RQ → pergunta sobre desempenho → métricas observáveis (latência, TPS, CPU, memória) |
| **Escalas de medição** | Todas as métricas em escala de razão (seção 3) |
| **Entidades e atributos** | PostgreSQL como produto; CPU/memória como recursos; atributos externos medidos diretamente |
| **Estatística descritiva** | Média, mediana, DP, IQR, percentis (seção 4) |
| **Teste de hipótese** | H₀/H₁ por métrica, decisão entre paramétrico e não paramétrico (seção 5) |
| **Tamanho do efeito** | d de Cohen / r de rank-biserial (seção 6) |
| **Ameaças à validade de conclusão** | Verificação de normalidade, múltiplas comparações, poder estatístico (seções 5.4) |
| **Lei de Goodhart** | Avaliação de múltiplas métricas; nenhuma isolada define "melhor versão" (seção 1) |

---

## 10. Critérios de aceitação — verificação

| Critério | Status |
|:---------|:-------|
| Métricas de análise definidas | ✅ Latência, TPS, CPU, Memória (seções 2 e 3) |
| Escalas de medição identificadas | ✅ Todas em escala de razão (seção 3) |
| Estratégia de análise estatística documentada | ✅ Descritiva (seção 4), hipóteses (seção 5), tamanho do efeito (seção 6) |
| Possíveis visualizações planejadas | ✅ Boxplot, histograma, Q-Q plot, barras, temporais (seção 7) |
| Indicadores de impacto identificados | ✅ Ganho de TPS, redução de latência, economia de CPU (seção 8) |

---

## 11. Pendências e próximos passos (Sprint 2)

- [ ] Executar coleta piloto e verificar se o script `docker stats` captura CPU/memória com resolução suficiente.
- [ ] Confirmar número de repetições (sugestão: mínimo 20–30 por versão) e justificar com base na variabilidade piloto.
- [ ] Verificar normalidade das distribuições coletadas (Shapiro-Wilk) e confirmar o teste a aplicar.
- [ ] Decidir se será necessário ajuste de Bonferroni para múltiplas comparações.
- [ ] Registrar hardware e condições do ambiente de teste para suportar análise de ameaças à validade.

---

*Documento criado na Sprint 1 — LAB05S01. Deve ser revisado e complementado ao longo das Sprints 2 e 3 conforme os dados forem coletados.*
