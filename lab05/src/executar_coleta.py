"""Orquestrador da coleta experimental do LAB05 (PostgreSQL 17 x PostgreSQL 18).

Executa o protocolo completo de benchmark com ``pgbench`` e monitoramento de
CPU e memória em paralelo, preservando dados brutos, série temporal de recursos,
logs de auditoria e metadados de ambiente/configuração (``pg_settings``).

Suporta dois backends de execução:
- ``native``: executa instâncias isoladas dos binários oficiais portáteis do
  PostgreSQL 17.12 e PostgreSQL 18.7 (sem interferir em instalações do sistema).
- ``docker``: executa via containers Docker pré-configurados (compatível com a
  infraestrutura prevista na Issue #64).
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import platform
import re
import shutil
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import psutil

LAB05_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = LAB05_DIR / "data" / "raw"
LOGS_DIR = RAW_DIR / "logs_pgbench"

DEFAULT_RUNTIME_DIR = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "lab05_pg_runtime"

# Configurações padronizadas aplicadas identicamente em PG17 e PG18
BASELINE_PG_CONF = [
    "listen_addresses = '127.0.0.1'",
    "max_connections = 100",
    "shared_buffers = 256MB",
    "work_mem = 4MB",
    "maintenance_work_mem = 64MB",
    "effective_cache_size = 1GB",
    "checkpoint_timeout = 15min",
    "max_wal_size = 1GB",
    "synchronous_commit = on",
    "logging_collector = off",
    "log_min_messages = warning",
]

BENCHMARK_CSV_FIELDS = [
    "run_id",
    "timestamp_utc",
    "block_id",
    "order_global",
    "versao",
    "versao_exata",
    "repeticao",
    "is_warmup",
    "backend",
    "random_seed",
    "scale_factor",
    "clientes",
    "threads",
    "duracao_planejada_s",
    "duracao_real_s",
    "transacoes_processadas",
    "transacoes_falhas",
    "latencia_media_ms",
    "latencia_dp_ms",
    "tempo_conexao_inicial_ms",
    "tps",
    "cpu_media_pct",
    "cpu_pico_pct",
    "cpu_normalizada_media_pct",
    "cpu_normalizada_pico_pct",
    "memoria_media_mib",
    "memoria_pico_mib",
    "amostras_recursos",
    "status",
    "observacoes",
]

TIMESERIES_CSV_FIELDS = [
    "run_id",
    "timestamp_utc",
    "segundo_relativo",
    "versao",
    "repeticao",
    "is_warmup",
    "cpu_pct",
    "cpu_normalizada_pct",
    "memoria_mib",
    "num_processos_pg",
]


@dataclass
class VersionTarget:
    """Especificação de uma versão do PostgreSQL participante do experimento."""

    label: str  # "PG17" ou "PG18"
    exact_version: str  # "17.12" ou "18.7"
    port: int
    bin_dir: Path | None = None
    data_dir: Path | None = None
    container_name: str | None = None
    db_name: str = "pgbench_lab05"
    db_user: str = "postgres"


def utc_now_iso() -> str:
    """Retorna o timestamp atual em UTC no formato ISO-8601."""
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def run_cmd(
    cmd: list[str],
    env: dict[str, str] | None = None,
    timeout: int = 300,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Executa um comando externo capturando stdout e stderr."""
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    return subprocess.run(
        cmd,
        env=merged_env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=check,
    )


def parse_pgbench_output(output: str) -> dict[str, Any]:
    """Extrai métricas estruturadas da saída textual padrão do ``pgbench``."""

    def _search_float(pattern: str) -> float | None:
        match = re.search(pattern, output, re.MULTILINE)
        return float(match.group(1)) if match else None

    def _search_int(pattern: str) -> int | None:
        match = re.search(pattern, output, re.MULTILINE)
        return int(match.group(1)) if match else None

    tx_processed = _search_int(
        r"number of transactions actually processed:\s*(\d+)"
    )
    tx_failed = _search_int(r"number of failed transactions:\s*(\d+)")
    if tx_failed is None:
        tx_failed = 0

    latency_avg = _search_float(r"latency average\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*ms")
    latency_std = _search_float(r"latency stddev\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*ms")
    init_conn = _search_float(
        r"initial connection time\s*=\s*([0-9]+(?:\.[0-9]+)?)\s*ms"
    )
    tps = _search_float(r"tps\s*=\s*([0-9]+(?:\.[0-9]+)?)")

    return {
        "transacoes_processadas": tx_processed,
        "transacoes_falhas": tx_failed,
        "latencia_media_ms": latency_avg,
        "latencia_dp_ms": latency_std,
        "tempo_conexao_inicial_ms": init_conn,
        "tps": tps,
    }


