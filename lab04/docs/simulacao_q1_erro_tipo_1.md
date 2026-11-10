# [LAB04S02] Simulação e Análise da Taxa de Erro Tipo I (Questão Q1)
**Issue correspondente:** `#51`  
**Laboratório:** LAB04 — Testes de Hipótese por Dentro: Cenário, Simulação e Visualização  
**Disciplina:** Laboratório de Experimentação de Software — 6º Período  
**Professor:** Danilo Maia  
**Par Selecionado:** P1 (Teste t de Welch × Teste U de Mann-Whitney)  

---

## 1. Objetivo da Questão Q1

O objetivo desta etapa é avaliar empiricamente como os dois testes estatísticos investigados (**t de Welch** e **U de Mann-Whitney**) se comportam quando a **hipótese nula ($H_0$) é estritamente verdadeira**, isto é, quando **não existe qualquer efeito** decorrente do uso de bots de revisão automatizada sobre o tempo até o merge (*lead time to merge*) de Pull Requests.

Em termos formais de inferência estatística, o **Erro Tipo I** ($\alpha$) ocorre quando o teste rejeita a hipótese nula $H_0$ dado que ela é verdadeira (falso positivo):
$$\alpha = P(\text{Rejeitar } H_0 \mid H_0 \text{ é verdadeira})$$

### Significado Prático em Engenharia de Software:
- **O que representa um falso positivo neste cenário:** Concluir falsamente que a adoção de bots de revisão automatizada acelera (ou retarda) significativamente o fluxo de entrega de código, quando na realidade os tempos de merge de ambos os grupos são governados rigorosamente pelo mesmo processo aleatório.
- **Impacto para a organização:** Decisões gerenciais errôneas, investimento financeiro e esforço de engenharia na contratação, configuração e manutenção de ferramentas de automação que não entregam o ganho de produtividade prometido.

---

## 2. Configuração do Cenário sob $H_0$ Verdadeira

Para garantir que $H_0$ seja rigorosamente verdadeira em todas as iterações simuladas, os dois grupos comparados (`sem_bot` e `com_bot`) foram amostrados a partir de **uma única distribuição teórica comum**, cujos parâmetros foram calibrados a partir do agrupamento total (*pooled*) dos 60 Pull Requests minerados empiricamente do repositório `tiangolo/fastapi`:

| Parâmetro de Simulação | Valor Adotado | Justificativa Teórica e Empírica |
|---|---|---|
| **Distribuição Pai** | **Log-normal** ($\text{Lognormal}(\mu_{\log}, \sigma_{\log})$) | Captura a assimetria positiva acentuada e a cauda pesada observadas em tempos de ciclo de software. |
| **$\mu_{\log, H_0}$** | $2{,}8053$ | Estimador de máxima verossimilhança da média logarítmica da amostra real combinada. |
| **$\sigma_{\log, H_0}$** | $0{,}9254$ | Estimador da dispersão na escala logarítmica da amostra real combinada. |
| **Mediana Teórica sob $H_0$** | $\exp(2{,}8053) \approx 16{,}53\text{ horas}$ | Ambas as populações compartilham a mesma mediana teórica exata. |
| **Média Teórica sob $H_0$** | $\exp\left(2{,}8053 + \frac{0{,}9254^2}{2}\right) \approx 25{,}37\text{ horas}$ | Ambas as populações compartilham a mesma média teórica exata. |
| **Tamanho Amostral por Grupo** | $n_{\text{sem}} = 30$, $n_{\text{com}} = 30$ | Tamanho padrão estabelecido no planejamento experimental (amostras moderadas). |
| **Número de Simulações ($N$)** | **$10.000$ repetições independentes** | Proporciona erro padrão da proporção estimado em $\text{SE} \approx 0{,}22\%$, garantindo margem de erro $\le \pm 0{,}43\%$. |
| **Nível Nominal de Significância** | $\alpha = 0{,}05$ ($5{,}0\%$) | Nível convencional adotado na literatura de experimentação de software. |
| **Direção do Teste** | **Bicaudal** (`two-sided`) | Detecta tanto aceleração quanto lentidão no merge de PRs. |
| **Semente Pseudoaleatória** | `semente = 42` | Garantia estrita de reprodutibilidade bit a bit via `numpy.random.default_rng(42)`. |

