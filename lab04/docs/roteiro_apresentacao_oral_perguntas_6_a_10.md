# [LAB04FINAL] Roteiro Individual da Apresentação Oral — Perguntas 6 a 10

**Issue correspondente:** `#60` (`[ LAB04FINAL ] Preparar apresentação oral das perguntas 6 a 10`)  
**Responsável:** Tiago Boaventura Amaral  
**Laboratório:** LAB04 — Testes de Hipótese por Dentro: Cenário, Simulação e Visualização  
**Disciplina:** Laboratório de Experimentação de Software — 6º Período  
**Professor:** Danilo Maia  

---

## 1. Visão Geral e Estratégia de Apresentação

- **Tempo por Pergunta:** Rigorosamente **~30 segundos** por resposta (tempo total do bloco: ~2 minutos e 30 segundos).
- **Abordagem Didática:** Apontar diretamente para a seção e para o gráfico correspondente no **Dashboard** antes ou durante a fala, vinculando o conceito teórico aos dados da simulação.
- **Foco Temático:** Compreensão da distribuição nula da estatística sob $H_0$ e da região crítica no **Gráfico G2**, significados e equívocos clássicos do **p-valor**, balanço de risco entre **Erro Tipo I e Erro Tipo II**, taxas empíricas de falso positivo no **Gráfico G3** e dinâmica das curvas de **Poder Estatístico no Gráfico G4**.

---

## 2. Fichas Detalhadas das Perguntas 6 a 10

---

### Pergunta 6 — Distribuição da Estatística sob $H_0$ e Região de Rejeição (G2)

- **Enunciado Oficial:** *"No G2: o que é a distribuição da estatística sob H₀, e por que a região de rejeição fica onde fica?"*
- **Pergunta Variante da Banca:** *"Por que a região de rejeição é dividida em duas caudas e o que define a fronteira crítica?"*
- **Seção do Dashboard:** `Seção 3. Como os testes funcionam`
- **Onde Apontar na Tela:**  
  Apontar para o **Gráfico G2**:
  1. A **curva cinza** central (distribuição teórica da estatística sob a hipótese nula $H_0$);
  2. As **duas áreas vermelhas sombreadas** nas pontas extremas (caudas de $2{,}5\%$ cada);
  3. As **linhas verticais tracejadas de corte crítico**: $t = \pm 2{,}0085$ no painel esquerdo (Welch) e $z = \pm 1{,}95996$ no painel direito (Mann-Whitney).

#### Fala Direta de 30 Segundos:
> *"A distribuição da estatística sob H₀ representa todos os valores que a estatística de teste assumiria por puro acaso se a hipótese nula fosse verdadeira, isto é, se os bots não alterassem o tempo de merge. No painel esquerdo temos a distribuição t de Student com 50,6 graus de liberdade e no direito a Normal padrão Z. A região de rejeição fica nas duas caudas mais extremas porque nosso teste é bicaudal com α = 5%, alocando 2,5% da probabilidade em cada lado: observar uma estatística tão distante do centro sob H₀ é tão improvável (menos de 5% de chance) que nos leva a rejeitar a hipótese de igualdade."*

#### Resposta Direta para a Pergunta Variante (30 Segundos):
> *"Como a nossa pergunta investiga se os bots aumentam OU diminuem o tempo de merge (teste bicaudal), o risco de falso positivo de 5% é repartido igualmente: 2,5% na cauda esquerda (efeito de aceleração) e 2,5% na cauda direita (efeito de atraso). Os limites críticos (t = ±2,01 e z = ±1,96) delimitam exatamente o ponto a partir do qual a probabilidade acumulada sob H₀ torna-se inferior a 5%."*

