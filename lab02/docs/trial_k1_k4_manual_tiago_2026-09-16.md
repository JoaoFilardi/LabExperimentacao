# Registro oficial do trial: Katas 01 e 04 sem IA

- Tratamento: A (sem assistente de IA)
- Participante: Tiago
- Data: 2026-09-16
- Assistente de IA: desabilitado
- Time-box por kata: 35 minutos
- Prompts/interacoes com IA: 0

## Resultados

| Kata | Testes totais | Aprovados | Falhos | Taxa de sucesso | Tempo | Censurado |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| K1 - Intervalos | 6 | 6 | 0 | 100% | 32 min 43 s (32,72 min) | Nao |
| K4 - Estoque | 6 | 6 | 0 | 100% | 34 min 08 s (34,13 min) | Nao |
| Total | 12 | 12 | 0 | 100% | - | - |

## Criterio de encerramento

Os dois Katas foram concluídos antes do limite de 35 minutos por trial, com todas as verificacoes da suite de aceitacao aprovadas. Portanto, nenhum trial foi censurado.

## Suites executadas

```text
python -m pytest tests/test_kata_01_intervalos.py
python -m pytest tests/test_kata_04_estoque.py
```

Resultados observados:

```text
K1: 6 passed
K4: 6 passed
```

## Observacao metodologica

Os tempos registrados sao os informados pelo participante no cronometro do trial. O tempo do K1 foi de 32 minutos e 43 segundos; o tempo do K4 foi de 34 minutos e 08 segundos. Cada kata teve seu proprio time-box de 35 minutos.
