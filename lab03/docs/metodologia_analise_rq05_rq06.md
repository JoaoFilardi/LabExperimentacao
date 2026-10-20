# Metodologia Estatística e Visual: Análise das RQ 05 e RQ 06 (Sprint 03)

## 1. Visão Geral e Enquadramento Científico

No âmbito do **Laboratório 03 — Mineração de Métricas DORA em Repositórios Open-Source** (Sprint 03, Seção 5 e Seção 10 do enunciado), este documento detalha o embasamento teórico, as formulações matemáticas, os testes não-paramétricos de hipóteses, o protocolo de controle da taxa de falsos positivos e os padrões gráficos adotados para responder a duas questões centrais:

* **RQ 05: Repositórios com maior frequência de deploy apresentam maior ou menor taxa de falha?**
* **RQ 06: Quais características dos repositórios estão associadas a um melhor desempenho DORA?**

O pipeline analítico é implementado de forma modular e fortemente tipada em `lab03/src/analise_rq05_rq06.py`. A execução processa a totalidade dos **310 repositórios qualificados** e a amostra-ouro validada por consenso (`lab03/data/amostra_ouro_final.csv`), gerando saídas tabulares (`.csv`, `.md`, `.tex`) e figuras vetoriais/rasterizadas em `lab03/data/figuras/`.

---

## 2. Metodologia da RQ 05 (Velocidade vs. Estabilidade)

### 2.1. O Paradigma DORA e o Mito do Trade-Off
A literatura tradicional de gerenciamento de software sustentava frequentemente a existência de uma compensação inversa (*trade-off*) entre velocidade de entrega e estabilidade operacional: quanto mais rápido um software é lançado, maior seria a propensão a falhas. Em contrapartida, as pesquisas do consórcio DORA (*State of DevOps*, Forsgren et al., *Accelerate*) postulam que equipes e projetos de alto desempenho desenvolvem mecanismos de engenharia que quebram esse *trade-off*, operando concomitantemente com alta frequência de entrega e reduzida taxa de falha de mudança (CFR).

Para examinar empiricamente essa hipótese em projetos de código aberto:
* **Variável Independente ($X$):** `deployment_frequency_weekly` (frequência de deploys em releases por semana na janela de 12 meses);
* **Variáveis Dependentes ($Y$):**
  1. **CFR Variante (a) — Proxy de CI:** Proporção de execuções de workflow falhas no default branch acionadas por eventos de `push` ($\frac{\text{falhas}}{\text{falhas} + \text{sucessos}}$).
  2. **CFR Variante (b) — Proxy de Entrega:** Proporção de releases seguidas por uma release corretiva dentro de um horizonte de 7 dias (com censura aplicada às releases ocorridas nos últimos 7 dias da janela).

### 2.2. Coeficiente de Correlação de Postos de Spearman ($\rho$)
Adotou-se o teste não-paramétrico de Spearman pelas seguintes razões metodológicas:
1. **Não-normalidade severa:** Tanto a frequência de deploys quanto a taxa de falha em repositórios abertos violam drasticamente a distribuição normal (testes de Shapiro-Wilk com $p < 0.001$), apresentando forte assimetria à direita (*heavy-tailed*);
2. **Monotonicidade:** O objetivo é testar se maiores valores de $X$ associam-se monotonamente a maiores ou menores valores de $Y$, sem impor restrição de relação linear rígida com variância uniforme (homocedasticidade).

A formulação matemática para $n$ pares ordenados de postos $(R(X_i), R(Y_i))$ é:
$$\rho = 1 - \frac{6 \sum_{i=1}^n [R(X_i) - R(Y_i)]^2}{n(n^2 - 1)}$$

A significância estatística ($p$-valor bicaudal) é obtida via `scipy.stats.spearmanr`. Adicionalmente, computa-se o **Intervalo de Confiança Bootstrap de 95%** (1.000 reamostragens com reposição).

A magnitude da associação segue a escala consolidada de Dancey & Reidy:
* $|\rho| < 0.10$: Desprezível
* $0.10 \le |\rho| < 0.30$: Fraca
* $0.30 \le |\rho| < 0.50$: Moderada
* $0.50 \le |\rho| < 0.70$: Forte
* $|\rho| \ge 0.70$: Muito Forte

### 2.3. Ressalva Epistemológica Obrigatória
Conforme exigido pelo enunciado do laboratório, reforça-se formalmente que **correlação não implica causalidade**. Uma eventual neutralidade ou correlação fraca observada entre velocidade e estabilidade decorre frequentemente de variáveis intervenientes e de controle (como maturidade do pipeline de CI/CD, cobertura de testes de regressão e práticas de *code review* em Pull Requests).

---

## 3. Metodologia da RQ 06 (Diferenças entre Subgrupos)

### 3.1. Fatores Analisados e Critérios de Agrupamento
Foram investigados 5 fatores estruturais sobre as quatro métricas DORA:
1. **Tipo de Projeto (`tipo_projeto`):** Categorizado a partir do consenso da amostra-ouro (`amostra_ouro_final.csv`):
   * `biblioteca/framework` ($N=25$)
   * `aplicação/serviço` ($N=17$)
   * `CLI` ($N=14$)
   * `outro` ($N=1$)
