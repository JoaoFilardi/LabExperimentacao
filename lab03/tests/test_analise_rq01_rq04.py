"""Testes unitários e de integração para o pipeline analise_rq01_rq04.py (LAB03S03 - Issue #39)."""

from pathlib import Path
import pandas as pd
import pytest

from lab03.src.analise_rq01_rq04 import (
    DORA_CATEGORIES,
    analisar_c1_geral,
    analisar_rq01_df,
    analisar_rq02_lt,
    analisar_rq03_cfr,
    analisar_rq04_rt,
    calcular_resumo_estatistico,
    classificar_cfr,
    classificar_df,
    classificar_dora_c1_df,
    classificar_lt,
    classificar_rt,
    executar_pipeline_analise,
    exportar_dataset_c1,
    exportar_tabelas_estatisticas,
    gerar_graficos_analise,
    verificar_integridade_dataset,
)


@pytest.fixture
def sample_metrics_df() -> pd.DataFrame:
    """Fixture com dataset representativo contendo todas as colunas obrigatórias."""
    data = [
        {
            "full_name": "repo/elite",
            "stars": 10000,
            "primary_language": "Python",
            "age_years": 5.0,
            "contributors_count": 100,
            "deployment_frequency_weekly": 8.5,     # Elite (>= 7.0)
            "valid_releases_count": 443,
            "lead_time_by_release_days": 0.5,       # Elite (< 1.0)
            "lead_time_by_release_iqr_days": 0.3,
            "lead_time_by_commit_days": 0.4,
            "lead_time_by_commit_iqr_days": 0.2,
            "total_commits_evaluated": 2000,
            "excluded_first_release_count": 1,
            "cfr_ci_proxy": 0.05,                   # Elite (<= 0.15)
            "cfr_ci_percentage": 5.0,
            "cfr_delivery_proxy": 0.10,             # Elite (<= 0.15)
            "cfr_delivery_percentage": 10.0,
            "cfr_delivery_censored_count": 0,
            "recovery_time_hours": 0.8,             # Elite (< 1.0)
            "recovery_time_iqr_hours": 0.5,
            "recovery_total_episodes": 10,
            "recovery_censored_episodes": 0,
            "recovery_censored_ratio": 0.0,
        },
        {
            "full_name": "repo/high",
            "stars": 5000,
            "primary_language": "TypeScript",
            "age_years": 3.0,
            "contributors_count": 40,
            "deployment_frequency_weekly": 2.0,     # High (>= 1.0 e < 7.0)
            "valid_releases_count": 104,
            "lead_time_by_release_days": 5.0,       # High (>= 1.0 e < 7.0)
            "lead_time_by_release_iqr_days": 3.0,
            "lead_time_by_commit_days": 3.5,
            "lead_time_by_commit_iqr_days": 2.0,
            "total_commits_evaluated": 800,
            "excluded_first_release_count": 1,
            "cfr_ci_proxy": 0.20,                   # High (> 0.15 e <= 0.30)
            "cfr_ci_percentage": 20.0,
            "cfr_delivery_proxy": 0.25,
            "cfr_delivery_percentage": 25.0,
            "cfr_delivery_censored_count": 1,
            "recovery_time_hours": 12.0,            # High (>= 1.0 e < 24.0)
            "recovery_time_iqr_hours": 8.0,
            "recovery_total_episodes": 15,
            "recovery_censored_episodes": 1,
            "recovery_censored_ratio": 0.0667,
        },
        {
            "full_name": "repo/medium",
            "stars": 2000,
            "primary_language": "Go",
            "age_years": 4.0,
            "contributors_count": 25,
            "deployment_frequency_weekly": 0.5,     # Medium (>= 0.23 e < 1.0)
            "valid_releases_count": 26,
            "lead_time_by_release_days": 18.0,      # Medium (>= 7.0 e < 30.0)
            "lead_time_by_release_iqr_days": 12.0,
            "lead_time_by_commit_days": 12.0,
            "lead_time_by_commit_iqr_days": 8.0,
            "total_commits_evaluated": 300,
            "excluded_first_release_count": 1,
            "cfr_ci_proxy": 0.35,                   # Medium (> 0.30 e <= 0.45)
            "cfr_ci_percentage": 35.0,
            "cfr_delivery_proxy": 0.40,
            "cfr_delivery_percentage": 40.0,
            "cfr_delivery_censored_count": 0,
            "recovery_time_hours": 48.0,            # Medium (>= 24.0 e < 168.0)
            "recovery_time_iqr_hours": 20.0,
            "recovery_total_episodes": 8,
            "recovery_censored_episodes": 1,
            "recovery_censored_ratio": 0.125,
        },
        {
            "full_name": "repo/low",
            "stars": 1200,
            "primary_language": "Java",
            "age_years": 8.0,
            "contributors_count": 15,
            "deployment_frequency_weekly": 0.1,     # Low (< 0.23)
            "valid_releases_count": 5,
            "lead_time_by_release_days": 45.0,      # Low (>= 30.0)
            "lead_time_by_release_iqr_days": 25.0,
            "lead_time_by_commit_days": 35.0,
            "lead_time_by_commit_iqr_days": 20.0,
            "total_commits_evaluated": 120,
            "excluded_first_release_count": 1,
            "cfr_ci_proxy": 0.55,                   # Low (> 0.45)
            "cfr_ci_percentage": 55.0,
            "cfr_delivery_proxy": 0.60,
            "cfr_delivery_percentage": 60.0,
            "cfr_delivery_censored_count": 2,
            "recovery_time_hours": 200.0,           # Low (>= 168.0)
            "recovery_time_iqr_hours": 80.0,
            "recovery_total_episodes": 4,
            "recovery_censored_episodes": 2,
            "recovery_censored_ratio": 0.5,
        },
    ]
    return pd.DataFrame(data)


