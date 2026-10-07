"""Testes unitários para extração de metadados e manipulação de datas."""

from datetime import datetime, timezone
import pytest

from lab03.src.config import WindowConfig, parse_iso_datetime
from lab03.src.selecao_repositorios import calculate_age_years


def test_parse_iso_datetime():
    dt1 = parse_iso_datetime("2024-03-01T00:00:00Z")
    assert dt1.tzinfo == timezone.utc
    assert dt1.year == 2024
    assert dt1.month == 3
    assert dt1.day == 1

    dt2 = parse_iso_datetime("2024-06-15T14:30:00+00:00")
    assert dt2.hour == 14
    assert dt2.minute == 30


def test_window_config_is_in_window():
    win = WindowConfig(
        start_date_str="2024-01-01T00:00:00Z",
        end_date_str="2024-12-31T23:59:59Z",
    )

    # Exatamente no início e fim
    assert win.is_in_window("2024-01-01T00:00:00Z")
    assert win.is_in_window("2024-12-31T23:59:59Z")

    # No meio
    assert win.is_in_window("2024-07-04T12:00:00Z")

    # Fora
    assert not win.is_in_window("2023-12-31T23:59:59Z")
    assert not win.is_in_window("2025-01-01T00:00:00Z")


def test_calculate_age_years():
    ref_dt = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    # Criado exatamente 1 ano antes
    age_1 = calculate_age_years("2024-01-01T00:00:00Z", reference_date=ref_dt)
    assert 0.99 <= age_1 <= 1.01

    # Criado há 5 anos
    age_5 = calculate_age_years("2020-01-01T00:00:00Z", reference_date=ref_dt)
    assert 4.95 <= age_5 <= 5.05

    # Data futura (não deve ser negativo)
    age_future = calculate_age_years("2026-01-01T00:00:00Z", reference_date=ref_dt)
    assert age_future == 0.0