---

## 3. Metodologia de Execução de Monte Carlo

1. **Geração dos Datasets Sintéticos:**
   Em cada uma das $10.000$ iterações, foram geradas $30$ observações independentes para o grupo `sem_bot` e $30$ observações para o grupo `com_bot` sob os parâmetros de $H_0$. O processo foi implementado tanto em rotina matricial de alto desempenho quanto em iteração sequencial no módulo [`lab04/src/simulacao_q1.py`](../src/simulacao_q1.py), preservando perfeita equivalência matemática.

2. **Aplicação Simultânea dos Testes:**
   Em cada dataset gerado, foram executados os dois testes do Par P1:
   - **Teste paramétrico:** Teste t de Welch (`scipy.stats.ttest_ind(..., equal_var=False, alternative='two-sided')`).
   - **Teste não-paramétrico:** Teste U de Mann-Whitney (`scipy.stats.mannwhitneyu(..., alternative='two-sided', method='asymptotic')`).

3. **Registro dos Resultados Individuais:**
   Para cada simulação, foram registrados: a estatística $t$, o $p$-valor de Welch, a indicação booleana de rejeição ($p < 0{,}05$), a estatística $U$, o $p$-valor de Mann-Whitney e sua indicação booleana de rejeição. Todos os $10.000$ registros foram persistidos no arquivo [`lab04/data/simulacao_q1_pvalores.csv`](../data/simulacao_q1_pvalores.csv).

4. **Cálculo da Taxa Empírica de Erro Tipo I:**
   A taxa empírica ($\hat{\alpha}$) foi calculada como a proporção de repetições em que $H_0$ foi incorretamente rejeitada:
   $$\hat{\alpha} = \frac{\sum_{i=1}^{N} \mathbb{I}(p_i < \alpha)}{N} = \frac{\text{Número de Rejeições}}{10.000}$$

5. **Intervalo de Confiança da Proporção (Wilson Score):**
   Para quantificar a precisão da estimativa de Monte Carlo a $95\%$ de confiança, utilizou-se o intervalo de escore de Wilson:
   $$\text{IC}_{95\%} = \frac{\hat{\alpha} + \frac{z^2}{2N} \pm z \sqrt{\frac{\hat{\alpha}(1 - \hat{\alpha})}{N} + \frac{z^2}{4N^2}}}{1 + \frac{z^2}{N}}, \quad \text{com } z = 1{,}95996$$

---

## 4. Resultados Obtidos nas 10.000 Simulações

Os resultados consolidados da simulação de Monte Carlo sob $H_0$ verdadeira encontram-se sumarizados na tabela abaixo (persistida em [`lab04/data/resultados_q1_erro_tipo_1.csv`](../data/resultados_q1_erro_tipo_1.csv)):

### Tabela 1: Taxa Empírica de Erro Tipo I em 10.000 Simulações sob $H_0$ ($\alpha = 0{,}05$)

| Métrica / Critério | Teste t de Welch (Paramétrico) | Teste U de Mann-Whitney (Não-Paramétrico) |
|---|---|---|
| **Abordagem Estatística** | Paramétrica (médias aritméticas) | Não-paramétrica (postos / dominância estocástica) |
| **Total de Simulações ($N$)** | $10.000$ | $10.000$ |
| **Rejeições Indevidas de $H_0$ ($k$)** | **$393$** | **$458$** |
| **Taxa Empírica ($\hat{\alpha}$)** | **$3{,}93\%$** ($0{,}0393$) | **$4{,}58\%$** ($0{,}0458$) |
| **Nível Nominal Teórico ($\alpha$)** | $5{,}00\%$ ($0{,}0500$) | $5{,}00\%$ ($0{,}0500$) |
| **Diferença frente ao Nominal ($\hat{\alpha} - \alpha$)** | **$-1{,}07\%$** (deflação de $21{,}4\%$ do erro) | **$-0{,}42\%$** (deflação de $8{,}4\%$ do erro) |
| **Intervalo de Confiança 95% (Wilson)** | **$[3{,}57\%; 4{,}33\%]$** | **$[4{,}19\%; 5{,}01\%]$** |
| **Classificação de Comportamento** | **Conservador** ($\hat{\alpha} < \text{limiar inferior}$) | **Nominal / Bem calibrado** ($\hat{\alpha} \approx \alpha$) |
| **Critério Estrito de Bradley (1978)** $[4{,}5\%; 5{,}5\%]$ | **Não** ($3{,}93\% < 4{,}50\%$) | **Sim** ($4{,}58\% \in [4{,}50\%; 5{,}50\%]$) |
| **Critério Liberal de Bradley (1978)** $[2{,}5\%; 7{,}5\%]$ | **Sim** ($3{,}93\% \in [2{,}50\%; 7{,}50\%]$) | **Sim** ($4{,}58\% \in [2{,}50\%; 7{,}50\%]$) |
| **Teste KS vs. Uniforme $U(0, 1)$ ($p$-valor)** | $D = 0{,}0347, \ p = 6{,}36 \times 10^{-11}$ | $D = 0{,}0092, \ p = 0{,}3633$ |