2. **Popularidade (`stars_quartile`):** Quartis da contagem de estrelas no GitHub ($Q_1 \le 25\%$, $Q_2: 25\%-50\%$, $Q_3: 50\%-75\%$, $Q_4 > 75\%$);
3. **Idade do Repositório (`age_quartile`):** Quartis de tempo decorrido desde a criação em anos ($Q_1, Q_2, Q_3, Q_4$);
4. **Linguagem Principal (`language_group`):** As linguagens mais frequentes na amostra (Python, JavaScript, TypeScript, Go) e agrupamento das demais em "Outras";
5. **Número de Contribuidores (`contributors_quartile`):** Quartis da contagem de colaboradores ativos no projeto.

### 3.2. Teste Não-Paramétrico Omnibus: Kruskal-Wallis ($H$)
Como as distribuições das quatro métricas DORA não aderem à normalidade e os tamanhos amostrais dos grupos podem diferir, utiliza-se o teste de **Kruskal-Wallis** (`scipy.stats.kruskal`) para determinar se há diferenças estocásticas entre as medianas dos subgrupos:

$$H = \frac{12}{n(n+1)} \sum_{j=1}^k \frac{R_j^2}{n_j} - 3(n+1)$$
onde $k$ é o número de grupos do fator, $n$ é a contagem total de observações válidas, $n_j$ é o tamanho amostral do grupo $j$, e $R_j$ é a soma dos postos das observações pertencentes ao grupo $j$.

### 3.3. Controle da Taxa de Erro Familiar (FWER): Correção de Holm-Bonferroni
Com 5 fatores testados contra as 5 métricas DORA, são conduzidos **25 testes estatísticos omnibus**. A realização de múltiplos testes ao nível de significância nominal $\alpha = 0.05$ inflaciona a probabilidade de falsos positivos:
$$\alpha_{\text{global}} = 1 - (1 - 0.05)^{25} \approx 72.3\%$$

Para salvaguardar o rigor da conclusão científica, aplica-se o procedimento sequencial de **Holm-Bonferroni** (`statsmodels.stats.multitest.multipletests(method='holm')`):
1. Ordenam-se os 25 p-valores brutos em ordem não-decrescente: $p_{(1)} \le p_{(2)} \le \dots \le p_{(25)}$;
2. Compara-se cada $p_{(i)}$ sucessivamente com o limiar ajustado $\frac{\alpha}{25 - i + 1}$;
3. Interrompe-se a rejeição no primeiro índice que violar o critério. O método de Holm é estritamente mais poderoso que a correção de Bonferroni tradicional sem comprometer o controle estrito da FWER a 5%.

### 3.4. Magnitude dos Efeitos (Effect Size)
* **Epsilon ao Quadrado ($\epsilon^2$) para Kruskal-Wallis:**
  $$\epsilon^2 = \frac{H}{n - 1}$$
  Indica a proporção da variabilidade dos postos explicada pelo fator. Varia no intervalo $[0, 1]$. Faixas de interpretação (Tomczak & Tomczak, 2014):
  * $\epsilon^2 < 0.01$: Desprezível
  * $0.01 \le \epsilon^2 < 0.06$: Pequeno
  * $0.06 \le \epsilon^2 < 0.14$: Médio
  * $\epsilon^2 \ge 0.14$: Grande

* **Cliff's Delta ($\delta$) para Contrastes Par a Par:**
  $$\delta = \frac{2 \cdot U_1}{n_A \cdot n_B} - 1$$
  Mede o grau de dominância não-paramétrica entre dois subgrupos específicos. Faixas de interpretação (Romano et al., 2006): $|\delta| < 0.147$ (desprezível), $< 0.330$ (pequeno), $< 0.474$ (médio), $\ge 0.474$ (grande).

---

## 4. Padrões de Visualização Gráfica

As figuras são geradas e exportadas duplamente em `lab03/data/figuras/`:
1. **`rq05_dispersao_df_vs_cfr.png` (300 DPI) e `.pdf` (Vetorial):**
   * Painel duplo lado a lado ($1 \times 2$) com escala logarítmica no eixo X;
   * Curva de suavização local **LOWESS** destacando a trajetória da tendência;
   * Caixa estatística com $\rho$, $p$-valor, intervalo de confiança bootstrap e $N$.
2. **`rq06_distribuicao_subgrupos.png` e `.pdf`:**
   * Grid $2 \times 2$ apresentando boxplots combinados com camada de pontos dispersos (*stripplot jitter*);
   * Escala logarítmica para métricas temporais (Lead Time e Recovery Time);
   * Subtítulos anotados com $\epsilon^2$, magnitude e $p_{\text{adj}}$ pós-Holm.
3. **`rq06_heatmap_effect_size.png` e `.pdf`:**
   * Matriz visual relacionando Fatores $\times$ Métricas DORA;
   * Células contendo o valor numérico de $\epsilon^2$ e marcadores de significância:
     `***` ($p_{\text{adj}} < 0.001$), `**` ($p_{\text{adj}} < 0.01$), `*` ($p_{\text{adj}} < 0.05$), `ns` (não significativo).
