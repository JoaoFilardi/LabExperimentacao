# [LAB04FINAL] Preparação para a Apresentação Oral — Perguntas 11 a 15
**Issue correspondente:** `#62`  
**Laboratório:** LAB04 — Testes de Hipótese por Dentro: Cenário, Simulação e Visualização  
**Disciplina:** Laboratório de Experimentação de Software — 6º Período  
**Professor:** Danilo Maia  
**Par Selecionado:** P1 (Teste t de Welch × Teste U de Mann-Whitney)  

---

## 1. Instruções Rápidas para o Momento da Apresentação

- **Tempo alvo por pergunta:** ~30 segundos (respostas curtas, diretas e objetivas).
- **Regra de ouro:** Sempre responder **apontando para a seção/gráfico correspondente no próprio Dashboard** (`http://localhost:8501`).
- **Apoio interativo no Dashboard:** Ao final da **Seção 7 (Conclusão)** do `app.py`, há um painel expansível (*"Roteiro de Apoio para a Apresentação Oral — Perguntas 11 a 15"*) com os cartões de resposta rápida e as tabelas auxiliares de $\alpha = 0{,}01$ e de tamanho amostral ($n = 15, \delta = 5\%$).

---

## 2. Roteiro de Fala (~30s) e Apoio Visual por Pergunta

### Pergunta 11 — Violação de Pressupostos (Q3) e Sensibilidade Diferencial
> **Pergunta do Professor:** *"Que violação de pressuposto vocês simularam, e por que ela afeta mais um teste do que o outro?"*

- **Onde apontar no Dashboard:**
  1. Na **Seção 4 (Gráfico G3)**, apontar para o **2º par de barras** (*Violação: Outliers 10%*) e para o **3º par de barras** (*Violação: Amostra Pequena $n=10$*).
  2. Na **Seção 5 (Gráfico G4)**, apontar para a queda drástica da **curva tracejada azul** (*t de Welch — Outliers 10%*) em comparação com a **curva tracejada laranja** (*Mann-Whitney — Outliers 10%*).
- **Fala direta (30 segundos):**
  > *"Simulamos duas violações severas na Q3: primeiro, a injeção de 10% de outliers extremos multiplicando o tempo por 5 vezes mais 50 horas; segundo, a redução da amostra para $n = 10$ PRs por grupo sob forte assimetria log-normal.  
  > Elas afetam drasticamente o teste t de Welch porque os outliers entram elevados ao quadrado no cálculo da variância amostral ($s^2$), inflando o erro padrão no denominador de $t$ e derrubando seu poder em $\delta = 50\%$ de $64{,}20\%$ para apenas $22{,}62\%$ ($-41{,}58\text{ p.p.}$), além de $n = 10$ inviabilizar o Teorema Central do Limite.  
  > Já o teste U de Mann-Whitney converte os tempos em postos ordenados de $1$ a $60$, limitando qualquer valor extremo ao posto máximo e mantendo $62{,}30\%$ de poder mesmo sob outliers severos."*
- **Dados de backup caso o professor aprofunde:**
  - **No Erro Tipo I (G3):** Welch cai de $3{,}93\%$ (base) para **$3{,}28\%$** (outliers) e **$2{,}90\%$** ($n=10$), ficando fortemente conservador; Mann-Whitney permanece estável em **$4{,}52\%$** (outliers) e **$4{,}33\%$** ($n=10$).
  - **No Poder em $\delta = 50\%$ (G4):** A perda de poder de Welch com outliers é de **$-41{,}58\text{ p.p.}$** ($64{,}20\% \to 22{,}62\%$), mais do que o dobro da perda de Mann-Whitney (**$-16{,}78\text{ p.p.}$**, $79{,}08\% \to 62{,}30\%$), gerando uma vantagem de **$+39{,}68\text{ p.p.}$** para o teste não-paramétrico.

---

### Pergunta 12 — Mudança de $\alpha = 0{,}05$ para $\alpha = 0{,}01$ no G3 e no G4
> **Pergunta do Professor:** *"Se vocês usassem $\alpha = 0{,}01$ em vez de $0{,}05$, o que mudaria no G3 e no G4?"*

- **Onde apontar no Dashboard:**
  1. Na **Seção 4 (Gráfico G3)**, apontar para a **linha horizontal tracejada vermelha em $5{,}0\%$**.
  2. Na **Seção 5 (Gráfico G4)**, apontar para o **painel esquerdo** mostrando como todas as curvas se deslocariam para baixo/direita.