---

## 5. Análise e Interpretação dos Resultados

### 5.1 Comportamento do Teste t de Welch: Por que é Conservador?

O Teste t de Welch apresentou uma taxa empírica de **$3{,}93\%$**, rejeitando $H_0$ em apenas 393 das 10.000 repetições. Como o limite superior do seu intervalo de confiança a 95% ($4{,}33\%$) é estritamente inferior ao valor nominal de $5{,}0\%$, essa redução não é flutuação amostral: trata-se de um **comportamento conservador sistemático**.

As causas estatísticas desse conservadorismo residem na interação entre o modelo paramétrico e as características empíricas dos dados de Engenharia de Software:
1. **Assimetria Positiva e Caudas Pesadas:** A distribuição lognormal modela tempos de merge em que a grande maioria dos PRs é integrada em poucas horas, mas alguns poucos PRs sofrem atrasos excepcionais (100h a 200h).
2. **Inflação do Desvio Padrão Amostral ($s$):** Quando uma amostra sorteia um ou dois valores extremos na cauda direita, a média amostral é puxada moderadamente para cima, mas o **desvio padrão amostral $s$ é inflado quadraticamente**. Como o desvio padrão entra no denominador da estatística $t = \frac{\bar{X}_1 - \bar{X}_2}{\sqrt{s_1^2/n_1 + s_2^2/n_2}}$, o valor absoluto $|t|$ é severamente atenuado (comprimido em direção a zero).
3. **Penalização dos Graus de Liberdade ($\nu$):** A equação de Welch-Satterthwaite penaliza distribuições com desvios padrões desiguais decorrentes dos outliers assimétricos, reduzindo os graus de liberdade efetivos e elevando o valor crítico necessário para a rejeição.
4. **Déficit na Cauda da Distribuição dos $p$-valores:** O teste de aderência de Kolmogorov-Smirnov revelou que a distribuição empírica dos $p$-valores do teste t desvia drasticamente da uniforme teórica $U(0, 1)$ ($p = 6{,}36 \times 10^{-11}$), apresentando um déficit acentuado de valores no intervalo crítico $[0{,}00; 0{,}05]$.

### 5.2 Comportamento do Teste U de Mann-Whitney: Robustez e Calibração Teórica

O Teste U de Mann-Whitney obteve uma taxa empírica de **$4{,}58\%$** (458 rejeições em 10.000 simulações), com intervalo de confiança de $[4{,}19\%; 5{,}01\%]$, abrangendo praticamente o valor nominal de $5{,}0\%$.