def _read_postmaster_pid(data_dir: Path) -> int | None:
    """Lê o PID principal do processo ``postgres`` em ``postmaster.pid``."""
    pid_file = data_dir / "postmaster.pid"
    if not pid_file.exists():
        return None
    first_line = pid_file.read_text(encoding="utf-8", errors="replace").splitlines()[0]
    return int(first_line.strip())


def _collect_pg_process_tree(root_pid: int) -> list[psutil.Process]:
    """Retorna o processo raiz do PostgreSQL e todos os seus filhos ativos."""
    try:
        root = psutil.Process(root_pid)
        procs = [root] + root.children(recursive=True)
        return [p for p in procs if p.is_running()]
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return []


class NativeResourceMonitor:
    """Monitora CPU (%) e memória RSS (MiB) da árvore de processos do PostgreSQL."""

    def __init__(
        self,
        root_pid: int,
        run_id: str,
        versao: str,
        repeticao: int,
        is_warmup: bool,
        interval_s: float = 1.0,
    ) -> None:
        self.root_pid = root_pid
        self.run_id = run_id
        self.versao = versao
        self.repeticao = repeticao
        self.is_warmup = is_warmup
        self.interval_s = interval_s
        self.logical_cpus = psutil.cpu_count(logical=True) or 1
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self.samples: list[dict[str, Any]] = []
        self._prev_cpu_times: dict[int, float] = {}

    def _snapshot_cpu_times(self) -> dict[int, float]:
        times: dict[int, float] = {}
        for proc in _collect_pg_process_tree(self.root_pid):
            try:
                ct = proc.cpu_times()
                times[proc.pid] = float(ct.user + ct.system)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return times

    def _run_loop(self) -> None:
        self._prev_cpu_times = self._snapshot_cpu_times()
        start_mono = time.monotonic()
        prev_mono = start_mono
        sample_idx = 0

        while not self._stop_event.wait(self.interval_s):
            now_mono = time.monotonic()
            dt_s = max(now_mono - prev_mono, 1e-6)
            prev_mono = now_mono
            sample_idx += 1

            procs = _collect_pg_process_tree(self.root_pid)
            curr_cpu_times: dict[int, float] = {}
            delta_cpu_s = 0.0
            total_rss_bytes = 0

            for proc in procs:
                try:
                    ct = proc.cpu_times()
                    total_t = float(ct.user + ct.system)
                    curr_cpu_times[proc.pid] = total_t
                    if proc.pid in self._prev_cpu_times:
                        delta_cpu_s += max(0.0, total_t - self._prev_cpu_times[proc.pid])
                    else:
                        # Processo recém-criado (ex.: backend do pgbench)
                        delta_cpu_s += total_t
                    total_rss_bytes += int(proc.memory_info().rss)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            self._prev_cpu_times = curr_cpu_times
            cpu_pct = (delta_cpu_s / dt_s) * 100.0
            cpu_norm_pct = min(cpu_pct / self.logical_cpus, 100.0)
            mem_mib = total_rss_bytes / (1024.0 * 1024.0)

            self.samples.append(
                {
                    "run_id": self.run_id,
                    "timestamp_utc": utc_now_iso(),
                    "segundo_relativo": round(now_mono - start_mono, 2),
                    "versao": self.versao,
                    "repeticao": self.repeticao,
                    "is_warmup": self.is_warmup,
                    "cpu_pct": round(cpu_pct, 4),
                    "cpu_normalizada_pct": round(cpu_norm_pct, 4),
                    "memoria_mib": round(mem_mib, 4),
                    "num_processos_pg": len(procs),
                }
            )

    def start(self) -> None:
        """Inicia a amostragem em thread paralela."""
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> list[dict[str, Any]]:
        """Encerra a amostragem e retorna as amostras coletadas."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=5.0)
        return self.samples


def _parse_docker_mem_to_mib(mem_usage_str: str) -> float:
    """Converte strings do ``docker stats`` (ex.: ``128.4MiB / 2GiB``) para MiB."""
    left = mem_usage_str.split("/")[0].strip()
    match = re.match(r"([0-9]+(?:\.[0-9]+)?)\s*([A-Za-z]+)", left)
    if not match:
        return 0.0
    val = float(match.group(1))
    unit = match.group(2).lower()
    factors = {
        "b": 1.0 / (1024.0 * 1024.0),
        "kib": 1.0 / 1024.0,
        "kb": 1000.0 / (1024.0 * 1024.0),
        "mib": 1.0,
        "mb": (1000.0 * 1000.0) / (1024.0 * 1024.0),
        "gib": 1024.0,
        "gb": (1000.0**3) / (1024.0 * 1024.0),
    }
    return val * factors.get(unit, 1.0)


class DockerResourceMonitor:
    """Monitora CPU (%) e memória (MiB) via ``docker stats --no-stream``."""

    def __init__(
        self,
        container_name: str,
        run_id: str,
        versao: str,
        repeticao: int,
        is_warmup: bool,
        interval_s: float = 1.0,
    ) -> None:
        self.container_name = container_name
        self.run_id = run_id
        self.versao = versao
        self.repeticao = repeticao
        self.is_warmup = is_warmup
        self.interval_s = interval_s
        self.logical_cpus = psutil.cpu_count(logical=True) or 1
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self.samples: list[dict[str, Any]] = []

    def _run_loop(self) -> None:
        start_mono = time.monotonic()
        while not self._stop_event.is_set():
            tick_start = time.monotonic()
            proc = run_cmd(
                [
                    "docker",
                    "stats",
                    "--no-stream",
                    "--format",
                    "{{.CPUPerc}}|{{.MemUsage}}|{{.PIDs}}",
                    self.container_name,
                ],
                check=False,
                timeout=15,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                parts = proc.stdout.strip().split("|")
                if len(parts) == 3:
                    cpu_pct = float(parts[0].replace("%", "").strip())
                    mem_mib = _parse_docker_mem_to_mib(parts[1])
                    pids = int(parts[2].strip()) if parts[2].strip().isdigit() else 0
                    self.samples.append(
                        {
                            "run_id": self.run_id,
                            "timestamp_utc": utc_now_iso(),
                            "segundo_relativo": round(time.monotonic() - start_mono, 2),
                            "versao": self.versao,
                            "repeticao": self.repeticao,
                            "is_warmup": self.is_warmup,
                            "cpu_pct": round(cpu_pct, 4),
                            "cpu_normalizada_pct": round(
                                min(cpu_pct / self.logical_cpus, 100.0), 4
                            ),
                            "memoria_mib": round(mem_mib, 4),
                            "num_processos_pg": pids,
                        }
                    )
            elapsed = time.monotonic() - tick_start
            wait_s = max(0.05, self.interval_s - elapsed)
            if self._stop_event.wait(wait_s):
                break

    def start(self) -> None:
        """Inicia a amostragem em thread paralela."""
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> list[dict[str, Any]]:
        """Encerra a amostragem e retorna as amostras coletadas."""
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=10.0)
        return self.samples


def _native_exe(target: VersionTarget, name: str) -> str:
    assert target.bin_dir is not None
    suffix = ".exe" if os.name == "nt" else ""
    return str(target.bin_dir / f"{name}{suffix}")


def native_init_and_configure(target: VersionTarget, scale_factor: int) -> dict[str, str]:
    """Inicializa ``PGDATA`` limpo, aplica ``postgresql.conf`` e popula ``pgbench``."""
    assert target.data_dir is not None
    if target.data_dir.exists():
        # Garante parada prévia caso exista instância residual
        native_stop(target)
        time.sleep(1.0)
        shutil.rmtree(target.data_dir, ignore_errors=False)

    target.data_dir.parent.mkdir(parents=True, exist_ok=True)

    run_cmd(
        [
            _native_exe(target, "initdb"),
            "-D",
            str(target.data_dir),
            "-U",
            target.db_user,
            "--auth=trust",
            "--encoding=UTF8",
            "--no-locale",
        ]
    )

    conf_file = target.data_dir / "postgresql.conf"
    with conf_file.open("a", encoding="utf-8") as fh:
        fh.write("\n# --- LAB05 Baseline Padronizado ---\n")
        fh.write(f"port = {target.port}\n")
        for line in BASELINE_PG_CONF:
            fh.write(f"{line}\n")

    native_start(target)
    try:
        run_cmd(
            [
                _native_exe(target, "createdb"),
                "-h",
                "127.0.0.1",
                "-p",
                str(target.port),
                "-U",
                target.db_user,
                target.db_name,
            ]
        )
        run_cmd(
            [
                _native_exe(target, "pgbench"),
                "-h",
                "127.0.0.1",
                "-p",
                str(target.port),
                "-U",
                target.db_user,
                "-i",
                "-s",
                str(scale_factor),
                "-q",
                target.db_name,
            ],
            timeout=600,
        )
        run_cmd(
            [
                _native_exe(target, "psql"),
                "-h",
                "127.0.0.1",
                "-p",
                str(target.port),
                "-U",
                target.db_user,
                "-d",
                target.db_name,
                "-c",
                "VACUUM ANALYZE;",
                "-c",
                "CHECKPOINT;",
            ]
        )
        settings = fetch_pg_settings_native(target)
    finally:
        native_stop(target)

    return settings


def native_start(target: VersionTarget) -> None:
    """Inicia a instância nativa do PostgreSQL e aguarda disponibilidade."""
    assert target.data_dir is not None
    log_path = target.data_dir / "server.log"
    # No Windows, usar DEVNULL evita herança de pipes de stdout/stderr pelo
    # processo filho postgres.exe, que bloquearia subprocess.run indefinidamente.
    subprocess.run(
        [
            _native_exe(target, "pg_ctl"),
            "-D",
            str(target.data_dir),
            "-l",
            str(log_path),
            "-w",
            "-t",
            "60",
            "start",
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=90,
        check=True,
    )


def native_stop(target: VersionTarget) -> None:
    """Encerra a instância nativa do PostgreSQL de forma limpa."""
    assert target.data_dir is not None
    if not (target.data_dir / "postmaster.pid").exists():
        return
    subprocess.run(
        [
            _native_exe(target, "pg_ctl"),
            "-D",
            str(target.data_dir),
            "-m",
            "fast",
            "-w",
            "-t",
            "60",
            "stop",
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=90,
        check=False,
    )


def fetch_pg_settings_native(target: VersionTarget) -> dict[str, str]:
    """Coleta todos os parâmetros efetivos (``pg_settings``) para auditoria."""
    res = run_cmd(
        [
            _native_exe(target, "psql"),
            "-h",
            "127.0.0.1",
            "-p",
            str(target.port),
            "-U",
            target.db_user,
            "-d",
            target.db_name,
            "-At",
            "-F",
            "\t",
            "-c",
            "SELECT name, setting || CASE WHEN unit IS NOT NULL AND unit <> '' THEN ' ' || unit ELSE '' END "
            "FROM pg_settings ORDER BY name;",
        ]
    )
    settings: dict[str, str] = {}
    for line in res.stdout.splitlines():
        if "\t" in line:
            k, v = line.split("\t", 1)
            settings[k.strip()] = v.strip()
    return settings


def build_abba_schedule(repetitions_per_version: int, block_size: int) -> list[tuple[int, str, int]]:
    """Constrói sequência contrabalanceada ABBA de blocos entre PG17 e PG18.

    Retorna tuplas ``(block_id, versao_label, tamanho_do_bloco)``.
    """
    if repetitions_per_version % block_size != 0:
        raise ValueError(
            f"repetitions_per_version ({repetitions_per_version}) deve ser múltiplo de block_size ({block_size})."
        )
    num_blocks_per_version = repetitions_per_version // block_size
    pattern = ["PG17", "PG18", "PG18", "PG17"]
    blocks: list[str] = []
    idx = 0
    while blocks.count("PG17") < num_blocks_per_version or blocks.count("PG18") < num_blocks_per_version:
        cand = pattern[idx % len(pattern)]
        idx += 1
        if blocks.count(cand) < num_blocks_per_version:
            blocks.append(cand)
    return [(i + 1, label, block_size) for i, label in enumerate(blocks)]


def summarize_samples(samples: list[dict[str, Any]]) -> dict[str, Any]:
    """Calcula médias e picos de CPU e memória a partir da série temporal."""
    if not samples:
        return {
            "cpu_media_pct": None,
            "cpu_pico_pct": None,
            "cpu_normalizada_media_pct": None,
            "cpu_normalizada_pico_pct": None,
            "memoria_media_mib": None,
            "memoria_pico_mib": None,
            "amostras_recursos": 0,
        }
    cpus = [s["cpu_pct"] for s in samples]
    cpus_norm = [s["cpu_normalizada_pct"] for s in samples]
    mems = [s["memoria_mib"] for s in samples]
    return {
        "cpu_media_pct": round(sum(cpus) / len(cpus), 4),
        "cpu_pico_pct": round(max(cpus), 4),
        "cpu_normalizada_media_pct": round(sum(cpus_norm) / len(cpus_norm), 4),
        "cpu_normalizada_pico_pct": round(max(cpus_norm), 4),
        "memoria_media_mib": round(sum(mems) / len(mems), 4),
        "memoria_pico_mib": round(max(mems), 4),
        "amostras_recursos": len(samples),
    }


def collect_machine_metadata(backend: str, args: argparse.Namespace) -> dict[str, Any]:
    """Coleta especificações de hardware, sistema operacional e parâmetros."""
    vm = psutil.virtual_memory()
    return {
        "coleta_iniciada_utc": utc_now_iso(),
        "backend": backend,
        "sistema_operacional": platform.platform(),
        "processador": platform.processor(),
        "arquitetura": platform.machine(),
        "nucleos_fisicos": psutil.cpu_count(logical=False),
        "nucleos_logicos": psutil.cpu_count(logical=True),
        "memoria_total_gib": round(vm.total / (1024**3), 2),
        "python_version": platform.python_version(),
        "psutil_version": psutil.__version__,
        "parametros_experimento": {
            "repeticoes_por_versao": args.repetitions,
            "tamanho_bloco_abba": args.block_size,
            "scale_factor": args.scale,
            "clientes": args.clients,
            "threads": args.threads,
            "duracao_execucao_s": args.duration,
            "duracao_warmup_s": args.warmup_duration,
            "cooldown_entre_rodadas_s": args.run_cooldown,
            "cooldown_entre_blocos_s": args.block_cooldown,
            "intervalo_amostragem_recursos_s": args.sample_interval,
            "seed_base": args.seed_base,
            "baseline_postgresql_conf": BASELINE_PG_CONF,
        },
    }


def compute_settings_diff(
    settings_17: dict[str, str], settings_18: dict[str, str]
) -> dict[str, Any]:
    """Calcula diferenças de parâmetros efetivos (``pg_settings``) entre PG17 e PG18."""
    all_keys = sorted(set(settings_17) | set(settings_18))
    only_17: dict[str, str] = {}
    only_18: dict[str, str] = {}
    changed: dict[str, dict[str, str]] = {}

    ignored_path_keys = {
        "config_file",
        "data_directory",
        "hba_file",
        "ident_file",
        "port",
        "server_version",
        "server_version_num",
        "lc_collate",
        "lc_ctype",
    }

    for key in all_keys:
        if key in ignored_path_keys:
            continue
        in_17 = key in settings_17
        in_18 = key in settings_18
        if in_17 and not in_18:
            only_17[key] = settings_17[key]
        elif in_18 and not in_17:
            only_18[key] = settings_18[key]
        elif settings_17[key] != settings_18[key]:
            changed[key] = {"PG17": settings_17[key], "PG18": settings_18[key]}

    return {
        "total_parametros_pg17": len(settings_17),
        "total_parametros_pg18": len(settings_18),
        "apenas_no_pg17": only_17,
        "apenas_no_pg18": only_18,
        "valores_diferentes_entre_versoes": changed,
    }


def execute_single_run(
    backend: str,
    target: VersionTarget,
    run_id: str,
    block_id: int,
    order_global: int,
    repeticao: int,
    is_warmup: bool,
    scale_factor: int,
    clients: int,
    threads: int,
    duration_s: int,
    random_seed: int,
    sample_interval_s: float,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Executa uma rodada de ``pgbench`` com monitoramento paralelo de recursos."""
    ts_start = utc_now_iso()
    monitor: NativeResourceMonitor | DockerResourceMonitor

    if backend == "native":
        assert target.data_dir is not None
        root_pid = _read_postmaster_pid(target.data_dir)
        if root_pid is None:
            raise RuntimeError(f"postmaster.pid não encontrado em {target.data_dir}")
        monitor = NativeResourceMonitor(
            root_pid=root_pid,
            run_id=run_id,
            versao=target.label,
            repeticao=repeticao,
            is_warmup=is_warmup,
            interval_s=sample_interval_s,
        )
        cmd = [
            _native_exe(target, "pgbench"),
            "-h",
            "127.0.0.1",
            "-p",
            str(target.port),
            "-U",
            target.db_user,
            "-c",
            str(clients),
            "-j",
            str(threads),
            "-T",
            str(duration_s),
            "-P",
            "5",
            f"--random-seed={random_seed}",
            target.db_name,
        ]
    else:
        assert target.container_name is not None
        monitor = DockerResourceMonitor(
            container_name=target.container_name,
            run_id=run_id,
            versao=target.label,
            repeticao=repeticao,
            is_warmup=is_warmup,
            interval_s=sample_interval_s,
        )
        cmd = [
            "docker",
            "exec",
            target.container_name,
            "pgbench",
            "-U",
            target.db_user,
            "-c",
            str(clients),
            "-j",
            str(threads),
            "-T",
            str(duration_s),
            "-P",
            "5",
            f"--random-seed={random_seed}",
            target.db_name,
        ]

    monitor.start()
    t0 = time.monotonic()
    proc = run_cmd(cmd, check=False, timeout=max(120, duration_s * 6))
    real_duration = round(time.monotonic() - t0, 3)
    samples = monitor.stop()

    log_file = LOGS_DIR / f"{run_id}_{target.label}_rep{repeticao:02d}.log"
    log_file.write_text(
        f"CMD: {' '.join(cmd)}\n"
        f"RETURNCODE: {proc.returncode}\n"
        f"--- STDOUT ---\n{proc.stdout}\n"
        f"--- STDERR ---\n{proc.stderr}\n",
        encoding="utf-8",
    )

    parsed = parse_pgbench_output(proc.stdout + "\n" + proc.stderr)
    res_summary = summarize_samples(samples)

    status = "OK"
    obs = ""
    if proc.returncode != 0:
        status = "ERRO"
        obs = f"pgbench retornou código {proc.returncode}"
    elif parsed["tps"] is None or parsed["latencia_media_ms"] is None:
        status = "ERRO"
        obs = "Falha ao extrair métricas principais do output do pgbench"

    row = {
        "run_id": run_id,
        "timestamp_utc": ts_start,
        "block_id": block_id,
        "order_global": order_global,
        "versao": target.label,
        "versao_exata": target.exact_version,
        "repeticao": repeticao,
        "is_warmup": is_warmup,
        "backend": "native_windows_binaries" if backend == "native" else "docker",
        "random_seed": random_seed,
        "scale_factor": scale_factor,
        "clientes": clients,
        "threads": threads,
        "duracao_planejada_s": duration_s,
        "duracao_real_s": real_duration,
        **parsed,
        **res_summary,
        "status": status,
        "observacoes": obs,
    }
    return row, samples


