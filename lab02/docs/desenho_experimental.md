# Documento de Desenho Experimental: Impacto de Assistentes de IA na Codificação

**Disciplina:** Laboratório de Experimentação de Software  
**Curso:** Engenharia de Software — 6º Período  
**Professor:** Danilo Maia  
**Artefato:** Sprint 01 — Issue #01: Desenho Experimental, Formalização de Hipóteses e Ameaças à Validade  
**Status:** Pronto para Publicação / Aprovado  

---

## Sumário Executivo

Este documento estabelece o protocolo metodológico e experimental da pesquisa empírica conduzida pelo grupo para avaliar quantitativamente os efeitos do uso de ferramentas de Inteligência Artificial Generativa no processo de desenvolvimento e resolução de tarefas de programação (*katas*). O estudo adota as diretrizes clássicas de Engenharia de Software Experimental (Wohlin et al., 2012; Basili et al., 1994; Juristo & Moreno, 2001), empregando o paradigma GQM (*Goal-Question-Metric*), delineamento *within-subject* (crossover contrabalanceado), controle de variáveis de confusão, censura estatística de dados à direita e análise inferencial não-paramétrica pareada.

---

## 1. Objetivo da Pesquisa (Abordagem GQM — Goal Question Metric)

A formulação do objetivo do experimento orienta-se pelo framework GQM (*Goal-Question-Metric*), estabelecido por Basili & Rombach (1988), garantindo o alinhamento estrito entre a meta científica global, as questões de investigação empírica e as medidas quantitativas coletadas.

### 1.1. Definição do Objetivo (Goal)

A meta experimental do estudo é formalizada conforme o template estruturado de Basili:

> **Analisar** o uso de assistentes de inteligência artificial generativa na resolução de tarefas de programação,  
> **com o propósito de** comparar o seu efeito frente à prática de codificação estritamente manual,  
> **com respeito a** produtividade temporal (*time-to-green*), qualidade funcional (taxa de aprovação nos testes de aceitação e defeitos) e qualidade estrutural do código-fonte (complexidade ciclomática e linhas de código),  
> **do ponto de vista** dos engenheiros de software e pesquisadores empíricos,  
> **no contexto de** *katas* de programação de complexidade equivalente, implementados por estudantes de graduação em Engenharia de Software sob regime controlado de *crossover within-subject* e limites rígidos de tempo (*time-boxed*).

---

### 1.2. Questões de Pesquisa e Métricas Quantitativas (Questions & Metrics)

A partir da meta definida, derivam-se três Questões de Pesquisa (Research Questions — RQs) e suas respectivas métricas operacionais:

```
                  ┌────────────────────────────────────────────────────────┐
                  │                          GOAL                          │
                  │   Avaliar impacto de IA vs. Manual em Katas de Código  │
                  └──────────────────────────┬─────────────────────────────┘
                                             │
         ┌───────────────────────────────────┼───────────────────────────────────┐
         ▼                                   ▼                                   ▼
  ┌──────────────┐                    ┌──────────────┐                    ┌──────────────┐
  │     RQ1      │                    │     RQ2      │                    │     RQ3      │
  │ Produtividade│                    │  Qualidade   │                    │  Qualidade   │
  │   Temporal   │                    │  Funcional   │                    │  Estrutural  │
  └──────┬───────┘                    └──────┬───────┘                    └──────┬───────┘
         │                                   │                                   │
  ┌──────┴───────┐                    ┌──────┴───────┐                    ┌──────┴───────┐
  │• Time-to-    │                    │• Taxa de     │                    │• Complexidade│
  │  green (min) │                    │  Sucesso (%) │                    │  McCabe v(G) │
  │• Censura     │                    │• Testes      │                    │• SLOC / LOC  │
  │  (35 min)    │                    │  Falhando    │                    │• Duplicação% │
  │• Nº Prompts  │                    │• Densidade   │                    │• Índice      │
  │  (explorat.) │                    │  Defeitos    │                    │  Manutenib.  │
  └──────────────┘                    └──────────────┘                    └──────────────┘
```

#### RQ1: Produtividade e Eficiência Temporal
* **Pergunta de Pesquisa:** *O uso de assistente de IA reduz o tempo necessário para resolver uma tarefa de programação até a validação funcional completa?*
* **Métrica Primária — Time-to-Green ($T_{TTG}$):** Tempo cronometrado decorrido, expresso em minutos decimais ($t \in \mathbb{R}^+$), desde a leitura do enunciado e abertura do ambiente até o exato instante em que 100% da suíte de testes de aceitação automatizados passa com sucesso (`exit code 0`).
* **Regra de Censura de Dados ($C_{trial}$):** Indicador binário de censura à direita:
  $$\delta_i = \begin{cases} 0, & \text{se a suíte completa passou com } T_{TTG} < 35.0 \text{ min} \\ 1, & \text{se atingiu o time-box (35.0 min) sem aprovação total} \end{cases}$$
* **Métrica Agregada Central:** Mediana ($\tilde{M}$) e Intervalo Interquartil ($IQR = Q_3 - Q_1$), tendo em vista que distribuições de tempo com censura violam a simetria gaussiana.
* **Métrica Exploratória Complementar:** Frequência de Prompts e Interações ($N_{prompts}$), contabilizando o número total de prompts submetidos ao assistente de IA durante o trial.

