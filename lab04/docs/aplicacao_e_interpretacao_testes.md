# [LAB04S01] Aplicação e Interpretação dos Dois Testes Estatísticos
**Issue correspondente:** `#49`  
**Laboratório:** LAB04 — Testes de Hipótese por Dentro: Cenário, Simulação e Visualização  
**Disciplina:** Laboratório de Experimentação de Software — 6º Período  
**Professor:** Danilo Maia  

---

## 1. Visão Geral e Identificação dos Testes

Este documento registra a implementação, a aplicação empírica e a interpretação detalhada dos dois testes de hipótese selecionados pelo grupo (**Par P1**) sobre o conjunto de dados simulado oficial da Sprint 01 (`semente = 42`, $n_1 = 30$, $n_2 = 30$) e sobre a amostra de dados reais coletada do repositório `tiangolo/fastapi`.

| Parâmetro de Configuração | Especificação Adotada |
|---|---|
| **Par de Testes Selecionado** | **P1: Teste t de Welch × Teste U de Mann-Whitney (Wilcoxon rank-sum)** |
| **Pergunta de Pesquisa** | *"A utilização de bots de revisão automatizada altera o tempo decorrido até o merge de Pull Requests em projetos de Engenharia de Software?"* |
| **Grupos Comparados** | `sem_bot` (controle, $n = 30$) vs. `com_bot` (tratamento, $n = 30$) |
| **Variável Resposta ($Y$)** | Tempo decorrido até o merge (`tempo_horas`, em horas decimais) |
| **Direção do Teste** | **Bicaudal** (`two-sided`) |
| **Nível de Significância ($\alpha$)** | $\alpha = 0{,}05$ (95% de confiança) |
| **Módulo de Implementação** | [`lab04/src/testes_estatisticos.py`](../src/testes_estatisticos.py) |
| **Arquivo de Saída Tabular** | [`lab04/data/resultados_testes_s01.csv`](../data/resultados_testes_s01.csv) |

---

## 2. O Que Cada Teste Compara Efetivamente e Condições de Aplicação

### 2.1 Teste t de Welch (*Welch's two-sample t-test*)
- **Abordagem:** Paramétrica (`scipy.stats.ttest_ind(..., equal_var=False, alternative="two-sided")`).
- **O que compara efetivamente:** Compara as **médias aritméticas populacionais** ($\mu_{\text{com\_bot}}$ vs. $\mu_{\text{sem\_bot}}$), avaliando se a diferença observada entre as médias amostrais ($\bar{X}_{\text{com}} - \bar{X}_{\text{sem}}$) é significativamente diferente de zero quando padronizada pelo erro padrão combinado de Welch.
- **Hipóteses Operacionais:**
  - $H_0: \mu_{\text{com\_bot}} = \mu_{\text{sem\_bot}} \iff \mu_{\text{com\_bot}} - \mu_{\text{sem\_bot}} = 0$
  - $H_1: \mu_{\text{com\_bot}} \neq \mu_{\text{sem\_bot}} \iff \mu_{\text{com\_bot}} - \mu_{\text{sem\_bot}} \neq 0$
- **Estatística de Teste e Graus de Liberdade:**
  $$t = \frac{\bar{X}_{\text{com}} - \bar{X}_{\text{sem}}}{\sqrt{\frac{s_{\text{com}}^2}{n_{\text{com}}} + \frac{s_{\text{sem}}^2}{n_{\text{sem}}}}}, \qquad \nu \approx \frac{\left(\frac{s_{\text{com}}^2}{n_{\text{com}}} + \frac{s_{\text{sem}}^2}{n_{\text{sem}}}\right)^2}{\frac{(s_{\text{com}}^2 / n_{\text{com}})^2}{n_{\text{com}} - 1} + \frac{(s_{\text{sem}}^2 / n_{\text{sem}})^2}{n_{\text{sem}} - 1}}$$
- **Condições de Aplicação (Pressupostos):**
  1. Independência mútua entre as observações dentro de cada grupo e entre os dois grupos;
  2. Variável dependente contínua medida em escala intervalar ou de razão;
  3. Normalidade aproximada da distribuição amostral das médias em cada grupo (vulnerável a forte assimetria e *outliers* em amostras pequenas/moderadas);
  4. **Não exige homocedasticidade** ($\sigma_{\text{com}}^2 \neq \sigma_{\text{sem}}^2$ é tratado pelo ajuste de Welch-Satterthwaite nos graus de liberdade $\nu$).

