# [LAB04S02] Simulação de Violações dos Pressupostos Estatísticos (Questão Q3)
**Issue correspondente:** `#55`  
**Laboratório:** LAB04 — Testes de Hipótese por Dentro: Cenário, Simulação e Visualização  
**Disciplina:** Laboratório de Experimentação de Software — 6º Período  
**Professor:** Danilo Maia  
**Par Selecionado:** P1 (Teste t de Welch × Teste U de Mann-Whitney)  

---

## 1. Objetivo da Questão Q3

O objetivo desta etapa é investigar empiricamente **o que muda quando os dados "não se comportam bem"**, isto é, quando as amostras violam severamente os pressupostos teóricos do teste paramétrico (**Teste t de Welch**). Para isso, repetimos integralmente as simulações de **Erro Tipo I (Q1, sob $H_0$ verdadeira)** e de **Poder Estatístico (Q2, sob $H_1$ com tamanhos de efeito crescentes)** em duas situações realistas de violação de pressupostos, comparando os resultados com o cenário original.

---

## 2. Pressupostos dos Testes e Situações de Violação Simuladas

### 2.1 Pressupostos Relevantes do Par P1
- **Teste t de Welch (Paramétrico):**
  1. Independência entre as observações dentro e entre os grupos;
  2. Variável contínua em escala de razão/intervalo;
  3. **Normalidade das médias amostrais ($\bar{X}_1, \bar{X}_2$)** em cada grupo — garantida exatamente se as populações forem normais ou assintoticamente pelo Teorema Central do Limite (TCL) caso o tamanho amostral $n$ seja suficientemente grande e a distribuição não possua caudas extremas;
  4. **Estabilidade da variância amostral ($s^2$)** usada no erro padrão e na fórmula de graus de liberdade de Welch-Satterthwaite.
- **Teste U de Mann-Whitney (Não-Paramétrico):**
  1. Independência entre as observações;
  2. Escala ordinal ou contínua que permita ordenação conjunta de postos ($1$ a $N = n_1 + n_2$);
  3. **Dispensa normalidade e é robusto a valores extremos**, pois opera exclusivamente sobre os postos relativos.

### 2.2 As Duas Violações Simuladas e sua Relevância em Engenharia de Software

| Código | Situação Simulada | Pressuposto Violado | Por que é relevante no cenário de Pull Requests? |
|---|---|---|---|
| **`Q1_Base` / `Q2_Base`** *(Cenário Original)* | Distribuição Log-normal calibrada nos dados reais ($\mu_{\log} = 2{,}8053$, $\sigma_{\log} = 0{,}9254$, $n = 30$ por grupo) | Assimetria positiva natural do processo ($\text{skewness} \approx 1{,}8$) | Representa o fluxo normal de revisão de PRs em repositórios open-source consolidados (`tiangolo/fastapi`). |
| **`Q3_Outliers`** *(Violação 1: Outliers Severos)* | **10% de contaminação severa** ($6$ de $60$ PRs sorteados aleatoriamente sofrem ampliação de $5\times + 50\text{ h}$, mantendo $n = 30$ por grupo) | Estabilidade finita da variância amostral ($s^2$) e normalidade das médias | Em projetos reais de software, cerca de 5% a 10% dos PRs sofrem bloqueios atípicos (quebras de pipeline de CI/CD, férias de revisores especialistas, conflitos complexos de *rebase* ou disputas arquiteturais), levando centenas de horas até o merge. |
| **`Q3_AmostraPequena`** *(Violação 2: Amostra Pequena)* | **Tamanho amostral reduzido para $n = 10$ PRs por grupo** sob a mesma distribuição Log-normal assimétrica | Convergência assintótica do Teorema Central do Limite (TCL) e aproximação $t$ de Welch-Satterthwaite | Em sprints curtas, times pequenos ou experimentos piloto de adoção de um novo bot, frequentemente avalia-se o impacto com apenas ~10 PRs por grupo. Com $n = 10$ e forte assimetria à direita, o TCL não consegue normalizar a média amostral. |

### 2.3 Garantia de Validade sob $H_0$ Verdadeira ($\delta = 0\%$)
- Em todas as condições, quando o tamanho do efeito é $\delta = 0\%$, ambos os grupos (`sem_bot` e `com_bot`) são amostrados **rigorosamente da mesma distribuição de probabilidade**.
- Na condição `Q3_Outliers` sob $H_0$, os 6 índices contaminados ($10\%$ de $60$) são sorteados uniformemente sem reposição entre todas as 60 observações conjuntas, garantindo que ambos os grupos tenham exatamente a mesma distribuição marginal contaminada e que **não exista qualquer efeito real entre os grupos**.

