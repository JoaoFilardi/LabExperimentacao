# [LAB04S01] Definição de Cenário, Testes Estatísticos e Hipóteses
**Issue correspondente:** `#45`  
**Laboratório:** LAB04 — Testes de Hipótese por Dentro: Cenário, Simulação e Visualização  
**Disciplina:** Laboratório de Experimentação de Software — 6º Período  
**Professor:** Danilo Maia  

---

## 1. Visão Geral e Identificação

| Item | Especificação Adotada |
|---|---|
| **Par de Testes Selecionado** | **P1: Teste t de Welch × Teste U de Mann-Whitney (Wilcoxon rank-sum)** |
| **Cenário de Engenharia de Software** | Impacto do uso de bots de revisão automatizada no tempo até o merge (*lead time to merge*) de Pull Requests |
| **Tipo de Teste** | **Bicaudal** (*two-tailed*) |
| **Nível de Significância ($\alpha$)** | $\alpha = 0{,}05$ (95% de nível de confiança) |
| **Amostra Real Prevista** | 30 Pull Requests com bot e 30 Pull Requests sem bot ($n_1 = 30$, $n_2 = 30$) de repositório open-source |
| **Previsão Inicial do Grupo** | Superioridade do **Teste U de Mann-Whitney** em dados realistas de software (assimetria e outliers) |

---

## 2. Cenário de Engenharia de Software

### 2.1 Contextualização Prática
Na prática contemporânea de desenvolvimento de software ágil e colaborativo, a prática de *Code Review* (revisão de código por pares) é fundamental para garantir a manutenibilidade, a confiabilidade e a conformidade arquitetural do código integrado. Contudo, revisões manuais frequentes podem se tornar um gargalo significativo, aumentando o *lead time to merge* (tempo total decorrido entre a submissão de um Pull Request e a sua integração efetiva à ramificação principal).

Para mitigar esse atraso, equipes e organizações adotam com frequência **bots de revisão automatizada** (ex.: *Reviewdog*, *SonarCloud Bot*, *Codecov*, *Dependabot*, linters e checadores de estilo integrados via GitHub Actions). A promessa de fornecedores e defensores dessas ferramentas é acelerar o ciclo de revisão ao detectar violações sintáticas, falhas de cobertura e vulnerabilidades triviais antes da intervenção humana.

Entretanto, a literatura científica empírica de Engenharia de Software (e.g., Wessel et al., 2020; Kinsman et al., 2021) aponta que a inserção de bots nem sempre resulta em aceleração do processo:
1. **Redução de tempo esperada:** Bots realizam triagens imediatas, poupam revisores humanos de inspeções mecânicas e liberam os autores para corrigir pendências rapidamente.
2. **Potencial aumento de tempo (efeito adverso):** Notificações em massa geram sobrecarga cognitiva (*bot noise* e *alert fatigue*), falsos-positivos em linters obrigam o desenvolvedor a ciclos adicionais de commits para contornar verificações rígidas, e falhas transitórias em pipelines de checagem podem manter PRs bloqueados desnecessariamente.

Diante dessa dualidade real de mercado, investigamos empiricamente se a presença de bots de revisão gera um impacto mensurável no tempo decorrido até o merge de Pull Requests.

### 2.2 Grupos Comparados e Variável Dependente
- **Grupo 1 — Com Bot de Revisão (`com_bot`):** Pull Requests que receberam análises, comentários automáticos ou validações de bots de revisão de código durante o processo de avaliação.
- **Grupo 2 — Sem Bot de Revisão (`sem_bot`):** Pull Requests revisados exclusivamente pelo fluxo humano tradicional, sem a presença de bots de análise/revisão.
- **Variável Dependente ($Y$):** Tempo decorrido até o merge (*lead time to merge*), mensurado em **horas decimais**, definido como:
  $$Y = \text{Data/Hora de Conclusão (merged\_at)} - \text{Data/Hora de Criação (created\_at)}$$

---

## 3. Pergunta de Pesquisa (Research Question)

