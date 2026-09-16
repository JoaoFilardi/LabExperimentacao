# Desenho Experimental: Impacto de Assistentes de IA na Codificação

**Disciplina:** Laboratório de Experimentação de Software — 6º Período  
**Artefato:** Sprint 01 — Issue #01: Desenho Experimental, Hipóteses e Ameaças à Validade  
**Status:** Aprovado / Publicação Oficial  

---

## 1. Objetivo da Pesquisa (Abordagem GQM)

O objetivo segue o padrão estruturado GQM (*Goal-Question-Metric*) de Basili et al. (1994):

> **Analisar** o uso de assistentes de inteligência artificial generativa na resolução de tarefas de programação,  
> **com o propósito de** comparar sua eficácia frente à codificação manual tradicional,  
> **com respeito a** tempo de resolução (*time-to-green*), qualidade funcional (defeitos e testes aprovados) e qualidade estrutural do código (complexidade ciclomática e linhas de código),  
> **do ponto de vista** dos pesquisadores e engenheiros de software,  
> **no contexto de** katas de programação de complexidade equivalente, resolvidos individualmente sob delineamento *crossover within-subject* e *time-box* rígido de 35 minutos.

### Mapeamento Questions & Metrics (RQ1 a RQ3)

* **RQ1 (Produtividade Temporal):** *O uso de assistente de IA reduz o tempo necessário para resolver uma tarefa de programação?*
  * **Métrica Primária:** *Time-to-green* ($T_{\text{TTG}}$), medido em minutos desde o início do trial até a aprovação de 100% dos testes de aceitação (`exit code 0`).
  * **Censura de Dados:** Se atingir o *time-box* de 35 minutos sem aprovação total, fixa-se $T_{\text{TTG}} = 35.0$ minutos com flag de censura à direita ($\delta = 1$). O trial **não** é descartado.
  * **Métrica Agregada:** Mediana e Intervalo Interquartil ($IQR = Q_3 - Q_1$), robustos a outliers e censuras.
  * **Métrica Exploratória:** Quantidade de prompts e interações com a IA ($N_{\text{prompts}}$).

* **RQ2 (Qualidade Funcional e Defeitos):** *O uso de assistente de IA reduz a quantidade de defeitos (testes que falham) no código final?*
  * **Métrica Primária:** Taxa de Sucesso nos Testes ($SR_{\text{test}}$), normalizando katas com diferentes volumes de asserções:
    $$SR_{\text{test}} = \left( \frac{N_{\text{pass}}}{N_{\text{total}}} \right) \times 100\%$$
  * **Métrica Secundária:** Contagem absoluta de testes falhando ao término do tempo ($N_{\text{fail}} = N_{\text{total}} - N_{\text{pass}}$).
  * **Métrica Complementar:** Densidade de defeitos por KLOC ($FD = \frac{N_{\text{fail}}}{LOC / 1000}$).

* **RQ3 (Qualidade Estrutural):** *O uso de assistente de IA altera a complexidade ciclomática ou o tamanho do código produzido?*
  * **Métrica Primária:** Complexidade Ciclomática média de McCabe ($CC$) por função/método, obtida via Radon/CK ($v(G) = E - N + 2P$).
  * **Métrica de Controle Obrigatória:** Linhas de Código Efetivas ($SLOC / LOC$), essencial para verificar se o código gerado por IA é conciso ou excessivamente prolixo.
  * **Métrica Complementar:** Índice de Manutenibilidade ($MI$), combinando $v(G)$, Halstead e $LOC$.

| Dimensão | Questão | Métrica | Escala / Unidade | Ferramenta |
| :--- | :---: | :--- | :---: | :--- |
| **Tempo** | **RQ1** | *Time-to-green* ($T_{\text{TTG}}$) | Minutos ($[0, 35]$) | Cronômetro / Runner |
| **Tempo** | **RQ1** | Censura ($\delta$) | Binário ($\{0, 1\}$) | Log do trial |
| **Qualidade Funcional** | **RQ2** | Taxa de Sucesso ($SR_{\text{test}}$) | Percentual ($[0, 100]\%$) | `pytest` / `JUnit` |
| **Qualidade Funcional** | **RQ2** | Testes Falhando ($N_{\text{fail}}$) | Inteiro ($\ge 0$) | `pytest` / `JUnit` |
| **Qualidade Estrutural** | **RQ3** | Complexidade Ciclomática ($CC$) | Inteiro ($\ge 1$) | Radon (`cc`) / CK |
| **Qualidade Estrutural** | **RQ3** | Linhas de Código ($SLOC$) | Inteiro ($\ge 1$) | Radon (`raw`) / CK |
| **Qualidade Estrutural** | **RQ3** | Índice de Manutenibilidade ($MI$) | Escalar ($[0, 100]$) | Radon (`mi`) |

---

## 2. Formalização das Hipóteses Estatísticas

