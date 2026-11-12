# [LAB04FINAL] Aplicação de Testes Estatísticos aos Dados Reais e Consolidação Final

**Atividade:** `[ LAB04FINAL ] Aplicar testes aos dados reais e finalizar análises estatísticas`  
**Laboratório:** LAB04 — Testes de Hipótese por Dentro: Cenário, Simulação e Visualização  
**Disciplina:** Laboratório de Experimentação de Software — 6º Período  
**Professor:** Danilo Maia  

---

## 1. Visão Geral e Objetivo

Este documento consolida a entrega final do LAB04 referente à aplicação dos dois testes estatísticos selecionados (**Par P1: Teste t de Welch × Teste U de Mann-Whitney**) sobre a amostra de dados reais coletada do repositório `tiangolo/fastapi`, a apresentação da **Tabela Comparativa da Seção 6** no Dashboard, e a finalização das interpretações dos gráficos **G3 (Erro Tipo I)** e **G4 (Poder Estatístico)** com destaque para as condições de melhor desempenho.

| Dimensão Experimental | Definição Adotada |
|---|---|
| **Repositório Minerado** | `tiangolo/fastapi` (GitHub público) |
| **Amostra Analisada** | 60 Pull Requests ($n_{\text{sem\_bot}} = 30$, $n_{\text{com\_bot}} = 30$) |
| **Variável Resposta ($Y$)** | Tempo até o merge (`tempo_horas`, em horas decimais) |
| **Par de Testes** | P1: t de Welch (paramétrico) × Mann-Whitney / Wilcoxon rank-sum (não-paramétrico) |
| **Direção do Teste** | Bicaudal (*two-sided*) |
| **Nível de Significância ($\alpha$)** | $\alpha = 0{,}05$ (95% de confiança) |
| **Módulos de Execução** | [`lab04/src/analise_dados_reais.py`](../src/analise_dados_reais.py) e [`lab04/app.py`](../app.py) |
| **Artefato Tabular Salvo** | [`lab04/data/tabela_comparativa_dados_reais.csv`](../data/tabela_comparativa_dados_reais.csv) |

---

## 2. Integridade dos Dados e Compatibilidade com os Testes

A amostra foi validada pelo módulo de qualidade com os seguintes resultados:
- **Tamanho Amostral:** 60 Pull Requests válidos (exatamente 30 no grupo `sem_bot` e 30 no grupo `com_bot`).
- **Completude:** 0 valores ausentes (*missing values*) ou nulos na variável `tempo_horas`.
- **Unicidade:** 0 identificadores de PR (`pr_id`) duplicados; nenhuma linha redundante.
- **Validade de Domínio:** Todos os tempos de merge são estritamente positivos ($Y > 0$), garantindo viabilidade para escala logarítmica e contínua.
- **Consistência Temporal:** Em 100% dos registros, `merged_at >= created_at` e `tempo_horas` coincide com a diferença calculada entre as datas.

### Verificação de Pressupostos e Compatibilidade:
1. **Teste de Normalidade (Shapiro-Wilk):**
   - Grupo `sem_bot`: $W = 0{,}8081, \quad p = 0{,}000112$ ($p < 0{,}001 \implies$ normalidade rejeitada).
   - Grupo `com_bot`: $W = 0{,}7947, \quad p = 0{,}000053$ ($p < 0{,}001 \implies$ normalidade rejeitada).
2. **Assimetria (*Skewness*):**
   - Ambos os grupos exibem forte assimetria positiva à direita: $\text{skew} = 1{,}6950$ (`sem_bot`) e $\text{skew} = 1{,}8158$ (`com_bot`).
3. **Outliers de Cauda Longa (Critério de Tukey $1{,}5 \cdot \text{IQR}$):**
   - 3 observações extremas em `sem_bot` (máximo de $105{,}5\text{ h}$) e 3 em `com_bot` (máximo de $88{,}0\text{ h}$).
