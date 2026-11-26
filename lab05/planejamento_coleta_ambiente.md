# Preparação do Ambiente e Planejamento de Coleta de Dados

**Experimento:** Comparação de desempenho e consumo de recursos entre PostgreSQL 17 e PostgreSQL 18  
**Issue:** `#64` — `[ LAB05S01 ] Preparar ambiente e planejamento de coleta de dados`  
**Responsável:** Integrante B — Instrumentação e Operação  
**Sprint:** 1 (`LAB05S01`)  
**Data:** 25/11/2026  

---

## 1. Objetivo e Escopo da Entrega

Este documento consolida a preparação da infraestrutura, a seleção das ferramentas de instrumentação, a definição operacional das métricas coletadas, os procedimentos de armazenamento e versionamento, os cuidados éticos e o roteiro de coleta piloto para o experimento **PostgreSQL 17 × PostgreSQL 18**, em alinhamento estrito com:

- [contextualizacao_lab05_postgresql.md](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/contextualizacao_lab05_postgresql.md)
- [planejamento_metodologico.md](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/planejamento_metodologico.md) *(Issue `#63`)*
- [planejamento_analise_estatistica.md](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/planejamento_analise_estatistica.md) *(Issue `#65`)*

> **Integração com o repositório:** durante o avanço do projeto, a equipe já integrou os scripts principais de automação e validação ([executar_coleta.py](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/src/executar_coleta.py) e [validar_dados.py](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/src/validar_dados.py)). Para evitar duplicação de código e preservar intactos os dados da Sprint 2, a preparação da Issue `#64` reutiliza esses módulos e adiciona a infraestrutura Docker prevista ([docker-compose.yml](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/docker/docker-compose.yml)) e o orquestrador isolado de piloto ([coleta_piloto.py](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/src/coleta_piloto.py)).

---

## 2. Requisitos Técnicos para Execução da Pesquisa

| Categoria | Requisito mínimo / adotado | Finalidade no experimento |
| :--- | :--- | :--- |
| **Sistema operacional** | Windows 11 (com Docker Desktop + WSL2) ou ambiente com binários oficiais portáteis do PostgreSQL | Hospedar isoladamente as instâncias PostgreSQL 17 e 18 e executar o orquestrador Python. |
| **Motor de containers** | Docker Desktop + Docker Compose v2 (`docker compose`) | Executar `postgres:17.12-bookworm` e `postgres:18.7-bookworm` com limites idênticos de CPU/memória e volumes separados. |
| **Runtime Python** | Python `>= 3.11` (testado no projeto com `3.14`) | Executar coleta piloto, coleta definitiva, monitoramento de recursos e validação automática. |
| **Dependências Python** | `pandas>=2.2.0`, `numpy>=1.26.0`, `scipy>=1.13.0`, `psutil>=6.0.0`, `pytest>=8.0.0` ([requirements.txt](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/requirements.txt)) | Orquestração via `subprocess`, amostragem via `psutil`, validação tabular via `pandas` e suíte de testes via `pytest`. |
| **Recursos de hardware** | CPU multi-core (mín. 4 núcleos lógicos recomendados), `>= 8 GiB` RAM, `>= 5 GiB` livres em disco | Alocar até `4.0 CPUs` e `2 GiB` de RAM por container sem estrangulamento severo do hospedeiro. |
| **Portas de rede locais** | `127.0.0.1:5432` (PG17 Docker), `127.0.0.1:5433` (PG18 Docker); ou `55432`/`55433` (modo nativo) | Evitar conflito de portas entre as versões e com eventuais bancos locais pré-existentes. |
| **Ferramenta de carga** | `pgbench` (nativo dentro de cada imagem oficial `postgres` ou dos binários portáteis) | Inicializar esquema TPC-B-like e gerar carga transacional controlada e determinística (`--random-seed`). |

---

## 3. Ferramentas Selecionadas para Instrumentação e Coleta