#### Pontos-Chave e Fundamentação Técnica:
- **Distribuição sob $H_0$:** É a distribuição amostral teórica da estatística quando não existe efeito de tratamento ($\mu_{\text{com}} = \mu_{\text{sem}}$ ou $P(X_{\text{com}} > Y_{\text{sem}}) = 0{,}50$).
- **Painel Esquerdo (Welch):** Distribuição $t$ de Student com graus de liberdade de Welch-Satterthwaite ($\nu \approx 50{,}61$). Limites críticos bicaudais: $t_{\text{crit}} = \pm 2{,}0085$.
- **Painel Direito (Mann-Whitney):** Distribuição Normal padronizada $Z \sim \mathcal{N}(0, 1)$ obtida pela aproximação assintótica da soma de postos. Limites críticos: $z_{\text{crit}} = \pm 1{,}9600$.
- **Por que fica nos extremos?** Sob $H_0$, a maior densidade de probabilidade concentra-se em torno de zero (ausência de diferença). Valores nas caudas têm densidade ínfima; portanto, se observarmos uma estatística nessa região extrema, a hipótese de que ela decorre de mero ruído amostral torna-se implausível.

---

### Pergunta 7 — Significado e Equívocos Conceituais do p-valor no Exemplo (G2)

- **Enunciado Oficial:** *"O que significa o p-valor do exemplo mostrado no G2? E o que ele não significa?"*
- **Pergunta Variante da Banca:** *"Se o p-valor for maior que 0,05, isso prova que H₀ é verdadeira?"*
- **Seção do Dashboard:** `Seção 3. Como os testes funcionam`
- **Onde Apontar na Tela:**  
  Apontar para:
  1. A **linha vertical pontilhada** (azul/laranja) indicando a estatística observada da amostra simulada da S01 ($t_{\text{obs}} = -0{,}5828$ no painel esquerdo e $z_{\text{obs}} = -1{,}5154$ no painel direito);
  2. A **área sombreada sob a curva** além da linha observada (azul/laranja), que representa visualmente a probabilidade acumulada do p-valor ($p = 0{,}5626$ para Welch e $p = 0{,}1315$ para Mann-Whitney);
  3. A tabela da Seção 3 destacando que ambos caem **fora da região vermelha de rejeição**.

#### Fala Direta de 30 Segundos:
> *"O p-valor do exemplo é a probabilidade de sortear uma amostra com estatística tão ou mais extrema que a observada, assumindo que a hipótese nula H₀ seja verdadeira. No G2, ele é a área sob a curva além da linha da amostra: 56,26% em Welch e 13,15% em Mann-Whitney. O que ele NÃO significa: NÃO é a probabilidade de H₀ ser verdadeira, NÃO é a chance de estarmos errados e NÃO mede o tamanho do efeito ou sua importância prática. Além disso, obter p maior que 0,05 jamais 'prova' que H₀ é verdadeira: apenas indica que os dados não forneceram evidência suficiente para rejeitá-la com o tamanho da amostra."*

#### Resposta Direta para a Pergunta Variante (30 Segundos):
> *"Definitivamente não. Na inferência estatística, ausência de evidência não é evidência de ausência. Um p-valor maior que 0,05 apenas indica que os dados são estatisticamente compatíveis com H₀ diante da alta dispersão, o que frequentemente ocorre quando a amostra é moderada (n = 30) e o teste não tem poder estatístico suficiente para detectar a diferença existente (um Erro Tipo II)."*

#### Pontos-Chave e Fundamentação Técnica:
- **Definição Formal:** $p\text{-valor} = P(|T| \ge |t_{\text{obs}}| \mid H_0 \text{ é verdadeira})$.
- **Valores no Exemplo (semente = 42):**
  - Teste t de Welch: $t_{\text{obs}} = -0{,}5828 \implies p = 0{,}562615$ ($56{,}26\%$ de chance de observar diferença tão grande por acaso).
  - Teste U de Mann-Whitney: $U_{\text{obs}} = 347{,}5$ ($z_{\text{obs}} = -1{,}5154$) $\implies p = 0{,}131546$ ($13{,}15\%$ de chance sob $H_0$).
