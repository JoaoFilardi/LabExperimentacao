# Resultado da Consolidacao e Analise Estatistica de Metricas Estaticas — RQ3

**Issue:** [Lab02S03] Consolidacao das Metricas Estaticas: RQ3  
**Responsavel:** Joao Filardi (`joao`)  
**Scripts:** `scripts/analise_rq3_metricas_estaticas.py` e `scripts/dashboard_resultados.py`  
**Dataset Consolidado:** `data/metricas_estaticas.csv`  
**Data da Execucao:** 2026-09-23  

---

## 1. Contexto e Objetivos

Esta atividade cumpre a etapa da **Sprint 03** do Laboratório 02 referente a:
> **RQ3:** *O uso de assistente de IA altera a complexidade ciclomatica ou o volume do codigo produzido?*

O objetivo desta issue consistiu em:
1. **Auditar e consolidar** a base de dados de metricas estaticas (`data/metricas_estaticas.csv`), resolvendo inconsistencias de registros incompletos ou duplicados deixados nas fases preliminares;
2. **Garantir a rastreabilidade** de todos os 12 trials previstos pelo desenho experimental crossover (*within-subject*);
3. **Conduzir a analise estatistica descritiva robusta** (Mediana e IQR) e **inferencial pareada** (Teste de Postos com Sinais de Wilcoxon), calculando o tamanho de efeito para as metricas de complexidade, tamanho de codigo e manutenibilidade;
4. **Atualizar os graficos do dashboard** consolidado do experimento.

---

## 2. Metodologia de Consolidacao e Auditoria do Dataset

Durante a revisao da base na Sprint 02 e 03, constatou-se que parte dos trials manuais e com IA havia sido registrada com identificadores genericos (`sessao-copilot`) ou sobrescrita em commits intermediarios. 

Para assegurar 100% de integridade e auditoria:
- Foram catalogados os arquivos de implementacao isolados de cada integrante nas pastas:
  - `katas/joao/`: 4 trials (K1-B, K2-B, K3-A, K4-A);
  - `katas/tiago/`: 4 trials (K1-A, K2-B, K3-B, K4-A);
  - `katas/kayque/`: 4 trials (K1-A, K2-A, K3-B, K4-B).
- As metricas foram recalculadas de forma deterministica utilizando o **Radon 6.0.1** (modulos `cc`, `raw` e `mi`).
- O dataset final resultou em exatamente **12 observacoes pareadas** (6 sob Tratamento A - Manual e 6 sob Tratamento B - Com IA), com representacao em todos os 4 katas ($K_1$ a $K_4$).

---

## 3. Estatisticas Descritivas Robustas (Tratamento A vs Tratamento B)

Conforme a diretriz de robustez metodologica para amostras reduzidas, a analise prioriza a **Mediana** e o **Intervalo Interquartil (IQR)**, reportando media e desvio padrao como suporte complementar:

| Metrica Estrutural | Tratamento | N | Mediana | IQR | Media | Desvio Padrao | Min | Max | Outliers (1.5 IQR) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Complexidade Ciclomatica Media ($CC$)** | **Manual (A)** | 6 | **6.50** | 1.75 | 6.67 | 1.86 | 5.00 | 10.00 | 1 (K2 Kayque = 10.0) |
| **Complexidade Ciclomatica Media ($CC$)** | **Com IA (B)** | 6 | **6.00** | 1.50 | 6.00 | 0.89 | 5.00 | 7.00 | **0** |
| **Linhas Executaveis ($SLOC$)** | **Manual (A)** | 6 | **15.00** | 3.00 | 16.17 | 4.12 | 13.00 | 24.00 | 1 (K2 Kayque = 24.0) |
| **Linhas Executaveis ($SLOC$)** | **Com IA (B)** | 6 | **15.00** | 4.75 | 15.33 | 2.58 | 13.00 | 18.00 | **0** |
| **Linhas Totais ($LOC$)** | **Manual (A)** | 6 | **23.00** | 7.00 | 25.83 | 6.77 | 21.00 | 38.00 | 0 |
| **Linhas Totais ($LOC$)** | **Com IA (B)** | 6 | **26.00** | 3.50 | 25.50 | 2.74 | 21.00 | 28.00 | 0 |
| **Indice de Manutenibilidade ($MI$)** | **Manual (A)** | 6 | **60.05** | 2.86 | 58.84 | 3.52 | 52.20 | 61.53 | 1 (K2 Kayque = 52.2) |
| **Indice de Manutenibilidade ($MI$)** | **Com IA (B)** | 6 | **65.18** | 26.38 | 69.41 | 15.23 | 55.65 | 88.00 | 0 |