A pergunta norteadora desta investigação foi formulada de maneira clara, unívoca e objetiva:

> **"A utilização de bots de revisão automatizada altera o tempo decorrido até o merge de Pull Requests em projetos de Engenharia de Software?"**

---

## 4. Hipóteses Estatísticas ($H_0$ e $H_1$)

Para garantir alinhamento tanto conceitual quanto com a mecânica particular de cada teste estatístico (um paramétrico focado em médias e outro não-paramétrico focado em ordenação de postos / dominância estocástica), as hipóteses são definidas em dois níveis:

### 4.1 Formulação Conceitual Geral
- **Hipótese Nula ($H_0$):** Não há diferença no tempo até o merge de Pull Requests entre o grupo assistido por bots e o grupo revisado exclusivamente por humanos.
- **Hipótese Alternativa ($H_1$):** Há diferença significativa no tempo até o merge de Pull Requests entre o grupo assistido por bots e o grupo revisado exclusivamente por humanos.

---

### 4.2 Formulação Matemática Operacional por Teste

#### A. Para o Teste t de Welch (comparação de médias populacionais):
- **$H_0$:** $\mu_{\text{com\_bot}} = \mu_{\text{sem\_bot}} \quad \iff \quad \mu_{\text{com\_bot}} - \mu_{\text{sem\_bot}} = 0$
- **$H_1$:** $\mu_{\text{com\_bot}} \neq \mu_{\text{sem\_bot}} \quad \iff \quad \mu_{\text{com\_bot}} - \mu_{\text{sem\_bot}} \neq 0$

*Onde $\mu_{\text{com\_bot}}$ e $\mu_{\text{sem\_bot}}$ denotam os tempos médios populacionais até o merge de cada grupo.*

#### B. Para o Teste U de Mann-Whitney (comparação de distribuições / postos):
- **$H_0$:** $P(X_{\text{com\_bot}} > Y_{\text{sem\_bot}}) = P(Y_{\text{sem\_bot}} > X_{\text{com\_bot}}) = 0{,}5$  
  *(A probabilidade de um PR escolhido aleatoriamente do grupo com bot ter tempo de merge maior do que um PR do grupo sem bot é de 50%; as distribuições populacionais são estocasticamente iguais).*  
  *Sob o pressuposto de que as distribuições compartilham formatos similares de dispersão e assimetria, $H_0$ equivale à igualdade das medianas populacionais: $\tilde{\mu}_{\text{com\_bot}} = \tilde{\mu}_{\text{sem\_bot}}$.*
- **$H_1$:** $P(X_{\text{com\_bot}} > Y_{\text{sem\_bot}}) \neq 0{,}5$  
  *(Uma distribuição tende a assumir valores estocasticamente maiores ou menores do que a outra; sob formatos similares, medianas distintas: $\tilde{\mu}_{\text{com\_bot}} \neq \tilde{\mu}_{\text{sem\_bot}}$).*

---

## 5. Direcionalidade dos Testes: Escolha por Teste Bicaudal e Justificativa

Adotou-se formalmente o **teste bicaudal (*two-tailed test*)**.

### Justificativa Metodológica e Empírica:
1. **Possibilidade de Efeito Adverso Real:** Em experimentação científica de software, adotar um teste unicaudal pressupõe a certeza teórica de que a intervenção tecnológica só pode agir em uma única direção (redução de tempo) ou que qualquer aumento de tempo é irrelevante. Como demonstrado na literatura de Engenharia de Software, bots podem induzir gargalos significativos decorrentes de *alert fatigue*, falsos positivos e retrabalho de formatação. O teste bicaudal garante sensibilidade para capturar tanto o benefício (aceleração) quanto o prejuízo (lentidão).
2. **Mitigação do Viés de Confirmação:** Um teste unicaudal à esquerda descartaria sumariamente qualquer cenário em que os bots desacelerassem o fluxo de trabalho, classificando aumentos dramáticos de tempo como mera "não rejeição de $H_0$" ($p \to 1$). O teste bicaudal mantém a neutralidade analítica da equipe.
3. **Conservadorismo Estatístico:** Ao repartir a probabilidade de falso-positivo entre os dois extremos ($\alpha / 2 = 0{,}025$ em cada cauda), o teste bicaudal exige uma evidência amostral mais substancial para rejeitar a hipótese nula, conferindo maior robustez e segurança à decisão gerencial de Engenharia de Software.

