# [LAB04S01] Justificativa das Distribuições e Parâmetros dos Dados Simulados
**Issue correspondente:** `#46`  
**Laboratório:** LAB04 — Testes de Hipótese por Dentro: Cenário, Simulação e Visualização  
**Disciplina:** Laboratório de Experimentação de Software — 6º Período  
**Professor:** Danilo Maia  

---

## 1. Visão Geral e Objetivo

Esta documentação fundamenta a escolha das distribuições de probabilidade e a calibração rigorosa de seus parâmetros para a geração reproduzível de dados simulados no âmbito do **LAB04**. O objetivo é garantir que as simulações numéricas (Erro Tipo I em Q1, Poder em Q2 e Violação de Pressupostos em Q3) reflitam com fidelidade o comportamento empírico real do tempo decorrido até o merge (*lead time to merge*, em horas) de Pull Requests em projetos de Engenharia de Software.

---

## 2. Análise Descritiva dos Dados Reais Coletados

A amostra empírica é composta por **60 Pull Requests** coletados do repositório público de larga escala **`tiangolo/fastapi`** no GitHub, divididos equitativamente em dois grupos independentes de 30 observações ($n_1 = 30$, $n_2 = 30$):
* **Grupo `sem_bot` ($n = 30$):** Pull Requests avaliados e aprovados exclusivamente pelo fluxo de revisão humana tradicional, sem intervenção de bots automáticos.
* **Grupo `com_bot` ($n = 30$):** Pull Requests que contaram com validações, checagens e comentários automatizados de bots de revisão (*Codecov*, *Dependabot*, *GitHub Actions*, *pre-commit.ci*).