#### RQ2: Eficácia e Qualidade Funcional (Defeitos)
* **Pergunta de Pesquisa:** *O uso de assistente de IA reduz a quantidade de defeitos residuais e eleva a taxa de sucesso nos testes automatizados ao término do tempo limite?*
* **Métrica Primária — Taxa de Sucesso dos Testes de Aceitação ($SR_{test}$):** Percentual normalizado de casos de testes de aceitação que obtiveram resultado satisfatório ao término do trial:
  $$SR_{test} = \left( \frac{N_{pass}}{N_{total}} \right) \times 100\%$$
  onde $N_{total}$ é o total de asserções da suíte de testes do kata e $N_{pass}$ é o número de testes com resultado positivo.
* **Métrica Secundária — Contagem Absoluta de Testes com Falha ($N_{fail}$):**
  $$N_{fail} = N_{total} - N_{pass}$$
* **Métrica Opcional de Aprofundamento — Densidade de Defeitos ($FD$):**
  $$FD = \frac{N_{fail}}{LOC / 1000} \quad (\text{Defeitos por KLOC})$$

#### RQ3: Qualidade Estrutural e Arquitetura do Código
* **Pergunta de Pesquisa:** *O uso de assistente de IA altera a complexidade ciclomática, o volume de código ou a manutenibilidade da solução gerada?*
* **Métrica Primária — Complexidade Ciclomática de McCabe ($v(G)$):** Métrica extraída via análise estática (Radon para Python ou CK para Java), quantificando os caminhos linearmente independentes no grafo de fluxo de controle por método/função:
  $$v(G) = E - N + 2P$$
  onde $E$ é o número de arestas, $N$ o número de nós e $P$ o número de componentes conexos. Reporta-se a média por método ($\overline{CC}$) e a complexidade ponderada total ($WMC$).
* **Métrica Obrigatória de Normalização e Controle — Linhas de Código-Fonte ($LOC / SLOC$):** Contagem de linhas efetivas de código executável (*Source Lines of Code*), desconsiderando linhas em branco e comentários puros. Imprescindível para contextualizar se a IA gera código excessivamente prolixo ou conciso.
* **Métrica Complementar 1 — Taxa de Duplicação de Código ($\% Dup$):** Percentual de linhas de código duplicadas identificadas via ferramenta estática (ex.: PMD CPD ou jscpd).
* **Métrica Complementar 2 — Índice de Manutenibilidade ($MI$):** Métrica composta calculada por ferramentas como Radon, integrando Complexidade de McCabe, Volume de Halstead e $LOC$:
  $$MI = \max\left(0, \frac{171 - 5.2 \ln(V) - 0.23 \cdot v(G) - 16.2 \ln(LOC)}{171} \times 100\right)$$

---

### 1.3. Quadro Síntese GQM

| Dimensão | Questão (Question) | Métrica Operacional (Metric) | Tipo de Dado | Ferramenta / Coleta |
| :--- | :--- | :--- | :--- | :--- |
| **Tempo / Produtividade** | **RQ1** | Time-to-green ($T_{TTG}$) | Razão contínua ($[0, 35]$ min) | Cronômetro do Trial / Runner de Testes |
| | | Status de Censura ($\delta$) | Binário ($\{0, 1\}$) | Registro de log operacional |
| | | Frequência de Prompts ($N_{prompts}$) | Discreta ($\mathbb{N}$) | Log de interações com o assistente |
| **Qualidade Funcional** | **RQ2** | Taxa de Sucesso nos Testes ($SR_{test}$) | Razão contínua ($[0, 100]\%$) | Framework de Testes (`pytest` / `JUnit`) |
| | | Testes Falhando ($N_{fail}$) | Discreta ($\mathbb{N}$) | Framework de Testes |
| | | Densidade de Defeitos ($FD$) | Razão contínua | $N_{fail} / (LOC / 1000)$ |
| **Qualidade Estrutural** | **RQ3** | Complexidade Ciclomática ($v(G)$) | Razão discreta ($\ge 1$) | Análise Estática (Radon / CK) |
| | | Linhas de Código ($SLOC$) | Discreta ($\mathbb{N}^+$) | Análise Estática (Radon / CK / cloc) |
| | | Taxa de Duplicação ($\% Dup$) | Razão contínua ($[0, 100]\%$) | PMD CPD / jscpd |
| | | Índice de Manutenibilidade ($MI$) | Razão contínua ($[0, 100]$) | Radon ($MI$) |

---

## 2. Formalização das Hipóteses Estatísticas

A formulação das hipóteses estatísticas apoia-se em testes não-paramétricos pareados para amostras dependentes, considerando o delineamento *within-subject*. Denomina-se o Tratamento Manual como $A$ (Controle) e o Tratamento Assistido por IA como $B$ (Experimental). As hipóteses avaliam as medianas populacionais $\tilde{M}_A$ e $\tilde{M}_B$, ou equivalentemente a probabilidade de dominância estocástica nas diferenças pareadas $D_i = X_{B, i} - X_{A, i}$.

