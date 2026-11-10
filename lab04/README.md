# LAB04 — Laboratório 04 · 20 pontos

| Informação | Detalhe |
|---|---|
| Curso | Engenharia de Software |
| Disciplina | Laboratório de Experimentação de Software |
| Turno | Noite |
| Período / Sala | 6º |
| Professor(a) | Danilo Maia |

## Testes de hipótese por dentro: cenário, simulação e visualização

## 1. Objetivo
Entender como um teste de hipótese funciona e quando escolher um teste em vez de outro, usando simulação e gráficos.

O grupo vai criar um cenário de Engenharia de Software, escolher dois testes que poderiam responder à mesma pergunta e comparar os dois. Como é o próprio grupo que gera os dados da simulação, ele sabe a resposta certa e pode verificar quantas vezes cada teste acerta ou erra. Uma pequena amostra de dados reais serve para deixar a simulação realista e para testar, no fim, se a recomendação do grupo se sustenta.

Este laboratório é independente dos anteriores: não usa dados nem resultados de outros laboratórios.

**Material de apoio:** guia *Testes de Hipótese em Experimentação de Software* (Testes 1 a 11, com exemplos e código em Python e R).
## 2. O que o grupo deve fazer

### a) Escolher um par de testes

O grupo escolhe o par que quiser entre os abaixo.

| Par | Testes | Exemplo de cenário |
|---|---|---|
| P1 | t de Welch × Mann-Whitney | Tempo até o merge de PRs, com e sem bot de revisão |
| P2 | t pareado × Wilcoxon pareado | Tempo de build antes e depois de ativar o cache |
| P3 | ANOVA × Kruskal-Wallis | Tempo de revisão de PRs pequenos, médios e grandes |
| P4 | Z para proporção × binomial exato | Taxa de builds com falha frente a uma meta de 5% |
| P5 | Pearson × Spearman | Tamanho do módulo (LOC) × nº de defeitos |

### b) Coletar uma amostra pequena de dados reais

Cerca de **30 observações por grupo comparado**.

| Par | Coleta sugerida |
|---|---|
| P1 | Tempo até o merge de PRs de um repositório público, com e sem bot de revisão (anotado da página do GitHub ou de um dataset pronto) |
| P2 | Tempo de build ou dos testes de um projeto open-source, rodado ~15 vezes na própria máquina, com e sem cache (ou outra otimização) |
| P3 | Tempo de revisão de PRs pequenos, médios e grandes de um repositório público |
| P4 | Execuções de CI com falha na aba Actions de um repositório público |
| P5 | Dataset público de defeitos por módulo (ex.: NASA MDP / PROMISE) |

Registre de onde vieram os dados e como foram coletados. Não é preciso construir um pipeline: uma planilha ou um CSV bastam.

### c) Criar o cenário

- A pergunta, em uma frase;
- As hipóteses H0 e H1;
- Como os dados da simulação serão gerados: a distribuição de cada grupo e seus parâmetros, escolhidos a partir dos dados reais (ex.: “o tempo de merge real é assimétrico, com mediana de 10 h; usamos uma lognormal com essa mediana”);
- Antes de simular, qual dos dois testes o grupo espera que se saia melhor, e por quê.

### d) Simular e comparar os testes

Responder a três perguntas:

#### Q1 — Erro tipo I

**Quando não há efeito, com que frequência cada teste “encontra” um efeito?**

Gere **10.000 conjuntos de dados** com H0 verdadeira, aplique os dois testes e conte a proporção de p-valores < 0,05. O esperado é algo próximo de 5%.

#### Q2 — Poder

**Quando há efeito, com que frequência cada teste o detecta?**

Repita a simulação com efeitos de tamanhos crescentes (**no mínimo 5 valores, começando em zero**) e conte a proporção de rejeições.

#### Q3 — Violação de pressupostos

**O que muda quando os dados não “se comportam bem”?**

Repita Q1 e Q2 em pelo menos uma situação que viole os pressupostos do teste paramétrico, como dados muito assimétricos, outliers ou amostras pequenas.

### e) Visualizar: produzir quatro gráficos

| Gráfico | O que mostra |
|---|---|
| G1 | Os dados reais ao lado dos dados simulados: histograma de cada grupo |
| G2 | A distribuição da estatística do teste quando H0 é verdadeira, com a região de rejeição sombreada e o p-valor de um exemplo marcado como área |
| G3 | Erro tipo I dos dois testes em cada situação simulada, com uma linha em 5% (Q1 e Q3) |
| G4 | Curvas de poder dos dois testes no mesmo gráfico: proporção de rejeições × tamanho do efeito (Q2 e Q3) |