### 2.2 Teste U de Mann-Whitney (*Wilcoxon rank-sum test*)
- **Abordagem:** Não-paramétrica (`scipy.stats.mannwhitneyu(..., alternative="two-sided")`).
- **O que compara efetivamente:** Compara a **ordenação conjunta de postos (*ranks*)** e a **dominância estocástica** entre as duas distribuições, isto é, a probabilidade $P(X_{\text{com\_bot}} > Y_{\text{sem\_bot}})$ de uma observação sorteada de um grupo superar uma observação do outro. Sob distribuições de formato semelhante, equivale à comparação entre as **medianas populacionais** ($\tilde{\mu}_{\text{com\_bot}}$ vs. $\tilde{\mu}_{\text{sem\_bot}}$).
- **Hipóteses Operacionais:**
  - $H_0: P(X_{\text{com\_bot}} > Y_{\text{sem\_bot}}) = 0{,}50$ (ausência de dominância estocástica / medianas equivalentes)
  - $H_1: P(X_{\text{com\_bot}} > Y_{\text{sem\_bot}}) \neq 0{,}50$ (presença de dominância estocástica / deslocamento de postos e medianas)
- **Estatística de Teste e Aproximação Normal Padronizada:**
  $$U_{\text{com}} = R_{\text{com}} - \frac{n_{\text{com}}(n_{\text{com}} + 1)}{2}, \qquad z = \frac{U_{\text{com}} - \frac{n_{\text{com}} n_{\text{sem}}}{2}}{\sqrt{\frac{n_{\text{com}} n_{\text{sem}}(n_{\text{com}} + n_{\text{sem}} + 1)}{12}}}$$
- **Condições de Aplicação (Pressupostos):**
  1. Independência das observações dentro dos grupos e entre os grupos;
  2. Variável em escala ao menos ordinal ou contínua que permita ranqueamento conjunto;
  3. **Livre de distribuição (*distribution-free*):** dispensa normalidade e é robusto a valores extremos (*outliers*), pois cada observação contribui apenas com sua posição relativa (posto de $1$ a $N = n_1 + n_2$).

---

## 3. Resultados Obtidos no Conjunto de Dados Simulado (S01 — Semente = 42)

O conjunto de dados [`lab04/data/dados_simulados_s01.csv`](../data/dados_simulados_s01.csv) foi gerado com semente fixa `42` ($n_{\text{sem\_bot}} = 30$, $n_{\text{com\_bot}} = 30$) sob os parâmetros lognormais ajustados a partir da amostra real ($\mu_{\log,\text{sem}} = 2{,}9721, \sigma_{\log,\text{sem}} = 0{,}8670$; $\mu_{\log,\text{com}} = 2{,}6385, \sigma_{\log,\text{com}} = 0{,}9632$).

### Tabela 1: Resultados dos Dois Testes sobre os Dados Simulados (S01, `semente = 42`)

| Métrica / Parâmetro | Teste t de Welch (Paramétrico) | Teste U de Mann-Whitney (Não-Paramétrico) |
|---|---|---|
| **O que compara** | Médias aritméticas ($\mu_{\text{com}}$ vs. $\mu_{\text{sem}}$) | Postos ordenados / Dominância estocástica / Medianas |
| **Tamanho Amostral ($n_{\text{sem}}, n_{\text{com}}$)** | $30 \text{ vs. } 30$ | $30 \text{ vs. } 30$ |
| **Medida Central (`sem_bot` vs. `com_bot`)** | Média: $24{,}01\text{ h}$ vs. $21{,}33\text{ h}$ | Mediana: $21{,}25\text{ h}$ vs. $16{,}46\text{ h}$ |
| **Diferença Central ($\text{com\_bot} - \text{sem\_bot}$)** | $\Delta \bar{X} = -2{,}68\text{ h}$ ($-11{,}2\%$) | $\Delta \tilde{X} = -4{,}78\text{ h}$ ($-22{,}5\%$) |
| **Medida de Dispersão (`sem_bot` vs. `com_bot`)** | DP: $13{,}99\text{ h}$ vs. $20{,}92\text{ h}$ | IQR: $16{,}87\text{ h}$ vs. $17{,}43\text{ h}$ |
| **Estatística do Teste** | $t = -0{,}5828$ | $U = 347{,}5000$ |
| **Parâmetro Auxiliar sob $H_0$** | $\text{gl} = 50{,}6112$ (Welch-Satterthwaite) | $z = -1{,}5154$ (aproximação normal) |
| **$p$-valor (bicaudal)** | **$p = 0{,}562615$** | **$p = 0{,}131546$** |
| **Nível de Significância ($\alpha$)** | $\alpha = 0{,}05$ | $\alpha = 0{,}05$ |
| **Comparação com $\alpha = 0{,}05$** | $0{,}5626 \ge 0{,}05$ | $0{,}1315 \ge 0{,}05$ |
| **Decisão Estatística** | **Não rejeitar $H_0$** | **Não rejeitar $H_0$** |
| **Tamanho do Efeito** | $d = -0{,}1505$ (*trivial / desprezível*) | $r_{rb} = -0{,}2278$ (*pequeno*, $61{,}4\%$ de pares favoráveis) |

