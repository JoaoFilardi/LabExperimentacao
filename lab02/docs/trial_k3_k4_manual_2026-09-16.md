# Registro do Trial: Katas 03 e 04 Manual / Sem IA (Sprint 02)

**Issue:** [#17 — [Lab02S02] Execucao Trial : Katas 03 e 04 (Sem IA / Codificacao Manual)](https://github.com/JoaoFilardi/LabExperimentacao/issues/17)  
**Tratamento:** A (Codificação Manual / Baseline / Sem IA)  
**Participante:** João Filardi (`joao`)  
**Data:** 2026-09-16  
**Katas Avaliados:** K3 (`katas/kata_03_janelas.py`) e K4 (`katas/kata_04_estoque.py`)  

---

## 1. Sumário de Execução dos Testes

- **Suítes de Aceitação:** `tests/test_kata_03_janelas.py` e `tests/test_kata_04_estoque.py`
- **Ambiente de Execução:** Python 3.14.0 | pytest 9.1.1 | Windows
- **Comando de Verificação:** `python -m pytest tests/test_kata_03_janelas.py tests/test_kata_04_estoque.py`
- **Testes Totais:** 13 (7 em K3 + 6 em K4)
- **Testes Aprovados:** 13 (100%)
- **Testes Falhos:** 0 (0%)
- **Exit Code:** 0
- **Tempo de Execução do Runner:** 0.08 s
- **Time-to-Green Experimental (TTG):**
  - **Kata 03:** ~16 minutos
  - **Kata 04:** ~24 minutos
  - **Status de Censura:** Ambos não censurados ($\delta = 0$, concluídos dentro do limite de 35 min por kata)

---

## 2. Condições Operacionais do Tratamento A

Em conformidade rigorosa com o Desenho Experimental para o grupo de controle (Tratamento A):
- **Assistentes de IA Generativa:** Nenhuma ferramenta de IA (Copilot, Cursor, ChatGPT, Claude, Gemini) foi acionada durante a codificação.
- **Consultas Externas:** Sem buscas por respostas prontas em fóruns ou plataformas de desafios.
- **Raciocínio Algorítmico:**
  - *Kata 03:* Implementação direta de janela deslizante iterativa, calculando médias locais e validação de limites.
  - *Kata 04:* Filtragem com cálculo de déficit de estoque (`repor`), seguida de ordenação com duplo critério (maior reposição decrescente e desempate por nome alfabético crescente).

---

## 3. Métricas Estáticas de Código (RQ3)

Métricas coletadas via `scripts/analise_estatica.py` com **Radon 6.0.1** e registradas no arquivo consolidado `lab02/data/metricas_estaticas.csv`:

| Kata | Arquivo | Complexidade Média ($CC$) | Complexidade Máxima | LOC Total | SLOC | Linhas em Branco | Índice de Manutenibilidade ($MI$) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **K3** | `katas/kata_03_janelas.py` | 7.0 | 7 | 21 | 13 | 7 | 57.92 |
| **K4** | `katas/kata_04_estoque.py` | 5.0 | 5 | 25 | 15 | 9 | 61.25 |

---

## 4. Rastreabilidade e Conclusão

- **Conformidade Experimental:** Ambos os trials foram executados dentro do time-box de 35 minutos, validando o protocolo do modelo *within-subject*.
- **Encerramento da Issue:** Atendimento completo dos requisitos da Issue #17 para o participante João Filardi, integrando o código-fonte desenvolvido, testes 100% aprovados e métricas estáticas registradas na base de dados do projeto.