- **Fala direta (30 segundos):**
  > *"Se reduzíssemos $\alpha$ de $0{,}05$ para $0{,}01$, exigiríamos evidência muito mais forte ($p < 0{,}01$) para rejeitar $H_0$.  
  > No gráfico G3, a linha horizontal de referência desceria de $5\%$ para $1\%$, e as barras empíricas de Erro Tipo I cairiam proporcionalmente: no cenário base, Mann-Whitney cairia de $4{,}58\%$ para $0{,}81\%$ e Welch de $3{,}93\%$ para $0{,}42\%$, mantendo o perfil conservador do teste t.  
  > Já no gráfico G4, como o limiar crítico fica mais rigoroso, todas as curvas de poder se deslocariam para baixo e para a direita: em $\delta = 50\%$, o poder de Mann-Whitney cairia de $79{,}08\%$ para $55{,}47\%$ e o de Welch de $64{,}20\%$ para $34{,}14\%$, aumentando o Erro Tipo II ($\beta$) em troca de menos falsos positivos."*
- **Tabela empírica exata ($\alpha = 0{,}05$ vs. $\alpha = 0{,}01$, 10.000 simulações, `semente = 42`):**

| Efeito ($\delta$) | Papel Estatístico | Welch ($\alpha=5\%$) | Welch ($\alpha=1\%$) | Queda Welch | Mann-Whitney ($\alpha=5\%$) | Mann-Whitney ($\alpha=1\%$) | Queda MW |
|---|---|---|---|---|---|---|---|
| **$0\%$ ($H_0$)** | **Erro Tipo I (G3)** | $3{,}93\%$ | **$0{,}42\%$** | $-3{,}51\text{ p.p.}$ | $4{,}58\%$ | **$0{,}81\%$** | $-3{,}77\text{ p.p.}$ |
| **$10\%$** | **Poder (G4)** | $5{,}46\%$ | **$0{,}76\%$** | $-4{,}70\text{ p.p.}$ | $6{,}88\%$ | **$1{,}54\%$** | $-5{,}34\text{ p.p.}$ |
| **$20\%$** | **Poder (G4)** | $10{,}92\%$ | **$2{,}30\%$** | $-8{,}62\text{ p.p.}$ | $14{,}30\%$ | **$4{,}38\%$** | $-9{,}92\text{ p.p.}$ |
| **$30\%$** | **Poder (G4)** | $22{,}49\%$ | **$6{,}39\%$** | $-16{,}10\text{ p.p.}$ | $29{,}59\%$ | **$11{,}91\%$** | $-17{,}68\text{ p.p.}$ |
| **$40\%$** | **Poder (G4)** | $40{,}52\%$ | **$15{,}65\%$** | $-24{,}87\text{ p.p.}$ | $52{,}82\%$ | **$28{,}32\%$** | $-24{,}50\text{ p.p.}$ |
| **$50\%$** | **Poder (G4)** | $64{,}20\%$ | **$34{,}14\%$** | **$-30{,}06\text{ p.p.}$** | $79{,}08\%$ | **$55{,}47\%$** | **$-23{,}61\text{ p.p.}$** |

---

### Pergunta 13 — Expectativa Pré-Simulação × Resultados (e Variante de Subdimensionamento $n=15, \delta=5\%$)

> **Nota importante:** Cobrimos abaixo as **duas formulações** da Pergunta 13 presentes no material da disciplina (a formulação da Seção 5 do `README.md` sobre expectativa pré-simulação e a formulação de arguição sobre detecção de efeito de $5\%$ com $n = 15$).

#### Formulação A (Seção 5 do `README.md`): Expectativa antes de simular × O que a simulação mostrou
> **Pergunta do Professor:** *"A simulação confirmou o que o grupo esperava antes de simular? Se não, o que explica a diferença?"*

- **Onde apontar no Dashboard:**
  1. Na **Seção 1 (Cenário)** e **Seção 7 (Conclusão)**, onde está registrada a previsão pré-simulação do grupo.
  2. Nos gráficos **G3** (Seção 4) e **G4** (Seção 5).
- **Fala direta (30 segundos):**
  > *"Sim, a simulação confirmou integralmente nossa expectativa teórica prévia: antes de simular, previmos que o teste U de Mann-Whitney superaria o teste t de Welch porque os tempos de merge seguem uma distribuição log-normal fortemente assimétrica à direita (assimetria acima de $1{,}45$ e razão média/mediana de $1{,}45\times$).  
  > O ponto mais interessante que a simulação esclareceu na prática foi a direção do desvio do teste t no G3: em vez de ficar liberal (inflando falsos positivos), o teste t de Welch ficou sistematicamente conservador ($3{,}93\%$ na base e $3{,}28\%$ com outliers), porque quando ambos os grupos compartilham caudas pesadas, os extremos inflam o denominador da estatística $t$, reduzindo tanto as rejeições sob $H_0$ quanto o poder sob $H_1$."*

