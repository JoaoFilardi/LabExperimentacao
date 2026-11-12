# [LAB04S02] Implementação e Interpretação do Gráfico G4
**Issue correspondente:** `#54`  
**Laboratório:** LAB04 — Testes de Hipótese por Dentro: Cenário, Simulação e Visualização  
**Disciplina:** Laboratório de Experimentação de Software — 6º Período  
**Professor:** Danilo Maia  
**Par Selecionado:** P1 (Teste t de Welch × Teste U de Mann-Whitney)  

---

## 1. Visão Geral e Objetivo do Gráfico G4

O objetivo do gráfico **G4** é comparar visualmente e quantitativamente as **curvas de poder estatístico** ($1 - \beta$, isto é, a proporção de rejeições de $H_0$ quando existe efeito real) do teste paramétrico (**t de Welch**) e do teste não-paramétrico (**U de Mann-Whitney**) em função do **tamanho do efeito** ($\delta \in \{0\%, 10\%, 20\%, 30\%, 40\%, 50\%\}$ de redução no tempo até o merge), integrando em uma mesma visualização:

1. **O Cenário Original realista (Questão Q2):** Distribuição log-normal calibrada nos dados reais minerados do repositório `tiangolo/fastapi` ($n = 30$ por grupo);
2. **As Situações de Violação de Pressupostos (Questão Q3):**
   - Contaminação severa por $10\%$ de outliers ($5\times + 50\text{ h}$, $n = 30$ por grupo);
   - Amostra pequena ($n = 10$ por grupo) sob a assimetria log-normal original;
3. **O Controle Teórico Gaussiano (Normal Simétrica sem Outliers, $n = 30$):** Incluído no painel direito para demonstrar empiricamente **quando e por que a vantagem de poder estatístico muda de lado** a favor do teste t de Welch.

---

## 2. Arquitetura Visual e Padrões Gráficos Adotados

O gráfico G4 foi implementado no módulo [`lab04/src/grafico_g4.py`](../src/grafico_g4.py) e exportado em alta resolução ($200\text{ DPI}$) para [`lab04/data/g4_curvas_poder.png`](../data/g4_curvas_poder.png), composto por dois painéis complementares ($1 \times 2$):

- **Painel Esquerdo — Curvas de Poder Estatístico (Q2 vs. Q3):**
  - Eixo $X$: *"Tamanho do efeito: redução no tempo até o merge (%)"* ($\delta$ de $0\%$ a $50\%$);
  - Eixo $Y$: *"Proporção de rejeições de H₀ / Poder (%)"*;
  - **Paleta de cores padronizada com G2 e G3:**
    - **Azul (`#1f77b4`)** para o teste paramétrico (**t de Welch**);
    - **Laranja (`#ff7f0e`)** para o teste não-paramétrico (**U de Mann-Whitney**);
  - **Estilos de linha e marcadores por condição experimental:**
    - Linha contínua (`-`) e círculo (`o`) com bandas de confiança de Wilson a $95\%$ para o **Cenário Original (Q2: $n = 30$)**;
    - Linha tracejada (`--`) e quadrado (`s`) para **Violação: Outliers 10% (Q3: $n = 30$)**;
    - Linha pontilhada (`:`) e triângulo (`^`) para **Violação: Amostra Pequena (Q3: $n = 10$)**;
  - **Linhas de referência horizontais:**
    - Vermelha traço-ponto (`-.`) em $y = 5{,}0\%$ ($\alpha = 0{,}05$, valor esperado em efeito zero);
    - Verde tracejada (`--`) em $y = 80{,}0\%$ (meta clássica de poder estatístico $1 - \beta = 0{,}80$).
- **Painel Direito — Diferença de Poder ($\text{Poder}_{\text{Mann-Whitney}} - \text{Poder}_{\text{Welch}}$) e Quando Muda de Lado:**
  - Eixo $Y$: Diferença de poder em pontos percentuais ($\text{p.p.}$);
  - **Faixa superior sombreada em laranja ($\Delta > 0$):** Zona em que o teste U de Mann-Whitney tem maior poder estatístico (todas as condições log-normais de Q2 e Q3);
  - **Faixa inferior sombreada em azul ($\Delta < 0$):** Zona em que o teste t de Welch passa a ter maior poder estatístico (**Controle Teórico Normal Simétrico sem Outliers**).

---

## 3. Tabelas de Resultados Consolidados do Gráfico G4