| Ferramenta | Papel no estudo | Justificativa técnica |
| :--- | :--- | :--- |
| **Docker + Docker Compose** | Isolamento e reprodutibilidade de ambiente | Evita instalar múltiplas versões diretamente no SO, fixa tags exatas (`postgres:17.12-bookworm` e `postgres:18.7-bookworm`) na mesma base Debian Bookworm e aplica tetos idênticos de CPU e RAM (`4.0 CPUs`, `2 GiB`). |
| **`pgbench`** *(ferramenta oficial PostgreSQL)* | Gerador de carga e medidor de latência/TPS | Ferramenta padrão do próprio SGBD, com geração determinística via `--random-seed` e medição direta de transações processadas, falhas, latência média, desvio padrão e TPS. |
| **Python 3** | Orquestração e automação do protocolo | Automatiza o desenho contrabalanceado ABBA, warm-ups, cooldowns, coleta de `pg_settings`, geração de CSVs/logs e pós-validação sem intervenção manual sujeita a erro humano. |
| **`docker stats` / `psutil`** | Instrumentação de CPU e memória RAM | No modo `docker`, `DockerResourceMonitor` consulta `docker stats --no-stream` a cada `1,0 s`; no modo `native`, `NativeResourceMonitor` usa `psutil` na árvore de processos (`postmaster` + filhos). Ambos produzem exatamente o mesmo esquema de série temporal. |
| **`pandas` + `pytest`** | Consistência e testes automatizados | Garante verificação objetiva de nulos, duplicidades, domínio, consistência cruzada entre métricas e sinalização não destrutiva de outliers (`1,5 × IQR`). |
| **Git / GitHub** | Versionamento de infraestrutura, scripts e dados | Garante trilha auditável e reprodutibilidade integral para toda a equipe e avaliadores. |

---

## 4. Ambiente Preparado (Infraestrutura Docker e Paridade de Configuração)

### 4.1 Especificação dos containers ([docker-compose.yml](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/docker/docker-compose.yml))

1. **Tags explícitas e mesma base de SO (sem `latest`):**
   - **Tratamento A:** `postgres:17.12-bookworm` (`container_name: postgres_17`, porta `127.0.0.1:5432:5432`).
   - **Tratamento B:** `postgres:18.7-bookworm` (`container_name: postgres_18`, porta `127.0.0.1:5433:5432`).
2. **Volumes isolados e compatibilidade com a mudança do PostgreSQL 18:**
   - No `postgres:17.12-bookworm`, o volume `lab05_pg17_data` é montado em `/var/lib/postgresql/data`.
   - A partir do PostgreSQL 18, a imagem oficial alterou o `PGDATA` padrão para `/var/lib/postgresql/18/docker` e o ponto de montagem para `/var/lib/postgresql`. Por isso, `lab05_pg18_data` é montado em `/var/lib/postgresql`.
3. **Limites equivalentes de recursos:**
   - Ambos os serviços recebem `cpus: 4.0`, `mem_limit: 2g` e `memswap_limit: 2g`.
4. **Parâmetros baseline equivalentes ([postgresql-baseline.conf](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/docker/postgresql-baseline.conf)):**
   - Aplicados identicamente via flags `-c` nos dois containers e em paridade com `BASELINE_PG_CONF` de [executar_coleta.py](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/src/executar_coleta.py):
     - `max_connections = 100`
     - `shared_buffers = 256MB`
     - `work_mem = 4MB`
     - `maintenance_work_mem = 64MB`
     - `effective_cache_size = 1GB`
     - `checkpoint_timeout = 15min`
     - `max_wal_size = 1GB`
     - `synchronous_commit = on`
     - `logging_collector = off`
     - `log_min_messages = warning`
5. **Auditoria obrigatória de padrões arquiteturais do PG18:**
   - O orquestrador coleta `SELECT name, setting ... FROM pg_settings` de ambos os containers para registrar diferenças nativas *out-of-the-box* entre PG17 e PG18 (por exemplo, `data_checksums`, `io_method`, `io_workers`, `effective_io_concurrency` e `maintenance_io_concurrency`), sem alterá-las artificialmente.

---

## 5. Definição das Informações Coletadas

Todas as decisões em aberto listadas na Seção 11 de [planejamento_metodologico.md](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/planejamento_metodologico.md) ficam padronizadas conforme abaixo:

### 5.1 Métricas principais e critério padronizado de TPS