#### Formulação B (Variante de arguição / Seção 6): Efeito de $5\%$ com amostra $n = 15$
> **Pergunta do Professor:** *"Se o efeito verdadeiro é de 5%, mas a amostra tem $n = 15$, vocês esperam que os testes o detectem? Onde isso aparece nos gráficos?"*

- **Onde apontar no Dashboard:**
  - No **canto inferior esquerdo do Gráfico G4 (Seção 5)**, entre $\delta = 0\%$ e $\delta = 10\%$, apontando para a proximidade das curvas em relação à linha vermelha de $\alpha = 5\%$ e para as curvas pontilhadas de amostra pequena ($n = 10$).
- **Fala direta (30 segundos):**
  > *"Não esperamos que nenhum dos dois testes o detecte. Isso aparece claramente no canto inferior esquerdo do gráfico G4: mesmo com $n = 30$, para efeitos pequenos de $5\%$ a $10\%$ o poder fica entre $4{,}4\%$ e $7{,}1\%$, praticamente colado na linha vermelha de $\alpha = 5\%$; e na curva pontilhada de amostra reduzida ($n = 10$) o poder em $\delta = 10\%$ é de apenas $3{,}41\%$ a $5{,}13\%$.  
  > Simulando especificamente $n = 15$ com efeito de $5\%$, Mann-Whitney tem apenas $4{,}45\%$ de poder e Welch $3{,}35\%$, ou seja, mais de $95\%$ de chance de cometer Erro Tipo II ($\beta$) por subdimensionamento amostral."*

---

### Pergunta 14 — Conclusão nos Dados Reais e Importância Prática do Tamanho do Efeito
> **Pergunta do Professor:** *"Nos dados reais, os dois testes chegaram à mesma conclusão? O tamanho do efeito tem importância prática?"*

- **Onde apontar no Dashboard:**
  1. Na **Tabela da Seção 6 (Dados reais)**, apontando para a coluna `p_valor` (`0.0969` no t de Welch vs. `0.0446` no Mann-Whitney) e `decisao_h0`.
  2. Na **Seção 2 (Gráfico G1)**, apontando para os outliers na cauda direita do histograma de dados reais.
- **Fala direta (30 segundos):**
  > *"Não, nos dados reais minerados do repositório `tiangolo/fastapi` ($n = 30$ por grupo) os dois testes chegaram a conclusões opostas a $\alpha = 5\%$: o teste U de Mann-Whitney rejeitou $H_0$ ($U = 577{,}5$; $p = 0{,}0446$), enquanto o teste t de Welch não rejeitou $H_0$ ($t = 1{,}688$; $p = 0{,}0969$).  
  > Isso aconteceu porque os $3$ outliers severos do grupo com bot (PRs de $53\text{ h}$ a $70\text{ h}$) inflaram o desvio padrão para $19{,}21\text{ h}$, mascarando o efeito no teste t — exatamente como previsto pelo gráfico G4.  
  > E sim, o tamanho do efeito tem grande importância prática: a mediana caiu $48{,}2\%$ (de $16{,}49\text{ h}$ para $8{,}54\text{ h}$, economizando quase $8\text{ horas}$ de espera por PR), com correlação rank-biserial de $+0{,}2833$ e $d$ de Cohen de $+0{,}4358$."*
- **Resumo numérico da Seção 6 para consulta rápida:**
  - **Grupo `sem_bot` ($n=30$):** Média $= 25{,}75\text{ h}$ ($\text{DP} = 21{,}24\text{ h}$), Mediana $= 16{,}49\text{ h}$ ($\text{IQR} = 18{,}91\text{ h}$).
  - **Grupo `com_bot` ($n=30$):** Média $= 16{,}92\text{ h}$ ($\text{DP} = 19{,}21\text{ h}$), Mediana $= 8{,}54\text{ h}$ ($\text{IQR} = 11{,}62\text{ h}$).
  - **Redução absoluta e relativa:** $-8{,}83\text{ h}$ na média ($-34{,}3\%$) e $-7{,}95\text{ h}$ na mediana ($-48{,}2\%$).

---

