# [LAB04S02] Implementação e Interpretação do Gráfico G3
**Issue correspondente:** `#52`  
**Laboratório:** LAB04 — Testes de Hipótese por Dentro: Cenário, Simulação e Visualização  
**Disciplina:** Laboratório de Experimentação de Software — 6º Período  
**Professor:** Danilo Maia  
**Par Selecionado:** P1 (Teste t de Welch × Teste U de Mann-Whitney)  

---

## 1. Visão Geral e Objetivo do Gráfico G3

O objetivo do gráfico **G3** é comparar visualmente e quantitativamente a **taxa empírica de Erro Tipo I** ($\alpha$) do teste paramétrico (**t de Welch**) e do teste não-paramétrico (**U de Mann-Whitney**) sob a hipótese nula verdadeira ($H_0$), contrastando o comportamento de ambos no **cenário original realista (Questão Q1)** com situações de **violação severa de pressupostos (Questão Q3)**.

Como preconizado pelo enunciado do laboratório, quando $H_0$ é verdadeira não deve existir efeito real. O valor teórico esperado para a taxa de rejeição indevida é exatamente o nível de significância adotado:
$$\alpha = 0{,}05 \implies 5{,}0\%$$

---

## 2. Condições Experimentais Simuladas sob $H_0$

Foram executadas **10.000 simulações de Monte Carlo independentes** para cada uma das três condições experimentais sob a hipótese nula verdadeira ($H_0$), totalizando **60.000 amostras simuladas** e **60.000 execuções de testes estatísticos**:

1. **Cenário Original (Q1 — Log-normal realista, $n = 30$):**  
   Ambos os grupos (`sem_bot` e `com_bot`) provêm rigorosamente da distribuição lognormal ajustada aos dados reais minerados do repositório `tiangolo/fastapi` ($\mu_{\log} = 2{,}8053$, $\sigma_{\log} = 0{,}9254$, $n=30$). Representa a condição baseline típica de engenharia de software, com assimetria positiva natural.
2. **Violação de Pressupostos (Q3 — Injeção de Outliers Extremos, $n = 30$):**  
   Simula o efeito de falhas atípicas de infraestrutura de CI, disputas demoradas de requisitos ou bloqueios de dependências externas. Sorteia aleatoriamente $10\%$ das observações de cada dataset gerado sob $H_0$ e aplica contaminação severa multiplicando o tempo por $5\times + 50\text{ h}$.
3. **Violação de Pressupostos (Q3 — Amostra Pequena, $n = 10$):**  
   Reduz o tamanho amostral para apenas $n = 10$ Pull Requests por grupo sob a distribuição assimétrica original. Investiga a situação em que o Teorema Central do Limite (TCL) não atinge volume amostral suficiente para garantir a aproximação normal da distribuição amostral da média.

---

## 3. Elementos Gráficos e Padrões Visuais Adotados

O gráfico foi implementado no módulo [`lab04/src/grafico_g3.py`](../src/grafico_g3.py) e exportado em alta resolução para [`lab04/data/g3_erro_tipo_1.png`](../data/g3_erro_tipo_1.png):

- **Paleta de cores padronizada em todo o projeto:**  
  - Azul (`#1f77b4`) para o teste paramétrico (**t de Welch**);
  - Laranja (`#ff7f0e`) para o teste não-paramétrico (**U de Mann-Whitney**);
  - Vermelho (`#d62728`) para a linha de referência nominal de $5{,}0\%$.
- **Linha de referência nominal e margem de calibração:**  
  - Linha tracejada horizontal em $y = 5{,}0\%$ ($\alpha = 0{,}05$);
  - Faixa sombreada vermelha clara delimitando o intervalo de calibração estrita de Bradley (1978): $[4{,}5\%; 5{,}5\%]$.
- **Barras de erro estatísticas:**  
  - Intervalos de confiança de Wilson a $95\%$ calculados para cada proporção empírica.
