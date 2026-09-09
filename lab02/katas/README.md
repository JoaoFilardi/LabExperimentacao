# Katas e testes de aceitacao

Esta pasta implementa a issue **Lab02S01 - Selecao de Katas e Testes de Aceitacao**.

## Objetos experimentais

Os quatro katas sao autorais e foram definidos para terem escopo de arquivo unico,
entrada deterministica e dificuldade comparavel. Cada participante deve resolver
dois katas no Tratamento A (manual) e dois no Tratamento B (com IA), conforme a
matriz contrabalanceada do desenho experimental.

| ID  | Kata                      | Habilidade principal     | Funcao                   | Testes |
| --- | ------------------------- | ------------------------ | ------------------------ | -----: |
| K1  | Intervalos de atendimento | Ordenacao e consolidacao | `mesclar_intervalos`     |      6 |
| K2  | Resumo de transacoes      | Agregacao e validacao    | `resumir_transacoes`     |      6 |
| K3  | Janelas de temperatura    | Janela deslizante        | `contar_janelas_validas` |      6 |
| K4  | Reposicao de estoque      | Ordenacao por prioridade | `planejar_reposicao`     |      6 |

Os enunciados estao nos docstrings dos arquivos de implementacao. Os arquivos em
`tests/` representam a suite fechada de aceitacao e nao devem ser alterados durante
os trials.

## Execucao

Na pasta `lab02`, instale `pytest` no ambiente escolhido e execute uma suite por vez:

```text
python -m pytest tests/test_kata_01_intervalos.py
python -m pytest tests/test_kata_02_transacoes.py
python -m pytest tests/test_kata_03_janelas.py
python -m pytest tests/test_kata_04_estoque.py
```

Antes da implementacao, os testes devem falhar por `NotImplementedError`. Durante
cada trial, o participante pode alterar apenas o arquivo da kata em execucao. O
tempo de cada trial continua limitado a 35 minutos, conforme o README do Lab02 e o
desenho experimental.

## Criterios de aceitacao

Um kata esta funcionalmente concluido quando sua suite apresenta `6 passed` e o
comando termina com exit code 0. O registro do experimento deve guardar o total de
testes, aprovados, falhos e o tempo ate a suite completa passar. Caso o time-box
seja atingido, registrar 35.0 minutos e o trial como censurado.