def parse_args() -> argparse.Namespace:
    """Define os argumentos de linha de comando do coletor."""
    parser = argparse.ArgumentParser(
        description="Executa coleta controlada de desempenho PostgreSQL 17 x PostgreSQL 18 (LAB05S02)."
    )
    parser.add_argument(
        "--backend",
        choices=["native", "docker"],
        default="native",
        help="Backend de execução dos bancos (padrão: native).",
    )
    parser.add_argument(
        "--runtime-dir",
        type=Path,
        default=DEFAULT_RUNTIME_DIR,
        help="Diretório externo ao repositório contendo binários e PGDATA (modo native).",
    )
    parser.add_argument("--repetitions", type=int, default=30, help="Repetições válidas por versão.")
    parser.add_argument("--block-size", type=int, default=5, help="Repetições por bloco ABBA.")
    parser.add_argument("--scale", type=int, default=10, help="Scale factor do pgbench (-s).")
    parser.add_argument("--clients", type=int, default=8, help="Clientes simultâneos (-c).")
    parser.add_argument("--threads", type=int, default=4, help="Threads do pgbench (-j).")
    parser.add_argument("--duration", type=int, default=10, help="Duração de cada repetição em segundos (-T).")
    parser.add_argument("--warmup-duration", type=int, default=5, help="Duração do warm-up por bloco em segundos.")
    parser.add_argument("--run-cooldown", type=float, default=2.0, help="Pausa entre repetições (s).")
    parser.add_argument("--block-cooldown", type=float, default=3.0, help="Pausa ao alternar versão (s).")
    parser.add_argument("--sample-interval", type=float, default=1.0, help="Intervalo de coleta de recursos (s).")
    parser.add_argument("--seed-base", type=int, default=4200, help="Semente base determinística para pgbench.")
    parser.add_argument("--container-pg17", type=str, default="postgres_17", help="Nome do container PG17 (modo docker).")
    parser.add_argument("--container-pg18", type=str, default="postgres_18", help="Nome do container PG18 (modo docker).")
    return parser.parse_args()


