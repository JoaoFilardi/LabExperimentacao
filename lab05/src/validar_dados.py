"""Validação, auditoria e geração dos datasets tratados do LAB05 (Issue #66).

Lê os dados brutos em ``lab05/data/raw/``, executa verificações de integridade,
completude, domínio de unidades, consistência cruzada com a série temporal e
sinalização não destrutiva de outliers (regra 1,5 × IQR), gerando os arquivos
validados em ``lab05/data/processed/``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

LAB05_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = LAB05_DIR / "data" / "raw"
PROCESSED_DIR = LAB05_DIR / "data" / "processed"

REQUIRED_BENCHMARK_COLS = [
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
]

REQUIRED_TIMESERIES_COLS = [
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

CORE_METRICS = [
    ("latencia_media_ms", "outlier_latencia"),
    ("tps", "outlier_tps"),
    ("cpu_media_pct", "outlier_cpu"),
    ("memoria_media_mib", "outlier_memoria"),
]


def _flag_iqr_outliers(df: pd.DataFrame, col: str) -> pd.Series:
    """Identifica outliers por versão utilizando a regra 1,5 × IQR (sem excluir)."""
    flags = pd.Series(False, index=df.index)
    for _, grp in df.groupby("versao"):
        q1 = grp[col].quantile(0.25)
        q3 = grp[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        is_out = (grp[col] < lower) | (grp[col] > upper)
        flags.loc[grp.index] = is_out
    return flags


def validate_datasets(
    raw_dir: Path = RAW_DIR,
    processed_dir: Path = PROCESSED_DIR,
) -> dict[str, Any]:
    """Executa toda a bateria de validações e grava os artefatos tratados."""
    processed_dir.mkdir(parents=True, exist_ok=True)

    bench_path = raw_dir / "benchmark_raw.csv"
    ts_path = raw_dir / "resource_timeseries_raw.csv"
    meta_path = raw_dir / "metadata_ambiente.json"

    errors: list[str] = []
    warnings: list[str] = []

    for p in (bench_path, ts_path, meta_path):
        if not p.exists():
            raise FileNotFoundError(f"Arquivo obrigatório não encontrado: {p}")

    df_raw = pd.read_csv(bench_path)
    df_ts_raw = pd.read_csv(ts_path)
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))

    # 1. Validação de schema
    missing_b_cols = [c for c in REQUIRED_BENCHMARK_COLS if c not in df_raw.columns]
    missing_t_cols = [c for c in REQUIRED_TIMESERIES_COLS if c not in df_ts_raw.columns]
    if missing_b_cols:
        errors.append(f"Colunas ausentes em benchmark_raw.csv: {missing_b_cols}")
    if missing_t_cols:
        errors.append(f"Colunas ausentes em resource_timeseries_raw.csv: {missing_t_cols}")

    if errors:
        return {"aprovado": False, "erros": errors, "avisos": warnings}

    # Normaliza booleanos
    df_raw["is_warmup"] = df_raw["is_warmup"].astype(bool)
    df_ts_raw["is_warmup"] = df_ts_raw["is_warmup"].astype(bool)

    # 2. Separação entre warm-up e execuções medidas
    df_warmup = df_raw[df_raw["is_warmup"]].copy()
    df_measured = df_raw[~df_raw["is_warmup"]].copy()

    # 3. Verificação de status e falhas
    failed_runs = df_measured[df_measured["status"] != "OK"]
    if not failed_runs.empty:
        errors.append(
            f"Encontradas {len(failed_runs)} execuções medidas com status != OK: "
            f"{failed_runs['run_id'].tolist()}"
        )

    tx_fail_runs = df_measured[df_measured["transacoes_falhas"] > 0]
    if not tx_fail_runs.empty:
        warnings.append(
            f"{len(tx_fail_runs)} execuções apresentaram transacoes_falhas > 0."
        )

    df_valid = df_measured[df_measured["status"] == "OK"].copy()

    # 4. Valores ausentes nas colunas obrigatórias
    null_counts = df_valid[REQUIRED_BENCHMARK_COLS].isna().sum()
    cols_with_nulls = {k: int(v) for k, v in null_counts.items() if v > 0}
    if cols_with_nulls:
        errors.append(f"Valores ausentes em colunas obrigatórias: {cols_with_nulls}")

    ts_null_counts = df_ts_raw[REQUIRED_TIMESERIES_COLS].isna().sum()
    ts_cols_with_nulls = {k: int(v) for k, v in ts_null_counts.items() if v > 0}
    if ts_cols_with_nulls:
        errors.append(
            f"Valores ausentes em resource_timeseries_raw.csv: {ts_cols_with_nulls}"
        )

    # 5. Duplicidades
    dup_run_ids = int(df_raw["run_id"].duplicated().sum())
    dup_ver_rep = int(df_valid.duplicated(subset=["versao", "repeticao"]).sum())
    if dup_run_ids > 0:
        errors.append(f"Encontrados {dup_run_ids} run_id duplicados em benchmark_raw.csv.")
    if dup_ver_rep > 0:
        errors.append(
            f"Encontrados {dup_ver_rep} pares (versao, repeticao) duplicados."
        )

    # 6. Balanceamento entre tratamentos (PG17 x PG18)
    counts_by_ver = {k: int(v) for k, v in df_valid["versao"].value_counts().items()}
    if set(counts_by_ver.keys()) != {"PG17", "PG18"}:
        errors.append(f"Versões esperadas {{'PG17', 'PG18'}}, encontradas: {counts_by_ver}")
    elif counts_by_ver["PG17"] != counts_by_ver["PG18"]:
        errors.append(
            f"Desbalanceamento entre versões: PG17={counts_by_ver['PG17']} vs PG18={counts_by_ver['PG18']}"
        )

    # 7. Restrições de domínio e escala de razão
    domain_checks = {
        "latencia_media_ms_positiva": bool((df_valid["latencia_media_ms"] > 0).all()),
        "latencia_dp_ms_nao_negativa": bool((df_valid["latencia_dp_ms"] >= 0).all()),
        "tps_positivo": bool((df_valid["tps"] > 0).all()),
        "transacoes_processadas_positivas": bool((df_valid["transacoes_processadas"] > 0).all()),
        "cpu_media_nao_negativa": bool((df_valid["cpu_media_pct"] >= 0).all()),
        "cpu_normalizada_no_intervalo_0_100": bool(
            ((df_valid["cpu_normalizada_media_pct"] >= 0) & (df_valid["cpu_normalizada_media_pct"] <= 100.5)).all()
        ),
        "memoria_media_positiva": bool((df_valid["memoria_media_mib"] > 0).all()),
        "memoria_pico_ge_media": bool(
            (df_valid["memoria_pico_mib"] >= df_valid["memoria_media_mib"] - 1e-6).all()
        ),
        "amostras_recursos_suficientes": bool((df_valid["amostras_recursos"] >= 5).all()),
    }
    for check_name, passed in domain_checks.items():
        if not passed:
            errors.append(f"Falha na verificação de domínio: {check_name}")

    # 8. Consistência cruzada TPS x (transações / duração)
    est_tps = df_valid["transacoes_processadas"] / df_valid["duracao_real_s"]
    rel_diff_tps = ((df_valid["tps"] - est_tps).abs() / df_valid["tps"]).max()
    tps_consistency_ok = bool(rel_diff_tps <= 0.20)
    if not tps_consistency_ok:
        warnings.append(
            f"Diferença relativa máxima entre TPS reportado e tx/duracao_real foi {rel_diff_tps:.2%}."
        )

    # 9. Consistência cruzada com a série temporal de recursos
    valid_run_ids = set(df_valid["run_id"])
    df_ts_valid = df_ts_raw[df_ts_raw["run_id"].isin(valid_run_ids)].copy()

    ts_agg = (
        df_ts_valid.groupby("run_id")
        .agg(
            ts_count=("cpu_pct", "count"),
            ts_cpu_mean=("cpu_pct", "mean"),
            ts_mem_mean=("memoria_mib", "mean"),
        )
        .reset_index()
    )
    merged = df_valid[["run_id", "amostras_recursos", "cpu_media_pct", "memoria_media_mib"]].merge(
        ts_agg, on="run_id", how="left"
    )
    missing_ts_runs = merged[merged["ts_count"].isna()]["run_id"].tolist()
    if missing_ts_runs:
        errors.append(f"Execuções sem série temporal correspondente: {missing_ts_runs}")
    else:
        max_cpu_diff = float((merged["cpu_media_pct"] - merged["ts_cpu_mean"]).abs().max())
        max_mem_diff = float((merged["memoria_media_mib"] - merged["ts_mem_mean"]).abs().max())
        count_mismatch = int((merged["amostras_recursos"] != merged["ts_count"]).sum())
        if count_mismatch > 0 or max_cpu_diff > 0.15 or max_mem_diff > 0.15:
            errors.append(
                f"Inconsistência entre benchmark e série temporal "
                f"(count_mismatch={count_mismatch}, max_cpu_diff={max_cpu_diff:.4f}, max_mem_diff={max_mem_diff:.4f})"
            )

    # 10. Sinalização não destrutiva de outliers (1,5 x IQR por versão)
    outlier_summary: dict[str, dict[str, int]] = {}
    for metric_col, flag_col in CORE_METRICS:
        df_valid[flag_col] = _flag_iqr_outliers(df_valid, metric_col)
        outlier_summary[metric_col] = {
            ver: int(grp[flag_col].sum()) for ver, grp in df_valid.groupby("versao")
        }

    # Ordenação limpa para análise (Sprint 2 — Issue #68)
    df_valid = df_valid.sort_values(["order_global"]).reset_index(drop=True)
    df_ts_valid = df_ts_valid.sort_values(["run_id", "segundo_relativo"]).reset_index(drop=True)

    # Estatísticas básicas de verificação (checagem de sanidade — não substitui análise da Issue #68)
    sanity_overview: dict[str, dict[str, dict[str, float]]] = {}
    for ver, grp in df_valid.groupby("versao"):
        sanity_overview[str(ver)] = {}
        for metric_col, _ in CORE_METRICS:
            sanity_overview[str(ver)][metric_col] = {
                "n": int(len(grp)),
                "media": round(float(grp[metric_col].mean()), 4),
                "mediana": round(float(grp[metric_col].median()), 4),
                "dp": round(float(grp[metric_col].std(ddof=1)), 4),
                "min": round(float(grp[metric_col].min()), 4),
                "max": round(float(grp[metric_col].max()), 4),
            }

    # Salva datasets tratados
    valid_bench_path = processed_dir / "benchmark_validado.csv"
    valid_ts_path = processed_dir / "resource_timeseries_validado.csv"
    report_path = processed_dir / "relatorio_validacao.json"

    df_valid.to_csv(valid_bench_path, index=False, encoding="utf-8")
    df_ts_valid.to_csv(valid_ts_path, index=False, encoding="utf-8")

    block_balance = {
        str(ver): round(float(grp["block_id"].mean()), 3)
        for ver, grp in df_valid.groupby("versao")
    }

    report: dict[str, Any] = {
        "aprovado": len(errors) == 0,
        "erros": errors,
        "avisos": warnings,
        "contagens": {
            "total_linhas_raw": int(len(df_raw)),
            "execucoes_warmup_excluidas_do_tratado": int(len(df_warmup)),
            "execucoes_medidas_validas": int(len(df_valid)),
            "por_versao": counts_by_ver,
            "amostras_serie_temporal_raw": int(len(df_ts_raw)),
            "amostras_serie_temporal_validadas": int(len(df_ts_valid)),
        },
        "balanceamento_blocos_media_indice": block_balance,
        "verificacoes_dominio": domain_checks,
        "consistencia_tps_diff_relativa_max": round(float(rel_diff_tps), 4),
        "outliers_sinalizados_iqr_nao_removidos": outlier_summary,
        "resumo_sanidade_por_versao": sanity_overview,
        "metadados_origem": {
            "backend": metadata.get("backend"),
            "coleta_iniciada_utc": metadata.get("coleta_iniciada_utc"),
            "coleta_finalizada_utc": metadata.get("coleta_finalizada_utc"),
        },
    }

    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report


def main() -> None:
    """Ponto de entrada CLI do validador de dados."""
    report = validate_datasets()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if not report["aprovado"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