### 3.1 Curvas de Poder no Cenário Original (Q2) e sob Violações de Pressupostos (Q3)

| Condição Experimental | Efeito ($\delta$) | Poder t de Welch (%) | IC 95% Welch | Poder Mann-Whitney (%) | IC 95% Mann-Whitney | Vantagem MW ($\Delta\text{ p.p.}$) | Perda Welch vs. Base | Perda MW vs. Base |
|---|---|---|---|---|---|---|---|---|
| **Cenário Original (Q2, $n=30$)** | $0\%$ ($H_0$) | $3{,}93\%$ | $[3{,}57\%; 4{,}33\%]$ | **$4{,}58\%$** | $[4{,}19\%; 5{,}01\%]$ | $+0{,}65\text{ p.p.}$ | — | — |
| **Cenário Original (Q2, $n=30$)** | $10\%$ | $5{,}46\%$ | $[5{,}03\%; 5{,}92\%]$ | **$6{,}88\%$** | $[6{,}40\%; 7{,}39\%]$ | $+1{,}42\text{ p.p.}$ | — | — |
| **Cenário Original (Q2, $n=30$)** | $20\%$ | $10{,}92\%$ | $[10{,}32\%; 11{,}55\%]$ | **$14{,}30\%$** | $[13{,}63\%; 15{,}00\%]$ | $+3{,}38\text{ p.p.}$ | — | — |
| **Cenário Original (Q2, $n=30$)** | $30\%$ | $22{,}49\%$ | $[21{,}68\%; 23{,}32\%]$ | **$29{,}59\%$** | $[28{,}70\%; 30{,}49\%]$ | $+7{,}10\text{ p.p.}$ | — | — |
| **Cenário Original (Q2, $n=30$)** | $40\%$ | $40{,}52\%$ | $[39{,}56\%; 41{,}49\%]$ | **$52{,}82\%$** | $[51{,}84\%; 53{,}80\%]$ | $+12{,}30\text{ p.p.}$ | — | — |
| **Cenário Original (Q2, $n=30$)** | $50\%$ | $64{,}20\%$ | $[63{,}26\%; 65{,}13\%]$ | **$79{,}08\%$** | $[78{,}27\%; 79{,}87\%]$ | **$+14{,}88\text{ p.p.}$** | — | — |
| **Violação: Outliers 10% (Q3, $n=30$)** | $0\%$ ($H_0$) | $3{,}28\%$ | $[2{,}95\%; 3{,}65\%]$ | **$4{,}52\%$** | $[4{,}13\%; 4{,}94\%]$ | $+1{,}24\text{ p.p.}$ | $-0{,}65\text{ p.p.}$ | $-0{,}06\text{ p.p.}$ |
| **Violação: Outliers 10% (Q3, $n=30$)** | $10\%$ | $3{,}69\%$ | $[3{,}34\%; 4{,}08\%]$ | **$6{,}09\%$** | $[5{,}64\%; 6{,}58\%]$ | $+2{,}40\text{ p.p.}$ | $-1{,}77\text{ p.p.}$ | $-0{,}79\text{ p.p.}$ |
| **Violação: Outliers 10% (Q3, $n=30$)** | $20\%$ | $5{,}32\%$ | $[4{,}90\%; 5{,}78\%]$ | **$11{,}07\%$** | $[10{,}47\%; 11{,}70\%]$ | $+5{,}75\text{ p.p.}$ | $-5{,}60\text{ p.p.}$ | $-3{,}23\text{ p.p.}$ |
| **Violação: Outliers 10% (Q3, $n=30$)** | $30\%$ | $8{,}78\%$ | $[8{,}24\%; 9{,}35\%]$ | **$21{,}65\%$** | $[20{,}85\%; 22{,}47\%]$ | $+12{,}87\text{ p.p.}$ | $-13{,}71\text{ p.p.}$ | $-7{,}94\text{ p.p.}$ |
| **Violação: Outliers 10% (Q3, $n=30$)** | $40\%$ | $14{,}13\%$ | $[13{,}46\%; 14{,}83\%]$ | **$39{,}04\%$** | $[38{,}09\%; 40{,}00\%]$ | $+24{,}91\text{ p.p.}$ | $-26{,}39\text{ p.p.}$ | $-13{,}78\text{ p.p.}$ |
| **Violação: Outliers 10% (Q3, $n=30$)** | $50\%$ | $22{,}62\%$ | $[21{,}81\%; 23{,}45\%]$ | **$62{,}30\%$** | $[61{,}35\%; 63{,}24\%]$ | **$+39{,}68\text{ p.p.}$** | **$-41{,}58\text{ p.p.}$** | $-16{,}78\text{ p.p.}$ |
| **Violação: Amostra Pequena (Q3, $n=10$)** | $0\%$ ($H_0$) | $2{,}90\%$ | $[2{,}59\%; 3{,}25\%]$ | **$4{,}33\%$** | $[3{,}95\%; 4{,}75\%]$ | $+1{,}43\text{ p.p.}$ | $-1{,}03\text{ p.p.}$ | $-0{,}25\text{ p.p.}$ |
| **Violação: Amostra Pequena (Q3, $n=10$)** | $10\%$ | $3{,}41\%$ | $[3{,}07\%; 3{,}78\%]$ | **$5{,}13\%$** | $[4{,}71\%; 5{,}58\%]$ | $+1{,}72\text{ p.p.}$ | $-2{,}05\text{ p.p.}$ | $-1{,}75\text{ p.p.}$ |
| **Violação: Amostra Pequena (Q3, $n=10$)** | $20\%$ | $4{,}77\%$ | $[4{,}37\%; 5{,}21\%]$ | **$7{,}35\%$** | $[6{,}85\%; 7{,}88\%]$ | $+2{,}58\text{ p.p.}$ | $-6{,}15\text{ p.p.}$ | $-6{,}95\text{ p.p.}$ |
| **Violação: Amostra Pequena (Q3, $n=10$)** | $30\%$ | $7{,}43\%$ | $[6{,}93\%; 7{,}96\%]$ | **$11{,}42\%$** | $[10{,}81\%; 12{,}06\%]$ | $+3{,}99\text{ p.p.}$ | $-15{,}06\text{ p.p.}$ | $-18{,}17\text{ p.p.}$ |
| **Violação: Amostra Pequena (Q3, $n=10$)** | $40\%$ | $12{,}46\%$ | $[11{,}83\%; 13{,}12\%]$ | **$19{,}16\%$** | $[18{,}40\%; 19{,}94\%]$ | $+6{,}70\text{ p.p.}$ | $-28{,}06\text{ p.p.}$ | $-33{,}66\text{ p.p.}$ |
| **Violação: Amostra Pequena (Q3, $n=10$)** | $50\%$ | $21{,}32\%$ | $[20{,}53\%; 22{,}13\%]$ | **$32{,}20\%$** | $[31{,}29\%; 33{,}12\%]$ | **$+10{,}88\text{ p.p.}$** | **$-42{,}88\text{ p.p.}$** | $-46{,}88\text{ p.p.}$ |