4. **Compatibilidade dos Testes:**
   - **Teste t de Welch:** Aplicável com reservas. O ajuste de Welch-Satterthwaite relaxa a homocedasticidade (razão de variâncias $s_{\text{sem}}^2 / s_{\text{com}}^2 = 1{,}455$), mas sua sensibilidade é comprometida pela forte violação de normalidade e pela cauda pesada.
   - **Teste U de Mann-Whitney:** **Perfeitamente compatível e estatisticamente superior.** Por ser livre de distribuição (*distribution-free*) e operar sobre postos relativos ($1$ a $60$), ele não assume normalidade e é imune a distorções causadas por outliers na cauda direita.

---

## 3. Aplicação dos Dois Testes Estatísticos aos Dados Reais

### 3.1 Teste t de Welch (Paramétrico)
- **O que compara:** Médias aritméticas populacionais ($\mu_{\text{com\_bot}}$ vs. $\mu_{\text{sem\_bot}}$), ponderando a variabilidade amostral pelo erro padrão combinado sem exigir igualdade de variâncias.
- **Tendência Central Observada:**
  - $\bar{X}_{\text{sem\_bot}} = 27{,}4233\text{ h}$, $\quad \bar{X}_{\text{com\_bot}} = 20{,}9500\text{ h}$
  - Diferença média: $\Delta \bar{X} = -6{,}4733\text{ h}$ (redução relativa de $-23{,}6\%$).
- **Dispersão Amostral:**
  - $s_{\text{sem\_bot}} = 24{,}2001\text{ h}$, $\quad s_{\text{com\_bot}} = 20{,}0598\text{ h}$.
- **Estatística Calculada:** $t = -1{,}1280$.
- **Graus de Liberdade (Welch-Satterthwaite):** $\nu = 56{,}0713$.
- **$p$-valor (bicaudal):** $p = 0{,}264132$.
- **Tamanho do Efeito:** $d$ de Cohen com desvios não agrupados = $-0{,}2912$ (magnitude: **pequeno**, $0{,}20 \le |d| < 0{,}50$).
- **Decisão Formal ($\alpha = 0{,}05$):** Como $p = 0{,}2641 \ge 0{,}05$, **NÃO SE REJEITA $H_0$**.

### 3.2 Teste U de Mann-Whitney (Não-paramétrico)
- **O que compara:** Ordenação conjunta de postos (*ranks*) e dominância estocástica $P(X_{\text{com\_bot}} > Y_{\text{sem\_bot}})$, refletindo deslocamento de medianas sob formatos distribucionais semelhantes.
- **Tendência Central Observada:**
  - $\tilde{X}_{\text{sem\_bot}} = 18{,}9000\text{ h}$, $\quad \tilde{X}_{\text{com\_bot}} = 13{,}6000\text{ h}$
  - Diferença de medianas: $\Delta \tilde{X} = -5{,}3000\text{ h}$ (redução relativa de $-28{,}0\%$).
- **Dispersão Amostral (Intervalo Interquartil):**
  - $\text{IQR}_{\text{sem\_bot}} = 20{,}9250\text{ h}$, $\quad \text{IQR}_{\text{com\_bot}} = 16{,}7750\text{ h}$.
- **Estatística Calculada:** $U = 357{,}0000$ (para $n_1 = 30, n_2 = 30$).
- **Parâmetro Auxiliar sob $H_0$:** $z = -1{,}37495$ (aproximação normal padronizada).
- **$p$-valor (bicaudal):** $p = 0{,}171450$.
- **Tamanho do Efeito Adotado:**
  - **Correlação Rank-Biserial ($r_{rb}$):** $r_{rb} = 2 \cdot \frac{U}{n_1 n_2} - 1 = -0{,}2067$ (magnitude: **pequena**, $0{,}15 \le |r| < 0{,}33$).
  - **Delta de Cliff ($\delta$):** $\delta = -0{,}2067$.
  - **Probabilidade de Superioridade (CLES):** $P(X_{\text{com\_bot}} < Y_{\text{sem\_bot}}) = 60{,}33\%$.
- **Decisão Formal ($\alpha = 0{,}05$):** Como $p = 0{,}1715 \ge 0{,}05$, **NÃO SE REJEITA $H_0$**.

---

## 4. Tabela Comparativa Exigida na Seção 6 — "Dados Reais"

A tabela abaixo reproduz fielmente os campos exigidos pelo enunciado e implementados em [`lab04/data/tabela_comparativa_dados_reais.csv`](../data/tabela_comparativa_dados_reais.csv) e no Dashboard:

| Teste | Abordagem | O que compara | Estatística | $p$-valor | Tamanho do Efeito | Decisão ($\alpha = 0{,}05$) | Conclusão Prática |
|---|---|---|---|---|---|---|---|
| **t de Welch** | Paramétrica | Médias aritméticas ($\mu$) | $t = -1{,}1280$ ($\text{gl} = 56{,}07$) | $0{,}2641$ | $d = -0{,}2912$ (*pequeno*) | Não rejeitar $H_0$ ($p \ge 0{,}05$) | Redução média de $6{,}47\text{ h}$ ($-23{,}6\%$), não estatisticamente significativa devido à alta variabilidade amostral. |
| **Mann-Whitney (Wilcoxon rank-sum)** | Não-paramétrica | Postos e Dominância Estocástica (Medianas) | $U = 357{,}0$ ($z = -1{,}3750$) | $0{,}1715$ | $r_{rb} = -0{,}2067$ (*pequeno*; $P(\text{com}<\text{sem}) = 60{,}3\%$) | Não rejeitar $H_0$ ($p \ge 0{,}05$) | Redução de $5{,}30\text{ h}$ na mediana ($-28{,}0\%$), não estatisticamente significativa para $n = 30$. |

---

## 5. Interpretação da Magnitude, Importância Prática e Comparação entre os Testes

### 5.1 Magnitude e Importância Prática do Efeito
1. **Magnitude Estatística Padronizada:**
   - Ambos os tamanhos de efeito mensurados situam-se na faixa classificada como **pequena** segundo as convenções da literatura ($|d| = 0{,}2912 < 0{,}50$; $|r_{rb}| = 0{,}2067 < 0{,}33$).
2. **Relevância Prática em Engenharia de Software:**
   - Em termos práticos de fluxo de desenvolvimento, uma redução de **$5{,}30\text{ horas}$ na mediana** (de $18{,}9\text{ h}$ para $13{,}6\text{ h}$) e de **$6{,}47\text{ horas}$ na média** representa um ganho real no tempo de espera do desenvolvedor por aprovações e merges. Economizar quase 6 horas por PR agiliza pipelines de integração contínua e diminui o desperdício de contexto (*context switching*).
   - Entretanto, a análise descritiva revela que a variabilidade é massiva: os desvios padrão superam $20\text{ h}$ a $24\text{ h}$, e o tempo de merge varia de meras $1{,}2\text{ h}$ até mais de $105\text{ h}$. Isso ocorre porque o gargalo principal em repositórios maduros continua sendo a disponibilidade de revisores humanos para avaliar decisões de arquitetura e lógica de negócio.

### 5.2 Comparação entre os Testes e Discussão de Divergências
- **Convergência de Decisão:** Ambos os testes convergem na mesma decisão estatística formal: **não rejeitar $H_0$ ao nível $\alpha = 0{,}05$**.
- **Diferença nos $p$-valores:** O teste de Mann-Whitney produziu um $p$-valor sensivelmente menor do que o teste t de Welch ($0{,}1715$ vs. $0{,}2641$, $\Delta p = 0{,}0927$).
- **Razão Estatística da Divergência:**
  - No teste t de Welch, observações extremas de tempos longos na cauda direita (PRs de $88{,}0\text{ h}$ e $105{,}5\text{ h}$) puxam as médias para cima e inflam os desvios padrão amostrais ($20{,}06\text{ h}$ e $24{,}20\text{ h}$), aumentando consideravelmente o denominador do teste ($s_{\text{erro combinado}} = 5{,}739\text{ h}$) e comprimindo a estatística $|t|$ para apenas $1{,}1280$.
  - No teste U de Mann-Whitney, os tempos são convertidos em postos ordenados ($1$ a $60$), de modo que valores extremos não inflam a dispersão de postos e seu peso fica estritamente delimitado. Como em $60{,}33\%$ dos pares comparados o PR assistido por bot foi mesclado mais rapidamente, o teste não-paramétrico capturou essa vantagem sistemática com maior nitidez.

