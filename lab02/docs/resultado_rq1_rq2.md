# Resultado da Analise Inferencial (Wilcoxon) — RQ1 e RQ2

**Issue:** [#21 — Analise Estatistica Inferencial (Teste de Wilcoxon) : RQ1 e RQ2](https://github.com/JoaoFilardi/LabExperimentacao/issues/21)  
**Script:** `scripts/analise_inferencial.py`  
**Dataset de entrada:** `data/log_trials_consolidado.csv` (12 trials completos)  
**Data da consolidacao final:** 2026-09-23  

---

## 1. O que foi executado

O script aplica o Teste de Postos com Sinais de Wilcoxon (*Wilcoxon Signed-Rank Test*) para amostras pareadas, comparando o Tratamento A (Manual) contra o Tratamento B (Com IA), pareado por kata ($K_1$ a $K_4$). Calcula mediana, IQR, estatistica $W$, p-valor e tamanho de efeito ($r$ de Rosenthal) para RQ1 (tempo) e RQ2 (taxa de sucesso).

Comando usado:
```bash
python scripts/analise_inferencial.py --log data/log_trials_consolidado.csv
```

---

## 2. Resultado obtido

### RQ1 — Produtividade Temporal (Time-to-Green)

| Metrica | Valor |
| :--- | :--- |
| **N pares (katas)** | **4** (todos os katas $K_1$, $K_2$, $K_3$, $K_4$) |
| **Mediana Manual (A)** | **28.19 min** (IQR = 5.10 min) |
| **Mediana Com IA (B)** | **8.14 min** (IQR = 0.91 min) |
| **Estatistica W** | **0.0000** (IA mais rapida em 100% dos katas) |
| **p-valor (unilateral)** | **0.0625** |
| **r de Rosenthal (tamanho de efeito)** | **0.7671** (efeito de grande magnitude, $r > 0.5$) |
| **Conclusao formal ($\alpha = 0.05$)** | Nao rejeita $H_0$ formalmente ($p \ge 0.05$), mas indica forte reducao temporal |

### RQ2 — Qualidade Funcional (Taxa de Sucesso nos Testes)

| Metrica | Valor |
| :--- | :--- |
| **N pares (katas)** | **4** ($K_1$ a $K_4$) |
| **Diferencas pareadas** | Todas iguais a zero (100% de sucesso em ambos os tratamentos) |
| **Resultado** | Teste nao computavel (variancia nula / efeito teto) |

---

## 3. Interpretacao e Discussao dos Resultados

### 3.1. RQ1 — Produtividade Temporal
1. **Reducao Expressiva de Tempo:** O uso de assistente de IA reduziu a mediana de resolução de **28.19 minutos para 8.14 minutos**, o que representa uma economia de mais de **71% no tempo de desenvolvimento**.
2. **Consistencia:** A dispersao com IA foi muito menor ($IQR = 0.91$ min vs $5.10$ min no manual), mostrando que a IA estabilizou o tempo de resolucao em torno de 6 a 10 minutos.
3. **Compreensao do p-valor ($p = 0.0625$):** 
   - Com $N = 4$ pares em um teste unilateral de Wilcoxon, o piso matematico teorico (quando a hipotese se confirma em 100% dos casos, $W = 0$) e:
     $$p_{\min} = \left(\frac{1}{2}\right)^4 = \frac{1}{16} = 0.0625$$
   - Ou seja, era **matematicamente impossivel** atingir $p < 0.05$ com $N=4$ pares. O fato de ter obtido $W = 0.0000$ e tamanho de efeito $r = 0.7671$ comprova que a diferenca a favor da IA foi maxima dentro da capacidade da amostra.

### 3.2. RQ2 — Qualidade Funcional e Efeito Teto
- Todos os 12 trials obtiveram 100% de sucesso nos testes de aceitacao.
- Como o time-box de 35 minutos foi suficiente para que os desenvolvedores corrigissem eventuais falhas antes da entrega final em ambos os tratamentos, observou-se um **efeito teto** (*ceiling effect*).
- O teste de Wilcoxon nao pôde ser computado devido a ausencia de variancia entre os tratamentos.