| Métrica | Campo no CSV | Instrumento / Definição exata | Unidade | Escala |
| :--- | :--- | :--- | :---: | :---: |
| **Latência média** | `latencia_media_ms` | `latency average` reportada pelo `pgbench` | `ms` | Razão |
| **Desvio padrão da latência** | `latencia_dp_ms` | `latency stddev` intrarrodada reportada pelo `pgbench` | `ms` | Razão |
| **Tempo inicial de conexão** | `tempo_conexao_inicial_ms` | `initial connection time` reportado pelo `pgbench` | `ms` | Razão |
| **Vazão (TPS)** | `tps` | **`without initial connection time`** (`tps = ...` padrão do `pgbench`), eliminando o ruído de handshake inicial da medição da vazão sustentada | `tx/s` | Razão |
| **CPU (bruta e normalizada)** | `cpu_media_pct`, `cpu_pico_pct`, `cpu_normalizada_media_pct`, `cpu_normalizada_pico_pct` | Média e pico durante a rodada via `docker stats` (ou `psutil` no modo nativo). Escala multi-core (`100% = 1 núcleo`) e normalizada (`0–100%` dos núcleos lógicos do host) | `%` | Razão |
| **Memória RAM** | `memoria_media_mib`, `memoria_pico_mib` | Média e pico de `MEM USAGE` (`docker stats`) ou soma RSS da árvore de processos (`psutil`) durante a rodada | `MiB` | Razão |

### 5.2 Metadados e informações complementares coletadas por execução

- **Identificação e desenho:** `run_id`, `timestamp_utc` (ISO-8601), `block_id`, `order_global`, `versao` (`PG17`/`PG18`), `versao_exata` (`17.12`/`18.7`), `repeticao`, `is_warmup` (`True`/`False`), `backend`.
- **Parâmetros de controle da rodada:** `random_seed`, `scale_factor`, `clientes`, `threads`, `duracao_planejada_s`, `duracao_real_s`.
- **Integridade transacional:** `transacoes_processadas`, `transacoes_falhas`, `amostras_recursos`, `status` (`OK`/`ERRO`), `observacoes`.
- **Série temporal contínua (`resource_timeseries_raw.csv`):** `run_id`, `timestamp_utc`, `segundo_relativo`, `versao`, `repeticao`, `is_warmup`, `cpu_pct`, `cpu_normalizada_pct`, `memoria_mib`, `num_processos_pg` (resolução alvo de `1,0 s`).
- **Auditoria do ambiente (`metadata_ambiente.json`):** hardware, SO, versão de Python/`psutil`, `docker inspect` (tag, ID da imagem, limites de CPU/RAM), agenda ABBA e dicionário completo + *diff* de `pg_settings`.
- **Logs brutos (`logs_pgbench/`):** saída integral `stdout`/`stderr` e código de retorno de cada chamada ao `pgbench`.

---

## 6. Parâmetros do Protocolo e Calibração para Coleta Piloto

Para validar o pipeline de ponta a ponta em tempo hábil (~2 a 3 minutos no piloto) antes da coleta definitiva ($n = 30$ por versão), o script [coleta_piloto.py](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/src/coleta_piloto.py) adota os seguintes parâmetros iniciais calibrados:

| Parâmetro | Valor no Piloto | Valor na Coleta Definitiva | Justificativa |
| :--- | :---: | :---: | :--- |
| **Delineamento** | 4 blocos ABBA (`PG17`, `PG18`, `PG18`, `PG17`) | 12 blocos ABBA | Mantém índice médio de bloco idêntico (`2,5` vs `2,5` no piloto; `6,5` vs `6,5` na definitiva). |
| **Repetições válidas ($n$)** | `4` por versão (`2`/bloco) | `30` por versão (`5`/bloco) | Suficiente no piloto para checar variabilidade, amostragem de `docker stats` e consistência cruzada. |
| **Scale factor (`-s`)** | `10` (~1.000.000 linhas em `pgbench_accounts`) | `10` | Base não trivial (~150–160 MB) que cabe em `shared_buffers = 256MB` após warm-up, reduzindo ruído de disco frio. |
| **Concorrência (`-c`, `-j`)** | `8` clientes / `4` threads | `8` clientes / `4` threads | Gera carga concorrente real acima de 1 sessão sem saturar completamente os limites do container antes da medição. |
| **Duração medida (`-T`)** | `10 s` | `10 s` | Garante ~7 a 10 amostras de `docker stats` (`>= 5` exigido pelo validador) e milhares de transações por rodada. |
| **Warm-up / Cooldown** | `5 s` warm-up por bloco; `2 s` entre rodadas; `3 s` entre blocos | Idêntico | Estabiliza buffers após troca de versão; warm-ups são registrados com `is_warmup=True` em `raw` e excluídos de `processed`. |
| **Semente (`--random-seed`)** | `4200 + repeticao` | `4200 + repeticao` | Garante sequência pseudoaleatória reproduzível e pareada entre PG17 e PG18. |
| **Amostragem de recursos** | `1,0 s` | `1,0 s` | Resolução adequada para capturar média, pico e evolução temporal durante `10 s`. |