### 2.1. Hipóteses para RQ1 (Produtividade e Time-to-green)

A literatura e os relatos anedóticos sugerem que assistentes de IA aceleram a escrita de código por meio de autocompletar semântico e síntese automática de blocos lógicos. Portanto, adota-se um **teste unilateral à esquerda** (*one-tailed, lower-tail*):

* **Hipótese Nula ($H_{0,1}$):**
  * *Texto:* O uso de assistente de IA não reduz o tempo necessário para resolver a tarefa de programação até a aprovação total nos testes em comparação ao desenvolvimento manual; o tempo com IA é igual ou estatisticamente superior ao tempo manual.
  * *Formulação Matemática:*
    $$H_{0,1}: \tilde{M}_{B, tempo} \ge \tilde{M}_{A, tempo} \iff P(T_B < T_A) \le 0.5$$

* **Hipótese Alternativa ($H_{1,1}$):**
  * *Texto:* O uso de assistente de IA reduz significativamente o tempo necessário para resolver a tarefa de programação até a aprovação total nos testes em relação ao desenvolvimento manual.
  * *Formulação Matemática:*
    $$H_{1,1}: \tilde{M}_{B, tempo} < \tilde{M}_{A, tempo} \iff P(T_B < T_A) > 0.5$$

---

### 2.2. Hipóteses para RQ2 (Qualidade Funcional e Taxa de Sucesso nos Testes)

Avalia-se se a capacidade do assistente de IA de sugerir código sintaticamente funcional se traduz em menor incidência de bugs de lógica e maior aderência aos testes unitários sob pressão de tempo. Adota-se um **teste unilateral à direita** (*one-tailed, upper-tail*):

* **Hipótese Nula ($H_{0,2}$):**
  * *Texto:* O uso de assistente de IA não eleva a taxa de sucesso nos testes de aceitação ao final do time-box em relação à codificação manual; a taxa de sucesso com IA é igual ou estatisticamente inferior à taxa manual.
  * *Formulação Matemática:*
    $$H_{0,2}: \tilde{M}_{B, SR} \le \tilde{M}_{A, SR} \iff P(SR_B > SR_A) \le 0.5$$

* **Hipótese Alternativa ($H_{1,2}$):**
  * *Texto:* O uso de assistente de IA produz uma taxa de sucesso nos testes de aceitação significativamente superior à obtida via codificação manual.
  * *Formulação Matemática:*
    $$H_{1,2}: \tilde{M}_{B, SR} > \tilde{M}_{A, SR} \iff P(SR_B > SR_A) > 0.5$$

---

### 2.3. Hipóteses para RQ3 (Qualidade Estrutural: Complexidade Ciclomática e LOC)

Ao gerar código, modelos LLM podem tanto produzir estruturas idiomáticas simplificadas quanto blocos defensivos redundantes, árvores de decisão aninhadas profundas e trechos prolixos (*hallucinated boilerplate*). Como a direção da variação não é consensual na literatura experimental, adota-se para a RQ3 um **teste bilateral** (*two-tailed*), desdobrado em duas sub-hipóteses:

#### 2.3.1. Complexidade Ciclomática ($v(G)$)
* **Hipótese Nula ($H_{0,3a}$):**
  * *Texto:* Não há diferença estatisticamente significativa na complexidade ciclomática média por método do código gerado com assistência de IA em relação ao código produzido manualmente.
  * *Formulação Matemática:*
    $$H_{0,3a}: \tilde{M}_{B, CC} = \tilde{M}_{A, CC} \iff P(CC_B > CC_A) = 0.5$$

* **Hipótese Alternativa ($H_{1,3a}$):**
  * *Texto:* Há diferença estatisticamente significativa na complexidade ciclomática média do código gerado com assistência de IA em comparação ao desenvolvimento manual.
  * *Formulação Matemática:*
    $$H_{1,3a}: \tilde{M}_{B, CC} \ne \tilde{M}_{A, CC} \iff P(CC_B > CC_A) \ne 0.5$$

#### 2.3.2. Volume de Código-Fonte ($LOC$)
* **Hipótese Nula ($H_{0,3b}$):**
  * *Texto:* Não há diferença estatisticamente significativa no número de linhas de código ($LOC$) produzidas entre o desenvolvimento assistido por IA e a codificação manual.
  * *Formulação Matemática:*
    $$H_{0,3b}: \tilde{M}_{B, LOC} = \tilde{M}_{A, LOC} \iff P(LOC_B > LOC_A) = 0.5$$

* **Hipótese Alternativa ($H_{1,3b}$):**
  * *Texto:* Há diferença estatisticamente significativa no volume de linhas de código ($LOC$) resultante do uso de assistente de IA frente à codificação manual.
  * *Formulação Matemática:*
    $$H_{1,3b}: \tilde{M}_{B, LOC} \ne \tilde{M}_{A, LOC} \iff P(LOC_B > LOC_A) \ne 0.5$$

---

### 2.4. Resumo das Hipóteses Estatísticas