- **Três Erros Conceituais Graves a Evitar:**
  1. *Falácia da Inversão Condicional:* Achar que $p\text{-valor} = P(H_0 \mid \text{dados})$. O p-valor condiciona em $H_0$, não nos dados.
  2. *Falácia da Prova da Nula:* Afirmar que $p > 0{,}05$ prova que as médias ou postos são idênticos. O teste apenas "não rejeita $H_0$".
  3. *Falácia da Relevância:* Achar que $p$-valor mede tamanho do efeito. Efeitos triviais podem ter $p < 0{,}001$ com amostras enormes, e efeitos vitais podem ter $p > 0{,}05$ com amostras pequenas.

---

### Pergunta 8 — Erro Tipo I vs. Erro Tipo II e Gravidade no Cenário

- **Enunciado Oficial:** *"No cenário de vocês, o que seria um erro tipo I e um erro tipo II? Qual dos dois seria mais grave?"*
- **Pergunta Variante da Banca:** *"Qual é o custo prático de cada erro para uma equipe de Engenharia de Software?"*
- **Seção do Dashboard:** `Seção 1. Cenário`, `Seção 4. Erro tipo I` e `Seção 5. Poder`
- **Onde Apontar na Tela:**  
  1. Na **Seção 1**, na pergunta de pesquisa e nas hipóteses $H_0$ e $H_1$;
  2. No **Gráfico G3**, na linha horizontal de $5\%$ que limita o Erro Tipo I ($\alpha$);
  3. No **Gráfico G4**, no complemento do Poder ($100\% - \text{Poder} = \beta$, a taxa de Erro Tipo II).

#### Fala Direta de 30 Segundos:
> *"No nosso cenário, o Erro Tipo I seria concluir falsamente que os bots alteram o tempo de merge quando na verdade não há efeito, fazendo a equipe desperdiçar tempo e dinheiro mantendo automações inúteis. O Erro Tipo II seria concluir que os bots não fazem diferença quando na verdade eles reduzem o tempo de integração, descartando uma automação que aceleraria o fluxo. Consideramos o Erro Tipo II mais grave no contexto de software: o custo de manter bots de CI hoje é irrisório (GitHub Actions e linters são baratos), enquanto perder a chance de reduzir o lead time dos desenvolvedores em 20% a 30% impõe um custo de oportunidade contínuo e cumulativo muito mais pesado para a empresa."*

#### Resposta Direta para a Pergunta Variante (30 Segundos):
> *"Em termos operacionais: errar pelo Tipo I custa poucas horas de configuração de scripts e alguns dólares de computação em nuvem; já errar pelo Tipo II custa centenas de horas de engenheiros bloqueados aguardando revisões manuais por semanas a fio. Por isso, para a organização, falhar em adotar uma melhoria real de produtividade acarreta prejuízo financeiro e atraso crônico de entregas."*

#### Pontos-Chave e Fundamentação Técnica:
- **Matriz de Decisão no Cenário de Pull Requests:**

| Realidade \ Decisão do Teste | Não Rejeitar $H_0$ | Rejeitar $H_0$ (Detectar Efeito) |
|---|---|---|
| **$H_0$ Verdadeira (Bot não tem efeito)** | Decisão Correta ($1 - \alpha = 95\%$) | **Erro Tipo I ($\alpha = 5\%$)** — Falso Positivo |
| **$H_1$ Verdadeira (Bot acelera o merge)** | **Erro Tipo II ($\beta$)** — Falso Negativo | Decisão Correta (Poder $= 1 - \beta$) |

- **Análise de Custos Reais em Engenharia de Software:**
  - *Custo do Erro Tipo I:* Baixo. Instalação de GitHub Apps/Actions (ex.: Codecov, Dependabot, Pre-commit CI) tem manutenção quase nula e custo próximo de zero.
  - *Custo do Erro Tipo II:* Elevadíssimo. O tempo de desenvolvedor é o recurso mais caro de uma empresa de tecnologia. Se um bot economiza $5{,}3\text{ h}$ de espera por PR, deixar de usá-lo multiplica o desperdício por centenas de PRs ao longo do ano.

---

### Pergunta 9 — Comportamento de Erro Tipo I em G3: Liberal vs. Conservador