Compara-se o **Tratamento A (Manual)** contra o **Tratamento B (Com IA)** em amostras pareadas. Como os dados possuem tamanho amostral reduzido e presença de censuras, as hipóteses avaliam a mediana populacional ($M$) ou dominância estocástica:

### 2.1. Hipótese RQ1 — Produtividade Temporal (Teste Unilateral à Esquerda)
* **Hipótese Nula ($H_{0,1}$):** O uso de IA não reduz o tempo de resolução; o tempo com IA é igual ou superior ao manual.
  $$H_{0,1}: \text{Mediana}(T_{\text{IA}}) \ge \text{Mediana}(T_{\text{Manual}})$$
* **Hipótese Alternativa ($H_{1,1}$):** O uso de IA reduz significativamente o tempo de resolução.
  $$H_{1,1}: \text{Mediana}(T_{\text{IA}}) < \text{Mediana}(T_{\text{Manual}})$$

### 2.2. Hipótese RQ2 — Qualidade Funcional (Teste Unilateral à Direita)
* **Hipótese Nula ($H_{0,2}$):** O uso de IA não eleva a taxa de aprovação nos testes de aceitação ao final do tempo limite.
  $$H_{0,2}: \text{Mediana}(SR_{\text{IA}}) \le \text{Mediana}(SR_{\text{Manual}})$$
* **Hipótese Alternativa ($H_{1,2}$):** O uso de IA eleva significativamente a taxa de aprovação nos testes.
  $$H_{1,2}: \text{Mediana}(SR_{\text{IA}}) > \text{Mediana}(SR_{\text{Manual}})$$

### 2.3. Hipótese RQ3 — Qualidade Estrutural (Testes Bilaterais)
Como modelos de IA podem gerar tanto código enxuto quanto estruturas prolixas ou excessivamente aninhadas, adota-se teste bicaudal:

* **Complexidade Ciclomática ($CC$):**
  * $H_{0,3a}: \text{Mediana}(CC_{\text{IA}}) = \text{Mediana}(CC_{\text{Manual}})$ (não altera a complexidade).
  * $H_{1,3a}: \text{Mediana}(CC_{\text{IA}}) \neq \text{Mediana}(CC_{\text{Manual}})$ (altera significativamente a complexidade).
* **Volume de Código ($LOC$):**
  * $H_{0,3b}: \text{Mediana}(LOC_{\text{IA}}) = \text{Mediana}(LOC_{\text{Manual}})$ (não altera o volume de linhas).
  * $H_{1,3b}: \text{Mediana}(LOC_{\text{IA}}) \neq \text{Mediana}(LOC_{\text{Manual}})$ (altera significativamente o volume de linhas).

---

## 3. Desenho Experimental e Protocolo de Execução

### 3.1. Arquitetura Within-Subject (Crossover Contrabalanceado)

Para anular a grande variabilidade individual de habilidade entre desenvolvedores ($10\times$ a $20\times$), cada participante é submetido a ambos os tratamentos (*within-subject*), servindo como seu próprio controle.

Para mitigar o **efeito de aprendizado** e o **efeito de ordem**:
1. Nenhum participante resolve o mesmo kata duas vezes.
2. Cada participante resolve exatamente 50% dos trials sob Tratamento A (Manual) e 50% sob Tratamento B (Com IA).
3. A ordem dos tratamentos é contrabalanceada entre os integrantes.

#### Matriz de Alocação de Trials

| Participante | Trial 1 | Trial 2 | Trial 3 | Trial 4 | Proporção |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **$P_1$ (Dev 1)** | $K_1$ — Manual | $K_2$ — Com IA | $K_3$ — Manual | $K_4$ — Com IA | 2 Manual / 2 IA |
| **$P_2$ (Dev 2)** | $K_1$ — Com IA | $K_2$ — Manual | $K_4$ — Manual | $K_3$ — Com IA | 2 Manual / 2 IA |
| **$P_3$ (Dev 3)** | $K_2$ — Com IA | $K_1$ — Manual | $K_4$ — Com IA | $K_3$ — Manual | 2 Manual / 2 IA |
| **Total Amostral** | **2 Manual / 1 IA** | **1 Manual / 2 IA** | **2 Manual / 1 IA** | **1 Manual / 2 IA** | **6 Manual / 6 IA (12 trials)** |

### 3.2. Condições Experimentais

* **Tratamento A (Manual / Baseline):** Resolução autônoma do desenvolvedor na IDE (VS Code) com extensões de IA desabilitadas. Permitida apenas consulta à documentação oficial da linguagem. Proibido qualquer chatbot, autocomplete baseado em LLM ou busca de soluções prontas.
* **Tratamento B (Assistido por IA):** Mesmo ambiente integrado a assistente de IA generativa (ex.: GitHub Copilot) com versão/modelo padronizados. Livre uso de autocompletar, geração de funções e depuração, com arquivamento obrigatório de todos os prompts.

### 3.3. Protocolo Operacional do Trial