# ==============================================================================
# Testes de Integridade dos Dados
# ==============================================================================

def test_verificar_integridade_dataset_valido(sample_metrics_df: pd.DataFrame):
    res = verificar_integridade_dataset(sample_metrics_df)
    assert res["valido"] is True
    assert res["n_total"] == 4
    assert len(res["erros"]) == 0


def test_verificar_integridade_dataset_coluna_ausente(sample_metrics_df: pd.DataFrame):
    df_invalido = sample_metrics_df.drop(columns=["deployment_frequency_weekly"])
    res = verificar_integridade_dataset(df_invalido)
    assert res["valido"] is False
    assert any("deployment_frequency_weekly" in err for err in res["erros"])


def test_verificar_integridade_dataset_valores_fora_faixa(sample_metrics_df: pd.DataFrame):
    df_invalido = sample_metrics_df.copy()
    df_invalido.loc[0, "cfr_ci_proxy"] = 1.5  # CFR > 1.0 é inválido
    res = verificar_integridade_dataset(df_invalido)
    assert res["valido"] is False
    assert any("cfr_ci_proxy" in err for err in res["erros"])


# ==============================================================================
# Testes de Estatísticas Descritivas
# ==============================================================================

def test_calcular_resumo_estatistico():
    serie = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0])
    stats = calcular_resumo_estatistico(serie, "Teste", "un")
    assert stats["n"] == 5
    assert stats["mediana"] == 30.0
    assert stats["q1"] == 20.0
    assert stats["q3"] == 40.0
    assert stats["iqr"] == 20.0
    assert stats["min"] == 10.0
    assert stats["max"] == 50.0


def test_calcular_resumo_estatistico_serie_vazia():
    serie_vazia = pd.Series([], dtype=float)
    stats = calcular_resumo_estatistico(serie_vazia, "Vazia", "un")
    assert stats["n"] == 0
    assert stats["mediana"] == 0.0


# ==============================================================================
# Testes de Classificação Individual DORA
# ==============================================================================

def test_classificar_df():
    assert classificar_df(7.0) == "Elite"
    assert classificar_df(10.0) == "Elite"
    assert classificar_df(1.0) == "High"
    assert classificar_df(6.99) == "High"
    assert classificar_df(0.23) == "Medium"
    assert classificar_df(0.99) == "Medium"
    assert classificar_df(0.22) == "Low"


def test_classificar_lt():
    assert classificar_lt(0.5) == "Elite"
    assert classificar_lt(0.99) == "Elite"
    assert classificar_lt(1.0) == "High"
    assert classificar_lt(6.99) == "High"
    assert classificar_lt(7.0) == "Medium"
    assert classificar_lt(29.99) == "Medium"
    assert classificar_lt(30.0) == "Low"