---

## 3. Resultados de Q1 Repetida em Q3: Taxa de Erro Tipo I ($H_0$ Verdadeira)

Foram executadas **10.000 simulações independentes** (`semente = 42`, $\alpha = 0{,}05$) para cada condição sob $H_0$ verdadeira (resultados salvos em [`lab04/data/resultados_q3_erro_tipo_1.csv`](../data/resultados_q3_erro_tipo_1.csv)):

### Tabela 1: Comparação da Taxa de Erro Tipo I ($\alpha = 5{,}0\%$) — Cenário Original vs. Violações (Q3)

| Condição Experimental | Teste Estatístico | Rejeições ($k / 10.000$) | Taxa Empírica ($\hat{\alpha}$) | Desvio vs. $\alpha = 5\%$ | Variação vs. Cenário Original | IC 95% (Wilson) | Comportamento |
|---|---|---|---|---|---|---|---|
| **Cenário Original (`Q1_Base`)**<br>Log-normal ($n=30$) | **t de Welch** | $393$ | **$3{,}93\%$** | $-1{,}07\text{ p.p.}$ | $0{,}00\text{ p.p.}$ *(ref.)* | $[3{,}57\%; 4{,}33\%]$ | Conservador |
| **Cenário Original (`Q1_Base`)**<br>Log-normal ($n=30$) | **U de Mann-Whitney** | $458$ | **$4{,}58\%$** | $-0{,}42\text{ p.p.}$ | $0{,}00\text{ p.p.}$ *(ref.)* | $[4{,}19\%; 5{,}01\%]$ | Nominal / Bem calibrado |
| **Violação 1 (`Q3_Outliers`)**<br>10% outliers $5\times + 50\text{ h}$ ($n=30$) | **t de Welch** | $328$ | **$3{,}28\%$** | **$-1{,}72\text{ p.p.}$** | **$-0{,}65\text{ p.p.}$** | $[2{,}95\%; 3{,}65\%]$ | **Conservador severo** |
| **Violação 1 (`Q3_Outliers`)**<br>10% outliers $5\times + 50\text{ h}$ ($n=30$) | **U de Mann-Whitney** | $452$ | **$4{,}52\%$** | $-0{,}48\text{ p.p.}$ | **$-0{,}06\text{ p.p.}$** | $[4{,}13\%; 4{,}94\%]$ | Estável (Bradley estrito) |
| **Violação 2 (`Q3_AmostraPequena`)**<br>Log-normal reduzida ($n=10$) | **t de Welch** | $290$ | **$2{,}90\%$** | **$-2{,}10\text{ p.p.}$** | **$-1{,}03\text{ p.p.}$** | $[2{,}59\%; 3{,}25\%]$ | **Conservador extremo** |
| **Violação 2 (`Q3_AmostraPequena`)**<br>Log-normal reduzida ($n=10$) | **U de Mann-Whitney** | $433$ | **$4{,}33\%$** | $-0{,}67\text{ p.p.}$ | **$-0{,}25\text{ p.p.}$** | $[3{,}95\%; 4{,}75\%]$ | Conservador leve |

---

## 4. Resultados de Q2 Repetida em Q3: Poder Estatístico ($H_1$ Verdadeira)

Para avaliar a capacidade de detectar um efeito real, repetimos as **10.000 simulações** em **6 tamanhos de efeito progressivos** $\delta \in \{0\%, 10\%, 20\%, 30\%, 40\%, 50\%\}$ (onde $\delta$ representa a redução percentual no tempo de merge proporcionada pelo bot: $Y_{\text{com}} = (1 - \delta) Y_{\text{sem}}$). Os dados completos estão em [`lab04/data/resultados_q3_poder_violacoes.csv`](../data/resultados_q3_poder_violacoes.csv) e [`lab04/data/resultados_q3_curvas_g4.csv`](../data/resultados_q3_curvas_g4.csv).

### Tabela 2: Curvas de Poder Estatístico (%) — Cenário Original vs. Violações de Pressupostos (Q3)