| Questão | Parâmetro Avaliado | Hipótese Nula ($H_0$) | Hipótese Alternativa ($H_1$) | Cauda do Teste |
| :--- | :--- | :--- | :--- | :--- |
| **RQ1** | Time-to-green ($T_{TTG}$) | $\tilde{M}_{B} \ge \tilde{M}_{A}$ | $\tilde{M}_{B} < \tilde{M}_{A}$ | Unilateral Esquerda |
| **RQ2** | Taxa de Sucesso ($SR_{test}$) | $\tilde{M}_{B} \le \tilde{M}_{A}$ | $\tilde{M}_{B} > \tilde{M}_{A}$ | Unilateral Direita |
| **RQ3a** | Complexidade Ciclomática ($CC$) | $\tilde{M}_{B} = \tilde{M}_{A}$ | $\tilde{M}_{B} \ne \tilde{M}_{A}$ | Bilateral |
| **RQ3b** | Linhas de Código ($LOC$) | $\tilde{M}_{B} = \tilde{M}_{A}$ | $\tilde{M}_{B} \ne \tilde{M}_{A}$ | Bilateral |

---

## 3. Desenho Experimental (Design & Protocolo de Trial)

### 3.1. Arquitetura Experimental: Crossover Within-Subject Contrabalanceado

Para garantir elevado rigor científico com uma amostra compacta de desenvolvedores, o experimento adota o delineamento **Within-Subject** (emparelhado por sujeito) com arranjo **Crossover Contrabalanceado** (*Cross-Over Balanced Design*).

```
   RODÍZIO EXPERIMENTAL CONTRABALANCEADO (CROSSOVER DESIGN)
   
                  RODADA 1                 RODADA 2
           ┌──────────────────────┐ ┌──────────────────────┐
   Suj. 1: │   KATA 1 — SEM IA    │ │   KATA 2 — COM IA    │ ... (50% Manual / 50% IA)
           └──────────────────────┘ └──────────────────────┘
           ┌──────────────────────┐ ┌──────────────────────┐
   Suj. 2: │   KATA 1 — COM IA    │ │   KATA 2 — SEM IA    │ ... (50% Manual / 50% IA)
           └──────────────────────┘ └──────────────────────┘
           ┌──────────────────────┐ ┌──────────────────────┐
   Suj. 3: │   KATA 2 — SEM IA    │ │   KATA 1 — COM IA    │ ... (50% Manual / 50% IA)
           └──────────────────────┘ └──────────────────────┘
```

#### 3.1.1. Justificativa Teórica do Modelo Within-Subject
Em experimentos de Engenharia de Software, a variabilidade individual de produtividade entre programadores pode atingir fatores de $10\times$ a $20\times$ (Sackman et al., 1968; Kitchenham et al., 2002; Wohlin et al., 2012). Um delineamento *between-subjects* (onde um grupo só programa com IA e outro só programa sem IA) exigiria dezenas de sujeitos aleatorizados para neutralizar esse ruído de habilidade basal. No delineamento *within-subject*, cada participante atua como seu próprio bloco de controle: a comparação estatística é realizada sobre a diferença pareada intra-sujeito ($X_{B, i} - X_{A, i}$), expurgando a variância decorrente de diferenças de habilidade prévia.

#### 3.1.2. Contrabalanceamento e Prevenção de Carryover Effect
A repetição de tarefas acarreta riscos de **efeito de aprendizado** (*learning effect*) e **efeito de fadiga** (*fatigue effect*). Se um desenvolvedor resolver a mesma kata no Tratamento A e depois no Tratamento B, a memorização da lógica do problema corromperá a medição do segundo trial. Para neutralizar esses vícios:
1. **Regra de Não-Repetição de Objeto:** Nenhum participante resolve a mesma kata duas vezes.
2. **Equiparação por Paridade de Tarefas:** Cada integrante executa rigorosamente metade dos trials sob o Tratamento A e a outra metade sob o Tratamento B ($50\% / 50\%$).
3. **Alternância Cruzada de Ordem:** A ordem de exposição (começar com IA vs. começar Manual) é invertida simetricamente entre os participantes para neutralizar viés temporal sistemático.

#### 3.1.3. Matriz Operacional de Execução dos Trials
Considerando a equipe de três pesquisadores ($P_1, P_2, P_3$) e um conjunto balanceado de 4 katas de nível de dificuldade equivalente ($K_1, K_2, K_3, K_4$):

| Participante | Ordem Trial 1 | Ordem Trial 2 | Ordem Trial 3 | Ordem Trial 4 | Total Trials | Proporção A / B |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **$P_1$ (Dev 1)** | $K_1$ — **Trat. A** (Manual) | $K_2$ — **Trat. B** (Com IA) | $K_3$ — **Trat. A** (Manual) | $K_4$ — **Trat. B** (Com IA) | 4 trials | 2 Manual / 2 IA |
| **$P_2$ (Dev 2)** | $K_1$ — **Trat. B** (Com IA) | $K_2$ — **Trat. A** (Manual) | $K_4$ — **Trat. A** (Manual) | $K_3$ — **Trat. B** (Com IA) | 4 trials | 2 Manual / 2 IA |
| **$P_3$ (Dev 3)** | $K_2$ — **Trat. B** (Com IA) | $K_1$ — **Trat. A** (Manual) | $K_4$ — **Trat. B** (Com IA) | $K_3$ — **Trat. A** (Manual) | 4 trials | 2 Manual / 2 IA |
| **Total Global** | 2 Manual / 1 IA | 1 Manual / 2 IA | 2 Manual / 1 IA | 1 Manual / 2 IA | **12 trials** | **6 Manual / 6 IA** |