---

## 7. Armazenamento, Organização e Versionamento dos Dados

### 7.1 Estrutura de diretórios

```text
lab05/
├── docker/
│   ├── docker-compose.yml               # Infraestrutura PG17.12 x PG18.7 isolada
│   └── postgresql-baseline.conf         # Referência documentada de parâmetros baseline
├── src/
│   ├── coleta_piloto.py                 # Coleta piloto (#64) com saída isolada em data/pilot/
│   ├── executar_coleta.py               # Coleta definitiva (#66) em data/raw/
│   └── validar_dados.py                 # Validador e gerador de data/.../processed/
├── tests/
│   ├── test_coleta_piloto.py            # Testes unitários da preparação e piloto (#64)
│   └── test_validacao_dados.py          # Testes do coletor e validador (#66)
└── data/
    ├── pilot/                           # Isolado para coleta piloto da Issue #64
    │   ├── raw/                         # benchmark_raw.csv, resource_timeseries_raw.csv, metadata_ambiente.json, logs_pgbench/
    │   └── processed/                   # benchmark_validado.csv, resource_timeseries_validado.csv, relatorio_validacao.json
    ├── raw/                             # Dados brutos definitivos (Sprint 2 - #66)
    └── processed/                       # Dados tratados definitivos (Sprint 2 - #66)
```

### 7.2 Regras de governança e versionamento

1. **Separação estrita entre piloto, bruto e tratado:** dados de piloto gravam exclusivamente em `lab05/data/pilot/`; dados definitivos gravam em `lab05/data/raw/` (imutável) e `lab05/data/processed/` (derivado reproduzível via `validar_dados.py`).
2. **Imutabilidade e integridade:** resultados brutos em `raw/` nunca são editados manualmente, nem execuções com erro ou valores desfavoráveis são apagadas.
3. **Sinalização não destrutiva:** eventuais outliers (`1,5 × IQR` por versão) recebem apenas flags booleanas (`outlier_latencia`, `outlier_tps`, `outlier_cpu`, `outlier_memoria`) em `processed/`.
4. **Codificação e formato:** todos os CSVs e JSONs são gravados em `UTF-8` com cabeçalhos padronizados e delimitador `,` (CSV) ou indentação `2` espaços (JSON).
5. **Versionamento no Git/GitHub:** infraestrutura Docker, scripts, testes e datasets versionados em commits vinculados às respectivas issues (`#64`, `#66`, `#68`).

---

## 8. Procedimentos Éticos e Integridade Científica

Em conformidade com a Seção 2 e a Seção 10 de [README.md](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/README.md) e com [contextualizacao_lab05_postgresql.md](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/contextualizacao_lab05_postgresql.md):

1. **Proibição de testes em sistemas de terceiros:** nenhuma carga ou teste de estresse é direcionado a servidores externos, APIs públicas ou instâncias de produção de terceiros. Toda execução ocorre exclusivamente em containers/processos locais controlados pela equipe (`127.0.0.1`).
2. **Dados estritamente sintéticos (LGPD e privacidade):** o banco `pgbench_lab05` contém apenas tabelas sintéticas geradas pelo `pgbench -i` (`pgbench_accounts`, `pgbench_branches`, `pgbench_tellers`, `pgbench_history`). Não há coleta, armazenamento ou processamento de dados pessoais.
3. **Credenciais fictícias:** utiliza-se exclusivamente a senha fictícia de laboratório `lab05_pg_bench` em ambiente local isolado (`127.0.0.1`), sem reutilização de senhas reais ou dados sensíveis dos integrantes.
4. **Conformidade com o escopo do LAB05:** não há mineração de repositório GitHub do PostgreSQL (commits, PRs ou issues); o objeto estudado é o SGBD em execução real.
5. **Integridade científica e transparência:**
   - Hipóteses formuladas de forma neutra e bilateral antes da coleta.
   - Preservação integral de execuções com falha, logs brutos e outliers.
   - Registro explícito de qualquer limitação ambiental, desvio de execução ou diferença arquitetural nativa entre versões (ex.: `data_checksums` e `io_method` no PG18).