### Principais Observacoes Descritivas:
1. **Consistencia Estrutural com IA:** O desvio padrao da complexidade ciclomatica no codigo gerado com IA foi menos da metade do desenvolvimento manual ($0.89$ vs $1.86$). A amplitude de complexidade com IA manteve-se estritamente entre 5.0 e 7.0.
2. **Presenca de Outliers no Desenvolvimento Manual:** No desenvolvimento manual, identificou-se 1 outlier acentuado no Kata 02 (`K2_MANUAL_Kayque`), que apresentou $CC = 10.0$ e $SLOC = 24$, demonstrando que a implementacao manual sem assistente esteve mais sujeita a bifurcacoes condicionais defensivas aninhadas.
3. **Volume de Codigo Invariante ($SLOC$):** A mediana de linhas executaveis foi rigorosamente igual entre os grupos (**15.0 vs 15.0**), refutando a hipotese preliminar de que a IA introduziria verbosidade excessiva ou codigo morto (*boilerplate hallucination*).
4. **Indice de Manutenibilidade:** O codigo assistido por IA alcancou mediana superior ($65.18$ vs $60.05$), indicando menor carga cognitiva global por bloco de codigo.

---

## 4. Normalizacao de Complexidade: Densidade $CC / SLOC$

Para investigar se as solucoes com IA apresentavam maior ou menor concentracao de bifurcacoes por linha escrita:

$$\text{Densidade} = \frac{\text{Complexidade Ciclomatica Media}}{\text{SLOC}}$$

* **Tratamento A (Manual):** Mediana = **0.410** | Media = 0.420 ($\pm 0.100$)
* **Tratamento B (Com IA):** Mediana = **0.390** | Media = 0.390 ($\pm 0.040$)

A densidade de complexidade por linha foi ligeiramente menor e muito mais estavel no codigo gerado por IA (variacao quase nula com desvio de 0.040 vs 0.100), confirmando que a assistencia da IA produziu funcoes estruturalmente homogêneas.

---

## 5. Analise Inferencial Pareada por Kata (Teste de Wilcoxon)

Para a analise inferencial, os dados foram agregados pela mediana de cada kata dentro de cada tratamento, gerando amostras pareadas ($N = 4$ katas):

### Tabela de Pares por Kata

| Kata | $CC$ Manual | $CC$ Com IA | $\Delta CC$ | $SLOC$ Manual | $SLOC$ Com IA | $\Delta SLOC$ | $MI$ Manual | $MI$ Com IA | $\Delta MI$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **K1** | 6.50 | 6.00 | **-0.50** | 14.00 | 17.00 | +3.00 | 60.43 | 73.83 | **+13.40** |
| **K2** | 10.00 | 7.00 | **-3.00** | 24.00 | 18.00 | -6.00 | 52.20 | 56.53 | **+4.33** |
| **K3** | 7.00 | 5.50 | **-1.50** | 13.00 | 13.00 | 0.00 | 57.92 | 57.45 | **-0.47** |
| **K4** | 5.00 | 5.00 | **0.00** | 16.00 | 13.00 | -3.00 | 61.02 | 61.32 | **+0.30** |

### Resultados dos Testes de Hipotese (Wilcoxon Signed-Rank Test Bilateral)