| Condição Experimental | Efeito ($\delta$) | Poder: t de Welch (%) | Poder: Mann-Whitney (%) | Vantagem de Mann-Whitney ($\text{MW} - \text{Welch}$) | Queda de Poder do Welch vs. Base | Queda de Poder do MW vs. Base |
|---|---|---|---|---|---|---|
| **Cenário Original (`Q2_Base`, $n=30$)** | $0\%$ *(H₀)* | $3{,}93\%$ | $4{,}58\%$ | $+0{,}65\text{ p.p.}$ | $0{,}00\text{ p.p.}$ | $0{,}00\text{ p.p.}$ |
| **Cenário Original (`Q2_Base`, $n=30$)** | $10\%$ | $5{,}46\%$ | $6{,}88\%$ | $+1{,}42\text{ p.p.}$ | $0{,}00\text{ p.p.}$ | $0{,}00\text{ p.p.}$ |
| **Cenário Original (`Q2_Base`, $n=30$)** | $20\%$ | $10{,}92\%$ | $14{,}30\%$ | $+3{,}38\text{ p.p.}$ | $0{,}00\text{ p.p.}$ | $0{,}00\text{ p.p.}$ |
| **Cenário Original (`Q2_Base`, $n=30$)** | $30\%$ | $22{,}49\%$ | $29{,}59\%$ | $+7{,}10\text{ p.p.}$ | $0{,}00\text{ p.p.}$ | $0{,}00\text{ p.p.}$ |
| **Cenário Original (`Q2_Base`, $n=30$)** | $40\%$ | $40{,}52\%$ | $52{,}82\%$ | $+12{,}30\text{ p.p.}$ | $0{,}00\text{ p.p.}$ | $0{,}00\text{ p.p.}$ |
| **Cenário Original (`Q2_Base`, $n=30$)** | $50\%$ | $64{,}20\%$ | $79{,}08\%$ | **$+14{,}88\text{ p.p.}$** | $0{,}00\text{ p.p.}$ | $0{,}00\text{ p.p.}$ |
| **Violação 1: Outliers (`Q3_Outliers`, $n=30$)** | $0\%$ *(H₀)* | $3{,}28\%$ | $4{,}52\%$ | $+1{,}24\text{ p.p.}$ | $-0{,}65\text{ p.p.}$ | $-0{,}06\text{ p.p.}$ |
| **Violação 1: Outliers (`Q3_Outliers`, $n=30$)** | $10\%$ | $3{,}69\%$ | $6{,}09\%$ | $+2{,}40\text{ p.p.}$ | $-1{,}77\text{ p.p.}$ | $-0{,}79\text{ p.p.}$ |
| **Violação 1: Outliers (`Q3_Outliers`, $n=30$)** | $20\%$ | $5{,}32\%$ | $11{,}07\%$ | $+5{,}75\text{ p.p.}$ | $-5{,}60\text{ p.p.}$ | $-3{,}23\text{ p.p.}$ |
| **Violação 1: Outliers (`Q3_Outliers`, $n=30$)** | $30\%$ | $8{,}78\%$ | $21{,}65\%$ | $+12{,}87\text{ p.p.}$ | $-13{,}71\text{ p.p.}$ | $-7{,}94\text{ p.p.}$ |
| **Violação 1: Outliers (`Q3_Outliers`, $n=30$)** | $40\%$ | $14{,}13\%$ | $39{,}04\%$ | $+24{,}91\text{ p.p.}$ | $-26{,}39\text{ p.p.}$ | $-13{,}78\text{ p.p.}$ |
| **Violação 1: Outliers (`Q3_Outliers`, $n=30$)** | $50\%$ | **$22{,}62\%$** | **$62{,}30\%$** | **$+39{,}68\text{ p.p.}$** | **$-41{,}58\text{ p.p.}$ ($-64{,}8\%$)** | **$-16{,}78\text{ p.p.}$ ($-21{,}2\%$)** |
| **Violação 2: Amostra Pequena (`Q3_AmostraPequena`, $n=10$)** | $0\%$ *(H₀)* | $2{,}90\%$ | $4{,}33\%$ | $+1{,}43\text{ p.p.}$ | $-1{,}03\text{ p.p.}$ | $-0{,}25\text{ p.p.}$ |
| **Violação 2: Amostra Pequena (`Q3_AmostraPequena`, $n=10$)** | $10\%$ | $3{,}41\%$ | $5{,}13\%$ | $+1{,}72\text{ p.p.}$ | $-2{,}05\text{ p.p.}$ | $-1{,}75\text{ p.p.}$ |
| **Violação 2: Amostra Pequena (`Q3_AmostraPequena`, $n=10$)** | $20\%$ | $4{,}77\%$ | $7{,}35\%$ | $+2{,}58\text{ p.p.}$ | $-6{,}15\text{ p.p.}$ | $-6{,}95\text{ p.p.}$ |
| **Violação 2: Amostra Pequena (`Q3_AmostraPequena`, $n=10$)** | $30\%$ | $7{,}43\%$ | $11{,}42\%$ | $+3{,}99\text{ p.p.}$ | $-15{,}06\text{ p.p.}$ | $-18{,}17\text{ p.p.}$ |
| **Violação 2: Amostra Pequena (`Q3_AmostraPequena`, $n=10$)** | $40\%$ | $12{,}46\%$ | $19{,}16\%$ | $+6{,}70\text{ p.p.}$ | $-28{,}06\text{ p.p.}$ | $-33{,}66\text{ p.p.}$ |
| **Violação 2: Amostra Pequena (`Q3_AmostraPequena`, $n=10$)** | $50\%$ | **$21{,}32\%$** | **$32{,}20\%$** | **$+10{,}88\text{ p.p.}$** | **$-42{,}88\text{ p.p.}$ ($-66{,}8\%$)** | **$-46{,}88\text{ p.p.}$ ($-59{,}3\%$)** |