- **Enunciado Oficial:** *"No G3, algum teste se afastou de 5%? Ele ficou liberal ou conservador, e por quê?"*
- **Pergunta Variante da Banca:** *"Por que os outliers tornaram o teste de Welch conservador em vez de torná-lo liberal?"*
- **Seção do Dashboard:** `Seção 4. Erro tipo I`
- **Onde Apontar na Tela:**  
  Apontar para o **Gráfico G3**:
  1. A **linha tracejada vermelha** em $5{,}0\%$ e a **faixa sombreada de Bradley** ($4{,}5\%$ a $5{,}5\%$);
  2. As **barras azuis do teste t de Welch**, destacando que todas estão significativamente abaixo de $5\%$: $3{,}93\%$ no Cenário Base, $3{,}28\%$ sob Outliers e $2{,}90\%$ com Amostra Pequena ($n=10$);
  3. As **barras laranjas de Mann-Whitney**, destacando que permanecem perfeitamente dentro da faixa sombreada: $4{,}58\%$, $4{,}52\%$ e $4{,}33\%$.

#### Fala Direta de 30 Segundos:
> *"Sim, o teste t de Welch afastou-se consideravelmente dos 5%, apresentando comportamento estritamente conservador em todos os cenários simulados: registrou 3,93% na base, 3,28% com outliers e 2,90% com amostra pequena de n = 10, rejeitando H₀ consideravelmente menos do que o nível nominal esperado. O teste de Mann-Whitney, em contraste, foi exemplar, mantendo-se entre 4,33% e 4,58%, dentro da margem estrita de Bradley. O teste de Welch ficou conservador porque a assimetria lognormal e os outliers entram elevados ao quadrado na variância amostral de ambos os grupos sob H₀, inflando o erro padrão no denominador de t e comprimindo a estatística, o que eleva os p-valores e freia falsos positivos às custas de perda de sensibilidade."*

#### Resposta Direta para a Pergunta Variante (30 Segundos):
> *"Quando a contaminação por outliers ocorre sob H₀ em ambos os grupos comparados, a diferença entre as médias amostrais no numerador permanece próxima de zero, mas a variância combinada no denominador é drasticamente inflada. Como o denominador cresce quadraticamente com os valores extremos, a razão t diminui em módulo, tornando muito raro atingir a região crítica de ±2,01 — gerando o padrão conservador (taxa bem abaixo de 5%)."*

#### Pontos-Chave e Fundamentação Técnica:
- **Definições Formais de Comportamento:**
  - *Liberal:* Rejeita $H_0$ com frequência superior a $\alpha$ ($> 5{,}5\%$), inflando falsos positivos e violando o controle de erro.
  - *Conservador:* Rejeita $H_0$ com frequência inferior a $\alpha$ ($< 4{,}5\%$), protegendo contra falsos positivos mas destruindo o poder estatístico ($1 - \beta$).
- **Taxas Empíricas com 10.000 Repetições de Monte Carlo (Semente = 42):**

| Condição Experimental sob $H_0$ | Teste t de Welch | Teste U de Mann-Whitney | Classificação de Welch | Classificação de Mann-Whitney |
|---|:---:|:---:|:---:|:---:|
| **1. Cenário Original (Q1 Base, $n=30$)** | $3{,}93\%$ (IC: $3{,}56\%$ a $4{,}33\%$) | $4{,}58\%$ (IC: $4{,}18\%$ a $5{,}00\%$) | **Conservador** | **Robusto / Nominal (Bradley)** |
| **2. Violação: Outliers (Q3, $n=30$)** | $3{,}28\%$ (IC: $2{,}94\%$ a $3{,}65\%$) | $4{,}52\%$ (IC: $4{,}13\%$ a $4{,}95\%$) | **Conservador Severo** | **Robusto / Nominal (Bradley)** |
| **3. Violação: Amostra Pequena (Q3, $n=10$)** | $2{,}90\%$ (IC: $2{,}58\%$ a $3{,}25\%$) | $4{,}33\%$ (IC: $3{,}94\%$ a $4{,}74\%$) | **Conservador Extremo** | **Robusto / Nominal** |

