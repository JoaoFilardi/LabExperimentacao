# Protocolo de Rotulagem Independente da Amostra-Ouro (Avaliador: Kayque)

Issue: #35 (LAB03S02). Arquivo de saída: `lab03/data/rotulagem_amostra_ouro_kayque.csv`.

## 1. Escopo
- 60 repositórios, 5 releases por repositório (300 linhas), a partir de `lab03/data/amostra_ouro_base.csv`.
- A base deve conter releases **reais** coletadas com `coletar_releases_amostra_ouro.py` (semente 42).
  Nesta rotulagem foi usada a base existente do grupo (ver limitação na seção 2).
- Cada release foi julgada a partir das informações disponíveis na base (tag e título).

## 2. Declaração de independência
- Rotulagem feita sem consultar os rótulos de Joao e Tiago e sem ver a saída da heurística automática.
- **Registro de exposição prévia:** antes de rotular, tive contato com os documentos de protocolo de
  Joao e Tiago e com o script `gerar_rotulagem_tiago.py`, que contêm critérios e decisões de
  classificação deles. Não copiei rótulos; os julgamentos abaixo são meus. Isso fica registrado para
  ser considerado na análise de concordância.
- **Limitação:** a base `amostra_ouro_base.csv` usada nesta rotulagem foi gerada sinteticamente (tags, títulos e datas simulados, sem release notes reais). A rotulagem de `is_corretiva` baseou-se exclusivamente no título da release. Os resultados não validam a heurística em releases reais.
- Data de início da rotulagem: 13/10/2026 / Data de conclusão: 13/10/2026

## 3. Critérios operacionais (seguem as definições da issue #35)
**tipo_projeto:** `biblioteca/framework`, `aplicação/serviço`, `CLI`, `outro`.
Critério de desempate: modo primário de consumo pretendido pelos mantenedores.

**entrega_real:** `sim` / `não` / `incerto`. Valor único por repositório. Justificar todo `incerto`.

**is_corretiva (por release):** `sim` / `não`.
Meu critério: marquei "sim" quando o título da release indica correção de defeitos (ex.: "Maintenance & Bugfixes") e "não" nas demais.
Casos mistos (correções + features): não houve, pois cada título indica um só propósito.

## 4. Casos ambíguos
| Repositório / release | Dúvida | Decisão | Justificativa |
|---|---|---|---|
| (adicionar aqui os casos em que a decisão não foi óbvia, ex.: pytest, vite, deno, bun, repositórios de documentação) | | | |

## 5. Como validar
```
python -m lab03.src.validar_rotulagem lab03/data/rotulagem_amostra_ouro_kayque.csv --base lab03/data/amostra_ouro_base.csv
```