> **Nota adicional sobre o efeito intermediário $\delta = 5\%$ (`poder_estatistico_q2.csv` da Issue `#53`):**  
> Na grade complementar com passo inicial de $5\%$ ($\delta \in \{0\%, 5\%, 10\%, 20\%, 30\%, 40\%\}$), em $\delta = 5\%$ o teste U de Mann-Whitney também supera o teste t de Welch ($5{,}17\%$ com $p\text{-valor médio} = 0{,}4968$ vs. $4{,}42\%$ com $p\text{-valor médio} = 0{,}4866$).

### 3.2 Controle Teórico Gaussiano: Quando a Vantagem Muda de Lado ($n = 30$)

| Condição Experimental | Efeito ($\delta$) | Poder t de Welch (%) | Poder Mann-Whitney (%) | Diferença ($\text{MW} - \text{Welch}$) | Teste Mais Poderoso |
|---|---|---|---|---|---|
| **Normal Simétrica sem Outliers ($n=30$)** | $0\%$ ($H_0$) | **$4{,}89\%$** | $4{,}58\%$ | $-0{,}31\text{ p.p.}$ | Calibrados em $\alpha = 5\%$ |
| **Normal Simétrica sem Outliers ($n=30$)** | $10\%$ | **$12{,}69\%$** | $11{,}83\%$ | **$-0{,}86\text{ p.p.}$** | **t de Welch** |
| **Normal Simétrica sem Outliers ($n=30$)** | $20\%$ | **$35{,}84\%$** | $33{,}86\%$ | **$-1{,}98\text{ p.p.}$** | **t de Welch** |
| **Normal Simétrica sem Outliers ($n=30$)** | $30\%$ | **$65{,}73\%$** | $63{,}03\%$ | **$-2{,}70\text{ p.p.}$** | **t de Welch** |
| **Normal Simétrica sem Outliers ($n=30$)** | $40\%$ | **$89{,}26\%$** | $87{,}32\%$ | **$-1{,}94\text{ p.p.}$** | **t de Welch** |
| **Normal Simétrica sem Outliers ($n=30$)** | $50\%$ | **$98{,}01\%$** | $97{,}36\%$ | **$-0{,}65\text{ p.p.}$** | **t de Welch** |

