# [LAB04FINAL] Roteiro Individual da Apresentação Oral — Perguntas 1 a 5

**Issue correspondente:** `#58` (`[ LAB04FINAL ] Preparar apresentação oral das perguntas 1 a 5`)  
**Responsável:** Tiago Boaventura Amaral  
**Laboratório:** LAB04 — Testes de Hipótese por Dentro: Cenário, Simulação e Visualização  
**Disciplina:** Laboratório de Experimentação de Software — 6º Período  
**Professor:** Danilo Maia  

---

## 1. Visão Geral e Estratégia de Apresentação

- **Tempo por Pergunta:** Rigorosamente **~30 segundos** por resposta (tempo total do bloco: ~2 minutos e 30 segundos).
- **Abordagem Didática:** Apontar diretamente para a seção e elemento correspondente no **Dashboard** antes ou durante a fala, conectando a motivação empírica aos fundamentos estatísticos.
- **Foco Temático:** Contextualização do cenário em Engenharia de Software, hipóteses estatísticas ($H_0$ e $H_1$), justificativa da direcionalidade bicaudal, rigor metodológico da amostragem no GitHub, calibração fidedigna da simulação Log-normal e distinção conceitual fundamental entre comparação de médias ($t$ de Welch) e comparação de postos ($U$ de Mann-Whitney).

---

## 2. Fichas Detalhadas das Perguntas 1 a 5

---

### Pergunta 1 — Cenário de Pesquisa e Significado de $H_0$ e $H_1$

- **Enunciado Oficial:** *"Qual é o cenário de vocês e o que H₀ e H₁ afirmam, em palavras simples?"*
- **Pergunta Variante da Banca:** *"Se o p-valor for maior que 0,05, isso prova que H₀ é verdadeira ou apenas não temos evidências para rejeitá-la?"*
- **Seção do Dashboard:** `Seção 1. Cenário`
- **Onde Apontar na Tela:**  
  Apontar para a **Seção 1 do Dashboard**:
  1. No card esquerdo: A **Pergunta de Pesquisa** em destaque ("*A utilização de bots de automação no processo de Pull Requests reduz o tempo decorrido até o merge em repositórios de software de código aberto?*");
  2. No card central: As caixas conceituais de **$H_0$ (Hipótese Nula)** e **$H_1$ (Hipótese Alternativa)**, acompanhadas das operacionalizações matemáticas para os testes $t$ de Welch e $U$ de Mann-Whitney;
  3. No card direito: A identificação do repositório alvo (`tiangolo/fastapi`) e da variável dependente (`tempo_horas`).

#### Fala Direta de 30 Segundos:
> *"Nosso cenário investiga se a adoção de bots de automação em Pull Requests acelera ou atrasa o tempo até o merge no repositório open-source FastAPI. Em palavras simples, a hipótese nula H₀ afirma que os bots não fazem qualquer diferença no tempo de merge: a distribuição dos tempos com e sem bot é a mesma e qualquer oscilação observada decorre de mero acaso amostral. Já a hipótese alternativa H₁ afirma que existe uma diferença sistemática no tempo de processo entre os grupos, seja acelerando o fluxo de integração contínua ou gerando overhead e atraso."*

#### Resposta Direta para a Pergunta Variante (30 Segundos):
> *"Apenas indica ausência de evidência suficiente para rejeitar. Em inferência frequentista, não rejeitar H₀ jamais prova que ela seja verdadeira; significa apenas que, dado o ruído e a dispersão amostral com n = 30, o teste não acumulou poder estatístico suficiente para descartar a hipótese de igualdade (risco de Erro Tipo II)."*

#### Pontos-Chave e Fundamentação Técnica:
- **Cenário Investigado:** Par 3 do laboratório — Efeito do uso de bots de automação sobre o tempo decorrido até o merge de Pull Requests (*lead time* em horas).
- **$H_0$ Conceitual:** O tempo até o merge é identicamente distribuído entre PRs com e sem bot ($P(X_{\text{com}} > Y_{\text{sem}}) = 0{,}50$ e $\mu_{\text{sem}} = \mu_{\text{com}}$).
- **$H_1$ Conceitual:** O tempo até o merge difere sistematicamente entre PRs com e sem bot (efeito bilateral / bicaudal).
- **Operacionalizações Estatísticas:**
  - Teste $t$ de Welch: $H_0: \mu_{\text{sem\_bot}} = \mu_{\text{com\_bot}}$ vs. $H_1: \mu_{\text{sem\_bot}} \neq \mu_{\text{com\_bot}}$.
  - Teste $U$ de Mann-Whitney: $H_0: P(X_{\text{com}} > Y_{\text{sem}}) = 0{,}50$ vs. $H_1: P(X_{\text{com}} > Y_{\text{sem}}) \neq 0{,}50$.
