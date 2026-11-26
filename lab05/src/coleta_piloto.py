"""Orquestrador da coleta piloto do LAB05 (Issue #64 — Sprint 1).

Prepara e verifica o ambiente (modo ``docker`` ou ``native``), inicializa a base
``pgbench`` com parâmetros padronizados, audita ``pg_settings`` (incluindo
diferenças nativas do PostgreSQL 18 como ``io_method`` e ``data_checksums``),
executa uma rodada piloto reduzida em desenho contrabalanceado ABBA e valida a
consistência dos dados gerados.

Os resultados da coleta piloto são gravados exclusivamente em
``lab05/data/pilot/`` para preservar intactos os conjuntos definitivos em
``lab05/data/raw/`` e ``lab05/data/processed/``.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from lab05.src import executar_coleta as ec  # noqa: E402
from lab05.src.validar_dados import validate_datasets  # noqa: E402

LAB05_DIR = Path(__file__).resolve().parents[1]
PILOT_DIR = LAB05_DIR / "data" / "pilot"
PILOT_RAW_DIR = PILOT_DIR / "raw"
PILOT_LOGS_DIR = PILOT_RAW_DIR / "logs_pgbench"
PILOT_PROCESSED_DIR = PILOT_DIR / "processed"


def parse_pg_settings_tsv(tsv_output: str) -> dict[str, str]:
    """Converte a saída TSV de ``pg_settings`` em dicionário ``{nome: valor}``."""
    settings: dict[str, str] = {}
    for line in tsv_output.splitlines():
        if "\t" in line:
            key, value = line.split("\t", 1)
            settings[key.strip()] = value.strip()
    return settings


def parse_docker_inspect_line(raw: str) -> dict[str, Any]:
    """Interpreta saída formatada de ``docker inspect`` para auditoria do container."""
    parts = [p.strip() for p in raw.strip().split("|")]
    if len(parts) < 5:
        return {"raw": raw.strip()}
    running = parts[0].lower() == "true"
    image_tag = parts[1]
    image_id = parts[2]
    nano_cpus = int(parts[3]) if parts[3].isdigit() else 0
    memory_bytes = int(parts[4]) if parts[4].isdigit() else 0
    return {
        "running": running,
        "image_tag": image_tag,
        "image_id": image_id,
        "cpus_limit": round(nano_cpus / 1e9, 3) if nano_cpus > 0 else None,
        "memory_limit_mib": round(memory_bytes / (1024.0 * 1024.0), 2) if memory_bytes > 0 else None,
    }


def docker_ensure_container_ready(
    container_name: str,
    db_user: str,
    db_name: str,
    timeout_s: int = 60,
) -> dict[str, Any]:
    """Verifica se o container Docker está ativo e aceitando conexões PostgreSQL."""
    inspect_proc = ec.run_cmd(
        [
            "docker",
            "inspect",
            "--format",
            "{{.State.Running}}|{{.Config.Image}}|{{.Image}}|{{.HostConfig.NanoCpus}}|{{.HostConfig.Memory}}",
            container_name,
        ],
        check=False,
        timeout=15,
    )
    if inspect_proc.returncode != 0:
        raise RuntimeError(
            f"Container '{container_name}' não encontrado ou Docker inacessível: "
            f"{inspect_proc.stderr.strip()}"
        )

    info = parse_docker_inspect_line(inspect_proc.stdout)
    if not info.get("running"):
        raise RuntimeError(
            f"Container '{container_name}' não está em execução. "
            "Execute 'docker compose -f lab05/docker/docker-compose.yml up -d'."
        )

    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        ready = ec.run_cmd(
            [
                "docker",
                "exec",
                container_name,
                "pg_isready",
                "-U",
                db_user,
                "-d",
                db_name,
            ],
            check=False,
            timeout=10,
        )
        if ready.returncode == 0:
            return info
        time.sleep(1.0)

    raise TimeoutError(
        f"PostgreSQL no container '{container_name}' não respondeu ao pg_isready em {timeout_s}s."
    )


def docker_init_and_configure(
    target: ec.VersionTarget,
    scale_factor: int,
) -> tuple[dict[str, str], dict[str, Any]]:
    """Recria a base ``pgbench_lab05`` no container e coleta ``pg_settings``."""
    assert target.container_name is not None
    info = docker_ensure_container_ready(
        target.container_name, target.db_user, "postgres"
    )

    # Recria base limpa para garantir paridade exata de volume de dados no piloto
    ec.run_cmd(
        [
            "docker",
            "exec",
            target.container_name,
            "psql",
            "-U",
            target.db_user,
            "-d",
            "postgres",
            "-c",
            f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{target.db_name}' AND pid <> pg_backend_pid();",
        ],
        check=False,
    )
    ec.run_cmd(
        [
            "docker",
            "exec",
            target.container_name,
            "psql",
            "-U",
            target.db_user,
            "-d",
            "postgres",
            "-c",
            f"DROP DATABASE IF EXISTS {target.db_name};",
        ]
    )
    ec.run_cmd(
        [
            "docker",
            "exec",
            target.container_name,
            "createdb",
            "-U",
            target.db_user,
            target.db_name,
        ]
    )
    ec.run_cmd(
        [
            "docker",
            "exec",
            target.container_name,
            "pgbench",
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
    ec.run_cmd(
        [
            "docker",
            "exec",
            target.container_name,
            "psql",
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

    settings_res = ec.run_cmd(
        [
            "docker",
            "exec",
            target.container_name,
            "psql",
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
    settings = parse_pg_settings_tsv(settings_res.stdout)
    return settings, info


def parse_pilot_args() -> argparse.Namespace:
    """Define os argumentos CLI da coleta piloto (Issue #64)."""
    parser = argparse.ArgumentParser(
        description="Executa coleta piloto controlada PostgreSQL 17 x PostgreSQL 18 (LAB05S01 - Issue #64)."
    )
    parser.add_argument(
        "--backend",
        choices=["docker", "native"],
        default="docker",
        help="Backend de execução do piloto (padrão: docker).",
    )
    parser.add_argument(
        "--runtime-dir",
        type=Path,
        default=ec.DEFAULT_RUNTIME_DIR,
        help="Diretório com binários portáteis e PGDATA (usado apenas no modo native).",
    )
    parser.add_argument(
        "--repetitions",
        type=int,
        default=4,
        help="Repetições válidas por versão no piloto (padrão: 4).",
    )
    parser.add_argument(
        "--block-size",
        type=int,
        default=2,
        help="Repetições por bloco ABBA no piloto (padrão: 2).",
    )
    parser.add_argument("--scale", type=int, default=10, help="Scale factor do pgbench (-s).")
    parser.add_argument("--clients", type=int, default=8, help="Clientes simultâneos (-c).")
    parser.add_argument("--threads", type=int, default=4, help="Threads do pgbench (-j).")
    parser.add_argument("--duration", type=int, default=10, help="Duração de cada repetição (s).")
    parser.add_argument("--warmup-duration", type=int, default=5, help="Duração do warm-up por bloco (s).")
    parser.add_argument("--run-cooldown", type=float, default=2.0, help="Pausa entre repetições (s).")
    parser.add_argument("--block-cooldown", type=float, default=3.0, help="Pausa ao alternar versão (s).")
    parser.add_argument("--sample-interval", type=float, default=1.0, help="Intervalo de amostragem (s).")
    parser.add_argument("--seed-base", type=int, default=4200, help="Semente base para pgbench.")
    parser.add_argument("--container-pg17", type=str, default="postgres_17", help="Container PG17.")
    parser.add_argument("--container-pg18", type=str, default="postgres_18", help="Container PG18.")
    return parser.parse_args()


def run_pilot(args: argparse.Namespace) -> dict[str, Any]:
    """Executa a coleta piloto completa e roda a validação de consistência."""
    PILOT_RAW_DIR.mkdir(parents=True, exist_ok=True)
    PILOT_LOGS_DIR.mkdir(parents=True, exist_ok=True)
    PILOT_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    metadata = ec.collect_machine_metadata(args.backend, args)
    metadata["escopo"] = "coleta_piloto_issue_64"
    schedule = ec.build_abba_schedule(args.repetitions, args.block_size)
    metadata["agenda_blocos_abba"] = [
        {"block_id": b, "versao": v, "repeticoes_no_bloco": sz} for b, v, sz in schedule
    ]

    if args.backend == "docker":
        docker_check = ec.run_cmd(["docker", "info"], check=False, timeout=15)
        if docker_check.returncode != 0:
            raise RuntimeError(
                "Docker daemon não está disponível. Inicie o Docker Desktop antes de rodar o piloto "
                f"ou utilize '--backend native'. Detalhe: {docker_check.stderr.strip()}"
            )
        targets = {
            "PG17": ec.VersionTarget(
                label="PG17",
                exact_version="17.12",
                port=5432,
                container_name=args.container_pg17,
            ),
            "PG18": ec.VersionTarget(
                label="PG18",
                exact_version="18.7",
                port=5433,
                container_name=args.container_pg18,
            ),
        }
        print("[LAB05 Piloto] Inicializando pgbench e auditando containers Docker...", flush=True)
        settings_17, info_17 = docker_init_and_configure(targets["PG17"], args.scale)
        settings_18, info_18 = docker_init_and_configure(targets["PG18"], args.scale)
        targets["PG17"].exact_version = settings_17.get("server_version", "17.12").split()[0]
        targets["PG18"].exact_version = settings_18.get("server_version", "18.7").split()[0]
        metadata["versoes_executadas"] = {
            "PG17": {
                "versao_exata": settings_17.get("server_version", "17.12"),
                "container": args.container_pg17,
                "porta": targets["PG17"].port,
                "docker_inspect": info_17,
            },
            "PG18": {
                "versao_exata": settings_18.get("server_version", "18.7"),
                "container": args.container_pg18,
                "porta": targets["PG18"].port,
                "docker_inspect": info_18,
            },
        }
        metadata["auditoria_pg_settings"] = ec.compute_settings_diff(settings_17, settings_18)
        metadata["pg_settings_completos"] = {"PG17": settings_17, "PG18": settings_18}
    else:
        targets = {
            "PG17": ec.VersionTarget(
                label="PG17",
                exact_version="17.12",
                port=55432,
                bin_dir=args.runtime_dir / "pg_17.12" / "pgsql" / "bin",
                data_dir=args.runtime_dir / "data_pg17",
            ),
            "PG18": ec.VersionTarget(
                label="PG18",
                exact_version="18.7",
                port=55433,
                bin_dir=args.runtime_dir / "pg_18.7" / "pgsql" / "bin",
                data_dir=args.runtime_dir / "data_pg18",
            ),
        }
        print("[LAB05 Piloto] Inicializando instâncias nativas PG17 e PG18...", flush=True)
        settings_17 = ec.native_init_and_configure(targets["PG17"], args.scale)
        settings_18 = ec.native_init_and_configure(targets["PG18"], args.scale)
        metadata["versoes_executadas"] = {
            "PG17": {"versao_exata": settings_17.get("server_version", "17.12"), "porta": targets["PG17"].port},
            "PG18": {"versao_exata": settings_18.get("server_version", "18.7"), "porta": targets["PG18"].port},
        }
        metadata["auditoria_pg_settings"] = ec.compute_settings_diff(settings_17, settings_18)
        metadata["pg_settings_completos"] = {"PG17": settings_17, "PG18": settings_18}

    benchmark_csv = PILOT_RAW_DIR / "benchmark_raw.csv"
    timeseries_csv = PILOT_RAW_DIR / "resource_timeseries_raw.csv"

    rep_counter = {"PG17": 0, "PG18": 0}
    order_global = 0
    original_logs_dir = ec.LOGS_DIR
    ec.LOGS_DIR = PILOT_LOGS_DIR

    try:
        with (
            benchmark_csv.open("w", newline="", encoding="utf-8") as bf,
            timeseries_csv.open("w", newline="", encoding="utf-8") as tf,
        ):
            b_writer = csv.DictWriter(bf, fieldnames=ec.BENCHMARK_CSV_FIELDS)
            t_writer = csv.DictWriter(tf, fieldnames=ec.TIMESERIES_CSV_FIELDS)
            b_writer.writeheader()
            t_writer.writeheader()

            for block_id, ver_label, block_reps in schedule:
                target = targets[ver_label]
                print(
                    f"[LAB05 Piloto] Bloco {block_id:02d}/{len(schedule):02d} — {ver_label} ({block_reps} repetições)",
                    flush=True,
                )
                if args.backend == "native":
                    ec.native_start(target)

                try:
                    order_global += 1
                    warmup_id = f"PILOT_{order_global:03d}"
                    w_row, w_samples = ec.execute_single_run(
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

                    for _ in range(block_reps):
                        rep_counter[ver_label] += 1
                        rep_num = rep_counter[ver_label]
                        order_global += 1
                        run_id = f"PILOT_{order_global:03d}"

                        row, samples = ec.execute_single_run(
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
                        ec.native_stop(target)

                time.sleep(args.block_cooldown)
    finally:
        ec.LOGS_DIR = original_logs_dir

    metadata["coleta_finalizada_utc"] = ec.utc_now_iso()
    metadata["total_execucoes_registradas"] = order_global
    metadata["total_repeticoes_medidas_por_versao"] = rep_counter

    meta_path = PILOT_RAW_DIR / "metadata_ambiente.json"
    meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    print("[LAB05 Piloto] Validando consistência dos dados piloto...", flush=True)
    report = validate_datasets(PILOT_RAW_DIR, PILOT_PROCESSED_DIR)
    return report


def main() -> None:
    """Ponto de entrada CLI da coleta piloto."""
    args = parse_pilot_args()
    report = run_pilot(args)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report["aprovado"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