- **Por que Welch ficou conservador?** A estatística de Welch é $t = \frac{\bar{X}_1 - \bar{X}_2}{\sqrt{s_1^2/n_1 + s_2^2/n_2}}$. Sob $H_0$, o numerador varia em torno de 0, mas valores esporádicos na cauda lognormal disparam $s^2$, inflando o denominador e achatando a cauda amostral de $t$, gerando sub-rejeição.

---

### Pergunta 10 — Poder Estatístico no Gráfico G4 e Evolução da Vantagem com o Efeito

- **Enunciado Oficial:** *"No G4, qual teste tem mais poder? A diferença entre eles muda conforme o tamanho do efeito?"*
- **Pergunta Variante da Banca:** *"Existe algum cenário em que o teste t de Welch supere o teste de Mann-Whitney em poder?"*
- **Seção do Dashboard:** `Seção 5. Poder`
- **Onde Apontar na Tela:**  
  1. No **Painel Esquerdo do Gráfico G4**, apontar para a **curva contínua laranja de Mann-Whitney**, mostrando que ela fica sistematicamente acima da curva azul de Welch;
  2. Destacar o ponto de **$\delta = 50\%$ de redução** ($79{,}08\%$ para Mann-Whitney vs. $64{,}20\%$ para Welch);
  3. No **Painel Direito do Gráfico G4**, apontar para a curva de diferença de poder ($\text{Poder}_{\text{MW}} - \text{Poder}_{\text{Welch}}$), mostrando que a vantagem abre de $+0{,}65\text{ p.p.}$ até $+14{,}88\text{ p.p.}$ no cenário base, e atinge $+39{,}68\text{ p.p.}$ sob outliers;
  4. Apontar para a **curva azul tracejada no painel direito (Controle Gaussiano)**, onde a diferença fica abaixo de zero ($\Delta < 0$).

#### Fala Direta de 30 Segundos:
> *"No gráfico G4, o teste U de Mann-Whitney tem expressivamente mais poder em todas as condições realistas de Engenharia de Software. A diferença a seu favor cresce à medida que o tamanho do efeito aumenta: em efeito zero ambos partem próximos de 4% a 5%, mas em 30% de redução a vantagem de Mann-Whitney é de +7,10 pontos percentuais (29,59% vs. 22,49%), atingindo o ápice em 50% de redução com +14,88 pontos percentuais de vantagem (79,08% contra 64,20%). Sob violação por outliers severos, a vantagem de Mann-Whitney dispara para quase 40 pontos percentuais (62,30% vs. 22,62%), pois postos ordenados não são arruinados pela cauda longa. A vantagem só muda de lado quando os dados são perfeitamente normais e simétricos sem outliers, onde Welch lidera por 2,68 p.p. devido à sua eficiência paramétrica ideal."*

#### Resposta Direta para a Pergunta Variante (30 Segundos):
> *"Sim, o teste t de Welch supera Mann-Whitney apenas na condição de Controle Teórico Gaussiano (Normal simétrica sem outliers), visível na curva azul tracejada no painel direito do G4. Nesse caso específico, em δ = 30%, Welch atinge 75,80% contra 73,12% de Mann-Whitney (vantagem de 2,68 p.p.), o que corresponde exatamente à Eficiência Assintótica Relativa (ARE = 3/π ≈ 95,5%) dos postos sob normalidade perfeita."*

#### Pontos-Chave e Fundamentação Técnica:
- **Poder Estatístico ($1 - \beta$):** Probabilidade de rejeitar $H_0$ quando existe um efeito real ($H_1$ verdadeira).
- **Curva Comparativa no Cenário Original ($n=30$, 10.000 simulações):**