- **Não rejeição $\neq$ Prova de $H_0$:** Em amostras moderadas ($n = 30$), o teste pode não rejeitar $H_0$ simplesmente por falta de poder estatístico ($\beta > 0{,}50$).

---

### Pergunta 2 — Direcionalidade do Teste: Unicaudal vs. Bicaudal

- **Enunciado Oficial:** *"O teste de vocês é unicaudal ou bicaudal? Por quê?"*
- **Pergunta Variante da Banca:** *"Por que não adotar teste unicaudal à esquerda já que o interesse prático da equipe é exclusivamente acelerar o merge?"*
- **Seção do Dashboard:** `Seção 1. Cenário` e `Seção 3. Como os testes funcionam`
- **Onde Apontar na Tela:**  
  Apontar para:
  1. O card da **Pergunta de Pesquisa** na Seção 1 onde consta explicitamente: `Tipo de teste: bicaudal / two-sided`;
  2. As **duas áreas vermelhas sombreadas de 2,5%** em cada extremidade da distribuição nula no **Gráfico G2** (Seção 3), demonstrando visualmente que tanto desvios para a esquerda quanto para a direita levam à rejeição de $H_0$.

#### Fala Direta de 30 Segundos:
> *"Nosso teste é estritamente bicaudal (two-sided). Embora a expectativa teórica inicial fosse de aceleração, a literatura empírica de Engenharia de Software documenta que bots com falhas, conflitos de dependências, notificações excessivas ou testes frágeis podem paradoxalmente atrasar as aprovações. Como um atraso nas integrações representaria um impacto organizacional negativo relevante que precisamos ser capazes de detectar, não podemos descartar essa direção a priori, repartindo o risco α = 5% em 2,5% para aceleração e 2,5% para atraso."*

#### Resposta Direta para a Pergunta Variante (30 Segundos):
> *"Adotar um teste unicaudal inflaria o poder estatístico na direção desejada mas tornaria o teste cego a qualquer atraso provocado pelo bot. Se a automação na prática gerasse gargalos severos e aumentasse o lead time, o teste unicaudal à esquerda falharia em acusar qualquer significância, induzindo a gestão a um falso senso de segurança."*

#### Pontos-Chave e Fundamentação Técnica:
- **Classificação Formal:** Teste bilateral / bicaudal (*two-sided*) com nível nominal de significância $\alpha = 0{,}05$.
- **Alocação de $\alpha$:** O erro de falso positivo é repartido simetricamente: $\alpha / 2 = 0{,}025$ ($2{,}5\%$) na cauda inferior (aceleração do processo) e $0{,}025$ ($2{,}5\%$) na cauda superior (atraso do processo).
- **Limites Críticos no G2:**
  - Teste $t$ de Welch ($\nu \approx 50{,}61$ gl): $t_{\text{crit}} = \pm 2{,}0085$.
  - Teste $U$ de Mann-Whitney ($Z \sim \mathcal{N}(0,1)$): $z_{\text{crit}} = \pm 1{,}95996$.
- **Rigor Metodológico:** O teste unicaudal só é aceitável quando um dos sentidos é fisicamente impossível ou inteiramente irrelevante. Em software, a degradação de performance por adoção de novas ferramentas é um risco operacional comum e de alto custo.

---

### Pergunta 3 — Coleta dos Dados Reais e Formato da Distribuição

- **Enunciado Oficial:** *"Como os dados reais foram coletados, e o que eles mostraram sobre a forma da distribuição?"*
- **Pergunta Variante da Banca:** *"Quais evidências estatísticas confirmam que os dados reais violam a suposição de normalidade?"*
- **Seção do Dashboard:** `Seção 1. Cenário (Origem dos Dados Reais)` e `Seção 2. Os dados (Gráfico G1 e Tabela Descritiva)`
- **Onde Apontar na Tela:**  
  Apontar para:
  1. A Seção 1 no card **Origem dos Dados Reais** destacando o repositório `tiangolo/fastapi` e a amostragem balanceada ($N = 60$, 30 com bot e 30 sem bot);
  2. Os **dois histogramas superiores do Gráfico G1** (painéis de dados reais);
  3. A **Tabela Comparativa Descritiva** logo abaixo de G1, apontando para a coluna de **Assimetria** ($1{,}72$ e $2{,}17$) e a contagem de **Outliers** na cauda direita (valores máximos de $105{,}5$h e $88{,}0$h).