As razões para o sucesso do teste não-paramétrico incluem:
1. **Imunidade à Escala das Caudas Longas:** O teste de Mann-Whitney opera sobre os **postos conjuntos** (*ranks* de $1$ a $N = 60$). Se um PR levou 300 horas para mergear, sua contribuição para o teste é exatamente a mesma de que se tivesse levado 80 horas: ele é apenas a observação de maior posto ($60$).
2. **Preservação da Distribuição Nula sob Postos:** Sob $H_0$, a distribuição amostral da estatística de postos $U$ depende exclusivamente da combinatória de ordenar dois conjuntos de 30 observações, sendo **livre de distribuição (*distribution-free*)**.
3. **Aprovação nos Critérios Formais de Bradley (1978):** Mann-Whitney atende tanto ao critério liberal $[2{,}5\%; 7{,}5\%]$ quanto ao **critério estrito de robustez** $[0{,}9\alpha; 1{,}1\alpha] = [4{,}5\%; 5{,}5\%]$.
4. **Uniformidade Estrita dos $p$-valores:** O teste de Kolmogorov-Smirnov resultou em $p = 0{,}3633$ ($> 0{,}05$), falhando em rejeitar a hipótese de que os $p$-valores de Mann-Whitney seguem uma distribuição perfeitamente uniforme $U(0, 1)$ sob $H_0$.

### 5.3 Diagnóstico sobre Comportamento Liberal

**Nenhum dos dois testes apresentou comportamento liberal.**
- Um teste é considerado liberal quando sua taxa empírica de falsos positivos supera significativamente o nível nominal estabelecido ($\hat{\alpha} > 5{,}0\%$, violando $\alpha$).
- Tanto Welch ($3{,}93\%$) quanto Mann-Whitney ($4{,}58\%$) mantiveram suas taxas abaixo do teto de $5{,}0\%$.
- Sob a perspectiva de proteção contra falsos alarmes, ambos os testes são seguros para uso prático. No entanto, o conservadorismo excessivo do teste t de Welch sugere que ele poderá sofrer de **perda de poder estatístico (maior Erro Tipo II)** na Questão Q2, quando um efeito real estiver de fato presente.

---

## 6. Respostas às Questões da Apresentação Oral

Esta análise fundamenta respostas diretas e precisas a perguntas do roteiro de apresentação oral do laboratório:

### Questão 8: *"No cenário de vocês, o que seria um erro tipo I e um erro tipo II? Qual dos dois seria mais grave?"*
> **Resposta:** O Erro Tipo I seria concluir que o uso de bots de revisão automatizada altera o tempo de merge de Pull Requests quando, na verdade, os bots não causam impacto mensurável no processo. O Erro Tipo II seria deixar de detectar uma redução real e significativa no tempo de merge proporcionada pelos bots devido à variabilidade ou ao tamanho amostral. No nosso contexto, o Erro Tipo I levaria a custos financeiros e esforço desnecessário em tooling ineficaz, enquanto o Erro Tipo II levaria a equipe a abrir mão de uma otimização válida de fluxo contínuo.

### Questão 9: *"No G3, algum teste se afastou de 5%? Ele ficou liberal ou conservador, e por quê?"*
> **Resposta:** Sim: o teste t de Welch afastou-se do valor teórico, apresentando comportamento conservador com taxa empírica de 3,93% (< 5,0%). Esse conservadorismo ocorre porque os tempos de software possuem distribuição lognormal assimétrica à direita, na qual outliers esporádicos inflam a variância amostral no denominador de t e comprimem a estatística em direção a zero. Já o teste U de Mann-Whitney operou sobre postos ordenados, neutralizando a magnitude dos outliers e mantendo taxa de 4,58%, dentro da tolerância estrita de calibração teórica. Nenhum dos testes foi liberal.

---

## 7. Integração com as Demais Etapas do LAB04

Os artefatos gerados nesta etapa estão organizados para alimentação direta das próximas fases da Sprint 02:
1. **Alimentação do Gráfico G3:** A função `obter_tabela_para_g3()` do módulo `simulacao_q1.py` fornece o schema padronizado de Erro Tipo I para a condição baseline sob $H_0$, pronto para ser plotado com a linha horizontal de 5% e contrastado com as violações de pressupostos da Questão Q3.
2. **Integração no Dashboard (`lab04/app.py`):** A Seção 4 ("Erro tipo I") exibe métricas dinâmicas, tabela de proporções e texto interpretativo conciso em conformidade com o enunciado do laboratório.
3. **Comparação Cruzada com Q2 (Poder):** O comportamento conservador observado no teste t de Welch sob $H_0$ levanta a hipótese empírica a ser testada na Questão Q2 de que o teste paramétrico perderá sensibilidade (menor poder) frente a efeitos reais quando comparado a Mann-Whitney.
