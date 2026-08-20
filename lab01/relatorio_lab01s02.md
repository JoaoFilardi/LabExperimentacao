# Relatório Lab01 — Sprint 2 (primeira versão)

Dados: `lab01/repositorios_1000.csv` (1000 repositórios, sem nomes repetidos).

Esta versão traz as hipóteses informais e a checagem dos dados. Gráficos e a comparação hipótese vs. resultado ficam para a próxima sprint.

---

## Hipóteses informais

Antes de olhar os gráficos da S03, a ideia é registrar o que o grupo espera encontrar.

### RQ01. Sistemas populares são maduros/antigos?

Métrica: idade do repositório (a partir da data de criação).

*(preencher hipótese)*

### RQ02. Sistemas populares recebem muita contribuição externa?

Métrica: total de pull requests aceitas.

*(preencher hipótese)*

### RQ03. Sistemas populares lançam releases com frequência?

A métrica é o total de GitHub Releases de cada repositório (`total_releases`). Não é “releases por ano”, é o total acumulado.

**Hipótese:** sim. Projetos muito populares costumam versionar o que entregam, então a mediana de releases deve ser maior que zero. Também deve aparecer um grupo com bastante release (dezenas ou centenas), principalmente bibliotecas e frameworks.

Isso não significa que todo mundo lança release. No GitHub tem muita lista *awesome*, livro, roadmap e projeto que só usa tag ou commit. Esses podem ter zero releases e mesmo assim muitas estrelas. A hipótese é sobre o conjunto, não sobre cada repositório.

### RQ04. Sistemas populares são atualizados com frequência?

A métrica é quantos dias se passaram desde o último push (`dias_ultimo_push`).

**Hipótese:** sim. A mediana deve ser baixa (alguns dias ou poucas semanas, não anos). A maior parte dos repositórios deve ter sido atualizada há menos de 30 dias.

Mesmo assim, popularidade antiga não impede abandono. Alguns projetos famosos podem estar parados há muito tempo. Isso não quebra a hipótese se a maioria continuar ativa.

### RQ05. Sistemas populares são escritos nas linguagens mais populares?

Métrica: linguagem primária de cada repositório.

*(preencher hipótese e a fonte usada para “linguagens mais populares”)*

### RQ06. Sistemas populares possuem um alto percentual de issues fechadas?

Métrica: razão entre issues fechadas e total de issues.

*(preencher hipótese)*

---

## Validação dos dados

A checagem olha nulos, valores que não são número, valores negativos, nomes duplicados, a distribuição (mínimo, máximo, média, mediana, quartis) e outliers. Outlier aqui é valor muito fora do comum: abaixo de Q1 − 1,5×IQR ou acima de Q3 + 1,5×IQR.

### RQ01 e RQ02

*(preencher validação: nulos, distribuição, outliers)*

### RQ03 e RQ04

Script de conferência:

```
python lab01/validacao_rq03_rq04.py
```

Nas colunas `total_releases` e `dias_ultimo_push` não tem nulo, não tem texto no lugar de número e não tem valor negativo. Os 1000 registros vieram preenchidos.

Zero não é dado faltando:

- em `total_releases`, zero quer dizer que o repositório não tem GitHub Release;
- em `dias_ultimo_push`, zero quer dizer que o último push foi no mesmo dia da coleta.

#### RQ03 — total de releases

| | |
|---|---|
| repositórios | 1000 |
| mínimo / máximo | 0 / 1000 |
| média | 126,16 |
| mediana | 39 |
| Q1 / Q3 | 0 / 146,25 |
| IQR | 146,25 |
| outliers | 92 (9,2%) |
| com zero release | 286 (28,6%) |

A média (126) ficou bem maior que a mediana (39). Isso acontece porque uns poucos repositórios têm muitos releases e puxam a média para cima. Por isso, para responder a RQ03, faz mais sentido usar a mediana.

Quase 29% com zero release não parece erro de coleta. O campo veio preenchido; são projetos que simplesmente não usam GitHub Releases (listas, material de estudo, etc.).

Os 92 outliers são, na prática, repositórios com mais de uns 366 releases. Esses pontos foram mantidos: são projetos reais, não linha quebrada no CSV.

Um detalhe estranho: **21 repositórios têm exatamente 1000 releases** (por exemplo `vercel/next.js`, `home-assistant/core` e `langchain-ai/langchain`). Pode ser um limite da API, que não devolve totais maiores que 1000. Isso quase não mexe na mediana (39). Já a média, o máximo e o ranking de “quem lança mais” ficam subestimados. Na S03, se o grupo for falar do máximo, vale tratar 1000 como “1000 ou mais”.

O que não foi tratado como erro nesta RQ:

- 286 repositórios com 0 releases: o GitHub conta Releases, não tags;
- 21 repositórios com 1000 releases: o valor ficou como está, com a possível limitação da API anotada aqui.

#### RQ04 — dias desde o último push

| | |
|---|---|
| repositórios | 1000 |
| mínimo / máximo | 0 / 2450 |
| média | 113,45 |
| mediana | 1 |
| Q1 / Q3 | 0 / 49,25 |
| IQR | 49,25 |
| outliers | 193 (19,3%) |
| atualizado no dia da coleta | 430 (43,0%) |

Quantos repositórios caem em cada faixa:

| Último push | Quantidade |
|---|---:|
| no mesmo dia | 430 |
| 1 a 7 dias | 190 |
| 8 a 30 dias | 105 |
| 31 a 90 dias | 65 |
| 91 a 365 dias | 96 |
| 1 a 2 anos | 47 |
| mais de 2 anos | 67 |

Não apareceu dia negativo, então não tem data futura no CSV (o que seria um erro claro).

De novo a média engana: mediana de 1 dia, média de cerca de 113, porque uns repositórios estão parados há anos e puxam a média. Para a RQ04, a mediana é o número certo.

Os 193 outliers são, no geral, repositórios sem push há mais de uns 123 dias. Nos extremos: `exacity/deeplearningbook-chinese` (2450 dias), `GitSquared/edex-ui` (1764) e `atom/atom` (1323). Faz sentido (projeto parado, descontinuado ou lista que quase não muda). Isso não foi tratado como dado corrompido.

Somando as faixas: cerca de 62% teve push na última semana e cerca de 72,5% nos últimos 30 dias. Isso combina com a hipótese da RQ04, mas a comparação de verdade fica para a S03.

### RQ05 e RQ06

*(preencher validação: nulos, distribuição, outliers; linguagem `N/A` entra nesta parte)*