---

## 6. Descrição dos Testes Estatísticos Selecionados (Par P1)

### 6.1 Teste t de Welch (*Welch's t-test*) — Abordagem Paramétrica
O teste t de Welch é uma modificação do teste t de Student para duas amostras independentes concebida para contornar a exigência de igualdade de variâncias populacionais (homocedasticidade).

- **O que compara:** A diferença entre as **médias aritméticas** dos dois grupos independentes ponderada pelo erro padrão combinado.
- **Estatística de Teste:**
  $$t = \frac{\bar{X}_1 - \bar{X}_2}{\sqrt{\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}}}$$
  onde os graus de liberdade ($\nu$) são corrigidos pela aproximação de Welch-Satterthwaite:
  $$\nu \approx \frac{\left(\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}\right)^2}{\frac{(s_1^2 / n_1)^2}{n_1 - 1} + \frac{(s_2^2 / n_2)^2}{n_2 - 1}}$$
- **Principais Pressupostos:**
  1. **Independência:** As observações em cada grupo e entre os grupos são mutuamente independentes.
  2. **Nível de Medida Contínuo:** A variável analisada é contínua em escala de razão ou intervalo.
  3. **Normalidade:** Os dados provêm de populações aproximadamente normais. Embora o Teorema Central do Limite (TCL) auxilie com amostras grandes, com amostras moderadas ($n \approx 30$) e caudas pesadas, a violação de normalidade afeta a precisão do p-valor.
  4. *Dispensa homocedasticidade:* Não requer que $\sigma_1^2 = \sigma_2^2$.

---

### 6.2 Teste U de Mann-Whitney (*Wilcoxon-Mann-Whitney*) — Abordagem Não-Paramétrica
O teste U de Mann-Whitney é o teste não-paramétrico padrão para comparação de dois grupos independentes baseado na soma de postos ordenados.

- **O que compara:** Avalia a **dominância estocástica** entre duas distribuições através do ranqueamento conjunto das observações. Determina se os valores de um grupo tendem sistematicamente a exceder os valores do outro grupo na ordenação de postos. Quando as distribuições possuem formatos similares, compara as **medianas**.
- **Estatística de Teste:**
  $$U_1 = n_1 n_2 + \frac{n_1(n_1 + 1)}{2} - R_1, \quad U_2 = n_1 n_2 - U_1, \quad U = \min(U_1, U_2)$$
  onde $R_1$ representa a soma dos postos atribuídos às observações do Grupo 1 no ranqueamento global conjunto.
- **Principais Pressupostos:**
  1. **Independência:** Amostras e observações independentes.
  2. **Escala de Mensuração:** A variável dependente deve ser contínua ou ordinal (permitindo ordenação consistente de menor para maior).
  3. **Forma das Distribuições (para inferência de medianas):** Para afirmar categoricamente que o teste compara medianas, assume-se que as duas distribuições possuem formatos semelhantes. Caso os formatos difiram, o teste mantém plena validade como teste de dominância estocástica ($P(X > Y) \neq 0{,}5$).
  4. *Dispensa normalidade e homocedasticidade:* É insensível a valores extremos e transformações monotônicas nos dados.

---

### 6.3 Quadro Comparativo dos Testes (Par P1)