O arquivo original dos dados reais encontra-se versionado em:
[`lab04/data/amostra_dados_reais.csv`](file:///c:/Users/fofam/OneDrive/Documentos/Faculdade/LabExperimentacao/lab04/data/amostra_dados_reais.csv)

### Tabela 1: Perfil Estatístico Descritivo da Amostra Real

| Métrica Estatística | Grupo Sem Bot (`sem_bot`) | Grupo Com Bot (`com_bot`) | Amostra Agrupada (*Pooled*) |
|---|---|---|---|
| **Tamanho Amostral ($n$)** | 30 | 30 | 60 |
| **Média Aritmética ($\bar{X}$)** | $27{,}42$ horas | $20{,}95$ horas | $24{,}19$ horas |
| **Desvio Padrão ($s$)** | $24{,}20$ horas | $20{,}06$ horas | $22{,}32$ horas |
| **Mediana ($\tilde{X}$)** | $18{,}90$ horas | $13{,}60$ horas | $15{,}40$ horas |
| **Intervalo Interquartil (IQR)** | $20{,}92$ horas | $16{,}78$ horas | $17{,}95$ horas |
| **Mínimo** | $2{,}40$ horas | $1{,}20$ horas | $1{,}20$ horas |
| **Máximo** | $105{,}50$ horas | $88{,}00$ horas | $105{,}50$ horas |
| **Coeficiente de Assimetria (*Skewness*)** | $+1{,}695$ | $+1{,}816$ | $+1{,}744$ |
| **Curtose de Excesso (*Kurtosis*)** | $+2{,}485$ | $+3{,}021$ | $+2{,}783$ |
| **Média Logarítmica ($\hat{\mu}_{\log}$)** | $2{,}9721$ | $2{,}6385$ | $2{,}8053$ |
| **Desvio Logarítmico ($\hat{\sigma}_{\log}$)** | $0{,}8670$ | $0{,}9632$ | $0{,}9254$ |

### Interpretação dos Dados Reais:
1. **Forte Assimetria Positiva:** Ambos os grupos exibem assimetria substancial ($\text{skewness} > 1{,}6$). A grande maioria dos Pull Requests é resolvida e mesclada rapidamente (em menos de 20 horas), enquanto um percentual menor sofre demoras consideráveis (cauda longa ultrapassando 80 a 100 horas).
2. **Presença de Cauda Pesada (*Heavy Tail*):** A curtose positiva expressiva ($> 2{,}4$) atesta a presença de eventos extremos e caudas mais pesadas do que as de uma distribuição normal de mesma média e variância.
3. **Média Superior à Mediana:** Em ambos os grupos, a média aritmética supera expressivamente a mediana ($\bar{X}_{\text{sem}} = 27{,}42\text{ h}$ vs $\tilde{X}_{\text{sem}} = 18{,}90\text{ h}$; $\bar{X}_{\text{com}} = 20{,}95\text{ h}$ vs $\tilde{X}_{\text{com}} = 13{,}60\text{ h}$), sintoma inequívoco de não-normalidade e de forte atração da média por observações atípicas.

---

## 3. Identificação e Justificativa da Distribuição Teórica

Para modelar matematicamente o comportamento do tempo até o merge, selecionou-se a **Distribuição Lognormal**:

$$Y \sim \text{Lognormal}(\mu_{\log}, \sigma_{\log})$$

onde a variável aleatória $Y > 0$ tem a propriedade de que seu logaritmo natural segue uma distribuição Gaussiana:
$$\ln(Y) \sim \mathcal{N}(\mu_{\log}, \sigma_{\log}^2)$$

### Por que a Lognormal foi a Distribuição Escolhida?

1. **Aderência aos Fundamentos de Engenharia de Software:** A literatura empírica de medição de software (e.g., Fenton & Bieman; Jorgensen; Mockus et al.) estabelece que tempos de ciclo (*cycle time*, *lead time*, duração de builds e revisões) são estritamente contínuos, positivos ($Y > 0$) e multiplicativos por natureza (pequenos atrasos em pipelines e revisões encadeiam-se de forma multiplicativa, convergindo assintoticamente para a Lognormal conforme o Teorema Central do Limite multiplicativo).
2. **Representação da Mediana e da Cauda Longa:** Na distribuição Lognormal:
   $$\text{Mediana}(Y) = \exp(\mu_{\log})$$
   $$\text{Média}(Y) = \exp\left(\mu_{\log} + \frac{\sigma_{\log}^2}{2}\right)$$
   Isso permite controlar com precisão matemática a assimetria e o afastamento natural entre a mediana e a média observado empiricamente.
3. **Estimativa Eficiente via Máxima Verossimilhança (MLE):** Os parâmetros $\mu_{\log}$ e $\sigma_{\log}$ podem ser diretamente estimados aplicando a média amostral e o desvio padrão amostral dos valores após transformação logarítmica $\ln(Y)$.

---

## 4. Definição dos Parâmetros das Distribuições

Com base na calibração direta sobre a amostra empírica, foram definidos os conjuntos de parâmetros para os diferentes cenários de simulação:

### 4.1 Parâmetros sob $H_0$ (Hipótese Nula Verdadeira — Cenário sem Efeito)
Na Questão **Q1 (Erro Tipo I)**, não deve existir diferença estatística entre os grupos (`com_bot` e `sem_bot`). Ambos são amostrados a partir da mesma distribuição teórica, calculada a partir do agrupamento total (*pooled*) dos dados reais:
* $\mu_{\log, H_0} = 2{,}8053$  
  *$\implies \text{Mediana teórica} = \exp(2{,}8053) \approx 16{,}53\text{ horas}$*
* $\sigma_{\log, H_0} = 0{,}9254$  
  *$\implies \text{Média teórica} = \exp\left(2{,}8053 + \frac{0{,}9254^2}{2}\right) \approx 25{,}37\text{ horas}$*

### 4.2 Parâmetros sob $H_1$ (Hipótese Alternativa — Dados com Efeito Empírico Real)
Para gerar datasets com o efeito real observado na amostra:
* **Grupo Sem Bot (`sem_bot`):**
  * $\mu_{\log, \text{sem}} = 2{,}9721 \implies \text{Mediana teórica} = 19{,}53\text{ h}$
  * $\sigma_{\log, \text{sem}} = 0{,}8670 \implies \text{Média teórica} = 28{,}45\text{ h}$
* **Grupo Com Bot (`com_bot`):**
  * $\mu_{\log, \text{com}} = 2{,}6385 \implies \text{Mediana teórica} = 13{,}99\text{ h}$
  * $\sigma_{\log, \text{com}} = 0{,}9632 \implies \text{Média teórica} = 22{,}25\text{ h}$

### 4.3 Parametrização para Tamanhos de Efeito Variáveis (Curvas de Poder em Q2)
Para responder à Questão **Q2 (Poder Estatístico)** na Sprint 2, o gerador implementa uma redução percentual parametrizável $\delta \in [0{,}00; 0{,}40]$ (0%, 10%, 20%, 30%, 40%):
$$\mu_{\log, \text{com}} = \mu_{\log, \text{sem}} + \ln(1 - \delta)$$
Quando $\delta = 0$, retorna-se ao cenário sob $H_0$. Conforme $\delta$ se expande, mede-se a probabilidade empírica de rejeição de $H_0$ (poder estatístico) de cada teste.

### 4.4 Parametrização para Violação Severa de Pressupostos (Q3)
Para investigar o impacto de anomalias extremas nos testes estatísticos:
* **Injeção de Outliers Extremos:** O gerador sorteia aleatoriamente uma proporção configurável de observações (e.g., $10\%$) e aplica uma ampliação drástica ($5\times + 50\text{ h}$), reproduzindo situações em que PRs ficam congelados por disputas de requisitos ou dependências externas quebradas.
* **Tamanhos Amostrais Pequenos:** O gerador permite reduzir $n$ para $n = 15$ ou $n = 10$, avaliando se o Teorema Central do Limite falha em sustentar o teste t de Welch.

---

## 5. Arquitetura do Código e Garantia de Reprodutibilidade

Todo o motor de simulação foi centralizado e modularizado em:
[`lab04/src/simulacao.py`](file:///c:/Users/fofam/OneDrive/Documentos/Faculdade/LabExperimentacao/lab04/src/simulacao.py)

### Principais Componentes Implementados:
1. **`ParametrosSimulacao` (dataclass):** Encapsula todos os parâmetros empíricos e configurações padrão de simulação de forma tipada e imutável.
2. **`GeradorDadosSimulados` (classe):** Motor de geração que gerencia a semente e o gerador pseudoaleatório `np.random.default_rng(semente)`.
3. **Semente Fixa Obrigatória:** Por padrão, utiliza-se a semente `42` (`numpy.random.default_rng(42)`). Execuções sucessivas geram conjuntos de dados idênticos bit a bit, garantindo auditabilidade científica estrita.
4. **Funções Específicas:**
   * `gerar_vetor_lognormal(tamanho, mu_log, sigma_log)`
   * `gerar_dataset_experimento(n_sem, n_com, sob_h0, efeito_reducao)`
   * `gerar_dataset_com_outliers(n_sem, n_com, prop_outliers, fator_multiplicador)`
   * `gerar_dataset_gaussiano(n_sem, n_com, media, desvio)`
   * `gerar_e_salvar_dataset_s01(semente, caminho_saida)`

---

## 6. Dataset Simulado Gerado para a Sprint 01

Executando o gerador com a semente oficial `42`, foi produzido o arquivo:
[`lab04/data/dados_simulados_s01.csv`](file:///c:/Users/fofam/OneDrive/Documentos/Faculdade/LabExperimentacao/lab04/data/dados_simulados_s01.csv)

### Tabela 2: Comparação entre a Amostra Real e a Amostra Simulada (S01)

| Métrica | Grupo | Amostra Real | Amostra Simulada (S01) |
|---|---|---|---|
| **$n$** | `sem_bot` | 30 | 30 |
| **Mediana** | `sem_bot` | $18{,}90\text{ h}$ | $21{,}25\text{ h}$ |
| **Média** | `sem_bot` | $27{,}42\text{ h}$ | $24{,}01\text{ h}$ |
| **Desvio Padrão** | `sem_bot` | $24{,}20\text{ h}$ | $13{,}99\text{ h}$ |
| **$n$** | `com_bot` | 30 | 30 |
| **Mediana** | `com_bot` | $13{,}60\text{ h}$ | $16{,}46\text{ h}$ |
| **Média** | `com_bot` | $20{,}95\text{ h}$ | $21{,}33\text{ h}$ |
| **Desvio Padrão** | `com_bot` | $20{,}06\text{ h}$ | $20{,}92\text{ h}$ |

A amostra simulada gerada preserva as características essenciais do cenário real: assimetria positiva, valores estritamente positivos, mediana substancialmente inferior à média e ordem de grandeza compatível com Pull Requests reais de Engenharia de Software.

---

## 7. Validação por Testes Automatizados

A integridade do código e a reprodutibilidade foram validadas por uma suíte de 13 testes unitários em:
[`lab04/tests/test_simulacao.py`](file:///c:/Users/fofam/OneDrive/Documentos/Faculdade/LabExperimentacao/lab04/tests/test_simulacao.py)

* **Reprodutibilidade:** Garante que a mesma semente gere exatamente os mesmos arrays e DataFrames.
* **Variabilidade:** Garante que sementes diferentes produzam dados estatisticamente distintos.
* **Convergência $H_0$:** Garante que sob $H_0$ com amostras grandes as medianas e médias convirjam.
* **Sensibilidade de Efeito:** Garante que `efeito_reducao > 0` desloque a mediana do tratamento.
* **Injeção de Outliers:** Garante a contaminação controlada nas caudas para a Questão Q3.