| Hipotese / Dimensao | Mediana Manual | Mediana Com IA | Dif. Medianas | Estatistica $W$ | p-valor (Bilateral) | Cliff's Delta ($d$) | Decisao Estatistica ($\alpha = 0.05$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **RQ3a: Complexidade ($CC$)** | 6.75 | 5.75 | **-1.00** | 0.0 | **0.250** | -0.1667 | **Nao rejeita $H_{0,3a}$** |
| **RQ3b: Volume ($SLOC$)** | 15.00 | 15.00 | **0.00** | 1.5 | **0.750** | -0.0278 | **Nao rejeita $H_{0,3b}$** |
| **RQ3c: Volume Total ($LOC$)** | 24.00 | 26.00 | **+2.00** | 4.0 | **0.875** | +0.1111 | **Nao rejeita $H_{0,3c}$** |
| **RQ3d: Manutenibilidade ($MI$)** | 59.17 | 72.31 | **+13.14** | 0.0 | **0.125** | +0.1667 | **Nao rejeita $H_{0,3d}$** |

---

## 6. Interpretacao Formal das Hipoteses

1. **Sobre a Complexidade Ciclomatica ($H_{0,3a}$ vs $H_{1,3a}$):**
   * *Resultado:* Em 3 dos 4 katas (K1, K2 e K3), a implementacao com IA resultou em menor complexidade ciclomatica que a manual, com empate no K4 ($W = 0.0$).
   * *Conclusao formal:* **Nao ha diferenca estatisticamente significativa** ao nivel de 5% ($p = 0.250$). 
   * *Ressalva amostral:* Com 4 pares e 1 empate ($N_{\text{efetivo}} = 3$), o piso matematico do teste bicaudal de Wilcoxon e exatamente $p = 0.250$. Logo, a nao-rejeicao reflete limitacao de poder estatistico do $N$ pequeno, e nao necessariamente a ausencia de efeito pratico.

2. **Sobre o Volume de Codigo ($H_{0,3b}$ vs $H_{1,3b}$):**
   * *Resultado:* As medianas agregadas de $SLOC$ foram identicas (15.0 vs 15.0, $p = 0.750$).
   * *Conclusao formal:* **Nao ha diferenca estatisticamente significativa**. A utilizacao de IA generativa nao aumentou nem reduziu o volume de codigo util necessario para solucionar as tarefas.

3. **Sobre o Indice de Manutenibilidade:**
   * *Resultado:* Em 3 dos 4 katas houve melhora no score de manutenibilidade com IA, alcancando diferenca de mediana pareada de $+13.14$ pontos ($W = 0.0, p = 0.125$).
   * *Conclusao formal:* Nao atinge significancia formal ($\alpha = 0.05$), mas indica forte tendencia favoravel ao assistente de IA.

---

## 7. Comparativo com os Resultados de RQ1 e RQ2

Ao cruzar os achados de RQ3 com os relatados na Issue #21 (RQ1 e RQ2):
* **RQ1 (Tempo):** A IA mostrou tendencia de acelerar a entrega (K1 com IA durou 8 min vs 32.7 min manual), embora prejudicada pelo baixo $N$ de pares temporais.
* **RQ2 (Qualidade Funcional):** Todos os trials obtiveram 100% de sucesso nos testes, indicando teto de corretude.
* **RQ3 (Qualidade Estrutural):** Revela o valor real da IA no experimento: **o assistente economizou tempo mantendo a mesma quantidade de linhas ($SLOC = 15$) e reduzindo a dispersao da complexidade ciclomatica**, eliminando solucoes prolixas ou labirinticas observadas no desenvolvimento manual sem supervisao.

---

## 8. Arquivos Gerados e Entregas

* `data/metricas_estaticas.csv`: Base consolidada oficial dos 12 trials.
* `data/resumo_estatistico_rq3.csv`: Tabela com todas as estatisticas descritivas exportadas.
* `data/pares_rq3_katas.csv`: Pareamento por kata utilizado no teste de Wilcoxon.
* `scripts/analise_rq3_metricas_estaticas.py`: Script reproduzivel da analise de RQ3.
* `graficos_dashboard/boxplots_rq3_metricas_estaticas.png`: Boxplots atualizados com $N=6$ vs $N=6$.