*Nota metodológica:* Se o grupo expandir o experimento para 6 katas ($K_1$ a $K_6$), a matriz é estendida preservando a paridade exata de 3 trials Manuais e 3 trials com IA por participante (totalizando 18 trials).

---

### 3.2. Detalhamento das Condições Experimentais

#### 3.2.1. Tratamento A: Codificação Manual (Baseline / Controle)
* **Definição:** Resolução da kata dependendo unicamente do raciocínio cognitivo autônomo do desenvolvedor.
* **Ferramentas Autorizadas:**
  * IDE padrão (VS Code com todas as extensões de IA generativa estritamente desabilitadas/desinstaladas);
  * Compilador / Interpretador oficial da linguagem;
  * Test runner local (`pytest` ou `JUnit`);
  * Documentação oficial da linguagem offline ou navegação estrita na documentação canônica (ex.: `docs.python.org`, MDN) exclusivamente para consulta de sintaxe.
* **Proibições Estritas:**
  * Proibição de uso de assistentes inline (GitHub Copilot, Cursor, Codeium, Tabnine);
  * Proibição de chatbots generativos em navegador (ChatGPT, Claude, Gemini, DeepSeek);
  * Proibição de consulta a fóruns de perguntas e respostas com soluções prontas (Stack Overflow, fóruns do LeetCode).

#### 3.2.2. Tratamento B: Codificação Assistida por IA (Experimental)
* **Definição:** Resolução da kata com auxílio explícito de assistente de IA generativa.
* **Ferramentas Autorizadas:**
  * Todas as ferramentas básicas do Tratamento A;
  * Assistente de IA padronizado (ex.: GitHub Copilot na IDE ou chatbot web acordado pelo trio), mantendo a versão e parâmetros do modelo congelados durante todo o experimento.
* **Protocolo de Interação com a IA:**
  * O participante tem liberdade de solicitar autocompletar de código, síntese completa de funções, geração de blocos de lógica ou depuração assistida a partir das falhas nos testes;
  * É obrigatório arquivar os prompts submetidos e as respostas geradas para auditoria no log do trial.

---

### 3.3. Regras Operacionais dos Trials

1. **Time-Box Rígido de 35 Minutos:**
   * Cada trial possui um limite absoluto de tempo de 35 minutos ($2100$ segundos).
   * O cronômetro é deflagrado no instante em que o participante abre o arquivo do kata e lê a especificação.
   * Caso os testes de aceitação passem com sucesso antes dos 35 minutos, o cronômetro é imediatamente interrompido e registra-se o $T_{TTG}$ exato.
   * Se o limite de 35 minutos for atingido sem a aprovação completa da suíte de testes, a execução é interrompida compulsoriamente pelo observador/cronometrista, independentemente do progresso.

2. **Estratégia de Censura de Dados (Data Censoring):**
   * **Princípio Metodológico:** Em análise de sobrevivência e tempo de evento (*time-to-event data*), trials que não concluem com sucesso dentro da janela temporal são classificados como **dados censurados à direita** (*right-censored*).
   * **Política contra Survivorship Bias (Viés de Sobrevivência):** É expressamente vedado descartar trials não concluídos. Descartar tarefas não finalizadas inflaria artificialmente a performance média, premiando tratamentos que levaram ao abandono precoce de problemas difíceis.
   * **Atribuição Numérica Padronizada:** Para os trials censurados, a variável $T_{TTG}$ é registrada como $35.0$ minutos e a flag de censura é marcada como $\delta_i = 1$. Na análise de medianas e no teste de Wilcoxon, o valor 35.0 atua como o pior ranqueamento temporal possível.

3. **Política de Registro de Logs, Versionamento e Rastreabilidade:**
   * **Git Workflow:** Cada trial é executado em uma branch dedicada ou pasta isolada.
     * *Commit 0 (Setup):* Commit do enunciado e da suíte de testes inalterada.
     * *Commit 1 (Final):* Código final obtido no término do trial (seja por sucesso ou por esgotamento do time-box).
   * **Rastreabilidade com GitHub Projects:** Cada trial corresponde a uma Issue específica no Kanban do projeto (rotulada `trial/P{id}/K{id}/Trat-{A|B}`), atribuída ao respectivo Assignee. Mensagens de commit devem referenciar obrigatoriamente a Issue (ex.: `feat(trial): conclude Kata 02 with Copilot closes #12`).
   * **Tabela de Log de Execução:** Imediatamente após o encerramento, o participante preenche a ficha do trial contendo:
     * ID do Sujeito, ID da Kata, Tratamento (A ou B);
     * Horário de início e término;
     * $T_{TTG}$ apurado (ou flag de censura se atingiu 35 min);
     * Saída do runner de testes (total de testes, testes aprovados, testes falhos);
     * Lista de prompts submetidos à IA (se Tratamento B);
     * Métricas estáticas extraídas via script automatizado.