1. **Time-box Rígido:** Limite máximo de **35 minutos** por trial. Se a suíte passar com 100% de sucesso antes, o cronômetro é pausado no $T_{\text{TTG}}$ exato. Ao atingir 35 minutos, encerra-se imediatamente.
2. **Censura de Dados (Data Censoring):** Trials que atingem 35 min sem aprovação completa recebem $T_{\text{TTG}} = 35.0$ min e indicador $\delta = 1$. O descarte é estritamente proibido para evitar *viés de sobrevivência* (*survivorship bias*).
3. **Rastreabilidade e Logs:** Cada trial é registrado como Issue no GitHub Projects com Assignee específico. O código final é commitado referenciando o número da Issue, registrando tempo, status dos testes, prompts enviados e métricas estáticas.

---

## 4. Mapeamento de Variáveis

* **Variável Independente:** Auxílio do Assistente de IA Generativa (fator qualitativo nominal de 2 níveis: Nível 0 = Ausente / Manual; Nível 1 = Presente / Com IA).
* **Variáveis Dependentes:**
  * *Time-to-green* ($T_{\text{TTG}}$ em minutos decimais, censurado em 35.0 min);
  * Taxa de sucesso nos testes de aceitação ($SR_{\text{test}}$ em %);
  * Contagem de falhas nos testes ($N_{\text{fail}}$);
  * Complexidade Ciclomática média de McCabe ($CC$);
  * Linhas efetivas de código ($SLOC$);
  * Índice de Manutenibilidade ($MI$).
* **Variáveis de Controle:**
  * *Ambiente Técnico:* Versão fixa de runtime (Python 3.14 / 3.11), VS Code padronizado e runner de testes idêntico (`pytest`).
  * *Suíte de Testes:* Testes de aceitação fechados e imutáveis em cada kata (6 testes unitários por kata).
  * *Objetos Experimentais:* 4 katas autorais com complexidade similar, escopo de arquivo único e baixa indexação na web.
  * *Participantes:* Estudantes do mesmo período letivo (6º período de Engenharia de Software) com experiência homogênea.

---

## 5. Ameaças à Validade e Estratégias de Mitigação

### 5.1. Validade Interna
* **Efeito de Aprendizado:** Mitigado pelo delineamento *crossover contrabalanceado*, garantindo que nenhum participante resolva o mesmo kata duas vezes.
* **Efeito de Fadiga:** Mitigado pela limitação de no máximo 2 trials por dia por participante, com intervalo obrigatório de repouso (mínimo de 30 minutos).
* **Memorização dos Modelos de IA (*Data Leakage*):** Mitigado pelo uso de katas autorais/pouco indexados, alterando contexto de domínio e assinaturas para que a IA não recupere respostas prontas de seu pré-treinamento.
* **Comunicação entre Participantes:** Mitigado pelo isolamento das sessões e embargo de compartilhamento de código até a conclusão de todos os trials.

### 5.2. Validade Externa
* **Representatividade das Tarefas (*Toy Problems* vs. Produção):** Katas são problemas isolados e menores que sistemas corporativos legados. Reconhece-se explicitamente que os resultados aplicam-se à fase de codificação e raciocínio algorítmico individual.
* **Perfil dos Desenvolvedores:** Participantes representam engenheiros de software em nível de entrada (*junior*), conforme aceito na literatura empírica (Runeson et al., 2003).

### 5.3. Validade de Construção
* **Time-to-green como Produtividade:** Aferir apenas o tempo poderia premiar soluções apressadas ou com débitos técnicos. Mitigado pela exigência de 100% de cobertura nos testes de aceitação e pela triangulação com métricas estruturais ($CC$, $SLOC$, $MI$).
* **Limitações da Métrica de McCabe:** A complexidade ciclomática mede apenas ramificações de controle. Mitigado pelo uso conjunto de $SLOC$ e do Índice de Manutenibilidade.

### 5.4. Validade de Conclusão Estatística
* **Amostra Pequena e Não-Normalidade:** Com 12 trials e censuras aos 35 min, viola-se a normalidade. Mitiga-se adotando o **Teste de Postos com Sinais de Wilcoxon** (*Wilcoxon Signed-Rank Test*), teste não-paramétrico pareado, com reporte de medianas e $IQR$.
* **Viés de Sobrevivência:** Mitigado pelo tratamento formal de censura à direita ($35.0$ min), mantendo a penalidade estatística das tarefas incompletas.
* **Tamanho de Efeito:** Mitigado pelo cálculo do coeficiente $r$ de Rosenthal ($r = \frac{|Z|}{\sqrt{N}}$) e *Cliff's Delta*.

---

## 6. Referências Principais

1. **Basili, V. R., Caldiera, G., & Rombach, H. D.** (1994). *The Goal Question Metric Approach*. Encyclopedia of Software Engineering.
2. **Wohlin, C. et al.** (2012). *Experimentation in Software Engineering*. Springer.
3. **McCabe, T. J.** (1976). *A Complexity Measure*. IEEE Transactions on Software Engineering.
4. **Wilcoxon, F.** (1945). *Individual comparisons by ranking methods*. Biometrics Bulletin.
