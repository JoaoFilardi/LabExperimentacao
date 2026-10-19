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