Em todos os gráficos: **título, eixos com nome e unidade, legenda, e a mesma cor para cada teste**.

## 3. Sprints

### Lab04S01 — 7 pontos

Dados reais coletados (item b) + cenário (item c) + código que gera os dados simulados + os dois testes aplicados a um conjunto de dados simulado, com a interpretação do resultado + gráficos G1 e G2.

### Lab04S02 — 7 pontos

Simulações das perguntas Q1, Q2 e Q3 + gráficos G3 e G4.

### Entrega Final — 6 pontos

O dashboard completo (**3 pontos**, seção 4) e a apresentação oral (**3 pontos**, seção 5).

**Importante:** Os gráficos das sprints já devem ser construídos dentro do dashboard: na S01 ele já mostra o G1 e o G2; na S02, o G3 e o G4.

## 4. Entrega final: o dashboard
A entrega final é apenas o dashboard, sem relatório em documento. Por isso, o dashboard precisa se explicar sozinho: cada gráfico vem acompanhado de um texto curto (2 a 4 frases) que diz o que o gráfico mostra e o que o grupo conclui dele.

O dashboard deve ter as seções abaixo, **nesta ordem**:

| Seção | Gráfico | O que o texto deve dizer |
|---|---|---|
| 1. Cenário | — | A pergunta, H₀ e H₁, de onde vieram os dados reais e quantas observações foram coletadas. |
| 2. Os dados | G1 | Como são os dados reais e os simulados (assimetria, outliers) e por que os parâmetros da simulação foram escolhidos assim. |
| 3. Como os testes funcionam | G2 | O que cada teste compara, onde fica a região de rejeição e o que significa o p-valor do exemplo. |
| 4. Erro tipo I | G3 | Se cada teste ficou perto de 5% em cada situação, e qual se desviou. |
| 5. Poder | G4 | Qual teste detecta melhor o efeito, e em que situações a vantagem muda de lado. |
| 6. Dados reais | Tabela | Estatística, p-valor, tamanho do efeito e conclusão de cada teste nos dados coletados. |
| 7. Conclusão | — | O que o grupo esperava antes de simular × o que encontrou, e a recomendação: qual teste usar no cenário, e quando a escolha mudaria. |

Pode ser feito em Streamlit, Dash, Plotly (página HTML), Quarto ou ferramenta equivalente, desde que gerado por código do repositório.
Deve abrir com um único comando descrito no README, ou estar publicado (ex.: GitHub Pages, Streamlit Community Cloud).
O link do dashboard e do repositório/GitHub Projects do grupo devem aparecer no topo do dashboard.
**Link do repositório/GitHub Projects:** https://github.com/JoaoFilardi/LabExperimentacao | https://github.com/JoaoFilardi/LabExperimentacao/projects

## 5. Apresentação oral: 15 perguntas
Na aula de apresentação, o grupo responde, usando o próprio dashboard, às 15 perguntas abaixo. A apresentação dura até 7 minutos; as respostas devem ser curtas e diretas (cerca de 30 segundos cada). As perguntas são divididas entre os integrantes, e cada um responde a pelo menos 4. O professor pode pedir a qualquer integrante que responda a qualquer pergunta.

1. Qual é o cenário de vocês e o que H₀ e H₁ afirmam, em palavras simples?
2. O teste de vocês é unicaudal ou bicaudal? Por quê?
3. Como os dados reais foram coletados, e o que eles mostraram sobre a forma da distribuição?
4. Como os dados reais ajudaram a escolher os parâmetros da simulação?
5. O que cada um dos dois testes compara de fato (médias, postos, proporções...)?
6. No G2: o que é a distribuição da estatística sob H₀, e por que a região de rejeição fica onde fica?
7. O que significa o p-valor do exemplo mostrado no G2? E o que ele não significa?
8. No cenário de vocês, o que seria um erro tipo I e um erro tipo II? Qual dos dois seria mais grave?
9. No G3, algum teste se afastou de 5%? Ele ficou liberal ou conservador, e por quê?
10. No G4, qual teste tem mais poder? A diferença entre eles muda conforme o tamanho do efeito?
11. Que violação de pressuposto vocês simularam, e por que ela afeta mais um teste do que o outro?
12. Se vocês usassem α = 0,01 em vez de 0,05, o que mudaria no G3 e no G4?
13. A simulação confirmou o que o grupo esperava antes de simular? Se não, o que explica a diferença?
14. Nos dados reais, os dois testes chegaram à mesma conclusão? O tamanho do efeito tem importância prática?
15. Qual teste vocês recomendam para o cenário, em que situação mudariam a recomendação, e qual é a principal limitação do estudo?

