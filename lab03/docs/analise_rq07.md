# RQ07: Sensibilidade das classificações DORA (Sprint 03, Issue #41)

## 1. Objetivo

Medir quanto a classificação DORA muda quando se alteram as definições operacionais de lead time e de change failure rate, e verificar se as conclusões das RQ01 a RQ06 permanecem.

## 2. Combinações de definições operacionais

C1 é a referência. Em todas as combinações a classificação geral é a mediana dos 4 scores (Elite=4, High=3, Medium=2, Low=1) arredondada para baixo, com os mesmos cortes da Seção 5.

| Combinação | Deploy | Lead time | CFR | Recovery | Descrição |
| --- | --- | --- | --- | --- | --- |
| C1 | deployment_frequency_weekly | lead_time_by_release_days | cfr_ci_proxy | recovery_time_hours | Deploy = release publicada; lead time por release; CFR pelo proxy de CI. |
| C2 | deployment_frequency_weekly | lead_time_by_commit_days | cfr_ci_proxy | recovery_time_hours | Igual à C1, trocando o lead time por release pelo lead time por commit. |
| C3 | deployment_frequency_weekly | lead_time_by_release_days | cfr_delivery_proxy | recovery_time_hours | Igual à C1, trocando o CFR por CI pelo CFR por entrega (release seguida de corretiva em 7 dias). |
| C4 | deployment_frequency_weekly | lead_time_by_commit_days | cfr_delivery_proxy | recovery_time_hours | Troca as duas definições de uma vez. |

## 3. Reprodução

```
python -m lab03.src.analise_rq07 --input lab03/data/classificacao_dora_c1.csv
```

Entrada: `classificacao_dora_c1.csv` (310 repositórios). Saídas: `classificacao_dora_combinacoes.csv`, `rq07_*.csv`, `tabelas_artigo_sbc_rq07.tex` e as figuras `rq07_*.png/.pdf`.

## 4. Resultados

### 4.1 Distribuição da classificação geral por combinação

| combinacao | n | Elite | High | Medium | Low |
| --- | --- | --- | --- | --- | --- |
| C1 | 310 | 0 | 111 | 199 | 0 |
| C2 | 310 | 0 | 143 | 167 | 0 |
| C3 | 310 | 0 | 46 | 244 | 20 |
| C4 | 310 | 0 | 67 | 225 | 18 |

### 4.2 Mudança de categoria e kappa ponderado por par

`pct_melhoraram`/`pct_pioraram` são relativos à segunda combinação do par. O kappa usa pesos lineares na escala Low < Medium < High < Elite.

| par | n_repositorios | n_mudaram | pct_mudaram | pct_melhoraram | pct_pioraram | delta_medio_score | kappa_ponderado_linear | interpretacao_kappa |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 x C2 | 310 | 32 | 10.32 | 10.32 | 0.0 | 0.1032 | 0.7889 | Concordância substancial |
| C1 x C3 | 310 | 84 | 27.1 | 0.0 | 27.1 | -0.2742 | 0.41 | Concordância moderada |
| C1 x C4 | 310 | 93 | 30.0 | 5.16 | 24.84 | -0.2 | 0.3649 | Concordância razoável |
| C2 x C3 | 310 | 115 | 37.1 | 0.0 | 37.1 | -0.3774 | 0.2976 | Concordância razoável |
| C2 x C4 | 310 | 93 | 30.0 | 0.0 | 30.0 | -0.3032 | 0.4344 | Concordância moderada |
| C3 x C4 | 310 | 23 | 7.42 | 7.42 | 0.0 | 0.0742 | 0.8214 | Concordância quase perfeita |

### 4.3 Onde a mudança acontece (por métrica)

| par | pct_mudou_df | pct_mudou_lt | pct_mudou_cfr | pct_mudou_rt |
| --- | --- | --- | --- | --- |
| C1 x C2 | 0.0 | 21.29 | 0.0 | 0.0 |
| C1 x C3 | 0.0 | 0.0 | 80.97 | 0.0 |
| C1 x C4 | 0.0 | 21.29 | 80.97 | 0.0 |
| C2 x C3 | 0.0 | 21.29 | 80.97 | 0.0 |
| C2 x C4 | 0.0 | 0.0 | 80.97 | 0.0 |
| C3 x C4 | 0.0 | 21.29 | 0.0 | 0.0 |

### 4.4 RQ05 por definição de CFR

| combinacoes | metrica_df | metrica_cfr | n | rho | p_valor | sinal | magnitude | significativo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1,C2 | deployment_frequency_weekly | cfr_ci_proxy | 310 | 0.0028 | 0.960531 | positivo | Desprezível | False |
| C3,C4 | deployment_frequency_weekly | cfr_delivery_proxy | 310 | 0.0127 | 0.824039 | positivo | Desprezível | False |

### 4.5 RQ06 por combinação (Kruskal-Wallis do score geral, Holm global)

