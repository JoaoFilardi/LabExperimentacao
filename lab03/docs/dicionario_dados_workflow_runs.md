# Dicionário de Dados - Workflow Runs, CFR (CI) e Tempo de Recuperação (LAB03S01)

Artefatos gerados por `python -m lab03.src.coleta_workflow_runs` a partir de `repositorios_selecionados.csv`. A classificação de sucesso/falha é a mesma usada pelo funil de seleção (módulo `metricas_ci`).

## 1. `workflow_runs.csv`

Uma linha por execução coletada (branch padrão, `event=push`, `created_at` na janela).

| Coluna | Tipo | Unidade | Descrição / Origem |
|---|---|---|---|
| `repo` | String | Texto | Identificador `owner/name`. |
| `id` | Inteiro | Identificador | `id` do workflow run na API. |
| `workflow_id` | Inteiro | Identificador | `workflow_id` (agrupamento da RQ 04). |
| `name` | String | Texto | Nome do workflow. |
| `created_at` | String (ISO-8601) | Data/Hora UTC | Criação do run (`created_at`). |
| `run_started_at` | String (ISO-8601) | Data/Hora UTC | Início da execução; fallback para `created_at`. |
| `updated_at` | String (ISO-8601) | Data/Hora UTC | Última atualização (fim aproximado da execução). |
| `status` | String | Categoria | `status` da API (`completed`, `in_progress`, …). |
| `conclusion` | String | Categoria | `conclusion` bruta da API. |
| `branch` | String | Texto | `head_branch` (deve coincidir com a branch padrão). |
| `event` | String | Categoria | Evento disparador (`push`). |
| `classificacao` | String | Categoria | `sucesso`, `falha` ou `ignorar` (Seção 3 do laboratório). |

## 2. `recovery_episodes.csv`

Um episódio de falha por workflow: começa na primeira falha após um sucesso e termina no sucesso seguinte.

| Coluna | Tipo | Unidade | Descrição / Fórmula |
|---|---|---|---|
| `repo` | String | Texto | Identificador `owner/name`. |
| `workflow_id` | Inteiro | Identificador | Workflow em que o episódio ocorreu. |
| `first_failure_id` | Inteiro | Identificador | `id` da primeira falha do episódio. |
| `first_failure_started_at` | String (ISO-8601) | Data/Hora UTC | `run_started_at` da primeira falha. |
| `failures_in_episode` | Inteiro | Contagem | Falhas consecutivas até a recuperação (ou o fim da janela). |
| `censored` | Booleano | Indicador | `true` se não houve sucesso posterior na janela. |
| `recovery_run_id` | Inteiro | Identificador | `id` do run de sucesso que encerra o episódio (vazio se censurado). |
| `recovery_updated_at` | String (ISO-8601) | Data/Hora UTC | `updated_at` do sucesso de recuperação. |
| `recovery_hours` | Float | Horas | `updated_at(sucesso) − run_started_at(primeira falha)`. Nulo se censurado. |

## 3. `qualidade_ci_repositorio.csv`

Resumo por repositório para integração com as RQs 03a e 04.

| Coluna | Tipo | Unidade | Descrição / Fórmula |
|---|---|---|---|
| `repo` | String | Texto | Identificador `owner/name`. |
| `default_branch` | String | Texto | Branch usada na coleta. |
| `total_runs_coletados` | Inteiro | Contagem | Runs após filtro de branch, evento e janela. |
| `runs_sucesso` | Inteiro | Contagem | `conclusion = success`. |
| `runs_falha` | Inteiro | Contagem | `failure`, `timed_out` ou `startup_failure`. |
| `runs_ignorados` | Inteiro | Contagem | Demais conclusões (ou vazias). |
| `cfr_ci` | Float | Proporção (0–1) | `runs_falha / (runs_falha + runs_sucesso)`. |
| `episodios_recuperados` | Inteiro | Contagem | Episódios com sucesso posterior na janela. |
| `episodios_censurados` | Inteiro | Contagem | Episódios sem recuperação na janela. |
| `proporcao_censurados` | Float | Proporção (0–1) | `episodios_censurados / total de episódios`. |
| `mediana_recuperacao_horas` | Float | Horas | Mediana dos `recovery_hours` dos episódios recuperados. |
| `erro` | String | Texto | Mensagem se a coleta do repositório falhou; vazio em sucesso. |
