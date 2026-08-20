# Relatório Parcial - Laboratório 01 (Sprint 2)

Este relatório apresenta a metodologia de coleta de dados, a formulação de hipóteses informais, os resultados de validação de consistência dos dados referentes à **RQ05** (Linguagem Primária) e **RQ06** (Percentual de Issues Fechadas), e a implementação do script de snapshot do GitHub Projects (Parte 2 do laboratório).

Sobre a **RQ07** (bônus): não foi implementada nesta sprint. Como é um item bônus (+1 ponto) que depende de cruzar RQ02/RQ03/RQ04 por linguagem — dados que ainda não estão organizados dessa forma no script de mineração —, ela foi deixada de fora por ora e pode ser retomada na S03 se o grupo decidir ir atrás do ponto extra.

---

## 1. Hipóteses Informais

Antes da análise quantitativa detalhada, formulamos as seguintes hipóteses:

- **Hipótese para RQ05 (Linguagem Primária):**
  - _Enunciado:_ Sistemas populares tendem a ser escritos nas linguagens mais populares do mercado.
  - _Justificativa:_ Linguagens amplamente adotadas (Python, JavaScript/TypeScript, Java, Go) possuem comunidades maiores, mais bibliotecas e mais desenvolvedores capazes de contribuir, o que facilita ganhar estrelas no GitHub. Como referência para "linguagens mais populares", usamos o **GitHub Octoverse** (relatório anual do próprio GitHub sobre as linguagens mais usadas em repositórios públicos), mantendo essa referência ao longo de todo o laboratório. Espera-se que a maioria dos 1.000 repositórios concentre-se em um grupo pequeno de linguagens do topo do Octoverse, com uma cauda longa de linguagens pouco frequentes.
- **Hipótese para RQ06 (Percentual de Issues Fechadas):**
  - _Enunciado:_ Sistemas populares possuem um alto percentual de issues fechadas.
  - _Justificativa:_ Projetos populares atraem mantenedores mais ativos e, muitas vezes, equipes ou empresas por trás deles, o que favorece o fechamento de issues (por resolução, duplicidade ou falta de resposta do autor). Espera-se mediana alta (acima de 70-80%), ainda que repositórios muito grandes possam acumular um número absoluto grande de issues abertas mesmo fechando a maioria delas.

---

## 2. Metodologia de Coleta de Dados

A coleta de dados foi realizada utilizando um script Python que consome a API GraphQL do GitHub através da biblioteca padrão do Python (`urllib.request`), em conformidade com as regras da disciplina de evitar dependências externas de terceiros (como `requests` ou `python-dotenv`).

Para mitigar o erro de gateway **502 Bad Gateway** (comum ao consultar campos complexos e agregados de repositórios massivos de uma só vez), o grupo implementou um controle de paginação que realiza a busca em lotes de **10 em 10 repositórios** utilizando os cursores `endCursor` e `hasNextPage`, totalizando 100 requisições para obter a amostra de 1.000 repositórios ordenados por número de estrelas em ordem decrescente.

Os dados foram salvos localmente no arquivo `repositorios_1000.csv`. Para esta parte do laboratório foram usadas as colunas `linguagem_primaria` (RQ05), `issues_total`, `issues_fechadas` e `razao_issues_fechadas` (RQ06). A linguagem primária vem do campo `primaryLanguage.name` da API; quando o repositório não tem linguagem detectada (ex.: repositório de apenas configuração ou dados), o valor gravado é `N/A`. A razão de issues fechadas é calculada como `(issues_fechadas / issues_total) * 100`, com o script já tratando o caso de divisão por zero (repositórios sem nenhuma issue recebem 0.00%, não um erro).

---

## 3. Resultados da Validação de Consistência (RQ05 e RQ06)

O script `validacao_rq05_rq06.py` foi executado para ler o arquivo `repositorios_1000.csv`, gerar estatísticas descritivas e identificar outliers pelo método do Intervalo Interquartil (IQR), da mesma forma que os scripts das demais partes do grupo.

Para rodar:

```
python lab01/validacao_rq05_rq06.py
```

### 3.1. RQ05 — Linguagem Primária (dado categórico)

| Métrica | Valor |
| :--- | :---: |
| Total de registros | 1000 |
| Valores vazios/ausentes | 0 |
| Repositórios sem linguagem definida (`N/A`) | 87 (8,70%) |
| Linguagens distintas (excluindo `N/A`) | 43 |

**Top 10 linguagens mais frequentes:**

| Linguagem | Quantidade | % da amostra |
| :--- | ---: | ---: |
| Python | 228 | 22,80% |
| TypeScript | 174 | 17,40% |
| JavaScript | 111 | 11,10% |
| N/A | 87 | 8,70% |
| Go | 76 | 7,60% |
| Rust | 57 | 5,70% |
| C++ | 41 | 4,10% |
| Java | 41 | 4,10% |
| Jupyter Notebook | 24 | 2,40% |
| C | 21 | 2,10% |

### 3.2. RQ06 — Percentual de Issues Fechadas

