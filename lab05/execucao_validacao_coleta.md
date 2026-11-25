# Execução e Validação da Coleta de Dados do Experimento

**Experimento:** Comparação de desempenho e consumo de recursos entre PostgreSQL 17 e PostgreSQL 18  
**Issue:** `#66` — `[ LAB05S02 ] Executar e validar a coleta de dados do experimento`  
**Responsável:** João Victor Filardi Souza Pinto (`JoaoFilardi`)  
**Sprint:** 2 (`LAB05S02`)  
**Data da execução:** 25/11/2026 (`21:56:33 UTC` a `22:11:47 UTC`)  

---

## 1. Resumo da Execução

A coleta definitiva do experimento foi executada com sucesso em **25/11/2026**, totalizando **72 execuções registradas** de `pgbench` (**60 repetições válidas medidas** — 30 no **PostgreSQL 17.12** e 30 no **PostgreSQL 18.7** — mais **12 execuções de aquecimento/*warm-up*** preservadas nos dados brutos e separadas dos dados tratados), somando **1.657.378 transações SQL reais processadas** (`836.780` no PG17 e `820.598` no PG18) com **0 transações falhas** e **0 erros de execução**.

Todos os conjuntos de dados brutos, logs do `pgbench`, metadados de ambiente/configuração (`pg_settings`), dados validados e relatórios de auditoria estão versionados no repositório e aprovados pelos testes automatizados (`pytest` — 6/6 testes aprovados).

---

## 2. Adaptação Transparente do Ambiente de Execução (Independência da Issue `#64`)

Conforme registrado em `contextualizacao_lab05_postgresql.md`, a estratégia original previa o uso do **Docker Desktop** (cuja configuração pertence à Issue `#64`, atribuída a outro integrante e ainda pendente no momento desta execução). Além disso, na estação de trabalho utilizada nesta execução, o Docker Desktop e o WSL2 não estavam instalados.

Para cumprir integralmente a Issue `#66` com **evidências 100% reais (sem qualquer simulação)** e **sem interferir nos arquivos ou escopo da Issue `#64`**, adotaram-se duas decisões técnicas documentadas:

1. **Execução com binários oficiais portáteis do PostgreSQL (EnterpriseDB / distribuição oficial Windows do `postgresql.org`):**
   - **PostgreSQL 17.12:** `postgresql-17.12-2-windows-x64-binaries.zip`
   - **PostgreSQL 18.7:** `postgresql-18.7-2-windows-x64-binaries.zip`
   - Os binários e os diretórios de dados (`data_pg17` e `data_pg18`) foram mantidos em diretório temporário externo ao repositório (`%LOCALAPPDATA%\lab05_pg_runtime`), garantindo isolamento total entre as duas versões e preservando intacta qualquer instalação prévia do sistema operacional.
   - As duas instâncias utilizaram portas exclusivas (`55432` para PG17 e `55433` para PG18), parâmetros padronizados de `postgresql.conf` e **execução estritamente sequencial** (apenas uma instância PostgreSQL ativa por vez).
   - O monitoramento de CPU (%) e memória RAM (MiB) foi realizado em paralelo a cada execução de `pgbench` sobre toda a árvore de processos da instância (`postmaster` + processos *workers*/*backends* filhos) via `psutil` em intervalos de `1,0 s`, gerando série temporal equivalente ao `docker stats`.
