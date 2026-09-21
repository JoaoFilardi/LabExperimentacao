# Resultado da Analise Inferencial (Wilcoxon) — RQ1 e RQ2

**Issue:** [#21 — Analise Estatistica Inferencial (Teste de Wilcoxon) : RQ1 e RQ2](https://github.com/JoaoFilardi/LabExperimentacao/issues/21)
**Script:** `scripts/analise_inferencial.py`
**Dataset de entrada:** `data/log_trials_consolidado.csv`
**Data da execucao:** 2026-09-20

---

## 1. O que foi executado

O script aplica o Teste de Postos com Sinais de Wilcoxon (*Wilcoxon Signed-Rank Test*)
para amostras pareadas, comparando o Tratamento A (Manual) contra o Tratamento B
(Com IA), pareado por kata (K1-K4). Calcula mediana, IQR, estatistica W, p-valor
e tamanho de efeito (r de Rosenthal) para RQ1 (tempo) e RQ2 (taxa de sucesso).

Comando usado:
```
python scripts/analise_inferencial.py --log data/log_trials_consolidado.csv
```

## 2. Resultado obtido

### RQ1 — Produtividade Temporal (Time-to-Green)

| Metrica | Valor |
| --- | --- |
| N pares (katas) | **1** (apenas K1) |
| Mediana Manual (A) | 32.72 min |
| Mediana Com IA (B) | 8.00 min |
| Estatistica W | 0.0 |
| p-valor (unilateral) | 0.5 |
| r de Rosenthal | 0.0 |
| Conclusao formal | Nao rejeita H0 (sem evidencia estatistica suficiente) |

### RQ2 — Qualidade Funcional (Taxa de Sucesso nos Testes)

| Metrica | Valor |
| --- | --- |
| N pares (katas) | 3 (K1, K3, K4) |
| Diferencas pareadas | Todas iguais a zero |
| Resultado | Teste nao computavel (variancia nula) |

## 3. Interpretacao e limitacoes (leitura obrigatoria antes de citar este resultado)

**RQ1 nao pode ser considerado testado com poder estatistico.** Com N=1 par, o
teste de Wilcoxon unilateral tem piso matematico de p=0.5 — e **impossivel**
rejeitar H0 com uma unica observacao, independentemente da magnitude da
diferenca observada. O unico par completo disponivel (K1: 8 min com IA vs
32.72 min manual) e sugestivo, mas **anedotico, nao inferencial**.

A causa da perda de N nao foi falta de trials, e sim problema de granularidade
dos logs: 2 dos 5 registros de trial mediram o tempo de dois katas em conjunto
(ex.: "K2+K3: 17 min" em vez de um tempo por kata), tornando impossivel isolar
o T_TTG individual de K2 e K3 nesses casos. Outros 3 registros ficaram sem
tempo capturado (`NAO_REGISTRADO`).

**RQ2 nao pode ser testado com os dados atuais.** Todos os 10 trials
registrados, nos dois tratamentos, obtiveram 100% de aprovacao nos testes de
aceitacao. Sem nenhuma variancia entre os grupos, o teste de Wilcoxon nao tem
o que comparar — nao e um resultado de "sem diferenca", e um resultado de
"nao ha dado com variacao suficiente para o teste rodar".

**Achado adicional (nao relacionado a RQ1/RQ2, mas relevante para a integridade
do dataset):** durante a consolidacao, identificou-se que 3 dos 12 registros de
`data/metricas_estaticas.csv` (usado em RQ3) eram duplicatas de conteudo — o
mesmo arquivo de codigo registrado sob nomes de participantes diferentes. Essas
duplicatas foram documentadas e removidas do dataset de RQ3
(`metricas_estaticas_anotado.csv` preserva o registro original para auditoria).
Isso nao afetou diretamente os pares usados em RQ1/RQ2 acima, mas reforca que
o N amostral real do experimento, hoje, e menor do que o numero de linhas nos
CSVs sugere.

## 4. Recomendacao para a Sprint 03

1. Reportar os resultados acima como estao — nao rejeitar H0 em nenhuma das
   duas RQs — mas com a ressalva explicita de N insuficiente, nao como
   ausencia de efeito.
2. Se houver tempo antes da entrega final, priorizar a coleta de tempo
   **por kata** (nao por sessao) nos proximos trials, e garantir que cada
   trial gere pelo menos uma falha real de teste em algum momento do processo
   para que RQ2 tenha alguma variancia para medir (isso e esperado organicamente
   se os trials forem cronometrados do zero, sem pre-visualizar os testes).
3. Confirmar com os participantes duplicados (Joao, Tiago) se o
   reaproveitamento de codigo identificado foi intencional, e ajustar o
   relato metodologico do artigo final de acordo com a resposta.