---

## 4. Texto Interpretativo Oficial do Dashboard (Seção 5 — Poder)

Conforme exigido pelo enunciado (2 a 4 frases que dizem qual teste tem mais poder e quando a vantagem muda de lado):

> *"O gráfico G4 mostra que o poder estatístico cresce com o tamanho do efeito e que o teste U de Mann-Whitney (laranja) supera o teste t de Welch (azul) em todas as situações log-normais simuladas, ampliando sua vantagem à medida que o efeito aumenta (em δ = 50%, atinge 79,08% contra 64,20% no cenário original, uma vantagem de +14,88 p.p.).  
> Sob violação de pressupostos por outliers severos (Q3), o poder de Welch sofre um colapso drástico (caindo para 22,62% em δ = 50%), enquanto Mann-Whitney mantém 62,30% (+39,68 p.p. de vantagem), e com amostra pequena (n = 10) Mann-Whitney também lidera (32,20% vs. 21,32%).  
> Como demonstra o painel direito, a vantagem só muda de lado em favor do teste t de Welch quando os dados seguem uma distribuição Normal simétrica sem outliers (onde Welch atinge 65,73% contra 63,03% de Mann-Whitney em δ = 30%, devido à eficiência assintótica relativa de 95,5% dos postos sob normalidade)."*

---

## 5. Análise Estatística Aprofundada

### 5.1 Por que Mann-Whitney tem mais poder nas distribuições log-normais (Q2 e Q3)?
1. **Sensibilidade da variância amostral à cauda direita:** Na distribuição log-normal dos tempos de merge ($\sigma_{\log} = 0{,}9254$), observações na cauda superior elevam $s^2$ quadraticamente. Como o erro padrão $\sqrt{s_1^2/n_1 + s_2^2/n_2}$ está no denominador de $t$, a razão sinal-ruído do teste t de Welch é penalizada mesmo quando existe redução real de $30\%$ a $50\%$ no grupo `com_bot`.
2. **Colapso sob contaminação por outliers ($Q3_{\text{Outliers}}$):** Quando $10\%$ dos PRs sofrem atrasos extremos ($5\times + 50\text{ h}$), o poder de Welch em $\delta = 50\%$ desaba de $64{,}20\%$ para **$22{,}62\%$** (perda de $-41{,}58\text{ p.p.}$). Notavelmente, a curva de Mann-Whitney **com** $10\%$ de outliers severos ($62{,}30\%$ em $\delta = 50\%$) praticamente empata com a curva do teste t de Welch **sem** outliers ($64{,}20\%$), porque os outliers recebem apenas os postos máximos ($55$ a $60$) sem inflar uma variância paramétrica.

### 5.2 Quando e por que a vantagem muda de lado?
- **Condição de inversão:** A vantagem muda de lado a favor do **teste t de Welch** quando os dados provêm de uma **distribuição Normal simétrica sem caudas pesadas nem outliers** (curva azul traço-ponto com losangos no painel direito do G4, situada inteiramente na região $\Delta < 0$).
- **Fundamentação teórica (Eficiência Assintótica Relativa de Pitman):** Sob normalidade estrita, a média amostral $\bar{X}$ é o estimador suficiente de variância uniformemente mínima (UMVUE) para o parâmetro de locação. Ao substituir as magnitudes exatas pelos postos ordenados ($1, \dots, N$), o teste U de Mann-Whitney descarta uma pequena fração da informação métrica, resultando em uma Eficiência Assintótica Relativa de Pitman de:
  $$\text{ARE}(\text{Mann-Whitney}, t \mid \mathcal{N}) = \frac{3}{\pi} \approx 0{,}9549 \ (95{,}5\%)$$
  Por isso, no controle gaussiano em $\delta = 30\%$, Welch alcança **$65{,}73\%$** de poder contra **$63{,}03\%$** de Mann-Whitney ($\Delta = -2{,}70\text{ p.p.}$). Já em distribuições log-normais ou contaminadas por outliers, a $\text{ARE}$ de Mann-Whitney supera amplamente $100\%$, podendo ultrapassar $300\%$.