| combinacao | fator | n | H | gl | p_bruto | p_holm | epsilon2 | significativo |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | stars_quartile | 310 | 2.2871 | 3 | 0.514998 | 1.0 | 0.0074 | False |
| C1 | age_quartile | 310 | 3.7406 | 3 | 0.290877 | 1.0 | 0.0121 | False |
| C1 | contributors_quartile | 310 | 2.2142 | 3 | 0.529163 | 1.0 | 0.0072 | False |
| C1 | language_group | 310 | 2.7196 | 5 | 0.743121 | 1.0 | 0.0088 | False |
| C2 | stars_quartile | 310 | 0.8609 | 3 | 0.834841 | 1.0 | 0.0028 | False |
| C2 | age_quartile | 310 | 1.7919 | 3 | 0.616692 | 1.0 | 0.0058 | False |
| C2 | contributors_quartile | 310 | 3.4696 | 3 | 0.324728 | 1.0 | 0.0112 | False |
| C2 | language_group | 310 | 5.179 | 5 | 0.394426 | 1.0 | 0.0168 | False |
| C3 | stars_quartile | 310 | 2.2063 | 3 | 0.530702 | 1.0 | 0.0071 | False |
| C3 | age_quartile | 310 | 8.1184 | 3 | 0.043628 | 0.61079 | 0.0263 | False |
| C3 | contributors_quartile | 310 | 7.2113 | 3 | 0.065461 | 0.850987 | 0.0233 | False |
| C3 | language_group | 310 | 2.7031 | 5 | 0.745639 | 1.0 | 0.0087 | False |
| C4 | stars_quartile | 310 | 1.2904 | 3 | 0.731408 | 1.0 | 0.0042 | False |
| C4 | age_quartile | 310 | 9.8453 | 3 | 0.019928 | 0.29892 | 0.0319 | False |
| C4 | contributors_quartile | 310 | 12.1373 | 3 | 0.006927 | 0.110836 | 0.0393 | False |
| C4 | language_group | 310 | 7.0115 | 5 | 0.219788 | 1.0 | 0.0227 | False |

### 4.6 Figuras

- `rq07_distribuicao_combinacoes.png`
- `rq07_matriz_mudanca_kappa.png`
- `rq07_transicoes_c1.png`

## 5. Robustez das conclusões das RQ01 a RQ06

| rq | pergunta | evidencia | veredito |
| --- | --- | --- | --- |
| RQ01 | Deployment Frequency | Todas as combinações usam a mesma definição de deploy (release publicada). | invariante por construção |
| RQ02 | Lead Time (por release x por commit) | 21.3% dos repositórios mudam de categoria de LT; Spearman entre variantes = 0.9802; Wilcoxon pareado p = 0.0. | parcialmente sensível |
| RQ03 | CFR (CI x entrega) | 81.0% dos repositórios mudam de categoria de CFR; Spearman entre variantes = -0.0485; Wilcoxon pareado p = 0.0. | sensível |
| RQ04 | Recovery Time | Todas as combinações usam o mesmo tempo de recuperação (episódios por workflow, com censura). | invariante por construção |
| RQ05 | DF x CFR (Spearman) | cfr_ci_proxy: rho=0.003 (Desprezível, p=0.9605); cfr_delivery_proxy: rho=0.013 (Desprezível, p=0.8240) | robusta |
| RQ06 | Fatores associados ao desempenho DORA | stars_quartile: significativo em nenhuma; age_quartile: significativo em nenhuma; contributors_quartile: significativo em nenhuma; language_group: significativo em nenhuma | robusta |
| Geral | Classificação DORA geral (C1 x demais) | % que muda de categoria: 10.3% a 30.0%; kappa linear: 0.365 a 0.789. | parcialmente sensível |

Foram comparadas 4 combinações (C1, C2, C3, C4) em 6 pares. A porcentagem de repositórios que mudam de categoria DORA geral varia de 7.4% (C3 x C4) a 37.1% (C2 x C3), e o kappa de Cohen ponderado linearmente varia de 0.298 a 0.821.

A dimensão que mais contribui para a instabilidade é CFR (média de 54.0% de repositórios mudando de categoria por par). Deployment Frequency e Recovery Time não são alterados pelas combinações C1 a C4; a variação vem exclusivamente das trocas de definição de lead time e de CFR.

Sentido da mudança em relação à referência: C2 tende a classificar melhor que C1 (delta médio de score +0.10); C3 tende a classificar pior que C1 (delta médio de score -0.27); C4 tende a classificar pior que C1 (delta médio de score -0.20).

**RQ02** (Lead Time (por release x por commit)): conclusão **parcialmente sensível**. 21.3% dos repositórios mudam de categoria de LT; Spearman entre variantes = 0.9802; Wilcoxon pareado p = 0.0.

**RQ03** (CFR (CI x entrega)): conclusão **sensível**. 81.0% dos repositórios mudam de categoria de CFR; Spearman entre variantes = -0.0485; Wilcoxon pareado p = 0.0.

**RQ05** (DF x CFR (Spearman)): conclusão **robusta**. cfr_ci_proxy: rho=0.003 (Desprezível, p=0.9605); cfr_delivery_proxy: rho=0.013 (Desprezível, p=0.8240)

**RQ06** (Fatores associados ao desempenho DORA): conclusão **robusta**. stars_quartile: significativo em nenhuma; age_quartile: significativo em nenhuma; contributors_quartile: significativo em nenhuma; language_group: significativo em nenhuma

**RQ01 e RQ04** usam a mesma definição em todas as combinações; suas conclusões são invariantes a estas escolhas, mas continuam dependentes das definições de deploy (release publicada) e de recuperação (episódios por workflow com censura), que não foram variadas aqui.

Convenção de leitura: uma dimensão é considerada robusta quando menos de 10% dos repositórios mudam de categoria, parcialmente sensível entre 10% e 30% e sensível acima disso. Os limiares são uma escolha desta análise, não do enunciado.

## 6. Limitações

- As combinações variam apenas lead time e CFR; a variante "release publicada x release + pré-release" só entra se o dataset tiver a coluna `deployment_frequency_with_prerelease_weekly` (C5).
- Os cortes DORA e a regra da mediana com arredondamento para baixo são os mesmos em todas as combinações; mudar a regra de agregação poderia alterar a sensibilidade.
- As variantes de lead time e de CFR são proxies de entrega e CI, não medidas diretas de deploy em produção.