---

## 9. Roteiro Operacional de Execução (Ambiente Docker + Coleta Piloto)

### Passo 1 — Preparar a estação de trabalho antes da coleta
- Conectar o notebook/desktop à fonte de energia (evitar modo economia de bateria).
- Fechar navegadores pesados, IDEs secundárias, jogos, atualizações automáticas e pausar sincronização de nuvem (ex.: OneDrive) durante a janela de medição.
- Confirmar que Docker Desktop (com backend WSL2) e Python (`pip install -r lab05/requirements.txt`) estão ativos.

### Passo 2 — Subir os containers isolados e validar saúde
```powershell
docker compose -f lab05/docker/docker-compose.yml up -d
docker ps --filter "name=postgres_1"
```
Verificar que `postgres_17` (`healthy`, porta `5432`) e `postgres_18` (`healthy`, porta `5433`) estão ativos.

### Passo 3 — Executar a coleta piloto e validar consistência automaticamente
```powershell
python lab05/src/coleta_piloto.py --backend docker
```
*(Caso a estação não possua Docker Desktop, utilizar `--backend native --runtime-dir <caminho>`.)*

### Passo 4 — Verificar testes automatizados e artefatos gerados
```powershell
pytest lab05/tests/test_coleta_piloto.py lab05/tests/test_validacao_dados.py -v
```
Confirmar em `lab05/data/pilot/processed/relatorio_validacao.json`:
- `"aprovado": true` e `"erros": []`;
- `4` repetições válidas para `PG17` e `4` para `PG18` (`12` linhas brutas contando os `4` warm-ups);
- Índice médio de bloco igual a `2.5` para ambas as versões;
- `0` nulos, `0` duplicidades, `0` transações falhas e `amostras_recursos >= 5` por rodada medida.

### Passo 5 — Encerrar os containers após o término
```powershell
docker compose -f lab05/docker/docker-compose.yml down
```

---

## 10. Resultados da Coleta Piloto e Validação de Consistência

A coleta piloto foi executada com sucesso em **26/11/2026 (`02:06:05 UTC` a `02:09:26 UTC`)** utilizando `coleta_piloto.py --backend native` (binários portáteis oficiais `17.12` e `18.7`, já que o Docker Desktop não estava instalado na estação), gravando os artefatos isoladamente em `lab05/data/pilot/`.

### 10.1 Verificação de consistência ([relatorio_validacao.json](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/data/pilot/processed/relatorio_validacao.json))

| Verificação | Resultado | Evidência observada no piloto |
| :--- | :---: | :--- |
| **Status geral (`aprovado`)** | ✅ Aprovado | `"aprovado": true`, `0` erros, `0` avisos. |
| **Execuções registradas** | ✅ Aprovado | `12` execuções brutas (`8` medidas válidas: `4` PG17 + `4` PG18; `4` warm-ups separados). |
| **Balanceamento ABBA** | ✅ Aprovado | Índice médio de bloco exatamente igual: **`2,5`** (`PG17`) vs **`2,5`** (`PG18`). |
| **Série temporal de recursos** | ✅ Aprovado | `95` amostras brutas (`75` validadas nas 8 rodadas medidas; `9–10` amostras por execução). |
| **Valores ausentes e duplicidades** | ✅ Aprovado | `0` nulos, `0` duplicidades, `0` transações falhas (`status == OK` em 100%). |
| **Consistência cruzada TPS** | ✅ Aprovado | Diferença relativa máxima entre `tps` e `tx / duracao_real_s` de **`4,10%`**. |
| **Auditoria `pg_settings`** | ✅ Aprovado | `380` parâmetros coletados no PG17 e `400` no PG18, confirmando `io_method = worker`, `io_workers = 3` e `data_checksums = on` ativos no PG18. |

