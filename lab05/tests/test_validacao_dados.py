"""Testes automatizados para os scripts de coleta e validação do LAB05 (Issue #66)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from lab05.src.executar_coleta import (
    _parse_docker_mem_to_mib,
    build_abba_schedule,
    compute_settings_diff,
    parse_pgbench_output,
)
from lab05.src.validar_dados import (
    PROCESSED_DIR,
    RAW_DIR,
    REQUIRED_BENCHMARK_COLS,
    REQUIRED_TIMESERIES_COLS,
    validate_datasets,
)


def test_parse_pgbench_output_padrao() -> None:
    sample_out = """
pgbench (18.7)
starting vacuum...end.
progress: 5.0 s, 1450.2 tps, lat 5.512 ms stddev 3.120, 0 failed
transaction type: <builtin: TPC-B (sort of)>
scaling factor: 10
query mode: simple
number of clients: 8
number of threads: 4
duration: 10 s
number of transactions actually processed: 14820
number of failed transactions: 0 (0.000%)
latency average = 5.398 ms
latency stddev = 2.987 ms
initial connection time = 18.421 ms
tps = 1484.721540 (without initial connection time)
"""
    parsed = parse_pgbench_output(sample_out)
    assert parsed["transacoes_processadas"] == 14820
    assert parsed["transacoes_falhas"] == 0
    assert parsed["latencia_media_ms"] == pytest.approx(5.398)
    assert parsed["latencia_dp_ms"] == pytest.approx(2.987)
    assert parsed["tempo_conexao_inicial_ms"] == pytest.approx(18.421)
    assert parsed["tps"] == pytest.approx(1484.721540)


def test_build_abba_schedule_balanceamento_temporal() -> None:
    schedule = build_abba_schedule(repetitions_per_version=30, block_size=5)
    assert len(schedule) == 12
    idx_17 = [b for b, v, _ in schedule if v == "PG17"]
    idx_18 = [b for b, v, _ in schedule if v == "PG18"]
    assert len(idx_17) == 6
    assert len(idx_18) == 6
    # Posição média temporal perfeitamente equilibrada
    assert sum(idx_17) / len(idx_17) == pytest.approx(sum(idx_18) / len(idx_18))


def test_parse_docker_mem_to_mib() -> None:
    assert _parse_docker_mem_to_mib("256MiB / 2GiB") == pytest.approx(256.0)
    assert _parse_docker_mem_to_mib("1.5GiB / 4GiB") == pytest.approx(1536.0)
    assert _parse_docker_mem_to_mib("512KiB / 2GiB") == pytest.approx(0.5)


def test_compute_settings_diff_detecta_novidades_pg18() -> None:
    s17 = {"shared_buffers": "256MB", "work_mem": "4MB", "old_param": "on"}
    s18 = {"shared_buffers": "256MB", "work_mem": "8MB", "io_method": "worker"}
    diff = compute_settings_diff(s17, s18)
    assert diff["apenas_no_pg17"] == {"old_param": "on"}
    assert diff["apenas_no_pg18"] == {"io_method": "worker"}
    assert diff["valores_diferentes_entre_versoes"] == {
        "work_mem": {"PG17": "4MB", "PG18": "8MB"}
    }


def test_datasets_reais_coletados_e_validados() -> None:
    """Valida integralmente os conjuntos de dados reais versionados no repositório."""
    assert (RAW_DIR / "benchmark_raw.csv").exists()
    assert (RAW_DIR / "resource_timeseries_raw.csv").exists()
    assert (RAW_DIR / "metadata_ambiente.json").exists()
    assert (PROCESSED_DIR / "benchmark_validado.csv").exists()
    assert (PROCESSED_DIR / "resource_timeseries_validado.csv").exists()
    assert (PROCESSED_DIR / "relatorio_validacao.json").exists()

    report = validate_datasets(RAW_DIR, PROCESSED_DIR)
    assert report["aprovado"] is True, f"Erros de validação: {report['erros']}"
    assert report["erros"] == []

    df_valid = pd.read_csv(PROCESSED_DIR / "benchmark_validado.csv")
    df_ts = pd.read_csv(PROCESSED_DIR / "resource_timeseries_validado.csv")

    for col in REQUIRED_BENCHMARK_COLS:
        assert col in df_valid.columns
    for col in REQUIRED_TIMESERIES_COLS:
        assert col in df_ts.columns

    # Balanceamento: 30 repetições válidas por versão
    counts = df_valid["versao"].value_counts().to_dict()
    assert counts == {"PG17": 30, "PG18": 30}
    assert (df_valid["is_warmup"] == False).all()  # noqa: E712
    assert (df_valid["status"] == "OK").all()
    assert df_valid[REQUIRED_BENCHMARK_COLS].isna().sum().sum() == 0
    assert df_ts[REQUIRED_TIMESERIES_COLS].isna().sum().sum() == 0

    # Preservação de metadados de auditoria
    meta = json.loads((RAW_DIR / "metadata_ambiente.json").read_text(encoding="utf-8"))
    assert "auditoria_pg_settings" in meta
    assert "parametros_experimento" in meta


def test_validator_rejeita_dados_corrompidos(tmp_path: Path) -> None:
    """Garante que o validador detecta nulos, duplicidade e violações de domínio."""
    raw = tmp_path / "raw"
    proc = tmp_path / "processed"
    raw.mkdir()

    bad_bench = pd.DataFrame(
        [
            {
                "run_id": "RUN_001",
                "timestamp_utc": "2026-11-25T21:00:00+00:00",
                "block_id": 1,
                "order_global": 1,
                "versao": "PG17",
                "versao_exata": "17.12",
                "repeticao": 1,
                "is_warmup": False,
                "backend": "native_windows_binaries",
                "random_seed": 4201,
                "scale_factor": 10,
                "clientes": 8,
                "threads": 4,
                "duracao_planejada_s": 10,
                "duracao_real_s": 10.1,
                "transacoes_processadas": 1000,
                "transacoes_falhas": 0,
                "latencia_media_ms": -1.0,  # inválido!
                "latencia_dp_ms": 0.5,
                "tempo_conexao_inicial_ms": 10.0,
                "tps": 100.0,
                "cpu_media_pct": 50.0,
                "cpu_pico_pct": 60.0,
                "cpu_normalizada_media_pct": 6.25,
                "cpu_normalizada_pico_pct": 7.5,
                "memoria_media_mib": 120.0,
                "memoria_pico_mib": 130.0,
                "amostras_recursos": 10,
                "status": "OK",
                "observacoes": "",
            },
            {
                "run_id": "RUN_001",  # duplicado!
                "timestamp_utc": "2026-11-25T21:00:15+00:00",
                "block_id": 1,
                "order_global": 2,
                "versao": "PG17",
                "versao_exata": "17.12",
                "repeticao": 1,
                "is_warmup": False,
                "backend": "native_windows_binaries",
                "random_seed": 4201,
                "scale_factor": 10,
                "clientes": 8,
                "threads": 4,
                "duracao_planejada_s": 10,
                "duracao_real_s": 10.1,
                "transacoes_processadas": 1000,
                "transacoes_falhas": 0,
                "latencia_media_ms": None,  # nulo!
                "latencia_dp_ms": 0.5,
                "tempo_conexao_inicial_ms": 10.0,
                "tps": 100.0,
                "cpu_media_pct": 50.0,
                "cpu_pico_pct": 60.0,
                "cpu_normalizada_media_pct": 6.25,
                "cpu_normalizada_pico_pct": 7.5,
                "memoria_media_mib": 120.0,
                "memoria_pico_mib": 130.0,
                "amostras_recursos": 10,
                "status": "OK",
                "observacoes": "",
            },
        ]
    )
    bad_ts = pd.DataFrame(
        [
            {
                "run_id": "RUN_001",
                "timestamp_utc": "2026-11-25T21:00:01+00:00",
                "segundo_relativo": 1.0,
                "versao": "PG17",
                "repeticao": 1,
                "is_warmup": False,
                "cpu_pct": 50.0,
                "cpu_normalizada_pct": 6.25,
                "memoria_mib": 120.0,
                "num_processos_pg": 12,
            }
        ]
    )
    bad_bench.to_csv(raw / "benchmark_raw.csv", index=False)
    bad_ts.to_csv(raw / "resource_timeseries_raw.csv", index=False)
    (raw / "metadata_ambiente.json").write_text("{}", encoding="utf-8")

    report = validate_datasets(raw, proc)
    assert report["aprovado"] is False
    assert len(report["erros"]) >= 3