| Dimensão | Teste t de Welch | Teste U de Mann-Whitney |
|---|---|---|
| **Classificação** | Paramétrico | Não-paramétrico |
| **Medida de Tendência Central** | Médias ($\mu_1 \text{ vs } \mu_2$) | Postos / Medianas ($\tilde{\mu}_1 \text{ vs } \tilde{\mu}_2$) |
| **Sensibilidade a Outliers** | Alta (outliers distorcem média e inflam variância) | Baixa (valores extremos mantêm apenas seu posto relativo) |
| **Pressuposto de Normalidade** | Exigido (dados normais em cada grupo) | Não exigido (livre de distribuição) |
| **Pressuposto de Variâncias Iguais** | Não exigido (ajusta graus de liberdade) | Não exigido |
| **Eficiência Assintótica Relativa (ARE)** | $100\%$ sob perfeita normalidade | $95{,}5\%$ sob normalidade; $> 100\%$ sob caudas pesadas |

---

## 7. Nível de Significância ($\alpha = 0{,}05$)

- Fixado formalmente em $\alpha = 0{,}05$ (5%), assegurando 95% de nível de confiança estatística.
- Para o teste bicaudal, a probabilidade crítica divide-se igualmente: $\alpha / 2 = 0{,}025$ (2,5%) na cauda inferior e $\alpha / 2 = 0{,}025$ (2,5%) na cauda superior.
- **Regra de Decisão:**
  $$\text{Se } p\text{-valor} < 0{,}05 \implies \text{Rejeita-se } H_0 \text{ (evidência estatisticamente significativa)}$$
  $$\text{Se } p\text{-valor} \ge 0{,}05 \implies \text{Não se rejeita } H_0 \text{ (evidência insuficiente)}$$

---

## 8. Previsão Inicial Pré-Simulação (Hypothesis Expectation)

> [!IMPORTANT]
> **Previsão Oficial do Grupo Registrada Antes das Simulações:**  
> O grupo espera que o **Teste U de Mann-Whitney apresente melhor desempenho global** (melhor controle empírico da taxa de Erro Tipo I e maior poder estatístico de detecção) quando aplicado ao cenário de tempo de Pull Requests em Engenharia de Software.

### Justificativa Teórica e Metodológica da Previsão:
1. **Comportamento Empírico dos Dados de Software:** Dados de tempo de ciclo (*lead time*, tempo de revisão, tempo até merge) em repositórios de software quase invariavelmente seguem distribuições com forte assimetria à direita (*positive skewness*, cauda longa) e presença rotineira de *outliers* severos (e.g., Pull Requests complexos, abandonados ou com discussões prolongadas que levam centenas de horas para serem mesclados). Tais comportamentos são tipicamente modelados por distribuições Lognormal, Weibull ou Pareto.
2. **Fragilidade do Teste t de Welch diante de Caudas Longas:** Embora o teste t de Welch corrija satisfatoriamente disparidades de variância, a presença de observações atípicas e a assimetria severa puxam excessivamente a média amostral ($\bar{X}$) e inflam o desvio padrão amostral ($s$). Isso acarreta duas consequências adversas:
   - *Perda de poder estatístico (Q2 e Q3):* O denominador da estatística $t$ torna-se inflado, diminuindo artificialmente o valor de $|t|$ e aumentando o Erro Tipo II (falha em detectar diferenças reais nos tempos da maioria dos PRs).
   - *Instabilidade na taxa de Erro Tipo I (Q3):* Em amostras de tamanho moderado ($n \approx 30$), fortes assimetrias violam os fundamentos da distribuição amostral teórica de Student.
3. **Resiliência do Teste U de Mann-Whitney:** Ao converter magnitudes brutas em postos relativos ($1, 2, \dots, N$), o teste de Mann-Whitney neutraliza a distorção introduzida por valores extremos nas caudas. Sua função de potência permanece robusta e estável mesmo diante de alta assimetria e ruídos de processo.
4. **Reserva do Cenário Teórico Puro:** O grupo reconhece que, na hipótese estritamente ideal e irrealista em que os tempos de PR seguissem uma distribuição gaussiana pura sem qualquer contaminação por outliers, o teste t de Welch seria o teste uniformemente mais poderoso (UMP), exibindo ligeira vantagem teórica de poder frente ao Mann-Whitney (cuja eficiência assintótica sob normalidade perfeita é de aproximadamente 95,5%). No entanto, como o cenário real de Engenharia de Software é marcadamente não-gaussiano, a superioridade prática esperada é do teste não-paramétrico.