def test_classificar_cfr():
    assert classificar_cfr(0.0) == "Elite"
    assert classificar_cfr(0.15) == "Elite"
    assert classificar_cfr(0.1501) == "High"
    assert classificar_cfr(0.30) == "High"
    assert classificar_cfr(0.3001) == "Medium"
    assert classificar_cfr(0.45) == "Medium"
    assert classificar_cfr(0.4501) == "Low"


def test_classificar_rt():
    assert classificar_rt(0.5) == "Elite"
    assert classificar_rt(0.99) == "Elite"
    assert classificar_rt(1.0) == "High"
    assert classificar_rt(23.99) == "High"
    assert classificar_rt(24.0) == "Medium"
    assert classificar_rt(167.99) == "Medium"
    assert classificar_rt(168.0) == "Low"


# ==============================================================================
# Testes de Classificação DORA C1 Geral
# ==============================================================================

def test_classificar_dora_c1_df(sample_metrics_df: pd.DataFrame):
    df_c1 = classificar_dora_c1_df(sample_metrics_df)

    # repo/elite: todas as 4 métricas são Elite (4, 4, 4, 4) -> mediana 4 -> Elite
    row_elite = df_c1[df_c1["full_name"] == "repo/elite"].iloc[0]
    assert row_elite["c1_df_category"] == "Elite"
    assert row_elite["c1_lt_category"] == "Elite"
    assert row_elite["c1_cfr_category"] == "Elite"
    assert row_elite["c1_rt_category"] == "Elite"
    assert row_elite["c1_overall_score"] == 4
    assert row_elite["c1_overall_category"] == "Elite"

    # repo/high: todas as 4 métricas são High (3, 3, 3, 3) -> mediana 3 -> High
    row_high = df_c1[df_c1["full_name"] == "repo/high"].iloc[0]
    assert row_high["c1_overall_score"] == 3
    assert row_high["c1_overall_category"] == "High"

    # repo/medium: todas as 4 métricas são Medium (2, 2, 2, 2) -> mediana 2 -> Medium
    row_med = df_c1[df_c1["full_name"] == "repo/medium"].iloc[0]
    assert row_med["c1_overall_score"] == 2
    assert row_med["c1_overall_category"] == "Medium"

    # repo/low: todas as 4 métricas são Low (1, 1, 1, 1) -> mediana 1 -> Low
    row_low = df_c1[df_c1["full_name"] == "repo/low"].iloc[0]
    assert row_low["c1_overall_score"] == 1
    assert row_low["c1_overall_category"] == "Low"


def test_classificar_dora_c1_arredondamento_para_baixo():
    """Verifica regra estrita de arredondamento para baixo da mediana de scores."""
    # Exemplo com notas (4, 3, 3, 1): mediana = 3.0 -> floor = 3 (High)
    df_test = pd.DataFrame([{
        "full_name": "repo/teste_floor",
        "deployment_frequency_weekly": 8.0,  # Elite (4)
        "lead_time_by_release_days": 5.0,    # High (3)
        "lead_time_by_commit_days": 4.0,
        "cfr_ci_proxy": 0.20,                # High (3)
        "cfr_delivery_proxy": 0.25,
        "recovery_time_hours": 200.0,        # Low (1)
    }])
    df_res = classificar_dora_c1_df(df_test)
    assert df_res.iloc[0]["c1_overall_score"] == 3
    assert df_res.iloc[0]["c1_overall_category"] == "High"

    # Exemplo com notas (4, 4, 3, 2): mediana = 3.5 -> floor = 3 (High)
    df_test2 = pd.DataFrame([{
        "full_name": "repo/teste_floor2",
        "deployment_frequency_weekly": 8.0,  # Elite (4)
        "lead_time_by_release_days": 0.5,    # Elite (4)
        "lead_time_by_commit_days": 0.4,
        "cfr_ci_proxy": 0.20,                # High (3)
        "cfr_delivery_proxy": 0.25,
        "recovery_time_hours": 50.0,         # Medium (2)
    }])
    df_res2 = classificar_dora_c1_df(df_test2)
    assert df_res2.iloc[0]["c1_overall_score"] == 3
    assert df_res2.iloc[0]["c1_overall_category"] == "High"


# ==============================================================================
# Testes das Análises por RQ
# ==============================================================================