### 10.2 Achados operacionais observados no piloto ([benchmark_validado.csv](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/data/pilot/processed/benchmark_validado.csv))

- **Hardware da estação piloto:** `Windows-11-10.0.26300-SP0` (`AMD64`), `6` núcleos físicos / `6` lógicos, `15,94 GiB` RAM, Python `3.14.7`, `psutil 7.2.2`.
- **Comportamento observado:**
  - Nos Blocos 1 (`PG17`: `3856,73` e `3728,59` TPS; latência `2,073`–`2,145 ms`) e Blocos 2–3 (`PG18`: `3497,48` a `3875,97` TPS; latência `2,063`–`2,286 ms`), ambas as versões operaram com alto aproveitamento de CPU (`251,7%`–`290,7%`) e memória estabilizada (`532,8`–`590,7 MiB`).
  - No Bloco 4 (`PG17`, rodadas `PILOT_011` e `PILOT_012`), observou-se queda severa de vazão (`210,96` e `58,17` TPS; latência `37,80` e `135,37 ms`) acompanhada de baixo uso de CPU (`28,69%` e `10,94%`) — padrão típico de contenção momentânea de disco/I/O (`fsync` do WAL) no hospedeiro Windows.
- **Ajustes recomendados a partir do piloto para a coleta definitiva (`#66`):**
  1. Confirmar necessidade de amostra maior (`n = 30` repetições em 12 blocos ABBA) e fechamento rigoroso de processos em segundo plano (sincronização OneDrive, antivírus, indexadores) para reduzir oscilações de I/O de disco no hospedeiro.
  2. Preservar integralmente eventuais execuções atípicas em `raw/` e adotar medidas robustas (mediana/IQR) e sinalização não destrutiva de outliers na validação.

> **Nota sobre Docker Desktop:** a infraestrutura em [docker-compose.yml](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/docker/docker-compose.yml) permanece pronta e documentada para estações com Docker Desktop instalado (`--backend docker`); nesta estação específica, a execução utilizou o modo equivalente `--backend native` conforme previsto no plano.

---

## 11. Verificação dos Critérios de Aceitação (Issue `#64`)

| Critério / Atividade da Issue `#64` | Status | Evidência / Artefato |
| :--- | :---: | :--- |
| Requisitos técnicos identificados | ✅ | Seção 2 deste documento + [requirements.txt](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/requirements.txt). |
| Ambiente ou roteiro de coleta preparado | ✅ | [docker-compose.yml](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/docker/docker-compose.yml), [postgresql-baseline.conf](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/docker/postgresql-baseline.conf) e Seções 4 e 9 deste documento. |
| Ferramentas identificadas e justificadas | ✅ | Seção 3 (`Docker`, `pgbench`, `Python`, `docker stats`/`psutil`, `pandas`, `pytest`, `Git/GitHub`). |
| Métricas de coleta definidas | ✅ | Seção 5 (dicionário completo, escalas e padronização de `tps` = *without initial connection time*). |
| Scripts ou procedimentos iniciais implementados | ✅ | [coleta_piloto.py](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/src/coleta_piloto.py) e [test_coleta_piloto.py](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/tests/test_coleta_piloto.py), reutilizando [executar_coleta.py](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/src/executar_coleta.py) e [validar_dados.py](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/src/validar_dados.py). |
| Armazenamento e versionamento estabelecidos | ✅ | Seção 7 (isolamento `pilot` × `raw` × `processed`, imutabilidade, flags IQR e Git). |
| Procedimentos éticos documentados | ✅ | Seção 8 (ambiente 100% local, dados sintéticos, credenciais fictícias, integridade científica). |
| Coleta piloto executada e dados iniciais validados | ✅ | `12` execuções (`8` medidas + `4` warm-ups) em `lab05/data/pilot/` validadas com `"aprovado": true` em [relatorio_validacao.json](file:///c:/Users/kayqu/OneDrive/Documentos/GitHub/pmg-es-2025-2-ti4-3126100-conttarecontabilidade/LabExperimentacao/lab05/data/pilot/processed/relatorio_validacao.json) (Seção 10). |