| Métrica | Valor |
| :--- | :---: |
| Total de Registros | 1000 |
| Valores Nulos/Ausentes | 0 |
| Valores fora do intervalo [0, 100] | 0 |
| Mínimo | 0,00 |
| Máximo | 100,00 |
| Média | 76,79 |
| Primeiro Quartil (Q1 - 25%) | 67,19 |
| Mediana / Q2 (50%) | 86,48 |
| Terceiro Quartil (Q3 - 75%) | 96,55 |
| IQR (Q3 - Q1) | 29,36 |
| Limites de Outliers | [23,15 ; 140,59] |
| Quantidade de Outliers | 60 (6,00%) |
| Repositórios com `issues_total = 0` (razão definida como 0%) | 43 (4,30%) |
| Repositórios com 100% das issues fechadas | 28 (2,80%) |
| Repositórios com 0% das issues fechadas | 43 (4,30%) |

---

## 4. Discussão sobre Consistência e Outliers

- **Consistência e Nulos:** Não foram detectados valores nulos, vazios ou fora do intervalo esperado em `linguagem_primaria` (que ou tem um nome válido, ou o marcador `N/A`) nem em `razao_issues_fechadas` (sempre entre 0 e 100), o que confirma a consistência da extração via GraphQL.
- **RQ05 — `N/A` não é erro de coleta:** os 87 repositórios (8,70%) sem linguagem primária não indicam falha na consulta; são casos legítimos da API do GitHub, como repositórios compostos majoritariamente por dados/configuração, listas de links (`awesome-*`) ou monorepos sem uma linguagem dominante clara. Esses registros foram mantidos no CSV e tratados como categoria própria (`N/A`) na análise, em vez de descartados.
- **RQ05 — concentração em poucas linguagens:** as 3 linguagens mais frequentes (Python, TypeScript, JavaScript) já respondem por 51,3% da amostra, e somando Go, Rust, C++ e Java chega a quase 71%. Isso é compatível com a hipótese: a popularidade dos repositórios se concentra fortemente nas linguagens do topo do GitHub Octoverse, com uma cauda longa de 43 linguagens distintas que aparecem em poucos repositórios cada.
- **RQ06 — assimetria à esquerda (skew negativo):** diferente de RQ01–RQ04, aqui a distribuição pende para valores altos. A mediana (86,48%) é maior que a média (76,79%), puxada para baixo por uma cauda de repositórios com percentuais baixos. O IQR (67,19% a 96,55%) mostra que metade da amostra fecha entre dois terços e quase a totalidade das suas issues.
- **RQ06 — os dois extremos (0% e 100%) merecem atenção:** 43 repositórios (4,30%) têm `issues_total = 0`, e por definição do script (divisão por zero tratada) ficaram com razão 0,00%. Esse zero **não significa que o projeto ignora todas as issues** — significa que ele simplesmente não usa o recurso de Issues do GitHub (comum em repositórios que centralizam suporte em outro canal, ou em listas/materiais que não recebem issues). Já os 28 repositórios (2,80%) com 100% fecham exatamente todas as issues que já tiveram; nenhum desses casos foi tratado como erro de coleta.
- **RQ06 — outliers (60, 6,00%):** pelo método IQR, os outliers ficam abaixo de ~23,15%, ou seja, são repositórios com percentual de fechamento anormalmente baixo em relação ao restante da amostra (não há outliers no limite superior, já que 100% é o teto do dado). São projetos populares mas com muitas issues abertas acumuladas — plausível para repositórios grandes e ativos, não indício de dado corrompido.

---

## 5. Script de Snapshot do GitHub Projects (Parte 2 do laboratório)

Foi criado o script `snapshot_projects.py`, que consulta via GraphQL os itens do GitHub Projects (v2) do grupo e exporta, para cada item, o número da Issue, título, URL, **coluna atual (campo Status)**, estado da Issue (aberta/fechada), responsável (assignee) e datas de criação/atualização/fechamento. Ele reaproveita o `execute_query` já existente em `graphql_client.py`, seguindo a regra da disciplina de não usar bibliotecas de terceiros para consultar a API do GitHub.

Itens do Project que não estão vinculados a uma Issue real (ex.: draft issues soltas) são ignorados na exportação, de acordo com a regra do laboratório de que todo cartão deve ser uma Issue rastreável pela API.

**Configuração necessária** (variáveis de ambiente ou arquivo `.env`, no mesmo padrão do `GITHUB_TOKEN`):

- `GITHUB_TOKEN` — token com permissão de leitura do repositório e do Project;
- `PROJECT_OWNER` — login do usuário/organização dono do Project;
- `PROJECT_NUMBER` — número do Project (v2), visível na URL do board;
- `PROJECT_OWNER_TYPE` — `org` ou `user` (padrão `org`).

**Uso:**

```
python lab01/snapshot_projects.py --sprint S02
```

O comando gera o arquivo `lab01/snapshot_s02.csv`, com uma linha por Issue do board e seu status no momento da execução. Repetindo o comando ao final de cada sprint (trocando `--sprint`), os snapshots se acumulam (`snapshot_s01.csv`, `snapshot_s02.csv`, `snapshot_s03.csv`...) e formam a série histórica de movimentação do board que será usada como base de dados nos Labs 04 e 05, já que o GitHub Projects não guarda esse histórico de forma consultável pela API.

> **Observação para o grupo:** este relatório documenta e testa a lógica do script (sintaxe e tratamento de erros validados localmente), mas a geração efetiva do `snapshot_s02.csv` precisa ser rodada por quem tiver o `GITHUB_TOKEN` e acesso ao Project configurados, apontando `PROJECT_OWNER`/`PROJECT_NUMBER` para o board real do grupo.
