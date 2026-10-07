"""Módulo de configuração centralizada do Laboratório 03.

Carrega parâmetros operacionais a partir do config.yaml, gerencia credenciais
de acesso de forma segura e normaliza as definições da janela temporal de 12 meses.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Optional
import yaml


def find_github_token() -> Optional[str]:
    """Localiza o GITHUB_TOKEN no ambiente ou em arquivos .env seguros.

    Ordem de busca:
    1. Variável de ambiente GITHUB_TOKEN
    2. lab03/.env
    3. .env (raiz do repositório)
    4. lab01/.env (legado do laboratório anterior)
    """
    token = os.getenv("GITHUB_TOKEN")
    if token and token.strip():
        return token.strip()

    project_root = Path(__file__).resolve().parent.parent.parent
    candidate_paths = [
        project_root / "lab03" / ".env",
        project_root / ".env",
        project_root / "lab01" / ".env",
    ]

    for env_path in candidate_paths:
        if env_path.is_file():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            if k.strip() == "GITHUB_TOKEN" and v.strip():
                                return v.strip()
            except Exception:
                continue

    return None


def parse_iso_datetime(dt_str: str) -> datetime:
    """Converte string ISO em datetime ciente de fuso horário (UTC)."""
    clean_str = dt_str.strip()
    if clean_str.endswith("Z"):
        clean_str = clean_str[:-1] + "+00:00"
    dt = datetime.fromisoformat(clean_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@dataclass
class WindowConfig:
    start_date_str: str
    end_date_str: str
    description: str = ""
    start_date: datetime = field(init=False)
    end_date: datetime = field(init=False)

    def __post_init__(self) -> None:
        self.start_date = parse_iso_datetime(self.start_date_str)
        self.end_date = parse_iso_datetime(self.end_date_str)
        if self.end_date <= self.start_date:
            raise ValueError("end_date deve ser posterior a start_date")

    def is_in_window(self, dt: datetime | str) -> bool:
        """Verifica se um dado timestamp está estritamente dentro da janela."""
        if isinstance(dt, str):
            dt = parse_iso_datetime(dt)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return self.start_date <= dt <= self.end_date


@dataclass
class FunnelCriteria:
    min_stars: int = 1000
    min_releases: int = 5
    min_workflow_runs: int = 50
    target_repositories: int = 100
    target_repositories_s02: int = 300
    search_query_base: str = "stars:>1000 is:public fork:false archived:false"
    star_slices: List[str] = field(default_factory=lambda: [
        "stars:>50000",
        "stars:20000..50000",
        "stars:10000..20000",
        "stars:5000..10000",
        "stars:2000..5000",
        "stars:1000..2000",
    ])


@dataclass
class ApiConfig:
    base_url: str = "https://api.github.com"
    timeout_seconds: int = 30
    max_retries: int = 5
    backoff_factor: float = 2.0
    rate_limit_safety_margin: int = 20


@dataclass
class CacheConfig:
    enabled: bool = True
    cache_dir: Path = field(default_factory=lambda: Path("lab03/data/cache"))


@dataclass
class OutputConfig:
    data_dir: Path = field(default_factory=lambda: Path("lab03/data"))
    selected_repositories_csv: str = "repositorios_selecionados.csv"
    funnel_summary_csv: str = "funil_selecao.csv"
    funnel_detailed_csv: str = "funil_detalhado.csv"

    @property
    def selected_repositories_path(self) -> Path:
        return self.data_dir / self.selected_repositories_csv

    @property
    def funnel_summary_path(self) -> Path:
        return self.data_dir / self.funnel_summary_csv

    @property
    def funnel_detailed_path(self) -> Path:
        return self.data_dir / self.funnel_detailed_csv


@dataclass
class Config:
    window: WindowConfig
    funnel_criteria: FunnelCriteria
    api: ApiConfig
    cache: CacheConfig
    output: OutputConfig
    github_token: Optional[str] = None

    @classmethod
    def load(cls, config_path: Optional[str | Path] = None) -> "Config":
        """Carrega e valida as configurações a partir do arquivo YAML."""
        if config_path is None:
            # Tenta encontrar lab03/config.yaml a partir da raiz ou da pasta atual
            project_root = Path(__file__).resolve().parent.parent.parent
            candidate_paths = [
                project_root / "lab03" / "config.yaml",
                Path("lab03/config.yaml"),
                Path("config.yaml"),
            ]
            for p in candidate_paths:
                if p.is_file():
                    config_path = p
                    break
            if config_path is None:
                raise FileNotFoundError("Arquivo config.yaml nao encontrado para o Lab 03.")

        path = Path(config_path)
        if not path.is_file():
            raise FileNotFoundError(f"Arquivo de configuracao nao encontrado: {path}")

        with open(path, "r", encoding="utf-8") as f:
            raw: dict[str, Any] = yaml.safe_load(f) or {}

        window_data = raw.get("window", {})
        window = WindowConfig(
            start_date_str=window_data.get("start_date", "2024-03-01T00:00:00Z"),
            end_date_str=window_data.get("end_date", "2025-02-28T23:59:59Z"),
            description=window_data.get("description", ""),
        )

        funnel_data = raw.get("funnel_criteria", {})
        funnel_criteria = FunnelCriteria(
            min_stars=funnel_data.get("min_stars", 1000),
            min_releases=funnel_data.get("min_releases", 5),
            min_workflow_runs=funnel_data.get("min_workflow_runs", 50),
            target_repositories=funnel_data.get("target_repositories", 100),
            target_repositories_s02=funnel_data.get("target_repositories_s02", 300),
            search_query_base=funnel_data.get(
                "search_query_base", "stars:>1000 is:public fork:false archived:false"
            ),
            star_slices=funnel_data.get("star_slices", FunnelCriteria().star_slices),
        )

        api_data = raw.get("api", {})
        api = ApiConfig(
            base_url=api_data.get("base_url", "https://api.github.com"),
            timeout_seconds=api_data.get("timeout_seconds", 30),
            max_retries=api_data.get("max_retries", 5),
            backoff_factor=api_data.get("backoff_factor", 2.0),
            rate_limit_safety_margin=api_data.get("rate_limit_safety_margin", 20),
        )

        cache_data = raw.get("cache", {})
        cache_dir_raw = cache_data.get("cache_dir", "lab03/data/cache")
        cache = CacheConfig(
            enabled=cache_data.get("enabled", True),
            cache_dir=Path(cache_dir_raw),
        )

        output_data = raw.get("output", {})
        data_dir_raw = output_data.get("data_dir", "lab03/data")
        output = OutputConfig(
            data_dir=Path(data_dir_raw),
            selected_repositories_csv=output_data.get(
                "selected_repositories_csv", "repositorios_selecionados.csv"
            ),
            funnel_summary_csv=output_data.get(
                "funnel_summary_csv", "funil_selecao.csv"
            ),
            funnel_detailed_csv=output_data.get(
                "funnel_detailed_csv", "funil_detalhado.csv"
            ),
        )

        # Garante a existência dos diretórios
        cache.cache_dir.mkdir(parents=True, exist_ok=True)
        output.data_dir.mkdir(parents=True, exist_ok=True)

        token = find_github_token()

        return cls(
            window=window,
            funnel_criteria=funnel_criteria,
            api=api,
            cache=cache,
            output=output,
            github_token=token,
        )
