# Relatório Estatístico e Discussão: RQ 05 e RQ 06 (Sprint 03)

## 1. RQ 05: Repositórios com maior frequência de deploy apresentam maior ou menor taxa de falha?

### 1.1. Resultados da Correlação de Postos de Spearman

| Relação Avaliada | N | $\rho$ de Spearman | IC 95% Bootstrap | p-valor | Magnitude (Dancey & Reidy) |
|---|:---:|:---:|:---:|:---:|:---:|
| **DF vs. CFR (Proxy CI)** | 310 | **0.003** | [-0.10, 0.11] | p = 0.961 | Desprezível |
| **DF vs. CFR (Proxy Entrega)** | 310 | **0.013** | [-0.10, 0.13] | p = 0.824 | Desprezível |

### 1.2. Discussão Metodológica e Hipóteses DORA
* **Avaliação da Tese DORA:** O referencial DORA defende que velocidade e estabilidade não formam um *trade-off*. Na amostra de repositórios open-source analisada, a correlação entre frequência de deploys e a taxa de falha não exibe correlação positiva penalizadora forte, indicando que deploys mais frequentes não aumentam sistematicamente o risco de falhas operacionais.
* **Ressalva Epistemológica Obrigatória:** Destaca-se enfaticamente que **correlação não implica causalidade**. Uma eventual associação positiva ou neutra pode ser governada por variáveis de confusão não observadas, como o rigor da suíte de testes de integração contínua e a política de code review do projeto.

---

## 2. RQ 06: Quais características dos repositórios estão associadas a um melhor desempenho DORA?

### 2.1. Resultados dos Testes Omnibus de Kruskal-Wallis com Correção de Holm

| Fator | Métrica DORA | Estatística $H$ | Graus de Lib. ($gl$) | p-valor Bruto | p-valor Holm ($p_{\text{adj}}$) | Tamanho Efeito ($\epsilon^2$) | Magnitude | Significativo ($lpha=0.05$)? |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `tipo_projeto` | `deployment_frequency_weekly` | 5.01 | 2 | 0.0815 | 1.0000 | 0.090 | Médio | Não |
| `tipo_projeto` | `lead_time_by_release_days` | 0.43 | 2 | 0.8082 | 1.0000 | 0.008 | Desprezível | Não |
| `tipo_projeto` | `lead_time_by_commit_days` | 0.22 | 2 | 0.8962 | 1.0000 | 0.004 | Desprezível | Não |
| `tipo_projeto` | `cfr_ci_percentage` | 1.81 | 2 | 0.4044 | 1.0000 | 0.032 | Pequeno | Não |
| `tipo_projeto` | `recovery_time_hours` | 1.74 | 2 | 0.4181 | 1.0000 | 0.031 | Pequeno | Não |
| `stars_quartile` | `deployment_frequency_weekly` | 22.40 | 3 | 0.0001 | 0.0012 | 0.073 | Médio | **Sim** |
| `stars_quartile` | `lead_time_by_release_days` | 2.63 | 3 | 0.4528 | 1.0000 | 0.009 | Desprezível | Não |
| `stars_quartile` | `lead_time_by_commit_days` | 3.47 | 3 | 0.3241 | 1.0000 | 0.011 | Pequeno | Não |
| `stars_quartile` | `cfr_ci_percentage` | 2.96 | 3 | 0.3980 | 1.0000 | 0.010 | Desprezível | Não |
| `stars_quartile` | `recovery_time_hours` | 0.71 | 3 | 0.8720 | 1.0000 | 0.002 | Desprezível | Não |
| `age_quartile` | `deployment_frequency_weekly` | 15.54 | 3 | 0.0014 | 0.0310 | 0.050 | Pequeno | **Sim** |
| `age_quartile` | `lead_time_by_release_days` | 0.99 | 3 | 0.8036 | 1.0000 | 0.003 | Desprezível | Não |
| `age_quartile` | `lead_time_by_commit_days` | 2.17 | 3 | 0.5384 | 1.0000 | 0.007 | Desprezível | Não |
| `age_quartile` | `cfr_ci_percentage` | 1.24 | 3 | 0.7436 | 1.0000 | 0.004 | Desprezível | Não |
| `age_quartile` | `recovery_time_hours` | 2.43 | 3 | 0.4881 | 1.0000 | 0.008 | Desprezível | Não |
| `language_group` | `deployment_frequency_weekly` | 28.64 | 5 | 0.0000 | 0.0007 | 0.093 | Médio | **Sim** |
| `language_group` | `lead_time_by_release_days` | 3.93 | 5 | 0.5588 | 1.0000 | 0.013 | Pequeno | Não |
| `language_group` | `lead_time_by_commit_days` | 3.91 | 5 | 0.5624 | 1.0000 | 0.013 | Pequeno | Não |
| `language_group` | `cfr_ci_percentage` | 3.16 | 5 | 0.6752 | 1.0000 | 0.010 | Pequeno | Não |
| `language_group` | `recovery_time_hours` | 3.58 | 5 | 0.6108 | 1.0000 | 0.012 | Pequeno | Não |
| `contributors_quartile` | `deployment_frequency_weekly` | 52.38 | 3 | 0.0000 | 0.0000 | 0.170 | Grande | **Sim** |
| `contributors_quartile` | `lead_time_by_release_days` | 3.72 | 3 | 0.2935 | 1.0000 | 0.012 | Pequeno | Não |
| `contributors_quartile` | `lead_time_by_commit_days` | 3.11 | 3 | 0.3748 | 1.0000 | 0.010 | Pequeno | Não |
| `contributors_quartile` | `cfr_ci_percentage` | 0.79 | 3 | 0.8516 | 1.0000 | 0.003 | Desprezível | Não |
| `contributors_quartile` | `recovery_time_hours` | 2.59 | 3 | 0.4593 | 1.0000 | 0.008 | Desprezível | Não |

---

## 3. Figuras Vetoriais e Rasterizadas Geradas
* `rq05_dispersao_df_vs_cfr.png` (300 DPI) e `.pdf` (Vetorial)
* `rq06_distribuicao_subgrupos.png` e `.pdf`
* `rq06_heatmap_effect_size.png` e `.pdf`