- **Rótulos numéricos explícitos:**  
  - Valores percentuais exatos anotados sobre o topo de cada barra com precisão de duas casas decimais.
- **Identificação clara de eixos e legenda:**  
  - Eixo $Y$: *"Taxa Empírica de Erro Tipo I (%)"*;  
  - Eixo $X$: *"Cenário e Condição Experimental sob H₀"*;  
  - Título formal e subtítulo explicativo com indicação da semente fixa (`semente = 42`).

---

## 4. Tabela de Resultados Consolidados do Gráfico G3

| Cenário / Condição Experimental | Teste Estatístico | Abordagem | Rejeições ($k / 10.000$) | Taxa Empírica ($\hat{\alpha}$) | Nível Nominal ($\alpha$) | Desvio frente a $\alpha$ | IC 95% (Wilson) | Comportamento Classificado |
|---|---|---|---|---|---|---|---|---|
| **Cenário Original (Q1)**<br>Log-normal realista ($n=30$) | **t de Welch** | Paramétrico | $393$ | **$3{,}93\%$** | $5{,}0\%$ | **$-1{,}07\%$** | $[3{,}57\%; 4{,}33\%]$ | **Conservador** |
| **Cenário Original (Q1)**<br>Log-normal realista ($n=30$) | **Mann-Whitney** | Não-paramétrico | $458$ | **$4{,}58\%$** | $5{,}0\%$ | **$-0{,}42\%$** | $[4{,}19\%; 5{,}01\%]$ | **Nominal / Calibrado** |
| **Violação Outliers (Q3)**<br>10% contaminação severa ($n=30$) | **t de Welch** | Paramétrico | $328$ | **$3{,}28\%$** | $5{,}0\%$ | **$-1{,}72\%$** | $[2{,}95\%; 3{,}65\%]$ | **Conservador** |
| **Violação Outliers (Q3)**<br>10% contaminação severa ($n=30$) | **Mann-Whitney** | Não-paramétrico | $452$ | **$4{,}52\%$** | $5{,}0\%$ | **$-0{,}48\%$** | $[4{,}13\%; 4{,}94\%]$ | **Conservador leve** |
| **Violação Amostra Pequena (Q3)**<br>Log-normal reduzida ($n=10$) | **t de Welch** | Paramétrico | $290$ | **$2{,}90\%$** | $5{,}0\%$ | **$-2{,}10\%$** | $[2{,}59\%; 3{,}25\%]$ | **Conservador** |
| **Violação Amostra Pequena (Q3)**<br>Log-normal reduzida ($n=10$) | **Mann-Whitney** | Não-paramétrico | $433$ | **$4{,}33\%$** | $5{,}0\%$ | **$-0{,}67\%$** | $[3{,}95\%; 4{,}75\%]$ | **Conservador leve** |

---

## 5. Texto Interpretativo Oficial do Dashboard (Seção 4)

Conforme exigido pelo enunciado (2 a 4 frases concisas que dizem o que o gráfico mostra, se as taxas se aproximam de 5% e onde ocorreram os maiores desvios):

> *"O gráfico G3 compara a taxa empírica de Erro Tipo I dos dois testes em 10.000 simulações sob H₀ frente ao nível nominal de 5% (linha tracejada vermelha).  
> O teste U de Mann-Whitney manteve-se rigorosamente próximo aos 5% em todas as condições analisadas (4,58% na base, 4,52% com outliers e 4,33% com amostra pequena), confirmando robustez estrita por operar sobre postos ordenados.  
> Já o teste t de Welch apresentou comportamento conservador em todos os cenários, rejeitando H₀ consideravelmente menos do que o esperado (3,93% na base, 3,28% com outliers e 2,90% com amostra pequena).  
> Os maiores desvios ocorreram nas situações de violação de pressupostos (outliers severos e amostra pequena), nas quais a cauda longa e a variabilidade extrema inflam o erro padrão e distorcem a aproximação paramétrica do teste t."*

