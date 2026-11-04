# [LAB04S01] Fonte, Coleta e Análise Descritiva dos Dados Reais

**Arquivo de dados:** `lab04/data/amostra_dados_reais.csv`
**Estatísticas geradas:** `lab04/data/estatisticas_descritivas_reais.csv`
**Código:** `lab04/src/coleta_dados_reais.py` (coleta) · `lab04/src/dados_reais.py` (análise) · `lab04/tests/test_dados_reais.py`

> Itens marcados com **[PREENCHER]** dependem de como o grupo de fato obteve os dados e precisam ser confirmados antes da entrega.

## 1. Fonte

| Item | Valor |
|---|---|
| Plataforma | GitHub (API REST pública, `https://api.github.com`) |
| Repositório | `tiangolo/fastapi` (https://github.com/tiangolo/fastapi) |
| Janela temporal (`created_at`) | 2024-06-01 a 2024-06-30 (UTC) — **[PREENCHER: confirmar]** |
| Data da coleta | **[PREENCHER]** |
| Endpoints | `GET /repos/{repo}/pulls?state=closed`, `/issues/{n}/comments`, `/pulls/{n}/reviews`, `/pulls/{n}/comments` |

## 2. Procedimento de coleta

Reproduzível com:

```bash
export GITHUB_TOKEN=<token>   # opcional, mas evita o limite de 60 req/h
python -m lab04.src.coleta_dados_reais --repo tiangolo/fastapi \
    --inicio 2024-06-01 --fim 2024-06-30 --n 30 --seed 42
```

**[PREENCHER]** Se o CSV atual foi gerado por outro meio (consulta manual, GH Archive, BigQuery, notebook), descreva aqui exatamente como, e ajuste a seção 1.

## 3. Critérios de seleção

1. Apenas PRs **com merge** (`merged_at` não nulo) e criados na janela acima.
2. **Autor humano** (`user.type == "User"`): PRs abertos por bots (ex.: `dependabot[bot]`) são excluídos, para que "bot revisando" não se confunda com "bot como autor".
3. **`com_bot`**: PR com pelo menos uma interação (comentário, review ou comentário de review) feita por conta Bot (`user.type == "Bot"` ou login terminado em `[bot]`).
4. **`sem_bot`**: PR sem nenhuma interação de conta Bot.
5. `tempo_horas = merged_at − created_at`, em horas decimais, UTC; PRs com tempo ≤ 0 são descartados.
6. **Amostragem aleatória simples** de 30 PRs por grupo, com semente fixa (`seed = 42`).

## 4. Dicionário de dados

| Coluna | Tipo | Descrição |
|---|---|---|
| `pr_id` | int | Número do PR no repositório |
| `repositorio` | str | `owner/nome` |
| `grupo` | str | `com_bot` ou `sem_bot` |
| `bot_presente` | bool | Coerente com `grupo` (validado em código) |
| `nome_bot` | str | Logins dos bots que interagiram (`;` como separador) ou `nenhum` |
| `created_at` / `merged_at` | datetime | UTC |
| `tempo_horas` | float | **Unidade: horas.** `merged_at − created_at` |

## 5. Verificações de qualidade (`validar_qualidade`)

Valores ausentes · `pr_id` e linhas duplicados · rótulos de grupo inválidos · tempos ≤ 0 · `merged_at` anterior a `created_at` · `tempo_horas` divergente de `merged_at − created_at` (tolerância 0,05 h) · `bot_presente` incoerente com `grupo`.

**Resultado no CSV atual:** nenhuma ausência, duplicação ou inconsistência; 30 PRs por grupo.

## 6. Estatísticas descritivas (horas)

| Grupo | n | Média | DP | Mín | Q1 | Mediana | Q3 | Máx | Skew | Curtose | Outliers (Tukey) | μ_log | σ_log |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sem_bot | 30 | 27,42 | 24,20 | 2,40 | 12,38 | 18,90 | 33,30 | 105,50 | 1,69 | 2,49 | 3 | 2,972 | 0,867 |
| com_bot | 30 | 20,95 | 20,06 | 1,20 | 8,82 | 13,60 | 25,60 | 88,00 | 1,82 | 3,02 | 3 | 2,638 | 0,963 |
| pooled (H₀) | 60 | 24,19 | — | — | — | 16,65 | — | — | — | — | — | 2,805 | 0,924 |

## 7. Forma das distribuições

- Ambos os grupos têm **forte assimetria à direita** (skew ≈ 1,7–1,8), média > mediana e 3 outliers por grupo pela regra de Tukey (1,5·IQR).
- Shapiro-Wilk **rejeita normalidade** na escala original (p < 0,001 nos dois grupos) e **não rejeita** na escala logarítmica (p > 0,9) → a **lognormal é um modelo plausível**, coerente com a Seção 11 de `cenario_e_hipoteses.md`.
- Os coeficientes de variação são altos (≈ 0,9–1,0), o que sustenta testar cenários de cauda pesada em Q3.

## 8. Parâmetros para a simulação

| Uso | Parâmetro | Valor |
|---|---|---|
| Q1 (H₀ verdadeira) | μ_log, σ_log pooled | 2,805 · 0,924 |
| Q2/Q3 (efeito) | diferença de μ_log entre grupos | 2,972 − 2,638 = 0,334 (razão de medianas ≈ 1,40) |
| Q3 (cauda pesada) | σ_log por grupo | 0,867 (sem_bot) · 0,963 (com_bot) |

Obtidos por `obter_resumo_estatistico_reais()`.

## 9. Limitações

- Um único repositório, um mês: não generaliza para outros projetos.
- Observacional: a presença de bot não foi atribuída aleatoriamente (PRs maiores/menores podem receber bots de forma diferente), então a diferença observada não prova causalidade.
- n = 30 por grupo: estimativas de σ_log e de caudas são imprecisas.