def main() -> None:
    """Ponto de entrada da coleta completa do experimento."""
    args = parse_args()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    metadata = collect_machine_metadata(args.backend, args)
    schedule = build_abba_schedule(args.repetitions, args.block_size)
    metadata["agenda_blocos_abba"] = [
        {"block_id": b, "versao": v, "repeticoes_no_bloco": sz} for b, v, sz in schedule
    ]

    if args.backend == "native":
        targets = {
            "PG17": VersionTarget(
                label="PG17",
                exact_version="17.12",
                port=55432,
                bin_dir=args.runtime_dir / "pg_17.12" / "pgsql" / "bin",
                data_dir=args.runtime_dir / "data_pg17",
            ),
            "PG18": VersionTarget(
                label="PG18",
                exact_version="18.7",
                port=55433,
                bin_dir=args.runtime_dir / "pg_18.7" / "pgsql" / "bin",
                data_dir=args.runtime_dir / "data_pg18",
            ),
        }
        print("[LAB05] Inicializando instâncias isoladas PG17 (17.12) e PG18 (18.7)...", flush=True)
        settings_17 = native_init_and_configure(targets["PG17"], args.scale)
        settings_18 = native_init_and_configure(targets["PG18"], args.scale)
        metadata["versoes_executadas"] = {
            "PG17": {
                "versao_exata": settings_17.get("server_version", "17.12"),
                "porta": targets["PG17"].port,
                "origem_binarios": "https://get.enterprisedb.com/postgresql/postgresql-17.12-2-windows-x64-binaries.zip",
            },
            "PG18": {
                "versao_exata": settings_18.get("server_version", "18.7"),
                "porta": targets["PG18"].port,
                "origem_binarios": "https://get.enterprisedb.com/postgresql/postgresql-18.7-2-windows-x64-binaries.zip",
            },
        }
        metadata["auditoria_pg_settings"] = compute_settings_diff(settings_17, settings_18)
        metadata["pg_settings_completos"] = {"PG17": settings_17, "PG18": settings_18}
    else:
        targets = {
            "PG17": VersionTarget(
                label="PG17",
                exact_version="17.x-docker",
                port=5432,
                container_name=args.container_pg17,
            ),
            "PG18": VersionTarget(
                label="PG18",
                exact_version="18.x-docker",
                port=5433,
                container_name=args.container_pg18,
            ),
        }
        metadata["versoes_executadas"] = {
            "PG17": {"container": args.container_pg17},
            "PG18": {"container": args.container_pg18},
        }

    benchmark_csv = RAW_DIR / "benchmark_raw.csv"
    timeseries_csv = RAW_DIR / "resource_timeseries_raw.csv"

    rep_counter = {"PG17": 0, "PG18": 0}
    order_global = 0

    with (
        benchmark_csv.open("w", newline="", encoding="utf-8") as bf,
        timeseries_csv.open("w", newline="", encoding="utf-8") as tf,
    ):
        b_writer = csv.DictWriter(bf, fieldnames=BENCHMARK_CSV_FIELDS)
        t_writer = csv.DictWriter(tf, fieldnames=TIMESERIES_CSV_FIELDS)
        b_writer.writeheader()
        t_writer.writeheader()

        for block_id, ver_label, block_reps in schedule:
            target = targets[ver_label]
            print(
                f"[LAB05] Bloco {block_id:02d}/{len(schedule):02d} — {ver_label} ({block_reps} repetições)",
                flush=True,
            )
            if args.backend == "native":
                native_start(target)

            try:
                # 1. Warm-up padronizado no início de cada bloco (registrado em raw, is_warmup=True)
                order_global += 1
                warmup_id = f"RUN_{order_global:03d}"
                w_row, w_samples = execute_single_run(
                    backend=args.backend,
                    target=target,
                    run_id=warmup_id,
                    block_id=block_id,
                    order_global=order_global,
                    repeticao=0,
                    is_warmup=True,
                    scale_factor=args.scale,
                    clients=args.clients,
                    threads=args.threads,
                    duration_s=args.warmup_duration,
                    random_seed=args.seed_base + block_id,
                    sample_interval_s=args.sample_interval,
                )
                b_writer.writerow(w_row)
                t_writer.writerows(w_samples)
                bf.flush()
                tf.flush()
                time.sleep(args.run_cooldown)

                # 2. Repetições medidas do bloco
                for _ in range(block_reps):
                    rep_counter[ver_label] += 1
                    rep_num = rep_counter[ver_label]
                    order_global += 1
                    run_id = f"RUN_{order_global:03d}"

                    row, samples = execute_single_run(
                        backend=args.backend,
                        target=target,
                        run_id=run_id,
                        block_id=block_id,
                        order_global=order_global,
                        repeticao=rep_num,
                        is_warmup=False,
                        scale_factor=args.scale,
                        clients=args.clients,
                        threads=args.threads,
                        duration_s=args.duration,
                        random_seed=args.seed_base + rep_num,
                        sample_interval_s=args.sample_interval,
                    )
                    b_writer.writerow(row)
                    t_writer.writerows(samples)
                    bf.flush()
                    tf.flush()

                    print(
                        f"  -> {run_id} | {ver_label} rep {rep_num:02d}/{args.repetitions} | "
                        f"TPS={row['tps']} | Lat={row['latencia_media_ms']}ms | "
                        f"CPU={row['cpu_media_pct']}% | Mem={row['memoria_media_mib']}MiB | {row['status']}",
                        flush=True,
                    )
                    time.sleep(args.run_cooldown)
            finally:
                if args.backend == "native":
                    native_stop(target)

            time.sleep(args.block_cooldown)

    metadata["coleta_finalizada_utc"] = utc_now_iso()
    metadata["total_execucoes_registradas"] = order_global
    metadata["total_repeticoes_medidas_por_versao"] = rep_counter

    meta_path = RAW_DIR / "metadata_ambiente.json"
    meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[LAB05] Coleta finalizada com sucesso! Dados brutos em {RAW_DIR}", flush=True)


if __name__ == "__main__":
    main()