---

## 9. Análise de Consequências Práticas: Erro Tipo I vs. Erro Tipo II em Engenharia de Software

No contexto de tomada de decisão em Engenharia de Software para adoção de ferramentas de engenharia de plataforma e automação, os erros assumem as seguintes interpretações e impactos práticos:

| Tipo de Erro | Definição Estatística | Interpretação no Cenário de Bots de PR | Consequência Prática de Negócio |
|---|---|---|---|
| **Erro Tipo I ($\alpha$)** | Rejeitar $H_0$ quando $H_0$ é verdadeira (Falso Positivo) | Concluir que os bots alteram significativamente o tempo de merge quando, na realidade, o impacto no tempo é nulo | A equipe investe esforço de engenharia, tempo de manutenção de scripts de CI e custos com licenças de bots esperando aceleração inexistente, ou remove uma ferramenta funcional com base em um falso alarme de lentidão. |
| **Erro Tipo II ($\beta$)** | Não rejeitar $H_0$ quando $H_1$ é verdadeira (Falso Negativo) | Concluir que os bots não causam impacto mensurável quando, na realidade, existe um ganho (ou gargalo) real | O time perde a oportunidade de acelerar substancialmente o fluxo de entrega de valor, ou perpetua o uso de um bot ruidoso que está gerando lentidão sistemática sem ser detectado. |

**Avaliação de Gravidade:** No contexto corporativo de entrega contínua, o **Erro Tipo I** é frequentemente o mais indesejável em avaliações de aquisição/adoção de ferramentas, pois compromete o orçamento e o tempo da equipe com mudanças de processo inócuas. Por outro lado, caso o bot esteja introduzindo gargalos que degradam a experiência dos desenvolvedores, o **Erro Tipo II** torna-se crítico por mascarar uma regressão crônica de produtividade.

---

## 10. Planejamento da Coleta de Dados Reais (~30 observações por grupo)

Para fundamentar as distribuições simuladas e validar a recomendação empírica final (conforme exigido na Sprint 1 e na Seção 6 do Dashboard), a coleta de dados reais será realizada com os seguintes critérios:

- **Fonte dos Dados:** Repositório público open-source com histórico ativo de Pull Requests (e.g., projetos de médio/grande porte que utilizam GitHub Actions e bots como Codecov, Dependabot ou Reviewdog).
- **Tamanho da Amostra:** 30 Pull Requests com intervenção de bot de revisão e 30 Pull Requests revisados exclusivamente por humanos ($n_{\text{com\_bot}} = 30$, $n_{\text{sem\_bot}} = 30$).
- **Campos Extraídos:**
  - `pr_id`: Identificador numérico do Pull Request.
  - `grupo`: `"com_bot"` ou `"sem_bot"`.
  - `created_at`: Timestamp UTC de abertura do PR.
  - `merged_at`: Timestamp UTC da integração do PR.
  - `tempo_horas`: Duração calculada em horas decimais.
  - `bot_presente`: Booleano identificando presença de bot na interação.
- **Formato de Versionamento:** Arquivo CSV padronizado salvo no diretório `lab04/data/amostra_dados_reais.csv`.

---

## 11. Planejamento das Simulações (Sprints 1 e 2)

As simulações reproduzirão a dinâmica real observada através das seguintes diretrizes:

1. **Modelagem de Distribuição:** A partir dos parâmetros ajustados na amostra real (mediana $\tilde{m}$ e dispersão na escala logarítmica), os tempos serão simulados sob uma **Distribuição Lognormal**:
   $$Y \sim \text{Lognormal}(\mu_{\log}, \sigma_{\log})$$