---

## 4. Mapeamento de Variáveis

O isolamento do efeito causal e a consistência interna da pesquisa dependem da categorização formal e do controle rígido das variáveis intervenientes.

```
┌─────────────────────────────────┐
│     VARIÁVEL INDEPENDENTE       │
│  Presença do Assistente de IA   │
│  (Nível 0: Sem IA | 1: Com IA)  │
└────────────────┬────────────────┘
                 │
                 │  Aplica efeito causal controlado
                 ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         VARIÁVEIS DEPENDENTES                          │
│  • Tempo até aprovação completa (Time-to-green - T_TTG)                │
│  • Taxa de sucesso nos testes funcionais (SR_test %)                   │
│  • Defeitos residuais ao término do tempo (N_fail)                     │
│  • Complexidade ciclomática de McCabe (v(G))                           │
│  • Linhas de código-fonte executável (SLOC)                            │
└────────────────────────────────┬───────────────────────────────────────┘
                                 ▲
                                 │  Isoladas e mantidas invariantes por
┌────────────────────────────────┴───────────────────────────────────────┐
│                         VARIÁVEIS DE CONTROLE                          │
│  • Ambiente de execução (IDE fixa, mesma versão de compilador/runtime) │
│  • Suíte de testes de aceitação automatizada fixa e fechada            │
│  • Nível de complexidade algorítmica e baixa indexação dos Katas       │
│  • Formação técnica e senioridade basal homogênea dos participantes   │
│  • Time-box teto universal de 35 minutos                               │
└────────────────────────────────────────────────────────────────────────┘
```

### 4.1. Variável Independente (Fator Experimental)
* **Identificação:** Auxílio de Ferramenta de IA Generativa.
* **Natureza:** Qualitativa Nominal / Dicotômica.
* **Níveis de Tratamento:**
  * **Nível 0 ($T_A$):** Ausente (Desenvolvimento Manual Tradicional);
  * **Nível 1 ($T_B$):** Presente (Desenvolvimento Assistido por Assistente de IA padronizado).

---

### 4.2. Variáveis Dependentes (Métricas de Resposta)

| Variável | Símbolo | Escala de Medida | Unidade | Descrição Operacional |
| :--- | :---: | :--- | :---: | :--- |
| **Time-to-Green** | $T_{TTG}$ | Razão contínua (com censura à direita em 35.0) | Minutos decimais | Duração cronometrada até 100% de sucesso na suíte de testes. |
| **Taxa de Sucesso dos Testes** | $SR_{test}$ | Razão contínua | Percentual ($[0, 100]\%$) | Proporção de casos de teste de aceitação aprovados ao final do trial. |
| **Contagem de Falhas** | $N_{fail}$ | Discreta | Unidades ($\mathbb{N}$) | Número absoluto de asserções/testes que falharam ao término do time-box. |
| **Complexidade Ciclomática** | $v(G)$ | Discreta / Razão | Inteiro ($\ge 1$) | Média da métrica de McCabe por método/função calculada via Radon/CK. |
| **Tamanho do Código** | $SLOC$ | Discreta / Razão | Linhas de código | Total de linhas de código efetivo (excluindo comentários e espaços vazios). |
| **Índice de Manutenibilidade** | $MI$ | Razão contínua | Pontos ($[0, 100]$) | Escore composto de manutenibilidade calculado pelo Radon. |

---

### 4.3. Variáveis de Controle e Mecanismos de Neutralização

Para assegurar que as alterações observadas nas variáveis dependentes decorram unicamente da manipulação da variável independente, estabelecem-se os seguintes controles:

1. **Ambiente Tecnológico e Toolchain Fixos:**
   * Todos os participantes operam sob o mesmo ambiente de linguagem de programação (ex.: Python 3.11+ ou Java 17+ LTS);
   * Editor padronizado (VS Code com configurações uniformizadas de linting e formatador);
   * Runner de testes automatizado idêntico (`pytest` em modo verbose com logs estruturados).

2. **Invariância da Suíte de Testes de Aceitação:**
   * O código dos testes unitários é fechado e imutável. O desenvolvedor sob teste não tem autorização para modificar, comentar ou contornar as asserções da suíte.

3. **Homogeneidade e Calibração dos Katas:**
   * O conjunto de katas selecionados possui complexidade algorítmica intencionalmente calibrada no mesmo nível de esforço (tempo estimado de resolução manual entre 20 e 30 minutos);
   * Seleção focada em katas com baixa indexação na web para mitigar o viés de memorização (*data contamination*) da IA.

4. **Homogeneidade da População Amostral:**
   * Os participantes são estudantes do mesmo período letivo (6º período) do curso de Engenharia de Software, com histórico curricular idêntico nas disciplinas de algoritmos, estruturas de dados e paradigmas de programação.

---

## 5. Ameaças à Validade e Estratégias de Mitigação

