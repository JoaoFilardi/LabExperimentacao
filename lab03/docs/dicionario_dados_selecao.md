# Dicionário de Dados - Seleção de Repositórios e Funil de Coleta (LAB03S02)

Este documento descreve detalhadamente cada campo presente nos arquivos gerados pelo módulo de seleção de repositórios do **Laboratório 03: Mineração de Métricas DORA** (Sprint 02), consolidando a expansão amostral para **pelo menos 300 repositórios válidos** em estrito atendimento à Issue [#32](https://github.com/JoaoFilardi/LabExperimentacao/issues/32).

---

## 1. `repositorios_selecionados.csv`

Armazena a relação consolidada dos **310 repositórios qualificados** aprovados por todas as etapas do funil de seleção com seus respectivos metadados enriquecidos. Esses dados subsidiam a resposta às questões de pesquisa (especialmente a **RQ 06: Quais características dos repositórios estão associadas a um melhor desempenho DORA?**).

| Coluna | Tipo | Unidade / Formato | Descrição / Origem |
|---|---|---|---|
| `owner` | String | Texto | Login do proprietário ou organização no GitHub (ex: `tiangolo`). |
| `name` | String | Texto | Nome do repositório (ex: `fastapi`). |
| `full_name` | String | `owner/name` | Identificador canônico único no GitHub. |
| `html_url` | String | URL HTTPS | Link canônico para a página web do repositório no GitHub. |
| `default_branch` | String | Texto | Branch principal oficial (`main` ou `master`), obtido em `default_branch`. |
| `stars` | Inteiro | Contagem ($\ge 1.000$) | Quantidade de estrelas (`stargazers_count`) no momento da amostragem. |
| `forks_count` | Inteiro | Contagem ($\ge 0$) | Quantidade de bifurcações registradas no repositório. |
| `open_issues_count`| Inteiro | Contagem ($\ge 0$) | Quantidade de issues e PRs abertos no repositório. |
| `primary_language` | String | Categoria | Linguagem de programação predominante registrada no GitHub (`language`). |
| `created_at` | String | ISO 8601 UTC | Carimbo de data/hora de criação original do repositório. |
| `age_years` | Float | Anos decimais ($\ge 0$) | Idade calculada: $\frac{\text{fim da janela} - \text{created\_at}}{365.25 \times 86400}$. |
| `contributors_count`| Inteiro | Contagem | Estimativa do total de colaboradores via paginação do endpoint `/contributors`. |
| `total_workflows` | Inteiro | Contagem ($\ge 1$) | Número de arquivos de workflow configurados em `.github/workflows/`. |
| `releases_window_count`| Inteiro | Contagem ($\ge 5$) | Número de releases formais (`draft=false` e `prerelease=false`) publicadas na janela de 12 meses. |
| `runs_window_count`| Inteiro | Contagem ($\ge 50$) | Execuções de workflow no `default_branch` com `event=push` e conclusão válida na janela de 12 meses. |
| `description` | String | Texto livre | Descrição resumida do projeto cadastrada no repositório. |

---

## 2. `funil_selecao.csv`

Tabela agregada do funil de seleção que quantifica o descarte e a retenção de repositórios ao longo das 5 etapas da Sprint 02:

| Coluna | Tipo | Unidade / Domínio | Descrição |
|---|---|---|---|
| `etapa_num` | Inteiro | 1 a 5 | Identificador sequencial da etapa do funil. |
| `etapa_nome` | String | Texto | Título descritivo da fase de filtragem. |
| `total_restante` | Inteiro | Contagem | Número de repositórios sobreviventes após a aplicação do filtro. |
| `descartados_na_etapa` | Inteiro | Contagem | Quantidade de repositórios eliminados especificamente nesta etapa. |
| `taxa_retencao_etapa_pct` | Float | Percentual (%) | Proporção retida em relação à etapa imediatamente anterior: $\frac{\text{restante}}{\text{anterior}} \times 100$. |
| `taxa_retencao_acumulada_pct` | Float | Percentual (%) | Proporção retida em relação ao total inicial de candidatos: $\frac{\text{restante}}{\text{candidatos}} \times 100$. |
| `criterio_ou_motivo` | String | Texto | Critério operacional ou justificativa da eliminação. |

---

## 3. `funil_detalhado.csv`

Log de auditoria item a item de todos os repositórios avaliados durante a execução do pipeline (338 registros: 310 selecionados e 28 descartados com motivos explícitos), garantindo auditabilidade científica e rastreabilidade total:

| Coluna | Tipo | Domínio / Valores | Descrição |
|---|---|---|---|
| `full_name` | String | `owner/repo` | Identificador único no GitHub. |
| `stars` | Inteiro | Contagem | Estrelas do projeto no GitHub. |
| `language` | String | Texto | Linguagem predominante. |
| `status` | String | `SELECIONADO`, `DESCARTADO` | Decisão final do funil de triagem. |
| `motivo` | String | Texto livre | Justificativa técnica do descarte ou confirmação de aprovação. |
| `total_workflows` | Inteiro | Contagem | Total de workflows de CI detectados em `.github/workflows/`. |
| `releases_na_janela` | Inteiro | Contagem | Releases publicadas na janela de 12 meses. |
| `runs_na_janela` | Inteiro | Contagem | Workflow runs válidos do default branch na janela. |
