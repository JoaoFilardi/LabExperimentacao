# Concordância, consenso e validação da heurística (LAB03S02, issue #34)

## 1. Pré-condições
- As três rotulagens independentes (Kayque, Joao, Tiago) estão concluídas e versionadas.
- Os arquivos passam em `validar_rotulagem` e correspondem à **mesma amostra** (mesmos `repo_id`,
  `release_num`, `tag_name` e `release_url`). O executor interrompe a análise se não corresponderem.

## 2. Concordância (Fleiss' kappa)
- Implementação: `lab03/src/concordancia.py`, com `aggregate_raters` e `fleiss_kappa` do `statsmodels`.
- Unidade de análise:
  - `tipo_projeto` e `entrega_real`: atributos do repositório, **60 sujeitos** (`repo_id`).
  - `is_corretiva`: atributo da release, **300 sujeitos** (`repo_id`, `release_num`).
- Interpretação pelas faixas de Landis & Koch (1977).
- Se todos os avaliadores usarem uma única categoria em toda a amostra, o kappa é indefinido
  (variância zero) e é reportado como `indefinido`, junto com a concordância percentual total.
- Saídas: `lab03/data/concordancia_fleiss.csv` e `lab03/data/divergencias.csv`.

## 3. Procedimento de consenso e desempate
1. **Unanimidade (3 de 3):** o rótulo é adotado.
2. **Maioria (2 de 3):** o rótulo da maioria é adotado.
3. **Sem maioria** (3 rótulos distintos; só possível em `tipo_projeto` e `entrega_real`):
   o caso fica `PENDENTE` em `pendencias_consenso.csv`. O grupo decide em sessão e registra a
   decisão e o motivo em `lab03/data/desempates_consenso.csv`
   (colunas `dimensao, repo_id, release_num, valor_final, motivo`; use `release_num = 0` para
   dimensões por repositório). O executor reaplica os desempates de forma reproduzível.
4. Cada rótulo final registra o método (`unanimidade`, `maioria`, `desempate_grupo`, `pendente`).
- Saída: `lab03/data/amostra_ouro_final.csv` (versionada).

## 4. Avaliação da heurística
- Implementação: `lab03/src/heuristica_corretiva.py`; versões em `HEURISTICAS`.
- Classe positiva: `is_corretiva = sim`. Métricas: precisão, recall e F1, comparando a
  classificação da heurística com o rótulo de consenso.
- Regra: se o F1 da primeira versão for < 0,70, a próxima versão (refinamento) é avaliada;
  todas as versões avaliadas ficam registradas em `lab03/data/heuristica_avaliacao.csv`.
- Versões:
  - `v1_palavras_chave`: termos de correção (fix, bug, patch, hotfix, CVE, security, regression, crash)
    no título/notas da release.
  - `v2_palavras_e_semver`: refina a v1 usando sinais de evolução (feature, new, improvement,
    breaking...) e o bump de patch (x.y.Z, Z > 0) quando o texto é inconclusivo.
- Para avaliar a heurística que já existe no projeto (`releases.py`/`metricas.py`), adicione uma
  função `(row) -> "sim" | "não"` ao dicionário `HEURISTICAS`.

## 5. Limitação a declarar (base sintética)
Se a amostra-ouro foi gerada com tags e títulos fabricados (ex.: "Maintenance & Bugfixes"),
as heurísticas baseadas em título tendem a F1 próximo de 1,0 por circularidade, e o kappa
reflete a regra de rotulagem, não o julgamento sobre releases reais. Nesse caso, os resultados
não validam a heurística em releases reais.

## 6. Como reproduzir
```
python -m lab03.src.executar_analise_s02 \
  --kayque lab03/data/rotulagem_amostra_ouro_kayque.csv \
  --joao   lab03/data/rotulagem_amostra_ouro_joao.csv \
  --tiago  lab03/data/rotulagem_amostra_ouro_tiago.csv \
  [--desempates lab03/data/desempates_consenso.csv]
python -m pytest lab03/tests/test_analise_s02.py
```
Dependências: `pandas`, `statsmodels`, `openpyxl`.