2. **Compatibilidade preservada com Docker (`--backend docker`):**
   - O script [executar_coleta.py](file:///c:/Users/joaov/OneDrive/%C3%81rea%20de%20Trabalho/LabExperimentacao/lab05/src/executar_coleta.py) implementa suporte nativo a ambos os modos (`--backend native` e `--backend docker`), permitindo reexecução imediata sobre os containers da Issue `#64` caso a equipe deseje comparar os resultados em ambiente containerizado.

> **Nota para a Issue `#67` (revisão metodológica):** essa adaptação elimina o *overhead* de virtualização do WSL2/Docker Desktop no Windows, mas deve ser refletida na atualização das ameaças à validade e na descrição do ambiente final.

---

## 3. Especificações do Ambiente e Protocolo Executado

### 3.1 Hardware e software do hospedeiro

*Fonte:* [metadata_ambiente.json](file:///c:/Users/joaov/OneDrive/%C3%81rea%20de%20Trabalho/LabExperimentacao/lab05/data/raw/metadata_ambiente.json)

| Item | Valor registrado |
| :--- | :--- |
| **Sistema operacional** | `Windows-11-10.0.26200-SP0` (`AMD64`) |
| **Processador** | `Intel64 Family 6 Model 154 Stepping 4, GenuineIntel` |
| **Núcleos físicos / lógicos** | `6` físicos / `8` lógicos |
| **Memória RAM total** | `7,71 GiB` |
| **Python / `psutil`** | `Python 3.14.0` / `psutil 7.2.2` |
| **Versões do SGBD** | **PostgreSQL 17.12** (`55432`) × **PostgreSQL 18.7** (`55433`) |
| **Janela da coleta (UTC)** | `2026-11-25T21:56:33+00:00` até `2026-11-25T22:11:47+00:00` (`15 min 14 s`) |

### 3.2 Parâmetros padronizados do protocolo experimental

| Parâmetro | Valor adotado | Justificativa |
| :--- | :---: | :--- |
| **Delineamento temporal** | 12 blocos contrabalanceados **ABBA** (`5` repetições/bloco) | Equilibra exatamente a posição média no tempo (**índice médio de bloco = `6,5` para PG17 e `6,5` para PG18**), mitigando deriva térmica e efeitos de ordem. |
| **Repetições válidas por versão ($n$)** | `30` (60 medidas totais) | Atende à meta de `20–30` repetições prevista em `planejamento_analise_estatistica.md`. |
| **Carga de trabalho (`pgbench`)** | TPC-B-like padrão (`-s 10`, `-c 8`, `-j 4`, `-T 10`, `-P 5`) | 1.000.000 linhas em `pgbench_accounts`, ~27.000–29.000 transações por repetição (~1,65 milhão no total). |
| **Semente determinística** | `--random-seed = 4200 + repeticao` | Reprodutibilidade e paridade de distribuição pseudoaleatória de chaves entre repetições correspondentes. |
| **Warm-up por bloco** | `5 s` antes das 5 repetições de cada bloco (`12` warm-ups) | Estabiliza *shared buffers* e caches após cada reinício; registrado em `raw` (`is_warmup=True`) e excluído de `processed`. |
| **Cooldown** | `2 s` entre repetições / `3 s` ao trocar versão | Estabilização do sistema operacional e isolamento térmico/I/O entre blocos. |
| **Amostragem de recursos** | `1,0 s` (`459` amostras validadas; `507` brutas) | Captura série temporal contínua de CPU (%) e memória RSS (MiB) durante cada repetição. |
| **Configuração base (`postgresql.conf`)** | `shared_buffers=256MB`, `work_mem=4MB`, `maintenance_work_mem=64MB`, `effective_cache_size=1GB`, `max_connections=100`, `checkpoint_timeout=15min`, `max_wal_size=1GB`, `synchronous_commit=on` | Paridade explícita dos principais parâmetros de memória, WAL e concorrência. |

---

## 4. Auditoria de Equivalência de Configurações (`pg_settings`)

Antes das medições, o script coletou todos os parâmetros efetivos de ambas as instâncias (`380` parâmetros no PG17.12 e `400` no PG18.7), registrados integralmente em [metadata_ambiente.json](file:///c:/Users/joaov/OneDrive/%C3%81rea%20de%20Trabalho/LabExperimentacao/lab05/data/raw/metadata_ambiente.json).

Todos os parâmetros explícitos de *baseline* permaneceram idênticos entre as versões. A auditoria identificou diferenças **nativas de arquitetura/padrões da versão 18** que fazem parte do comportamento *out-of-the-box* da atualização PG17 → PG18 e são cruciais para a interpretação na Sprint 2/3:

| Parâmetro | PostgreSQL 17.12 | PostgreSQL 18.7 | Significado técnico |
| :--- | :---: | :---: | :--- |
| **`data_checksums`** | `off` | **`on`** | A partir do PostgreSQL 18, checksums de página de dados passaram a ser ativados **por padrão** no `initdb`, elevando a proteção contra corrupção de disco com pequeno custo adicional de CPU/escrita. |
| **`io_method`** *(novo no PG18)* | *(inexistente)* | **`worker`** | Novo subsistema nativo de I/O Assíncrono (AIO) do PostgreSQL 18 ativo por padrão. |
| **`io_workers`** *(novo no PG18)* | *(inexistente)* | **`3`** | Processos *background workers* adicionais alocados para o subsistema AIO. |
| **`effective_io_concurrency`** | `0` | **`16`** | Novo valor padrão introduzido junto à arquitetura de AIO no PG18. |
| **`maintenance_io_concurrency`** | `0` | **`16`** | Novo valor padrão de concorrência de I/O para operações de manutenção no PG18. |
| **`shared_memory_size`** | `279 MB` | **`286 MB`** | Memória compartilhada calculada automaticamente pelo SGBD com o mesmo `shared_buffers = 256MB` (crescimento esperado pelas estruturas de AIO e novos recursos). |

---

## 5. Estrutura dos Arquivos Versionados e Dicionário de Dados

A separação estrita entre **dados brutos** (`raw`) e **dados validados** (`processed`) segue a Seção 9 de `contextualizacao_lab05_postgresql.md`:

```text
lab05/
├── requirements.txt
├── execucao_validacao_coleta.md                  # Esta documentação (entregável #66)
├── src/
│   ├── executar_coleta.py                        # Orquestrador da coleta (native e docker)
│   └── validar_dados.py                          # Validador e gerador dos datasets tratados
├── tests/
│   └── test_validacao_dados.py                   # Testes automatizados de coleta e validação
└── data/
    ├── raw/                                      # Dados brutos imutáveis + trilha de auditoria
    │   ├── benchmark_raw.csv                     # 72 linhas (60 medidas + 12 warm-ups)
    │   ├── resource_timeseries_raw.csv           # 507 amostras de 1s de CPU e memória
    │   ├── metadata_ambiente.json                # Hardware, agenda ABBA e pg_settings completos
    │   └── logs_pgbench/                         # 72 arquivos .log integrais do pgbench
    └── processed/                                # Dados validados prontos para a Issue #68
        ├── benchmark_validado.csv                # 60 linhas válidas + flags não destrutivas de outliers
        ├── resource_timeseries_validado.csv      # 459 amostras vinculadas às 60 execuções válidas
        └── relatorio_validacao.json              # Relatório estruturado da bateria de validação
```

### Dicionário de dados — `benchmark_validado.csv`

| Coluna | Tipo | Unidade / Domínio | Descrição |
| :--- | :---: | :---: | :--- |
| `run_id` | `str` | `RUN_001`..`RUN_072` | Identificador único da execução (chave de ligação com `resource_timeseries_validado.csv` e logs). |
| `timestamp_utc` | `str` | ISO-8601 UTC | Instante de início da execução. |
| `block_id` | `int` | `1`..`12` | Índice do bloco ABBA em que a execução ocorreu. |
| `order_global` | `int` | `1`..`72` | Ordem cronológica global da rodada. |
| `versao` | `str` | `PG17` \| `PG18` | Tratamento experimental (variável independente). |
| `versao_exata` | `str` | `17.12` \| `18.7` | Versão menor exata executada. |
| `repeticao` | `int` | `1`..`30` | Número sequencial da repetição dentro da versão (`0` nos warm-ups em `raw`). |
| `is_warmup` | `bool` | `False` | Indicador de aquecimento (sempre `False` em `processed`; `True` nos 12 warm-ups de `raw`). |
| `backend` | `str` | `native_windows_binaries` | Modo de execução empregado. |
| `random_seed` | `int` | `4201`..`4230` | Semente passada ao `pgbench --random-seed`. |
| `scale_factor`, `clientes`, `threads`, `duracao_planejada_s` | `int` | `10`, `8`, `4`, `10 s` | Parâmetros fixos de controle do `pgbench`. |
| `duracao_real_s` | `float` | segundos (`s`) | Duração efetiva de relógio (*wall-clock*) da chamada do `pgbench`. |
| `transacoes_processadas` | `int` | contagem | Total de transações concluídas na rodada (`number of transactions actually processed`). |
| `transacoes_falhas` | `int` | contagem | Total de transações com falha (`0` em todas as rodadas). |
| `latencia_media_ms` | `float` | `ms` *(razão)* | Latência média por transação reportada pelo `pgbench`. |
| `latencia_dp_ms` | `float` | `ms` *(razão)* | Desvio padrão intrarrodada da latência reportado pelo `pgbench`. |
| `tempo_conexao_inicial_ms` | `float` | `ms` *(razão)* | Tempo inicial de abertura das conexões dos clientes. |
| `tps` | `float` | `tx/s` *(razão)* | Vazão em transações por segundo (`without initial connection time`). |
| `cpu_media_pct`, `cpu_pico_pct` | `float` | `%` *(escala multi-core / Docker: 100% = 1 núcleo)* | Consumo médio e de pico de CPU da árvore de processos do PostgreSQL. |
| `cpu_normalizada_media_pct`, `cpu_normalizada_pico_pct` | `float` | `%` (`0`–`100%` da máquina) | Consumo de CPU normalizado pelo total de `8` núcleos lógicos. |
| `memoria_media_mib`, `memoria_pico_mib` | `float` | `MiB` *(razão)* | Soma da memória residente (RSS) média e de pico dos processos do PostgreSQL. |
| `amostras_recursos` | `int` | contagem | Quantidade de amostras de `1 s` capturadas durante a execução. |
| `status`, `observacoes` | `str` | `OK` / texto | Status operacional e eventuais anotações de erro. |
| `outlier_latencia`, `outlier_tps`, `outlier_cpu`, `outlier_memoria` | `bool` | `True` / `False` | Flags não destrutivas (`1,5 × IQR` por versão) criadas na validação sem excluir nenhuma observação. |

---

## 6. Resultados da Validação dos Dados

A validação foi executada via [validar_dados.py](file:///c:/Users/joaov/OneDrive/%C3%81rea%20de%20Trabalho/LabExperimentacao/lab05/src/validar_dados.py), produzindo [relatorio_validacao.json](file:///c:/Users/joaov/OneDrive/%C3%81rea%20de%20Trabalho/LabExperimentacao/lab05/data/processed/relatorio_validacao.json):

| Verificação | Resultado | Evidência |
| :--- | :---: | :--- |
| **Completude e balanceamento** | ✅ Aprovado | `30` repetições válidas para `PG17` e `30` para `PG18` (`60` medidas + `12` warm-ups em `raw`). |
| **Balanceamento temporal ABBA** | ✅ Aprovado | Índice médio de bloco exatamente igual: **`6,5`** (`PG17`) vs **`6,5`** (`PG18`). |
| **Valores ausentes (`NaN`/nulos)** | ✅ Aprovado | `0` nulos em `benchmark_validado.csv` e `0` nulos em `resource_timeseries_validado.csv`. |
| **Duplicidades** | ✅ Aprovado | `0` `run_id` duplicados; `0` pares `(versao, repeticao)` duplicados. |
| **Erros e falhas de transação** | ✅ Aprovado | `100%` das execuções com `status == OK` e `transacoes_falhas == 0`. |
| **Restrições de domínio e escala** | ✅ Aprovado | Todas as 9 checagens de positividade, intervalo `[0, 100%]`, `pico >= média` e amostras mínimas passaram. |
| **Consistência cruzada `TPS × (tx/duração)`** | ✅ Aprovado | Diferença relativa máxima de **`5,00%`** (dentro da tolerância de `20%`, compatível com `initial connection time`). |
| **Consistência cruzada com série temporal** | ✅ Aprovado | Todas as `60` execuções vinculadas às `459` amostras com médias idênticas (`diff < 0,15`). |
| **Testes automatizados (`pytest`)** | ✅ Aprovado | `6 passed in 1.61s` ([test_validacao_dados.py](file:///c:/Users/joaov/OneDrive/%C3%81rea%20de%20Trabalho/LabExperimentacao/lab05/tests/test_validacao_dados.py)). |

### 6.1 Resumo de sanidade dos dados validados (pré-análise)

> **Escopo:** a tabela abaixo serve exclusivamente para verificação de sanidade e plausibilidade física das métricas coletadas na Issue `#66`. A análise estatística formal (normalidade, testes de hipótese, correção para múltiplas comparações, tamanho do efeito e gráficos) pertence à **Issue `#68`**.

| Versão | Métrica | $n$ | Média | Mediana | DP | Mínimo | Máximo |
| :---: | :--- | :-: | ---: | ---: | ---: | ---: | ---: |
| **PG17** | Latência média (`ms`) | 30 | `2,8355` | `2,8245` | `0,0701` | `2,7290` | `3,0020` |
| **PG18** | Latência média (`ms`) | 30 | `2,8848` | `2,8715` | `0,0760` | `2,7730` | `3,0960` |
| **PG17** | Vazão (`TPS`) | 30 | `2820,48` | `2830,30` | `68,94` | `2661,96` | `2928,42` |
| **PG18** | Vazão (`TPS`) | 30 | `2772,61` | `2783,93` | `71,34` | `2581,64` | `2882,20` |
| **PG17** | CPU média (`%` multi-core) | 30 | `489,18` | `488,27` | `15,38` | `441,80` | `512,42` |
| **PG18** | CPU média (`%` multi-core) | 30 | `493,97` | `496,78` | `16,02` | `439,49` | `521,81` |
| **PG17** | Memória RSS média (`MiB`) | 30 | `496,58` | `500,33` | `15,86` | `443,83` | `512,47` |
| **PG18** | Memória RSS média (`MiB`) | 30 | `536,93` | `541,64` | `15,88` | `490,75` | `551,18` |

### 6.2 Outliers sinalizados (preservados sem exclusão)

Em estrita observância à regra de integridade científica (*não apagar resultados desfavoráveis*), nenhuma execução foi removida. Observações fora do intervalo $[Q_1 - 1{,}5 \times \text{IQR},\; Q_3 + 1{,}5 \times \text{IQR}]$ foram apenas sinalizadas em colunas booleanas para análise de sensibilidade na Issue `#68`:

- **Latência (`outlier_latencia`):** `RUN_032` (`PG18` rep 11: `3,052 ms`) e `RUN_056` (`PG18` rep 21: `3,096 ms`).
- **TPS (`outlier_tps`):** `RUN_056` (`PG18` rep 21: `2581,64 TPS`).
- **CPU (`outlier_cpu`):** `RUN_014` (`PG18` rep 06: `439,49%`), `RUN_051` (`PG17` rep 22: `442,96%`) e `RUN_052` (`PG17` rep 23: `441,80%`).
- **Memória (`outlier_memoria`):** `RUN_014` (`PG18` rep 06: `492,35 MiB`), `RUN_018` (`PG18` rep 10: `501,10 MiB`), `RUN_051` (`PG17` rep 22: `443,83 MiB`), `RUN_052` (`PG17` rep 23: `444,85 MiB`) e `RUN_065` (`PG18` rep 29: `490,75 MiB`).

---

## 7. Problemas Encontrados e Ajustes Realizados Durante a Execução

Durante o teste de fumaça prévio à coleta definitiva, foram identificados e corrigidos dois problemas técnicos no script de automação:

1. **Bloqueio de herança de *pipes* do `pg_ctl` no Windows:** ao iniciar o servidor com `subprocess.run(..., capture_output=True)`, o processo filho `postgres.exe` herdava os descritores de `stdout`/`stderr`, impedindo o retorno do comando após a inicialização. **Correção:** redirecionamento explícito de `stdin`/`stdout`/`stderr` para `subprocess.DEVNULL` em `native_start()` e `native_stop()`, com log do servidor gravado em `server.log` via `-l`.
2. **`VACUUM ANALYZE` em bloco transacional implícito no `psql`:** passar `VACUUM ANALYZE; CHECKPOINT;` em uma única flag `-c` fazia o PostgreSQL encapsular os dois comandos em uma transação, retornando erro. **Correção:** separação em duas flags distintas (`-c "VACUUM ANALYZE;" -c "CHECKPOINT;"`).

Após esses dois ajustes, a coleta definitiva de 72 execuções transcorreu integralmente sem erros.

---

## 8. Como Reproduzir e Validar

```powershell
# 1. Instalar dependências (caso necessário)
pip install -r lab05/requirements.txt

# 2. (Opcional) Reexecutar coleta completa no modo nativo ou Docker
$env:PYTHONPATH="."
python lab05/src/executar_coleta.py --backend native --repetitions 30 --block-size 5
# ou, quando os containers da Issue #64 estiverem ativos:
# python lab05/src/executar_coleta.py --backend docker --container-pg17 postgres_17 --container-pg18 postgres_18

# 3. Executar validação e regenerar datasets tratados
python lab05/src/validar_dados.py

# 4. Rodar suíte de testes automatizados
pytest lab05/tests/test_validacao_dados.py -v
```

---

## 9. Verificação dos Critérios de Aceitação (Issue `#66`)

| Critério de aceitação da Issue `#66` | Status | Evidência |
| :--- | :---: | :--- |
| Coleta completa realizada | ✅ | 72 execuções reais registradas (30 medidas PG17 + 30 medidas PG18 + 12 warm-ups; 1.657.378 transações). |
| Dados organizados e estruturados | ✅ | Separação clara entre `lab05/data/raw/` e `lab05/data/processed/` com dicionário documentado. |
| Inconsistências identificadas e tratadas | ✅ | Warm-ups separados dos dados tratados; outliers IQR sinalizados sem exclusão; 0 nulos/duplicidades/falhas. |
| Dados validados | ✅ | `relatorio_validacao.json` aprovado (`"aprovado": true`) + `pytest` (`6 passed`). |
| Arquivos versionados no repositório | ✅ | Scripts, testes, dados brutos, dados validados, logs e documentação prontos para commit na pasta `lab05/`. |
| Procedimentos de coleta documentados | ✅ | Documentação completa neste arquivo (`lab05/execucao_validacao_coleta.md`) e metadados em `metadata_ambiente.json`. |

---

## 10. Disponibilização para as Próximas Issues (Sprint 2)

- **Para a Issue `#68` (Análise estatística):** consumir diretamente `lab05/data/processed/benchmark_validado.csv` (60 observações pareadas por semente / balanceadas por bloco ABBA) e `lab05/data/processed/resource_timeseries_validado.csv` (459 amostras para os gráficos temporais da Seção 7.3 de `planejamento_analise_estatistica.md`).
- **Para a Issue `#67` (Revisão de metodologia e ameaças à validade):** incorporar o achado técnico da auditoria `pg_settings` (`data_checksums = on`, `io_method = worker`, `io_workers = 3` ativos por padrão no PG18) e registrar a execução nativa com binários oficiais portáteis.