| Efeito Redução ($\delta$) | Poder t de Welch | Poder U de Mann-Whitney | Vantagem de Mann-Whitney |
|:---:|:---:|:---:|:---:|
| **$\delta = 0\%$ (H0)** | $3{,}93\%$ | $4{,}58\%$ | $+0{,}65\text{ p.p.}$ |
| **$\delta = 10\%$** | $7{,}49\%$ | $9{,}48\%$ | $+1{,}99\text{ p.p.}$ |
| **$\delta = 20\%$** | $13{,}10\%$ | $17{,}26\%$ | $+4{,}16\text{ p.p.}$ |
| **$\delta = 30\%$** | $22{,}49\%$ | $29{,}59\%$ | $+7{,}10\text{ p.p.}$ |
| **$\delta = 40\%$** | $40{,}57\%$ | $54{,}77\%$ | $+14{,}20\text{ p.p.}$ |
| **$\delta = 50\%$** | $64{,}20\%$ | **$79{,}08\%$** | **$+14{,}88\text{ p.p.}$** |

- **Sob Violação de Outliers (Q3 em $\delta = 50\%$):**
  - Welch sofre colapso: despenca de $64{,}20\%$ para **$22{,}62\%$** (perda de $41{,}58\text{ p.p.}$).
  - Mann-Whitney resiste: sustenta **$62{,}30\%$**.
  - Vantagem líquida de Mann-Whitney: **$+39{,}68\text{ pontos percentuais}$**.
- **Quando Welch vence?** No Controle Gaussiano Teórico ($\delta = 30\%$, $n = 30$):
  - Welch atinge $75{,}80\%$ vs. $73{,}12\%$ de Mann-Whitney (vantagem de Welch $= +2{,}68\text{ p.p.}$).
  - Justificativa matemática: Pelo teorema de Pitman, sob distribuição Gaussiana pura a ARE do teste de Wilcoxon/Mann-Whitney frente ao teste t é $\frac{3}{\pi} \approx 0{,}955$ ($95{,}5\%$).

---

## 3. Tabela Resumo Rápido — Perguntas 6 a 10

| Nº | Tema | Seção no Dashboard | Resposta-Chave em uma Frase |
|---|---|---|---|
| **P6** | Distribuição sob H₀ e Região de Rejeição | Seção 3 (G2) | A distribuição sob H₀ modela o ruído puro sem efeito de bot; a região de rejeição fica nas duas caudas (2,5% em cada lado) porque é um teste bicaudal com α = 5%. |
| **P7** | Significado e Equívocos do p-valor | Seção 3 (G2) | O p-valor é P(dados tão ou mais extremos sob H₀); não é a probabilidade de H₀ ser verdadeira e p > 0,05 não prova que não há efeito. |
| **P8** | Erro Tipo I vs. Erro Tipo II no Cenário | Seção 1, 4 (G3) e 5 (G4) | Tipo I é adotar bot inútil; Tipo II é descartar bot eficaz; Tipo II é mais grave pelo alto custo de oportunidade de manter revisões manuais lentas. |
| **P9** | Erro Tipo I em G3: Liberal vs. Conservador | Seção 4 (G3) | Mann-Whitney foi exemplar (4,58% base); Welch foi conservador (3,93% base e 2,90% com n=10) porque a variância dos outliers infla o denominador de t. |
| **P10** | Poder em G4 e Evolução da Vantagem | Seção 5 (G4) | Mann-Whitney tem mais poder em todos os cenários reais (vantagem cresce até +14,88 p.p. na base e +39,68 p.p. sob outliers); Welch só vence na Gaussiana pura. |

---

## 4. Checklist de Preparação e Ensaio

- [x] **Domínio dos Gráficos:** Identificar visualmente onde estão as curvas teóricas (G2), as barras empíricas (G3) e as curvas de potência (G4).
- [x] **Cronômetro:** Treinar a fala direta de cada pergunta garantindo que fique entre 25 e 32 segundos.
- [x] **Terminologia Estatística Precisa:** Utilizar termos corretos (*distribuição nula*, *graus de liberdade de Welch-Satterthwaite*, *eficiência assintótica de Pitman*, *faixa de Bradley*, *erro padrão inflado*).
- [x] **Ensaio em Grupo:** Praticar a transição entre o integrante responsável pelas perguntas 1 a 5, este bloco (6 a 10) e o responsável pelas perguntas 11 a 15.