2. **Q1 — Erro Tipo I (10.000 repetições):** Ambos os grupos gerados sob parâmetros estritamente idênticos ($H_0$ verdadeira); cômputo da proporção de rejeições ($p < 0{,}05$) para ambos os testes.
3. **Q2 — Análise de Poder (Curvas de Poder):** Simulação com no mínimo 5 tamanhos de efeito crescentes (diferenças induzidas na mediana/média entre os grupos), avaliando qual teste atinge mais rapidamente poderes de 80% e 90%.
4. **Q3 — Violação de Pressupostos:** Avaliação de cenários com:
   - Assimetria extrema (cauda pesada / alta variância logarítmica);
   - Injeção controlada de *outliers* severos (PRs com tempos anômalos);
   - Amostras de tamanho reduzido ($n = 15$).

---

## 12. Conteúdo Integrável para a Seção 1 ("Cenário") do Dashboard

Para atender estritamente à especificação da Seção 4 do `lab04/README.md` (onde cada seção é acompanhada de um texto sintético de 2 a 4 frases), disponibiliza-se o texto pronto para inserção no dashboard:

```markdown
### 1. Cenário: Bots de Revisão e Tempo de Merge de Pull Requests

Investigamos se a utilização de bots de revisão automatizada altera o tempo decorrido até o merge de Pull Requests em projetos de Engenharia de Software. Comparamos o teste paramétrico t de Welch com o não-paramétrico U de Mann-Whitney a um nível de significância de α = 0,05 em teste bicaudal, investigando as hipóteses H₀ (ausência de efeito no tempo de integração) e H₁ (presença de diferença significativa). A amostra empírica é composta por 60 Pull Requests (30 revisados com assistência de bots e 30 revisados de forma puramente manual) minerados do histórico de repositório open-source no GitHub. Nossa hipótese preliminar sustenta que o teste de Mann-Whitney apresentará superioridade de poder e robustez diante da assimetria acentuada e dos outliers inerentes a tempos de processo de software.
```

---

## 13. Guia Rápido de Apoio para a Apresentação Oral (15 Perguntas)

Respostas objetivas preparadas para as perguntas da apresentação diretamente ligadas a esta issue:

- **Pergunta 1 (Cenário e H₀/H₁ em palavras simples):**  
  *Investigamos se Pull Requests que recebem comentários/análises de bots de revisão são mesclados mais rápido ou mais devagar do que PRs revisados só por humanos. H₀ afirma que o tempo até o merge é idêntico entre os grupos; H₁ afirma que existe diferença mensurável de tempo.*
- **Pergunta 2 (Unicaudal ou bicaudal e por quê?):**  
  *Bicaudal. Bots podem acelerar a aprovação ao filtrar erros triviais, mas também podem atrasar o processo ao gerar ruído de alertas, falsos positivos e retrabalho de checagem. O teste bicaudal previne viés de confirmação e captura efeitos em ambas as direções.*
- **Pergunta 5 (O que cada teste compara de fato?):**  
  *O teste t de Welch compara as médias aritméticas ajustando os graus de liberdade para lidar com variâncias diferentes. O teste U de Mann-Whitney compara a soma dos postos das observações combinadas, avaliando a dominância estocástica entre distribuições (e as medianas, sob formas semelhantes).*
- **Pergunta 8 (Erro Tipo I e Tipo II no cenário, qual o mais grave?):**  
  *Erro Tipo I é concluir falsamente que os bots aceleram/alteram o tempo, gerando custos de licenciamento e manutenção de infraestrutura inútil. Erro Tipo II é não detectar uma melhora real (perdendo agilidade) ou não perceber que um bot está atrasando a equipe. Para decisões de investimento, o Erro Tipo I costuma ser mais nocivo financeiramente; para a produtividade dos devs, o Erro Tipo II prolonga gargalos silenciosos.*
- **Pergunta 13 (Expectativa pré-simulação):**  
  *O grupo esperava previamente a vitória do Mann-Whitney em dados assimétricos de software, pois o t de Welch tem sua média e variância infladas por outliers de cauda longa, perdendo poder estatístico de detecção.*