def test_analises_rq01_a_rq04(sample_metrics_df: pd.DataFrame):
    df_c1 = classificar_dora_c1_df(sample_metrics_df)

    # RQ 01
    r1 = analisar_rq01_df(df_c1)
    assert "estatisticas" in r1
    assert r1["estatisticas"]["n"] == 4
    assert sum(r1["distribuicao_contagem"].values()) == 4

    # RQ 02
    r2 = analisar_rq02_lt(df_c1)
    assert "variante_a" in r2
    assert "variante_b" in r2
    assert "diferenca" in r2
    # Mediana da Variante A (release) >= Variante B (commit)
    assert r2["variante_a"]["mediana"] >= r2["variante_b"]["mediana"]

    # RQ 03
    r3 = analisar_rq03_cfr(df_c1)
    assert "variante_a" in r3
    assert "variante_b" in r3
    assert "censura_entrega" in r3
    assert r3["censura_entrega"]["total_releases_censuradas"] == 3

    # RQ 04
    r4 = analisar_rq04_rt(df_c1)
    assert "tempo_recuperacao" in r4
    assert "censura_agregada" in r4
    assert r4["censura_agregada"]["total_episodios"] == 37
    assert r4["censura_agregada"]["episodios_censurados"] == 4

    # C1 Geral
    rc1 = analisar_c1_geral(df_c1)
    assert sum(rc1["distribuicao_contagem"].values()) == 4


# ==============================================================================
# Testes de Exportação e Pipeline Completo
# ==============================================================================

def test_exportacao_tabelas_e_dataset(tmp_path: Path, sample_metrics_df: pd.DataFrame):
    df_c1 = classificar_dora_c1_df(sample_metrics_df)
    r1 = analisar_rq01_df(df_c1)
    r2 = analisar_rq02_lt(df_c1)
    r3 = analisar_rq03_cfr(df_c1)
    r4 = analisar_rq04_rt(df_c1)
    rc1 = analisar_c1_geral(df_c1)

    tabelas = exportar_tabelas_estatisticas(r1, r2, r3, r4, rc1, tmp_path)
    assert tabelas["csv_desc"].exists()
    assert tabelas["md_desc"].exists()
    assert tabelas["csv_cat"].exists()
    assert tabelas["md_cat"].exists()
    assert tabelas["latex"].exists()

    p_dataset = exportar_dataset_c1(df_c1, tmp_path / "classificacao_dora_c1.csv")
    assert p_dataset.exists()
    df_lido = pd.read_csv(p_dataset)
    assert len(df_lido) == 4
    assert "c1_overall_category" in df_lido.columns


def test_geracao_graficos(tmp_path: Path, sample_metrics_df: pd.DataFrame):
    df_c1 = classificar_dora_c1_df(sample_metrics_df)
    figs = gerar_graficos_analise(df_c1, tmp_path)
    assert len(figs) == 6
    for f in figs:
        assert f.exists()
        assert f.stat().st_size > 0


def test_pipeline_completo_end_to_end(tmp_path: Path, sample_metrics_df: pd.DataFrame):
    csv_input = tmp_path / "metricas_input.csv"
    sample_metrics_df.to_csv(csv_input, index=False)

    out_dir = tmp_path / "saida"
    res = executar_pipeline_analise(
        input_csv_path=csv_input,
        output_dir=out_dir,
    )
    assert res["status"] == "sucesso"
    assert res["n_repositorios"] == 4
    assert (out_dir / "classificacao_dora_c1.csv").exists()
    assert (out_dir / "tabela_estatisticas_rq01_rq04.csv").exists()
    assert len(res["graficos"]) == 6


def test_analise_main_cli(tmp_path: Path, sample_metrics_df: pd.DataFrame, monkeypatch):
    """Testa execução do script principal via CLI."""
    from lab03.src.analise_rq01_rq04 import main as analise_main
    input_csv = tmp_path / "metricas.csv"
    sample_metrics_df.to_csv(input_csv, index=False)
    out_dir = tmp_path / "out"
    monkeypatch.setattr(
        "sys.argv",
        ["analise_rq01_rq04", "--input", str(input_csv), "--output-dir", str(out_dir)],
    )
    analise_main()
    assert (out_dir / "classificacao_dora_c1.csv").exists()


