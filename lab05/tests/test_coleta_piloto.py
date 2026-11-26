"""Testes unitários para o módulo de preparação e coleta piloto (Issue #64)."""

from __future__ import annotations

import pytest

from lab05.src.coleta_piloto import (
    PILOT_PROCESSED_DIR,
    PILOT_RAW_DIR,
    parse_docker_inspect_line,
    parse_pg_settings_tsv,
)
from lab05.src.executar_coleta import build_abba_schedule
from lab05.src.validar_dados import PROCESSED_DIR, RAW_DIR


def test_pilot_dirs_isolated_from_definitive_data() -> None:
    """Garante que o piloto não sobrescreve os dados definitivos da Sprint 2."""
    assert PILOT_RAW_DIR != RAW_DIR
    assert PILOT_PROCESSED_DIR != PROCESSED_DIR
    assert "pilot" in PILOT_RAW_DIR.parts
    assert "pilot" in PILOT_PROCESSED_DIR.parts


def test_pilot_abba_schedule_balanceamento() -> None:
    """Verifica balanceamento temporal perfeito com parâmetros padrão do piloto (4 reps, bloco 2)."""
    schedule = build_abba_schedule(repetitions_per_version=4, block_size=2)
    assert [v for _, v, _ in schedule] == ["PG17", "PG18", "PG18", "PG17"]
    idx_17 = [b for b, v, _ in schedule if v == "PG17"]
    idx_18 = [b for b, v, _ in schedule if v == "PG18"]
    assert sum(idx_17) / len(idx_17) == pytest.approx(sum(idx_18) / len(idx_18))


def test_parse_pg_settings_tsv() -> None:
    """Valida leitura do TSV retornado por psql sobre pg_settings."""
    tsv = "data_checksums\ton\nio_method\tworker\nshared_buffers\t256MB\n"
    parsed = parse_pg_settings_tsv(tsv)
    assert parsed == {
        "data_checksums": "on",
        "io_method": "worker",
        "shared_buffers": "256MB",
    }


def test_parse_docker_inspect_line() -> None:
    """Valida interpretação dos limites e metadados de container Docker."""
    line = "true|postgres:18.7-bookworm|sha256:abc123|4000000000|2147483648"
    parsed = parse_docker_inspect_line(line)
    assert parsed["running"] is True
    assert parsed["image_tag"] == "postgres:18.7-bookworm"
    assert parsed["image_id"] == "sha256:abc123"
    assert parsed["cpus_limit"] == pytest.approx(4.0)
    assert parsed["memory_limit_mib"] == pytest.approx(2048.0)