Conforme a taxonomia fundamental de Cook & Campbell (1979) e sua sistematização em Engenharia de Software por Wohlin et al. (2012), identificam-se as ameaças à validade e os protocolos formais de mitigação adotados neste experimento:

### 5.1. Validade Interna (Internal Validity)
A validade interna avalia se a relação observada entre a introdução da IA e os efeitos nas métricas dependentes é genuinamente causal, livre de fatores de confusão não controlados.

* **Ameaça 1: Efeito de Aprendizado (Learning / History Effect):**
  * *Risco:* A execução sequencial de katas semelhantes pode aumentar a proficiência do desenvolvedor ao longo das rodadas, fazendo com que trials posteriores apresentem melhor desempenho independentemente da presença de IA.
  * *Mitigação:* Adoção rigorosa do **delineamento crossover contrabalanceado**. Nenhum participante repete o mesmo kata em tratamentos diferentes, e a ordem de início (Manual primeiro vs. IA primeiro) é alternada simetricamente entre os participantes da equipe.
* **Ameaça 2: Efeito de Fadiga (Fatigue Effect):**
  * *Risco:* A resolução consecutiva de múltiplos problemas de programação de 35 minutos sob pressão de cronômetro induz exaustão cognitiva, deteriorando a velocidade e a qualidade do código nos últimos trials.
  * *Mitigação:* Limitação de no máximo 2 trials por dia por participante, com intervalo de repouso obrigatório de no mínimo 30 minutos entre execuções consecutivas.
* **Ameaça 3: Contaminação e Memorização dos Modelos de IA (Data Leakage / Memorization):**
  * *Risco:* Se os katas forem exercícios clássicos de plataformas de desafio (como o *Two Sum* do LeetCode ou *FizzBuzz*), os modelos de IA podem ter memorizado a solução exata em seu corpus de treinamento. Nesses casos, a IA atua como um sistema de recuperação de dados memorizados (*lookup*) e não como um assistente cognitivo em tempo real.
  * *Mitigação:* Adaptação das assinaturas, nomes de variáveis, contexto do domínio do problema e regras de negócio das katas, ou escolha de katas pouco populares/autorais, evitando exercícios do top-ranking público do LeetCode e HackerRank.
* **Ameaça 4: Comunicação Não Autorizada entre Sujeitos:**
  * *Risco:* Troca de insights ou compartilhamento de soluções entre os integrantes do trio antes da conclusão de todos os trials.
  * *Mitigação:* Execução assíncrona ou em sessões individuais com branches isoladas no Git, com embargo de discussão técnica sobre os katas até que todos os 12 trials estejam integralmente commitados e auditados.

---

### 5.2. Validade Externa (External Validity)
A validade externa diz respeito à capacidade de generalização dos achados empíricos para cenários industriais e populações mais amplas de engenheiros de software.

* **Ameaça 1: Representatividade das Tarefas (*Toy Problems* vs. Sistemas Industriais):**
  * *Risco:* Katas são programas autocontidos, de arquivo único e lógica isolada. O desenvolvimento industrial real envolve arquiteturas distribuídas, bases de código legadas de milhões de linhas, dependências externas complexas e requisitos ambíguos.
  * *Mitigação:* Reconhecimento explícito das limitações de escopo no relatório. Os katas são desenhados para capturar a etapa de codificação algorítmica pura e unitária, sendo as conclusões restritas a essa fase do ciclo de desenvolvimento.
* **Ameaça 2: Perfil dos Desenvolvedores (Estudantes vs. Engenheiros Sêniores):**
  * *Risco:* Estudantes de graduação podem interagir com a IA de forma diferente de desenvolvedores sêniores (ex.: aceitando sugestões de forma acrítica sem validação mental prévia).
  * *Mitigação:* Alinhamento metodológico com a literatura (Feldt et al., 2018; Runeson et al., 2003), que valida o uso de estudantes de fases avançadas como representantes adequados de desenvolvedores em nível de entrada (*junior software engineers*), mantendo a caracterização populacional transparente.

---

### 5.3. Validade de Construção (Construct Validity)
A validade de construção reflete se as variáveis e métricas quantitativas operacionalizadas medem com fidelidade os conceitos teóricos abstratos pretendidos (produtividade, qualidade funcional e qualidade estrutural).

* **Ameaça 1: Time-to-green como Proxy de Produtividade:**
  * *Risco:* O tempo até todos os testes passarem pode ignorar o tempo despendido na leitura do enunciado ou encobrir débitos técnicos deixados no código que penalizariam o ciclo de vida futuro do software.
  * *Mitigação:* O time-box é acoplado obrigatoriamente a métricas estáticas de qualidade pós-execução (RQ3) e ao rigor dos testes de aceitação (RQ2). Assim, "produtividade" não é computada apenas pela velocidade, mas pela entrega de software simultaneamente correto e avaliado estaticamente.
* **Ameaça 2: Limitações da Complexidade Ciclomática de McCabe:**
  * *Risco:* A complexidade ciclomática ($v(G)$) afere apenas bifurcações do fluxo de controle linear (estruturas condicionais e laços), não capturando acoplamento eferente, coesão conceitual ou clareza semântica de nomenclatura gerada pela IA.
  * *Mitigação:* Triangulação métrica integrando $v(G)$, $SLOC$ e o Índice de Manutenibilidade ($MI$), assegurando que variações em $v(G)$ sejam interpretadas em conjunto com o tamanho e a densidade das funções.