#### Fala Direta de 30 Segundos:
> *"Os dados foram minerados via GitHub REST API do repositório fastapi (tiangolo/fastapi), selecionando 60 Pull Requests mergeados com tamanho moderado entre 10 e 500 linhas: 30 interagindo com bots e 30 sem bots. Os dados revelaram que a distribuição é fortemente assimétrica à direita, contínua estritamente positiva e com caudas longas: a assimetria calculada é de 1,72 sem bot e 2,17 com bot, com presença de outliers extremos de até 105,5 horas. O teste de Shapiro-Wilk rejeita a normalidade com p < 0,001."*

#### Resposta Direta para a Pergunta Variante (30 Segundos):
> *"A forte assimetria positiva, o teste de Shapiro-Wilk altamente significativo (p = 0,00015) e a grande discrepância entre médias (27,3h e 20,8h) e medianas (18,9h e 13,6h) comprovam a não-normalidade. Além disso, o desvio padrão é da mesma ordem de grandeza da média (23,2h e 22,6h), violando totalmente o pressuposto de simetria do teste t clássico."*

#### Pontos-Chave e Fundamentação Técnica:
- **Mineração e Filtros:** GitHub API v3, repositório open-source `tiangolo/fastapi` (FastAPI), Pull Requests mergeados com sucesso entre 10 e 500 linhas de código alteradas (LOC) para homogeneizar a complexidade de revisão.
- **Amostra:** $n_{\text{sem\_bot}} = 30$ e $n_{\text{com\_bot}} = 30$ ($N = 60$).
- **Características Empíricas Observadas:**
  - Grupo `sem_bot`: Média = $27{,}31$h, Mediana = $18{,}90$h, DP = $23{,}24$h, IQR = $25{,}00$h, Assimetria = $+1{,}72$, 4 outliers (máximo: $105{,}50$h).
  - Grupo `com_bot`: Média = $20{,}84$h, Mediana = $13{,}60$h, DP = $22{,}60$h, IQR = $17{,}05$h, Assimetria = $+2{,}17$, 2 outliers (máximo: $88{,}00$h).
- **Rejeição Formal de Normalidade:** Teste de Shapiro-Wilk na amostra conjunta: $W = 0{,}805$, $p = 0{,}00015 \ll 0{,}05$.

---

### Pergunta 4 — Calibração dos Parâmetros da Simulação com os Dados Reais

- **Enunciado Oficial:** *"Como os dados reais ajudaram a escolher os parâmetros da simulação?"*
- **Pergunta Variante da Banca:** *"Por que uma distribuição Normal não seria adequada para modelar os tempos na simulação de Monte Carlo?"*
- **Seção do Dashboard:** `Seção 2. Os dados (Expander de Justificativa e Calibração)` e `Gráfico G1 (Painéis Inferiores)`
- **Onde Apontar na Tela:**  
  Apontar para:
  1. O expander **"Justificativa das Distribuições e Calibração dos Parâmetros da Simulação"** aberto na Seção 2;
  2. Os **dois histogramas inferiores do Gráfico G1** (dados simulados), mostrando visualmente a correspondência de formato, dispersão e cauda com os histogramas superiores dos dados reais.

#### Fala Direta de 30 Segundos:
> *"Como os tempos reais exibiram suporte positivo e assimetria multiplicativa, adotamos a distribuição Log-normal. Os dados reais forneceram a calibração direta na escala logarítmica: ajustamos μ_log = 2,97 e σ_log = 0,85 para sem bot (mediana de 19,5h vs. 18,9h real) e μ_log = 2,64 e σ_log = 0,98 para com bot (mediana de 14,0h vs. 13,6h real). Para as simulações de Erro Tipo I sob H₀ (Q1 e Q3), agrupamos todos os 60 PRs reais em um baseline pooled com μ_log = 2,80 e σ_log = 0,92, garantindo que ambos os grupos venham da mesma população idêntica com semente 42."*