---

## 4. Interpretação em Linguagem Simples e Relação com a Pergunta de Pesquisa

1. **Decisão para o Teste t de Welch ($p = 0{,}5626 \ge 0{,}05$):**  
   Não rejeitamos $H_0$. Embora o tempo médio até o merge no grupo simulado com bot ($21{,}33\text{ h}$) seja $2{,}68\text{ h}$ menor do que no grupo sem bot ($24{,}01\text{ h}$), essa diferença é muito pequena diante da alta dispersão amostral ($\text{DP} = 20{,}92\text{ h}$ com bot e $13{,}99\text{ h}$ sem bot). Em linguagem simples, uma diferença média dessa magnitude ocorreria por puro acaso em cerca de $56{,}3\%$ das amostras caso os bots não tivessem efeito algum.

2. **Decisão para o Teste U de Mann-Whitney ($p = 0{,}1315 \ge 0{,}05$):**  
   Não rejeitamos $H_0$. Na comparação por postos e medianas, o grupo com bot apresentou mediana $4{,}78\text{ h}$ menor ($16{,}46\text{ h}$ contra $21{,}25\text{ h}$ sem bot), vencendo em $61{,}4\%$ dos $900$ pares comparados ($U = 347{,}5$, correlação rank-biserial $r_{rb} = -0{,}2278$). Ainda assim, com $n = 30$ observações por grupo, o $p$-valor de $0{,}1315$ supera o limiar de $\alpha = 0{,}05$, não fornecendo evidência estatística conclusiva para descartar a hipótese nula.

3. **Resposta à Pergunta de Pesquisa nesta Amostra Única (e Lição Metodológica):**  
   A partir exclusivamente deste conjunto simulado de $n = 30$ por grupo, **nenhum dos dois testes permite afirmar com 95% de confiança que os bots de revisão alteram o tempo até o merge**. Como sabemos por construção da simulação que este dataset foi gerado sob $H_1$ (com mediana teórica menor no grupo `com_bot`), este resultado ilustra na prática um **Erro Tipo II (falso negativo)**: quando os dados têm cauda longa e variância elevada, uma única amostra de tamanho moderado ($n = 30$) pode não ter poder estatístico suficiente para detectar um efeito real de tamanho pequeno a moderado.

---

## 5. Diferenças Observadas entre os Dois Testes e Razões Estatísticas

Apesar de ambos os testes levarem à mesma decisão qualitativa ($\text{não rejeitar } H_0$ para $\alpha = 0{,}05$), há uma **diferença quantitativa expressiva** na sensibilidade demonstrada por cada teste sobre exatamente os mesmos dados:

- O $p$-valor do **Teste U de Mann-Whitney ($p = 0{,}1315$)** foi **mais de 4 vezes menor** do que o $p$-valor do **Teste t de Welch ($p = 0{,}5626$)** ($\Delta p = 0{,}4311$).
- Da mesma forma, a estatística padronizada de Mann-Whitney ($z = -1{,}5154$, efeito pequeno $r_{rb} = -0{,}2278$) capturou muito mais sinal do que a estatística de Welch ($t = -0{,}5828$, efeito trivial $d = -0{,}1505$).

### Por que isso aconteceu?
1. **Sensibilidade da Média e da Variância a Outliers no Grupo `com_bot`:**  
   No dataset simulado com semente `42`, o grupo `com_bot` sorteou uma observação extrema na cauda direita: o **PR #31 com `110,09 horas`** (além do PR #58 com `59,05 horas`), enquanto o maior valor do grupo `sem_bot` foi `56,38 horas`.
2. **Distorção no Teste t de Welch:**  
   Esse único outlier de `110,09 h` no grupo `com_bot` provocou dois efeitos simultâneos que degradam a estatística $t$:
   - **Inflou a média amostral de `com_bot`** para $21{,}33\text{ h}$ (quase alcançando a média de $24{,}01\text{ h}$ do grupo `sem_bot`, comprimindo o numerador $\bar{X}_{\text{com}} - \bar{X}_{\text{sem}}$ para apenas $-2{,}68\text{ h}$);
   - **Inflou o desvio padrão de `com_bot`** para $20{,}92\text{ h}$ (contra $13{,}99\text{ h}$ no grupo `sem_bot`), aumentando o erro padrão no denominador ($\text{EP} = 4{,}595\text{ h}$) e reduzindo $|t|$ para $0{,}5828$.