---

## 6. Respostas às Perguntas da Apresentação Oral Relacionadas ao G4

- **Pergunta 10:** *"Olhando para o G4, qual teste tem mais poder no cenário original? Isso muda na Q3? Por quê?"*  
  **Resposta:** No cenário original (Q2), o teste U de Mann-Whitney tem mais poder em todos os tamanhos de efeito (chegando a $79{,}08\%$ contra $64{,}20\%$ de Welch em $\delta = 50\%$, vantagem de $+14{,}88\text{ p.p.}$). Na Q3, Mann-Whitney continua sendo o mais poderoso e sua vantagem **aumenta drasticamente** sob outliers severos, atingindo $+39{,}68\text{ p.p.}$ ($62{,}30\%$ vs. $22{,}62\%$), porque os outliers inflam quadraticamente o erro padrão de Welch, enquanto os postos de Mann-Whitney limitam a influência de qualquer valor extremo ao posto máximo. A vantagem só muda de lado a favor de Welch sob distribuição Normal simétrica sem outliers ($\text{ARE} = 3/\pi \approx 95{,}5\%$).
- **Pergunta 11:** *"Que violação de pressuposto vocês simularam, e por que ela afeta mais um teste do que o outro?"*  
  **Resposta:** Simulamos (1) injeção de $10\%$ de outliers severos ($5\times + 50\text{ h}$, $n = 30$) e (2) redução do tamanho amostral para $n = 10$ sob assimetria log-normal. Elas afetam muito mais o teste t de Welch (cujo poder em $\delta = 50\%$ cai $-41{,}58\text{ p.p.}$ com outliers) porque o teste t depende diretamente das médias e variâncias amostrais e da convergência via Teorema Central do Limite, ao passo que Mann-Whitney opera sobre a ordenação relativa (postos).
- **Pergunta 12:** *"Se vocês usassem $\alpha = 0{,}01$ em vez de $0{,}05$, o que mudaria no G3 e no G4?"*  
  **Resposta:** No G3, a linha horizontal nominal desceria de $5\%$ para $1\%$ e as taxas empíricas cairiam para perto de $1\%$. No G4, o limiar crítico para rejeitar $H_0$ ($p < 0{,}01$) ficaria mais rigoroso, deslocando todas as curvas de poder **para baixo e para a direita** (menor poder estatístico para um mesmo tamanho de efeito $\delta$, exigindo efeitos maiores ou amostras maiores para atingir $80\%$ de poder).
- **Pergunta 13:** *"Se o efeito verdadeiro é de 5%, mas a amostra tem $n = 15$, vocês esperam que os testes o detectem? Onde isso aparece nos gráficos?"*  
  **Resposta:** Não esperamos que nenhum dos testes o detecte com confiabilidade. Isso aparece claramente no canto inferior esquerdo do G4: mesmo com $n = 30$, para efeitos entre $5\%$ e $10\%$ o poder fica entre $4{,}4\%$ e $7{,}1\%$ (praticamente indistinguível do ruído de $\alpha = 5\%$), e na curva pontilhada de amostra reduzida ($n = 10$) em $\delta = 10\%$ o poder é de apenas $3{,}41\%$ (Welch) e $5{,}13\%$ (Mann-Whitney). Com $n = 15$ e efeito de $5\%$, o experimento sofre de severo subdimensionamento amostral (*underpowered*), resultando em mais de $94\%$ de chance de Erro Tipo II ($\beta$).
- **Pergunta 15:** *"Qual teste vocês recomendam para o cenário do grupo, e em que situação a recomendação mudaria?"*  
  **Resposta:** Recomendamos o **Teste U de Mann-Whitney** para avaliar tempos de merge de Pull Requests e métricas de engenharia de software com assimetria positiva e outliers recorrentes, pois ele controla o Erro Tipo I próximo a $5\%$ ($4{,}58\%$) e oferece até $+39{,}68\text{ p.p.}$ mais poder sob outliers, além de ter detectado significância nos dados reais do `tiangolo/fastapi` ($p = 0{,}0446$ contra $p = 0{,}0969$ de Welch). A recomendação mudaria para o **Teste t de Welch** se os dados tivessem distribuição aproximadamente simétrica/Normal e livre de outliers severos (ou se a hipótese de negócio exigisse estritamente inferência sobre o custo total/médio em amostras grandes o suficiente para o TCL).