---

## 5. Diagnóstico Comparativo: Qual Teste Sofre Maior Alteração?

A tabela consolidada em [`lab04/data/resultados_q3_comparativo_impacto.csv`](../data/resultados_q3_comparativo_impacto.csv) sintetiza qual dos dois testes é mais penalizado pelas violações de pressupostos:

1. **No Erro Tipo I (Q1 vs. Q3):**
   - **O Teste t de Welch sofre a maior alteração em ambas as violações.**
   - Sob **outliers severos (`Q3_Outliers`)**, o Erro Tipo I de Welch cai mais $-0{,}65\text{ p.p.}$ (chegando a $3{,}28\%$, um desvio de $-1{,}72\text{ p.p.}$ abaixo dos $5\%$), enquanto Mann-Whitney varia apenas $-0{,}06\text{ p.p.}$ ($4{,}58\% \to 4{,}52\%$, praticamente inalterado!).
   - Sob **amostra pequena (`Q3_AmostraPequena`, $n=10$)**, o Erro Tipo I de Welch despenca para **$2{,}90\%$** (desvio de $-2{,}10\text{ p.p.}$ frente a $5\%$, uma perda de más de $42\%$ da taxa nominal), enquanto Mann-Whitney mantém $4{,}33\%$.

2. **No Poder Estatístico (Q2 vs. Q3):**
   - **Sob Outliers Severos (`Q3_Outliers`), o Teste t de Welch sofre um colapso dramático de poder:**
     - Em $\delta = 50\%$, o poder de Welch despenca de **$64{,}20\%$ para $22{,}62\%$** (queda de **$-41{,}58\text{ p.p.}$**, ou **$-64{,}8\%$** de perda relativa de poder!).
     - Já o Teste U de Mann-Whitney cai apenas de $79{,}08\%$ para **$62{,}30\%$** (perda relativa três vezes menor, de $-21{,}2\%$).
     - Como resultado, a vantagem de poder de Mann-Whitney sobre Welch em $\delta = 50\%$ salta de $+14{,}88\text{ p.p.}$ no cenário original para impressionantes **$+39{,}68\text{ p.p.}$** com outliers ($62{,}30\%$ vs. $22{,}62\%$ — quase **o triplo do poder**!).
   - **Sob Amostra Pequena (`Q3_AmostraPequena`, $n=10$):**
     - Reduzir a amostra de $n=30$ para $n=10$ diminui a informação disponível para ambos os testes, mas **o Teste t de Welch sofre a maior perda proporcional ($-66{,}8\%$ vs. $-59{,}3\%$ em $\delta = 50\%$)** e permanece substancialmente inferior ao Mann-Whitney em todos os níveis de efeito ($21{,}32\%$ contra $32{,}20\%$ em $\delta = 50\%$, vantagem de $+10{,}88\text{ p.p.}$ para Mann-Whitney).

---

## 6. Integração com os Gráficos G3 e G4

O módulo [`lab04/src/simulacao_q3.py`](../src/simulacao_q3.py) disponibiliza diretamente as funções adaptadoras:
- `obter_dados_q3_para_g3()` $\to$ alimenta o Gráfico G3 com as 3 condições sob $H_0$ (`Q1_Base`, `Q3_Outliers`, `Q3_AmostraPequena`).
- `obter_dados_q3_para_g4()` e o arquivo [`lab04/data/resultados_q3_curvas_g4.csv`](../data/resultados_q3_curvas_g4.csv) $\to$ fornecem as curvas completas de poder dos dois testes nas 3 condições para os 6 tamanhos de efeito ($0\%$ a $50\%$), prontos para o Gráfico G4.
