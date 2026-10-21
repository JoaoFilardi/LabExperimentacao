# Bônus RQ08 — Deployment rework rate (LAB03S03, Opção A)

## 1. Escolha do grupo
O grupo optou pela **Opção A (deployment rework rate)**. Justificativa: _(preencher, ex.: reutiliza a definição de release corretiva da S02 e permite comparar diretamente com o CFR variante (b))_.

## 2. Definições

**Rework rate (por repositório)**

```
rework_rate = releases corretivas na janela / releases válidas na janela
```

- Janela de observação: 2025-10-01 a 2026-09-30 (`config.yaml`).
- Release válida: `draft=false` e `prerelease=false` (mesmo critério de `releases.py`).
- Release corretiva: depende do classificador (seção 5). Foram avaliadas três definições.

**CFR variante (b):** proporção de releases seguidas por release corretiva em até 7 dias; releases dos últimos 7 dias da janela são censuradas e saem do denominador. Aqui ele é **recalculado** a partir das mesmas releases e do mesmo classificador do rework, para as duas métricas serem comparáveis.

**Diferença de interpretação**
- Rework rate: fração das releases que são **correções** (esforço de retrabalho).
- CFR (b): fração das releases que **falharam** (foram seguidas por uma correção em até 7 dias).
- Uma correção isolada (sem release nos 7 dias anteriores) conta no rework, mas não no CFR (b). Uma correção após várias releases seguidas marca todas elas como falhas no CFR (b).

## 3. Dados e critérios de inclusão
- Fonte das releases: API REST do GitHub, `releases_rework.csv.gz` (43.127 releases válidas coletadas, com título e corpo).
- `metricas_dora.csv` lista 310 repositórios. **100 deles retornaram HTTP 404** na coleta: 99 linhas `*/platform-service-N` (ex.: `microsoft/platform-service-1`), que não correspondem a repositórios existentes, e `gorm.io/gorm` (nome incorreto; o repositório é `go-gorm/gorm`). Foram excluídos da análise.
- Dos 210 repositórios coletados, **180** têm releases válidas dentro da janela e entram na análise.
- Os valores de `cfr_delivery_proxy` do CSV **não foram reproduzíveis**: o CFR recalculado coincide com o do CSV em apenas 1 a 3 dos 310 repositórios, qualquer que seja o classificador (seção 6). Por isso a comparação usa o CFR recalculado.

## 4. Reprodução
```bash
python -m lab03.src.analise_rq08_bonus --coletar --direto          # coleta (uma vez)
python -m lab03.src.analise_rq08_bonus                              # título + corpo (heurística S02)
python -m lab03.src.analise_rq08_bonus --heuristica semver_patch    # bump de patch
python -m lab03.src.analise_rq08_bonus --sem-corpo                  # somente título/tag
python -m pytest lab03/tests/test_analise_rq08_bonus.py
```
Saídas: `lab03/data/` (padrão), `lab03/data/rq08_semver_patch/` e `lab03/data/rq08_sem_corpo/`, cada uma com `rework_rate_por_repo.csv`, `rework_rate_resumo.csv`, `rework_rate_comparacao_cfr.csv`, `tabela_rework_rate.md` e `rework_vs_cfr_b.png`.

## 5. Classificadores avaliados

| Classificador | Regra de "release corretiva" |
|---|---|
| **Título + corpo** (`v1_palavras_chave`, heurística da S02) | Termos de correção (fix, bug, patch, hotfix, CVE, security, regression, crash) no título ou no corpo |
| **Somente título** (`--sem-corpo`) | Mesma regra, ignorando o corpo |
| **Semver patch** (`semver_patch`) | Tag com bump de patch (`x.y.Z`, Z > 0) |

Nas releases reais coletadas, a heurística com corpo classifica **76,3%** das releases como corretivas, e com apenas o título, **1,8%**. O corpo está preenchido em 97,3% das releases.

## 6. Resultados (180 repositórios)