---

### 5.4. Validade de Conclusão Estatística (Statistical Conclusion Validity)
Refere-se à solidez das inferências estatísticas formuladas, assegurando que o relacionamento detectado seja matematicamente confiável e não fruto de violações de premissas teóricas ou ruído amostral.

* **Ameaça 1: Tamanho Amostral Reduzido ($N$ pequeno) e Não-Normalidade:**
  * *Risco:* Com 12 trials no total (6 por tratamento), o teorema central do limite não assegura a normalidade das distribuições amostrais. A aplicação indevida de testes paramétricos (como o Teste t de Student pareado) acarretaria erro de tipo I ou perda substancial de poder estatístico.
  * *Mitigação:* Emprego do **Teste de Postos com Sinais de Wilcoxon** (*Wilcoxon Signed-Rank Test*), teste não-paramétrico específico para dados pareados que não requer normalidade ou variâncias homogêneas. A análise descritiva reportará estritamente medianas e $IQR$ ao invés de médias e desvios-padrão.
* **Ameaça 2: Distorção por Survivorship Bias em Dados Censurados:**
  * *Risco:* Trials não concluídos que atinjam o limite de 35 minutos poderiam ser incorretamente expurgados da amostra ou tratados como dados faltantes (*missing values*), falseando as comparações.
  * *Mitigação:* Aplicação formal da censura à direita: o tempo é fixado em 35.0 minutos, o que penaliza o tratamento no ranking de Wilcoxon de forma consistente com a realidade operacional da falha de entrega dentro do prazo.
* **Ameaça 3: Ausência de Quantificação do Tamanho do Efeito (*Effect Size*):**
  * *Risco:* Aferir unicamente o p-valor pode superestimar relevâncias sem significado prático ou subestimar tendências expressivas em amostras pequenas.
  * *Mitigação:* Cálculo do tamanho de efeito não-paramétrico através do coeficiente $r$ de Rosenthal para testes de Wilcoxon:
    $$r = \frac{Z}{\sqrt{N}}$$
    onde $Z$ é a estatística padronizada do teste de Wilcoxon e $N$ é o número total de observações pareadas, complementado pela métrica *Cliff's Delta* para variáveis ordinais.

---

## 6. Procedimentos de Coleta e Análise Estatística (Pipeline da Sprint 01 a 03)

Para garantir a reprodutibilidade integral do estudo, o fluxo de trabalho experimental é padronizado através das seguintes etapas sequenciais:

```
[Sprint 01: Setup & Desenho]
   │
   ├─► Seleção e auditoria dos Katas com testes fechados
   ├─► Implementação do script de cronometragem e runner de testes
   ├─► Implementação do script de extração de métricas estáticas (Radon / CK)
   │
[Sprint 02: Execução Crossover]
   │
   ├─► Execução dos 12 trials contrabalanceados conforme a Matriz
   ├─► Registro operacional de tempos, censuras e logs de prompt
   ├─► Commit atômico dos códigos finais vinculados às Issues no GitHub Projects
   │
[Sprint 03: Análise Inferencial & Dashboard]
   │
   ├─► Consolidação da base de dados em arquivo estruturado (CSV/JSON)
   ├─► Teste de Wilcoxon Signed-Rank pareado para RQ1, RQ2 e RQ3 (scipy.stats)
   ├─► Cálculo de tamanho de efeito (r de Rosenthal e Cliff's Delta)
   └─► Geração de visualizações gráficas (Boxplots pareados, violin plots e curvas de sobrevivência)
```

---

## 7. Referências Normativas e Bibliográficas

1. **Basili, V. R., Caldiera, G., & Rombach, H. D.** (1994). *The Goal Question Metric Approach*. Encyclopedia of Software Engineering, John Wiley & Sons, Inc., pp. 528–532.
2. **Wohlin, C., Runeson, P., Höst, M., Ohlsson, M. C., Regnell, B., & Wesslén, A.** (2012). *Experimentation in Software Engineering*. Springer Science & Business Media.
3. **Juristo, N., & Moreno, A. M.** (2001). *Basics of Software Engineering Experimentation*. Kluwer Academic Publishers.
4. **Kitchenham, B. A., Pfleeger, S. L., Pickard, L. M., Jones, P. W., Hoaglin, D. C., El Emam, K., & Rosenberg, J.** (2002). *Preliminary guidelines for empirical research in software engineering*. IEEE Transactions on Software Engineering, 28(8), 721–734.
5. **McCabe, T. J.** (1976). *A Complexity Measure*. IEEE Transactions on Software Engineering, SE-2(4), 308–320.
6. **Wilcoxon, F.** (1945). *Individual comparisons by ranking methods*. Biometrics Bulletin, 1(6), 80–83.
7. **Sackman, H., Erikson, W. J., & Grant, E. E.** (1968). *Exploratory experimental studies comparing online and offline programming performance for programmers*. Communications of the ACM, 11(1), 3–11.