## 6. Para discutir: tamanho da amostra
As perguntas abaixo não são exigências de entrega. Servem para enriquecer o dashboard e a apresentação, para quem quiser ir além.

- Com o tamanho da amostra real que o grupo coletou, qual seria o poder de cada teste para detectar o efeito observado? (as curvas do G4 ajudam a estimar)
- Quantas observações seriam necessárias para chegar a 80% de poder? Isso seria viável de coletar no cenário real?
- Se o resultado nos dados reais não foi significativo, isso mostra que não há efeito, ou só que a amostra era pequena demais para detectá-lo?
- Com amostras muito grandes, até diferenças minúsculas ficam “significativas”. Nesse caso, o que importa mais: o p-valor ou o tamanho do efeito?
- O tamanho da amostra muda qual dos dois testes é o melhor? Os pressupostos pesam mais com amostras pequenas ou grandes?

## 7. Regras
- O código deve rodar do início ao fim com um único comando, descrito no README, usando semente fixa (ex.: numpy.random.default_rng(42)), para que os resultados possam ser reproduzidos.
- Podem ser usadas bibliotecas prontas (NumPy, SciPy, statsmodels, pandas, Matplotlib, Seaborn, Plotly).
- Em cada sprint, cada integrante deve ser Assignee de ao menos uma Issue com código commitado.
- Prazo final: conforme cronograma da disciplina.
- Valor total: 20 pontos · desconto de até 10% da nota da sprint por qualidade insuficiente do uso do GitHub Projects (WIP não respeitado, Issues sem Assignee, cartões desatualizados, ausência de evolução semanal).
- Observação: a correção é feita a partir do GitHub Projects: commits sem referência ao número da Issue correspondente não serão considerados.

## 8. Dúvidas frequentes
### Se vamos coletar dados reais, por que simular?
Porque, com dados reais, não se sabe a resposta certa: não dá para saber se o teste acertou ou errou. Na simulação, o grupo controla se existe efeito e de que tamanho, e por isso consegue medir o erro tipo I e o poder. Os dados reais servem para deixar a simulação realista e para a aplicação final.

### Precisamos de muitos dados reais?
Não. Cerca de 30 observações por grupo comparado bastam. O foco do laboratório é a simulação.

### Por que 10.000 repetições?
Para que a proporção estimada (ex.: 5%) tenha pouca variação. Com 10.000 repetições, a margem de erro fica em torno de ±0,4 ponto percentual.

### O teste não paramétrico sempre ganha quando os dados não são normais?
Não necessariamente. Descobrir isso no cenário do grupo é justamente o objetivo do laboratório.

## 9. Como executar o dashboard e os scripts do projeto

### Pré-requisitos e instalação (Python 3.10+)
`ash
python -m pip install streamlit pandas numpy matplotlib scipy pytest
`

### Executar o dashboard completo (comando único na raiz do repositório)
`ash
python -m streamlit run lab04/app.py
`
O dashboard abre automaticamente em http://localhost:8501.

### Gerar artefatos e relatórios individualmente via linha de comando
- **Gráfico G1** (lab04/data/g1_reais_vs_simulados.png):
  `ash
  python -m lab04.src.grafico_g1
  `
- **Gráfico G2** (lab04/data/g2_distribuicao_sob_h0.png):
  `ash
  python -m lab04.src.grafico_g2
  `
- **Aplicação e interpretação dos dois testes estatísticos** (lab04/data/resultados_testes_s01.csv):
  `ash
  python -m lab04.src.testes_estatisticos
  
- **Simulações e análise do Erro Tipo I — Q1** (lab04/data/resultados_q1_erro_tipo_1.csv e lab04/data/simulacao_q1_pvalores.csv):
  ash
  python -m lab04.src.simulacao_q1
  `

### Executar a suíte de testes automatizados
`ash
python -m pytest lab04/tests
`

Os dados simulados utilizam semente fixa (semente = 42), garantindo reprodutibilidade exata de todos os números, tabelas e gráficos.