| Classificador | Rework: média | Rework: mediana (Q1–Q3) | CFR (b) recalc.: mediana (Q1–Q3) | Rework < CFR | Rework > CFR | Iguais | Spearman ρ (p) | Wilcoxon p | CFR do CSV confere |
|---|---|---|---|---|---|---|---|---|---|
| Título + corpo | 0,7987 | 0,9367 (0,75–1,00) | 0,2857 (0,00–0,55) | 10 | 156 | 14 | 0,10 (0,179) | 4,6e-27 | 2 de 310 |
| Semver patch | 0,6564 | 0,7183 (0,49–0,90) | 0,3333 (0,09–0,57) | 14 | 144 | 22 | 0,37 (2,8e-7) | 1,0e-23 | 3 de 310 |
| Somente título | 0,0118 | 0,0000 (0,00–0,00) | 0,0000 (0,00–0,00) | 0 | 4 | 176 | 0,90 (5,8e-68) | 0,068 | 1 de 310 |

_(Acrescentar o rework agregado e a figura de cada pasta, a partir de `tabela_rework_rate.md` e `rework_vs_cfr_b.png`.)_

Referência, `cfr_delivery_proxy` do CSV (n = 310, inclui as linhas inexistentes): média 0,3077, mediana 0,2935 (Q1 0,2015, Q3 0,4057).

## 7. Interpretação
- **O rework rate depende fortemente da definição de release corretiva.** A mediana vai de 0,94 (título + corpo) a 0,72 (semver patch) e 0,00 (só título). Nenhum desses valores pode ser lido como retrabalho real sem uma classificação validada em releases reais.
- **Título + corpo:** o rework fica saturado, porque quase todo changelog real cita termos como "fix" ou "bug". A correlação com o CFR (b) não é significativa (ρ = 0,10; p = 0,179).
- **Somente título:** o resultado é degenerado, com 176 dos 180 repositórios em zero nas duas métricas. O ρ = 0,90 vem de poucos repositórios não nulos e não é informativo.
- **Semver patch** é a definição mais interpretável: rework com mediana 0,72 e CFR (b) com mediana 0,33. O rework é maior que o CFR (b) em 144 dos 180 repositórios (80%). Isso é esperado, porque o rework conta toda release de patch, enquanto o CFR (b) só conta releases seguidas de correção em até 7 dias. A correlação é positiva e moderada-fraca (ρ = 0,37; p < 0,001): as duas métricas ordenam os repositórios de forma parecida, mas não são intercambiáveis. Os testes de Wilcoxon são significativos nas variantes com corpo e semver, mas refletem sobretudo que as métricas medem coisas diferentes, e não um efeito a investigar.
- **Releases de patch nem sempre corrigem falhas** (podem ser manutenção de rotina), então o rework pelo semver tende a superestimar o retrabalho. O versionamento por calendário (ex.: `2026.1.5`) gera falsos positivos.
- **Implicação para a RQ08:** o rework rate é útil como complemento ao CFR (b), mas só se a classificação de release corretiva for validada em releases reais. A heurística da S02, validada com F1 = 0,8764 em uma amostra provavelmente sintética, não se sustenta em releases reais.

## 8. Ameaças à validade
- **Validação da heurística:** a amostra-ouro da S02 não representa releases reais (ver `consenso_e_heuristica_s02.md`, seção 5). O F1 da S02 não vale para os dados desta análise.
- **CFR do CSV não reproduzido:** não foi possível reproduzir o `cfr_delivery_proxy` com nenhum dos três classificadores. _(Concluir após conferir a regra de `metricas.py`.)_
- **Linhas inexistentes em `metricas_dora.csv`:** 99 repositórios fictícios foram excluídos desta análise, mas permanecem no CSV e afetam as demais RQs.
- **Cobertura:** 180 dos 310 repositórios listados (58%); 30 repositórios coletados não têm releases válidas na janela.
- **Janela do CFR (b):** o resultado é sensível à janela de 7 dias; sugerido testar 3 e 14 dias com `--janela-cfr-dias`.