3. **Robustez de Postos no Teste U de Mann-Whitney:**  
   No teste de Mann-Whitney, o PR de `110,09 h` recebe simplesmente o posto máximo ($60º$ lugar entre as $60$ observações). Se ele valesse `60 h`, `110 h` ou `1.000 h`, seu posto continuaria sendo exatamente $60$. Por isso, o teste não-paramétrico não teve seu denominador destruído pela cauda longa e refletiu fielmente o fato de que a maioria dos PRs com bot teve tempos menores (mediana de $16{,}46\text{ h}$ vs. $21{,}25\text{ h}$).

---

## 6. Aplicação Comparativa na Amostra de Dados Reais (`tiangolo/fastapi`)

O mesmo módulo [`lab04/src/testes_estatisticos.py`](../src/testes_estatisticos.py) foi aplicado à amostra real coletada ([`lab04/data/amostra_dados_reais.csv`](../data/amostra_dados_reais.csv)), preparando desde já os resultados exigidos para a Seção 6 do Dashboard:

| Métrica / Parâmetro | Teste t de Welch (Dados Reais) | Teste U de Mann-Whitney (Dados Reais) |
|---|---|---|
| **Medida Central (`sem_bot` vs. `com_bot`)** | Média: $27{,}42\text{ h}$ vs. $20{,}95\text{ h}$ ($\Delta = -6{,}47\text{ h}$) | Mediana: $18{,}90\text{ h}$ vs. $13{,}60\text{ h}$ ($\Delta = -5{,}30\text{ h}$) |
| **Medida de Dispersão (`sem_bot` vs. `com_bot`)** | DP: $24{,}20\text{ h}$ vs. $20{,}06\text{ h}$ | IQR: $20{,}92\text{ h}$ vs. $16{,}77\text{ h}$ |
| **Estatística do Teste** | $t = -1{,}1280$ ($\text{gl} = 56{,}07$) | $U = 357{,}0000$ ($z = -1{,}3750$) |
| **$p$-valor (bicaudal)** | **$p = 0{,}264132$** | **$p = 0{,}171450$** |
| **Tamanho do Efeito** | $d = -0{,}2913$ (*pequeno*) | $r_{rb} = -0{,}2067$ (*pequeno*) |
| **Decisão ($\alpha = 0{,}05$)** | **Não rejeitar $H_0$** | **Não rejeitar $H_0$** |

Novamente, nos dados reais, o teste de Mann-Whitney apresenta um $p$-valor menor ($0{,}1715$ contra $0{,}2641$ do Welch) devido à forte assimetria positiva de ambos os grupos ($\text{skewness} > 1{,}69$), embora ambos não rejeitem $H_0$ com $n = 30$.

---

## 7. Organização Modular para Reutilização na Sprint 02 (Q1, Q2 e Q3)

O módulo [`lab04/src/testes_estatisticos.py`](../src/testes_estatisticos.py) foi estruturado em duas camadas complementares:
1. **Camada Analítica Detalhada (S01 e Dashboard):**
   - `executar_teste_welch(sem_bot, com_bot, alpha, alternativa) -> ResultadoTesteIndividual`
   - `executar_teste_mann_whitney(sem_bot, com_bot, alpha, alternativa) -> ResultadoTesteIndividual`
   - `aplicar_ambos_testes(df, alpha, alternativa, origem_dados, semente) -> ComparacaoTestes`
   - `executar_analise_simulados_s01()` e `executar_analise_dados_reais()`
   - `comparacao_para_dataframe()` e `salvar_resultados_testes_s01()`
2. **Camada de Alto Desempenho para Simulações de Monte Carlo (S02 — Q1, Q2 e Q3):**
   - `avaliar_par_rapido(sem_bot, com_bot, alpha, alternativa) -> dict`: executa apenas os núcleos numéricos (`ttest_ind` e `mannwhitneyu` assintótico) diretamente sobre arrays NumPy, retornando `t_stat`, `p_welch`, `rejeita_welch`, `u_stat`, `p_mann_whitney` e `rejeita_mann_whitney` sem overhead de formatação textual, permitindo rodar as **10.000 repetições** de Q1, Q2 e Q3 em poucos segundos.
   - `avaliar_dataframe_rapido(df, alpha, alternativa) -> dict`: conveniência direta para DataFrames gerados por `GeradorDadosSimulados`.