### Pergunta 15 — Recomendação Oficial, Quando Mudar de Escolha e Principal Limitação
> **Pergunta do Professor:** *"Qual teste vocês recomendam para o cenário, em que situação mudariam a recomendação, e qual é a principal limitação do estudo?"*

- **Onde apontar no Dashboard:**
  1. Na **Seção 7 (Conclusão)**.
  2. No **Painel Direito do Gráfico G4 (Seção 5)**, apontando primeiro para a **zona superior laranja ($\Delta > 0$)** onde Mann-Whitney domina nos cenários log-normais, e depois para a **curva azul traço-ponto na zona inferior azul ($\Delta < 0$)** do Controle Normal Simétrico.
- **Fala direta (30 segundos):**
  > *"Recomendamos o teste U de Mann-Whitney para avaliar o tempo de merge de Pull Requests e métricas de engenharia de software assimétricas, pois ele mantém o Erro Tipo I calibrado perto de $5\%$ ($4{,}58\%$) e entrega até $+39{,}68$ pontos percentuais a mais de poder que Welch quando há outliers.  
  > Mudaríamos a recomendação para o teste t de Welch se os dados seguissem uma distribuição Normal simétrica sem outliers — situação mostrada na zona azul do painel direito do G4, onde Welch supera Mann-Whitney ($65{,}73\%$ vs. $63{,}03\%$ em $\delta = 30\%$ devido à eficiência assintótica relativa de $95{,}5\%$ dos postos sob normalidade) — ou se a decisão gerencial exigisse estritamente inferência sobre a média em grande amostra.  
  > A principal limitação do estudo é que a amostra real é observacional e de um único repositório (`tiangolo/fastapi`, $n = 30$), sem controle para variáveis confundidoras como tamanho do PR em linhas de código, complexidade ou número de revisores."*

---

## 3. Quadro-Resumo de Bolso (Perguntas 11 a 15)

| Pergunta | Onde Olhar no Dashboard | Número-Chave Principal | Conclusão em 1 Frase |
|---|---|---|---|
| **11. Violação de pressupostos (Q3)** | **G3** (barras 2 e 3) e **G4** (curvas tracejadas/pontilhadas) | Poder em $\delta=50\%$ com outliers: **MW $62{,}30\%$ vs. Welch $22{,}62\%$** ($\Delta = +39{,}68\text{ p.p.}$) | Outliers entram ao quadrado em $s^2$ e destroem o poder de Welch, enquanto Mann-Whitney limita qualquer extremo ao posto máximo. |
| **12. Uso de $\alpha = 0{,}01$** | **G3** (linha de $5\% \to 1\%$) e **G4** (painel esquerdo) | Em $\alpha=1\%$: G3 base cai p/ **$0{,}81\%$ (MW)** e **$0{,}42\%$ (Welch)**; G4 em $\delta=50\%$ cai p/ **$55{,}47\%$** e **$34{,}14\%$** | Reduzir $\alpha$ para $1\%$ corta falsos positivos no G3, mas desloca as curvas do G4 para baixo/direita (menor poder, maior Erro Tipo II). |
| **13. Expectativa × Simulação (e $n=15, \delta=5\%$)** | **Seção 1**, **G3/G4** e canto inferior esquerdo do **G4** | Expectativa confirmada; Welch ficou **conservador ($3{,}93\%$)**; em $n=15, \delta=5\%$ poder é **$4{,}45\%$ (MW)** e **$3{,}35\%$ (Welch)** | A assimetria log-normal confirmou a superioridade de Mann-Whitney e revelou o conservadorismo de Welch; efeitos de $5\%$ com $n=15$ têm $>95\%$ de Erro Tipo II. |
| **14. Dados reais e efeito prático** | **Seção 6** (Tabela de dados reais) e **G1** | **MW $p = 0{,}0446$** (rejeita $H_0$) vs. **Welch $p = 0{,}0969$** (não rejeita); mediana cai **$-48{,}2\%$** ($-7{,}95\text{ h}$) | Os testes divergiram nos dados reais por causa dos outliers, e a economia de quase $8\text{ h}$ na mediana tem alta relevância prática. |
| **15. Recomendação, mudança e limitação** | **Seção 7** e **Painel Direito do G4** (zona azul $\Delta < 0$) | **MW recomendado** ($+14{,}88$ a $+39{,}68\text{ p.p.}$); **Welch vence na Normal** ($65{,}73\%$ vs. $63{,}03\%$ em $\delta=30\%$) | Recomendamos Mann-Whitney para tempos assimétricos de software, mudando para Welch sob normalidade sem outliers; a limitação é o desenho observacional em repositório único ($n=30$). |
