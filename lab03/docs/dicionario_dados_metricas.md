# Dicionário de Dados - Métricas DORA (LAB03S02)

Este documento descreve detalhadamente cada campo presente no arquivo `metricas_dora.csv`, gerado pelo pipeline de cálculo de métricas DORA do **Laboratório 03**.

---

## 1. Identificação e Metadados do Repositório

| Coluna | Tipo | Unidade | Descrição / Origem |
|---|---|---|---|
| `full_name` | String | Texto | Identificador único `owner/repo` no GitHub. |
| `stars` | Inteiro | Contagem | Quantidade de estrelas (`stargazers_count`). |
| `primary_language` | String | Categoria | Linguagem principal predominante (`language`). |
| `age_years` | Float | Anos | Idade do repositório calculada até o fechamento da janela. |
| `contributors_count` | Inteiro | Contagem | Estimativa do total de contribuidores. |

---

## 2. RQ 01: Deployment Frequency

| Coluna | Tipo | Unidade | Descrição / Fórmula |
|---|---|---|---|
| `deployment_frequency_weekly` | Float | Releases / semana | $\text{valid\_releases\_count} \div \text{semanas da janela} (\approx 52.14)$. |
| `valid_releases_count` | Inteiro | Contagem | Total de releases publicadas (`draft=false`, `prerelease=false`) na janela de 12 meses. |

---

## 3. RQ 02: Lead Time for Changes

| Coluna | Tipo | Unidade | Descrição / Fórmula |
|---|---|---|---|
| `lead_time_by_release_days` | Float | Dias | **Variante (a):** Mediana de $(\text{data da release} - \text{commit mais antigo da release})$ entre as releases do repositório. |
| `lead_time_by_release_iqr_days` | Float | Dias | Intervalo interquartil ($Q_3 - Q_1$) da Variante (a). |
| `lead_time_by_commit_days` | Float | Dias | **Variante (b):** Mediana de $(\text{data da release} - \text{commit.author.date})$ considerando todos os commits de todas as releases avaliadas. |
| `lead_time_by_commit_iqr_days` | Float | Dias | Intervalo interquartil ($Q_3 - Q_1$) da Variante (b). |
| `total_commits_evaluated` | Inteiro | Contagem | Total de commits analisados em comparações válidas. |
| `excluded_first_release_count` | Inteiro | Contagem | Releases ignoradas por ausência de release anterior para comparação. |

---

## 4. RQ 03: Change Failure Rate (CFR)

| Coluna | Tipo | Unidade | Descrição / Fórmula |
|---|---|---|---|
| `cfr_ci_proxy` | Float | Proporção (0 a 1) | **Variante (a):** $\frac{\text{runs com falha}}{\text{runs com falha} + \text{runs com sucesso}}$ no default branch com `event=push`. |
| `cfr_ci_percentage` | Float | % | Proporção do CFR CI em percentual ($0\% \text{ a } 100\%$). |
| `cfr_delivery_proxy` | Float | Proporção (0 a 1) | **Variante (b):** Proporção de releases seguidas por release corretiva em até 7 dias: $\frac{\text{releases com falha}}{\text{releases avaliadas}}$. |
| `cfr_delivery_percentage` | Float | % | Proporção do CFR Entrega em percentual. |
| `cfr_delivery_censored_count` | Inteiro | Contagem | Releases publicadas nos últimos 7 dias da janela, censuradas e excluídas do denominador. |

---

## 5. RQ 04: Failed Deployment Recovery Time

| Coluna | Tipo | Unidade | Descrição / Fórmula |
|---|---|---|---|
| `recovery_time_hours` | Float | Horas | Mediana da duração dos episódios de falha recuperados: $(\text{fim do run com sucesso} - \text{início da primeira falha do episódio})$. |
| `recovery_time_iqr_hours` | Float | Horas | Intervalo interquartil ($Q_3 - Q_1$) do tempo de recuperação em horas. |
| `recovery_total_episodes` | Inteiro | Contagem | Total de episódios de falha iniciados dentro da janela de observação. |
| `recovery_censored_episodes` | Inteiro | Contagem | Episódios de falha que não foram recuperados antes do encerramento da janela (censurados). |
| `recovery_censored_ratio` | Float | Proporção (0 a 1) | Taxa de episódios censurados: $\frac{\text{recovery\_censored\_episodes}}{\text{recovery\_total\_episodes}}$. |

---

## 6. Classificação DORA de Referência (C1)

| Coluna | Tipo | Valores Válidos | Descrição |
|---|---|---|---|
| `dora_overall_category` | String | `Elite`, `High`, `Medium`, `Low` | Categoria geral: mediana dos scores das 4 métricas (Elite=4, High=3, Medium=2, Low=1) arredondada para baixo. |
| `dora_df_category` | String | `Elite`, `High`, `Medium`, `Low` | Enquadramento em Deployment Frequency. |
| `dora_lt_category` | String | `Elite`, `High`, `Medium`, `Low` | Enquadramento em Lead Time (Variante a). |
| `dora_cfr_category` | String | `Elite`, `High`, `Medium`, `Low` | Enquadramento em Change Failure Rate (Variante a). |
| `dora_rt_category` | String | `Elite`, `High`, `Medium`, `Low` | Enquadramento em Recovery Time. |