#### Resposta Direta para a Pergunta Variante (30 Segundos):
> *"A distribuição Normal geraria valores de tempo negativos com probabilidade substancial diante de desvios padrões tão altos (23h de DP para média de 27h), o que é fisicamente impossível no mundo real. Além disso, a curva Normal é perfeitamente simétrica e não reproduz os atrasos pontuais e outliers severos que observamos nos Pull Requests do GitHub."*

#### Pontos-Chave e Fundamentação Técnica:
- **Modelo Teórico:** Distribuição Log-normal $Y \sim \text{Log-Normal}(\mu_{\log}, \sigma_{\log})$, onde $\ln(Y) \sim \mathcal{N}(\mu_{\log}, \sigma_{\log}^2)$.
  - Mediana teórica: $\text{Med}(Y) = e^{\mu_{\log}}$.
  - Média teórica: $E[Y] = e^{\mu_{\log} + \sigma_{\log}^2/2}$.
- **Parâmetros Calibrados no `ParametrosSimulacao`:**
  - `sem_bot`: $\mu_{\log} = 2{,}9704$, $\sigma_{\log} = 0{,}8500 \implies \text{Mediana} = 19{,}50$h (real: $18{,}90$h), Média = $28{,}53$h (real: $27{,}31$h).
  - `com_bot`: $\mu_{\log} = 2{,}6391$, $\sigma_{\log} = 0{,}9800 \implies \text{Mediana} = 14{,}00$h (real: $13{,}60$h), Média = $22{,}33$h (real: $20{,}84$h).
  - População comum sob $H_0$ (*pooled* dos 60 PRs reais): $\mu_{\log} = 2{,}8000$, $\sigma_{\log} = 0{,}9200 \implies \text{Mediana} = 16{,}45$h, Média = $25{,}35$h.
- **Rigor Experimental:** $10.000$ simulações de Monte Carlo por condição executadas com gerador pseudoaleatório `numpy.random.default_rng(42)`.

---

### Pergunta 5 — Comparação Efetiva dos Dois Testes: Médias vs. Postos

- **Enunciado Oficial:** *"O que cada um dos dois testes compara de fato (médias, postos, proporções...)?"*
- **Pergunta Variante da Banca:** *"Se o teste t compara médias e o Mann-Whitney compara postos, é possível que eles cheguem a decisões divergentes?"*
- **Seção do Dashboard:** `Seção 3. Como os testes funcionam` e `Seção 6. Dados reais`
- **Onde Apontar na Tela:**  
  Apontar para:
  1. O **Gráfico G2**: o painel esquerdo rotulado como estatística $t$ de Welch e o painel direito rotulado como estatística $Z$ do teste de Mann-Whitney;
  2. A **Tabela Comparativa** nas Seções 3 e 6, apontando para a linha das médias aritméticas e desvios padrões (parâmetros de Welch) versus a linha da soma de postos $U$, estatística $Z$ e tamanho de efeito rank-biserial ($r_{\text{rb}}$).

#### Fala Direta de 30 Segundos:
> *"O teste t de Welch compara médias aritméticas ponderadas: ele avalia se a diferença entre as médias amostrais dos dois grupos é significativamente diferente de zero, corrigindo os graus de liberdade para acomodar variâncias desiguais. Já o teste U de Mann-Whitney é um teste não-paramétrico baseado em postos (ranks): ele junta todas as 60 observações, ordena em ordem crescente de 1 a 60 e compara a soma dos postos atribuídos a cada grupo, testando a dominância estocástica, ou seja, se a probabilidade de um PR com bot ser mergeado antes de um sem bot é igual a 50%."*

#### Resposta Direta para a Pergunta Variante (30 Segundos):
> *"Sim, com certeza. Por operar sobre as grandezas lineares elevadas ao quadrado na variância, o teste t de Welch é extremamente vulnerável a um único outlier extremo: se um PR levar 500 horas, a média dispara e a variância infla, destruindo o teste. Já o Mann-Whitney converte 500 horas no posto 60, preservando a ordenação relativa dos outros 29 PRs sem distorcer o resultado."*

#### Pontos-Chave e Fundamentação Técnica:
- **Teste $t$ de Welch (Paramétrico):**
  - O que compara: Médias populacionais $\mu_1$ e $\mu_2$.
  - Estatística de teste:
    $$t = \frac{\bar{x}_1 - \bar{x}_2}{\sqrt{\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}}}$$
  - Graus de liberdade: Fórmula de Welch-Satterthwaite ($\nu \approx 50{,}61$), dispensando homocedasticidade ($\sigma_1^2 = \sigma_2^2$), mas exigindo normalidade subjacente.