def test_expandir_metricas_dora(tmp_path: Path):
    """Testa o utilitário de expansão do dataset de métricas DORA."""
    from lab03.src.expandir_metricas_dora import expand_metrics_dataset
    repos_csv = tmp_path / "repos.csv"
    pd.DataFrame([{
        "full_name": "owner/repo1",
        "stars": 2000,
        "primary_language": "Python",
        "age_years": 3.0,
        "contributors_count": 50,
        "releases_window_count": 10,
        "runs_window_count": 100,
    }]).to_csv(repos_csv, index=False)

    existing_csv = tmp_path / "existing.csv"
    pd.DataFrame([{
        "full_name": "owner/existing",
        "stars": 1000,
        "primary_language": "Go",
        "age_years": 1.0,
        "contributors_count": 10,
        "deployment_frequency_weekly": 0.5,
        "valid_releases_count": 26,
        "lead_time_by_release_days": 5.0,
        "lead_time_by_release_iqr_days": 2.0,
        "lead_time_by_commit_days": 4.0,
        "lead_time_by_commit_iqr_days": 1.5,
        "total_commits_evaluated": 100,
        "excluded_first_release_count": 1,
        "cfr_ci_proxy": 0.1,
        "cfr_ci_percentage": 10.0,
        "cfr_delivery_proxy": 0.2,
        "cfr_delivery_percentage": 20.0,
        "cfr_delivery_censored_count": 0,
        "recovery_time_hours": 2.0,
        "recovery_time_iqr_hours": 1.0,
        "recovery_total_episodes": 5,
        "recovery_censored_episodes": 0,
        "recovery_censored_ratio": 0.0,
        "dora_overall_category": "High",
        "dora_df_category": "Medium",
        "dora_lt_category": "High",
        "dora_cfr_category": "Elite",
        "dora_rt_category": "High",
    }]).to_csv(existing_csv, index=False)

    out_csv = tmp_path / "out_metrics.csv"
    df_exp = expand_metrics_dataset(repos_csv, existing_csv, out_csv, seed=123)
    assert len(df_exp) == 2
    assert out_csv.exists()


def test_gerar_notebook_analise(tmp_path: Path):
    """Testa geração do notebook interativo."""
    from lab03.src.gerar_notebook_analise import build_notebook
    nb_file = tmp_path / "test_nb.ipynb"
    build_notebook(nb_file)
    assert nb_file.exists()
    assert nb_file.stat().st_size > 0


def test_rotulagem_tiago_funcoes(tmp_path: Path):
    """Testa funções de suporte e geração da rotulagem Tiago."""
    from lab03.src.gerar_rotulagem_tiago import (
        get_classificacao_repo,
        get_classificacao_release,
        rotular_amostra_ouro_tiago,
    )
    t1, e1 = get_classificacao_repo(1, "repo", "lang")
    assert t1 == "biblioteca/framework"
    t2, e2 = get_classificacao_repo(26, "repo", "lang")
    assert t2 == "aplicação/serviço"
    t3, e3 = get_classificacao_repo(44, "repo", "lang")
    assert t3 == "CLI"
    t4, e4 = get_classificacao_repo(58, "repo", "lang")
    assert t4 == "outro"

    is_c, just = get_classificacao_release(
        1, "repo", "lang", 1, "v1.0.1", "patch release", "biblioteca/framework", "sim"
    )
    assert is_c in ("sim", "não")

    base_csv = Path("lab03/data/amostra_ouro_base.csv")
    if base_csv.exists():
        df_tiago = rotular_amostra_ouro_tiago(base_csv)
        assert len(df_tiago) == 300





def test_expandir_metricas_main_cli(tmp_path: Path, monkeypatch):
    """Testa CLI de expandir_metricas_dora."""
    from lab03.src.expandir_metricas_dora import main as expand_main
    repos_csv = Path("lab03/data/repositorios_selecionados.csv")
    metrics_csv = Path("lab03/data/metricas_dora.csv")
    out_csv = tmp_path / "metricas_cli_out.csv"

    if repos_csv.exists() and metrics_csv.exists():
        monkeypatch.setattr(
            "sys.argv",
            ["expandir_metricas_dora", "--repos", str(repos_csv), "--metrics", str(metrics_csv), "--output", str(out_csv)],
        )
        expand_main()
        assert out_csv.exists()

