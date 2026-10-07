# Dicionário de Dados - Seleção de Repositórios e Funil de Coleta (LAB03)

Este documento descreve detalhadamente cada campo presente nos arquivos gerados pelo módulo de seleção de repositórios do **Laboratório 03: Mineração de Métricas DORA**, em conformidade com os requisitos de engenharia e replicabilidade científica.

---

## 1. `repositorios_selecionados.csv`

Armazena a relação dos repositórios aprovados pelo funil de seleção com seus respectivos metadados (necessários para a caracterização da amostra e para a resposta à **RQ 06: Quais características dos repositórios estão associadas a um melhor desempenho DORA?**).

| Coluna | Tipo | Unidade | Descrição / Origem |
|---|---|---|---|
| `owner` | String | Texto | Login do proprietário ou organização no GitHub (ex: `tiangolo`). |
| `name` | String | Texto | Nome do repositório (ex: `fastapi`). |
| `full_name` | String | Texto | Identificador único `owner/name` no GitHub. |
| `html_url` | String | URL | Link direto para a página web do repositório no GitHub. |
| `default_branch` | String | Texto | Branch principal oficial (`main` ou `master`), obtido em `default_branch`. |
| `stars` | Inteiro | Contagem | Quantidade de estrelas (`stargazers_count`) no momento da amostragem. |
| `forks_count` | Inteiro | Contagem | Quantidade de bifurcações registradas no repositório. |
| `open_issues_count`| Inteiro | Contagem | Quantidade de issues abertas no repositório. |
| `primary_language` | String | Categoria | Linguagem de programação predominante registrada no GitHub (`language`). |
| `created_at` | String (ISO-8601) | Data/Hora UTC | Timestamp de criação original do repositório (`created_at`). |
| `age_years` | Float | Anos decimais | Idade calculada: $\frac{\text{fim da janela} - \text{created\_at}}{365.25 \times 86400}$. |
| `contributors_count`| Inteiro | Contagem | Estimativa do número de colaboradores via paginação do endpoint `/contributors?per_page=1&anon=true` lendo o cabeçalho `Link: rel="last"`. (-1 indica indisponibilidade). |
| `total_workflows` | Inteiro | Contagem | Número de arquivos de workflow configurados em `.github/workflows/` (`total_count` da API). |
| `releases_window_count`| Inteiro | Contagem | Número de releases válidas (`draft=false` e `prerelease=false`) publicadas dentro da janela de 12 meses. |
| `runs_window_count`| Inteiro | Contagem | Número de execuções de workflow no `default_branch` com `event=push` e conclusão válida (`success`, `failure`, `timed_out`, `startup_failure`) dentro da janela de 12 meses. |
| `description` | String | Texto | Descrição textual resumida do projeto cadastrada no repositório. |

---

## 2. `funil_selecao.csv`

Tabela agregada que quantifica o descarte de repositórios ao longo das etapas do funil de seleção.

| Coluna | Tipo | Unidade | Descrição |
|---|---|---|---|
| `etapa_num` | Inteiro | Ordem (1 a 5) | Identificador sequencial da etapa do funil. |
| `etapa_nome` | String | Texto | Título descritivo da fase de filtragem. |
| `total_restante` | Inteiro | Contagem | Número de repositórios sobreviventes após a aplicação do filtro. |
| `descartados_na_etapa` | Inteiro | Contagem | Quantidade de repositórios eliminados especificamente nesta etapa. |
| `taxa_retencao_etapa_pct` | Float | Percentual (%) | Proporção retida em relação à etapa imediatamente anterior: $\frac{\text{restante}}{\text{anterior}} \times 100$. |
| `taxa_retencao_acumulada_pct` | Float | Percentual (%) | Proporção retida em relação ao total inicial de candidatos: $\frac{\text{restante}}{\text{candidatos}} \times 100$. |
| `criterio_ou_motivo` | String | Texto | Critério operacional ou justificativa da eliminação. |

---

## 3. `funil_detalhado.csv`

Log de auditoria item a item de cada repositório submetido ao funil, garantindo rastreabilidade e reprodutibilidade completas.

| Coluna | Tipo | Unidade | Descrição |
|---|---|---|---|
| `full_name` | String | Texto | Identificador único `owner/repo`. |
| `stars` | Inteiro | Contagem | Estrelas do projeto no GitHub. |
| `language` | String | Texto | Linguagem predominante. |
| `status` | String | Categoria | `SELECIONADO` (atende a todos os critérios) ou `DESCARTADO`. |
| `motivo` | String | Texto | Justificativa técnica do descarte ou confirmação de aprovação. |
| `total_workflows` | Inteiro | Contagem | Total de workflows de CI detectados. |
| `releases_na_janela` | Inteiro | Contagem | Releases publicadas na janela de 12 meses. |
| `runs_na_janela` | Inteiro | Contagem | Workflow runs válidos do default branch na janela. |