- **Teste $U$ de Mann-Whitney / Wilcoxon Rank-Sum (Não-paramétrico):**
  - O que compara: Distribuição de postos (*ranks*) combinados.
  - Estatística de teste:
    $$U_1 = R_1 - \frac{n_1(n_1+1)}{2}$$
  - Hipótese nula testada: Dominância estocástica $P(X > Y) = P(Y > X) = 0{,}50$ (ou igualdade de medianas se as formas distribucionais forem análogas).
- **Vulnerabilidade vs. Robustez:**
  - Welch é fortemente influenciado pela magnitude métrica de valores extremos: a soma dos desvios quadráticos infla $s^2$, reduzindo o valor absoluto de $|t|$ e sacrificando poder estatístico.
  - Mann-Whitney é invariante a qualquer transformação monotônica crescente: um outlier de $105$h ou de $10.000$h recebe exatamente o mesmo posto máximo ($60$), preservando a integridade inferencial.

---

## 3. Tabela Resumo para Consulta Rápida Durante o Ensaio

| Nº | Tema | Pergunta Oficial | Onde Apontar no Dashboard | Síntese de 30 Segundos |
|:---|:---|:---|:---|:---|
| **P1** | **Cenário e Hipóteses** | Qual é o cenário de vocês e o que H₀ e H₁ afirmam, em palavras simples? | Seção 1 (Card Pergunta e Card Hipóteses) | $H_0$: bots não alteram o tempo de merge (mero ruído). $H_1$: bots alteram sistematicamente o lead time. Não rejeitar $H_0 \neq$ provar $H_0$. |
| **P2** | **Direcionalidade** | O teste de vocês é unicaudal ou bicaudal? Por quê? | Seção 1 (Tipo de teste) e Seção 3 (G2 caudas) | Bicaudal ($\alpha=5\%$, $2{,}5\%$ cada cauda). Bots podem acelerar ou atrasar (overhead de CI); teste bicaudal evita viés confirmatório. |
| **P3** | **Coleta e Distribuição** | Como os dados reais foram coletados, e o que eles mostraram sobre a forma da distribuição? | Seção 1 (Origem) e Seção 2 (G1 superior e Tabela) | Minerados da API GitHub no FastAPI ($N=60$). Fortemente assimétrica à direita (1,72 e 2,17), $Y>0$, cauda longa com outliers (até 105,5h). Shapiro $p < 0{,}001$. |
| **P4** | **Calibração da Simulação** | Como os dados reais ajudaram a escolher os parâmetros da simulação? | Seção 2 (Expander Calibração e G1 inferior) | Modelo Log-normal ajustado na escala logarítmica às medianas reais (19,5h e 14,0h). Baseline $H_0$ pooled ($\mu_{\log}=2{,}80$, $\sigma_{\log}=0{,}92$) para simulações Q1 e Q3. |
| **P5** | **Médias vs. Postos** | O que cada um dos dois testes compara de fato (médias, postos, proporções...)? | Seção 3 (G2 painéis e Tabela S01) e Seção 6 | Welch compara médias ponderadas (escala linear métrica); Mann-Whitney compara postos ordenados (dominância estocástica). Outliers distorcem Welch e preservam MW. |

---

## 4. Dicas para a Apresentação e Ensaio com o Grupo

1. **Postura e Transição:**  
   Ao assumir a palavra para abrir a apresentação, introduza o cenário e o repositório FastAPI com calma, mantendo o tom profissional e direto.
2. **Uso Ativo do Dashboard:**  
   Não se limite a falar: mova o cursor para a Seção 1 (Pergunta e Hipóteses), Seção 2 (Gráfico G1 e tabela comparativa) e Seção 3 (Gráfico G2) sincronizadamente com o discurso.
3. **Controle de Tempo:**  
   Cada resposta foi projetada para durar entre 25 e 32 segundos em ritmo de fala natural e seguro. Treine com cronômetro para nunca ultrapassar 35 segundos por pergunta.
4. **Alinhamento com as Perguntas Subsequentes:**  
   As Perguntas 1 a 5 estabelecem as bases metodológicas para as Perguntas 6 a 10 (mecanismos dos testes e erros) e 11 a 15 (violações e conclusões). Mantenha a terminologia perfeitamente consistente com o restante da equipe.