### 5.3 Diagnóstico de Poder Amostral com $n = 30$ (Conexão com o Gráfico G4)
- A ausência de significância estatística na amostra real não demonstra que os bots não têm efeito, mas sim que **a amostra de $n = 30$ possui poder insuficiente para detectar efeitos pequenos a moderados** sob alta dispersão.
- As curvas de poder simuladas no Gráfico G4 revelam que, para uma redução de $20\%$ a $30\%$ no tempo de merge com $n = 30$, o poder estatístico fica entre $28\%$ e $48\%$ (muito aquém do limiar ideal de $80\%$).
- Para que um efeito dessa magnitude ($|d| \approx 0{,}30$) alcance $80\%$ de poder estatístico a $\alpha = 0{,}05$, seriam necessários aproximadamente **$170$ a $190$ Pull Requests por grupo** (cerca de 360 PRs no total).

---

## 6. Textos Interpretativos Oficiais das Seções 4 (G3) e 5 (G4)

Atendendo estritamente ao critério de **2 a 4 frases concisas**, os textos foram revisados para destacar em quais situações cada teste apresentou melhor desempenho:

### Seção 4 — Erro Tipo I (Gráfico G3)
> "O gráfico G3 compara a taxa empírica de Erro Tipo I dos dois testes em 10.000 simulações sob H₀ frente ao nível nominal de 5% (linha tracejada vermelha). O teste U de Mann-Whitney apresentou o melhor desempenho em todas as condições simuladas, mantendo-se rigorosamente próximo aos 5% (4,58% na base, 4,52% com outliers e 4,33% com amostra pequena), confirmando robustez estrita por operar sobre postos ordenados. Já o teste t de Welch apresentou comportamento conservador em todos os cenários, rejeitando H₀ consideravelmente menos do que o esperado (3,93% na base, 3,28% com outliers e 2,90% com amostra pequena). Os maiores desvios ocorreram nas situações de violação de pressupostos (outliers severos e amostra pequena), nas quais a cauda longa e a variabilidade extrema inflam o erro padrão e distorcem a aproximação paramétrica do teste t."
*(Exatamente 4 frases — destaca melhor desempenho de Mann-Whitney).*

### Seção 5 — Poder Estatístico (Gráfico G4)
> "O gráfico G4 mostra que o poder estatístico cresce com o tamanho do efeito e que o teste U de Mann-Whitney (laranja) apresentou o melhor desempenho em todas as situações log-normais simuladas, ampliando sua vantagem à medida que o efeito aumenta (em δ = 50%, atinge 79,08% contra 64,20% no cenário original, uma vantagem de +14,88 p.p.). Sob violação de pressupostos por outliers severos (Q3), o poder de Welch sofre um colapso drástico (caindo para 22,62% em δ = 50%), enquanto Mann-Whitney mantém melhor desempenho com 62,30% (+39,68 p.p. de vantagem), liderando também com amostra pequena de n = 10 (40,23% vs. 28,51%). Como demonstra o painel direito, a situação em que o teste t de Welch apresenta melhor desempenho restringe-se exclusivamente à distribuição Normal simétrica sem outliers (onde Welch atinge 75,80% contra 73,12% de Mann-Whitney em δ = 30%, devido à sua eficiência ótima paramétrica sob normalidade)."
*(Exatamente 3 frases — destaca melhor desempenho de Mann-Whitney em cenários realistas e de Welch sob normalidade perfeita).*

---

## 7. Conclusão Final Geral

A convergência entre a teoria, as 10.000 simulações de Monte Carlo (Q1, Q2 e Q3) e a aplicação empírica nos dados reais confirma integralmente a previsão inicial do grupo:
1. **Recomendação Principal:** O **teste U de Mann-Whitney** é a recomendação oficial para dados de lead time de Pull Requests e tempos de processo em Engenharia de Software.
2. **Justificativa:** É estritamente calibrado no Erro Tipo I (próximo a 5%), alcança poder superior (até +39,68 p.p. sob outliers) e lida naturalmente com caudas pesadas e observações atípicas.
3. **Quando a Escolha Mudaria:** A recomendação mudaria em favor do **teste t de Welch** apenas se a distribuição dos dados fosse comprovadamente normal e simétrica sem contaminação por outliers, ou se o foco do estudo recaísse obrigatoriamente sobre o custo acumulado total das médias aritméticas após validação rigorosa de premissas.