---

## 6. Análise Estatística Aprofundada e Comparação dos Desvios

### 6.1 Desvios Observados no Teste t de Welch
1. **No Cenário Base ($3{,}93\%$):** A assimetria natural de tempos de merge já induz conservadorismo, pois amostras que contêm observações de cauda moderadamente distantes geram variâncias infladas que diminuem $|t|$.
2. **Sob Outliers Severos ($3{,}28\%$):** A contaminação artificial com valores multiplicados por $5\times + 50\text{ h}$ gera desvios padrões intra-amostrais gigantescos em amostras contaminadas. Como esses outliers entram ao quadrado no denominador da estatística $t$, o efeito é atenuar radicalmente a estatística observada, reduzindo ainda mais a proporção de falsos positivos para $3{,}28\%$.
3. **Sob Amostra Pequena ($2{,}90\%$):** Constitui o **maior desvio absoluto observado no experimento** ($-2{,}10$ pontos percentuais abaixo do nominal de $5{,}0\%$). Com apenas $n = 10$ PRs, o Teorema Central do Limite falha completamente em normalizar a média amostral de distribuições acentuadamente assimétricas. A aproximação $t$ de Welch colapsa para uma taxa de rejeição de menos de $3\%$.

### 6.2 Resiliência do Teste U de Mann-Whitney
1. **Imunidade a Outliers ($4{,}52\%$ vs. $4{,}58\%$):** Ao transformar os tempos em postos ($1$ a $60$), um outlier severo de $350\text{ h}$ recebe o mesmo posto máximo ($60$) que receberia uma observação de $90\text{ h}$. Consequentemente, a taxa de Erro Tipo I permanece praticamente idêntica à do cenário original ($4{,}52\%$ vs. $4{,}58\%$).
2. **Amostras Pequenas ($4{,}33\%$):** Mesmo com $n = 10$, onde a distribuição assintótica normal de $U$ sofre com a discretização de postos, Mann-Whitney ainda manteve taxa satisfatória de $4{,}33\%$, amplamente superior à taxa de $2{,}90\%$ de Welch.

---

## 7. Respostas às Perguntas da Apresentação Oral Relacionadas ao G3

- **Pergunta 9:** *"No G3, algum teste se afastou de 5%? Ele ficou liberal ou conservador, e por quê?"*  
  **Resposta:** Sim: o teste t de Welch afastou-se sistematicamente de 5%, ficando conservador em todos os cenários (3,93% na base, 3,28% com outliers e 2,90% com amostra pequena). Esse conservadorismo decorre da inflação da variância amostral causada por caudas pesadas e outliers no denominador da estatística t. Já Mann-Whitney permaneceu estável e próximo a 5%, operando sobre postos ordenados. Nenhum dos testes foi liberal.
- **Pergunta 11:** *"Que violação de pressuposto vocês simularam, e por que ela afeta mais um teste do que o outro?"*  
  **Resposta:** Simulamos contaminação por outliers severos (10% de dados multiplicados por 5x + 50h) e redução do tamanho amostral para n = 10 sob assimetria lognormal. Essas violações afetam drasticamente o teste t de Welch, pois destroem a normalidade das médias e inflam o erro padrão, enquanto o teste de Mann-Whitney é invariante a transformações monotônicas de escala dos outliers e mantém robustez por postos.
- **Pergunta 12:** *"Se vocês usassem α = 0,01 em vez de 0,05, o que mudaria no G3 e no G4?"*  
  **Resposta:** No G3, a linha horizontal se deslocaria para 1%, e ambas as barras empíricas diminuiriam proporcionalmente para taxas próximas a 1%. O teste t continuaria mais conservador que o nominal, e no G4 a curva de poder se deslocaria para a direita (menor poder para o mesmo tamanho de efeito), exigindo amostras maiores para detecção.
