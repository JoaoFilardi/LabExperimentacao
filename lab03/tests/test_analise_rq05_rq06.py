"""Testes automatizados unitários e de integração para o pipeline analise_rq05_rq06.py (LAB03S03)."""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from lab03.src.analise_rq05_rq06 import (
    CliffsDeltaResult,
    KruskalResult,
    SpearmanResult,
    aplicar_correcao_holm,
    calcular_cliffs_delta,
    calcular_correlacao_spearman,
    calcular_epsilon_quadrado,
    carregar_e_preparar_dados,
    categorizar_por_quartis,
    classificar_magnitude_cliffs_delta,
    classificar_magnitude_epsilon_quadrado,
    classificar_magnitude_spearman,
    executar_bateria_rq06,
    executar_kruskal_wallis,
    executar_pipeline_analise,
    exportar_artefatos_analise,
    formatar_p_valor,
    gerar_grafico_rq05,
    gerar_grafico_rq06_distribuicoes,
    gerar_grafico_rq06_heatmap,
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CSV_METRICAS = DATA_DIR / "metricas_dora.csv"
CSV_OURO = DATA_DIR / "amostra_ouro_final.csv"


@pytest.fixture
def sample_synthetic_df() -> pd.DataFrame:
    """Retorna DataFrame sintético controlado para testes estatísticos."""
    data = []
    # Cria 3 grupos com diferenças bem delineadas
    for i in range(30):
        if i < 10:
            tipo = "biblioteca/framework"
            df_val = 10.0 + i
            lt = 1.0 + (i * 0.1)
            cfr = 2.0
            rt = 0.5
            stars = 1000 + i * 10
            age = 2.0
            lang = "Python"
        elif i < 20:
            tipo = "aplicação/serviço"
            df_val = 5.0 + i
            lt = 10.0 + (i * 0.2)
            cfr = 15.0
            rt = 4.0
            stars = 5000 + i * 10
            age = 6.0
            lang = "TypeScript"
        else:
            tipo = "CLI"
            df_val = 1.0 + (i * 0.1)
            lt = 30.0 + i
            cfr = 35.0
            rt = 24.0
            stars = 20000 + i * 10
            age = 10.0
            lang = "Go"

        data.append({
            "full_name": f"org/repo_{i}",
            "stars": stars,
            "primary_language": lang,
            "age_years": age,
            "contributors_count": 10 + i,
            "deployment_frequency_weekly": df_val,
            "lead_time_by_release_days": lt,
            "lead_time_by_commit_days": lt * 0.8,
            "cfr_ci_percentage": cfr,
            "cfr_delivery_percentage": cfr * 1.2,
            "recovery_time_hours": rt,
            "tipo_projeto": tipo,
            "dora_overall_category": "Elite" if i < 10 else ("High" if i < 20 else "Medium"),
        })

    return pd.DataFrame(data)


# ==============================================================================
# TESTES DE FUNÇÕES ESTATÍSTICAS FUNDAMENTAIS
# ==============================================================================

def test_classificar_magnitude_spearman():
    """Valida a categorização de Dancey & Reidy para correlação de Spearman."""
    assert classificar_magnitude_spearman(0.05) == "Desprezível"
    assert classificar_magnitude_spearman(-0.08) == "Desprezível"
    assert classificar_magnitude_spearman(0.20) == "Fraca"
    assert classificar_magnitude_spearman(-0.25) == "Fraca"
    assert classificar_magnitude_spearman(0.40) == "Moderada"
    assert classificar_magnitude_spearman(0.65) == "Forte"
    assert classificar_magnitude_spearman(0.85) == "Muito Forte"
    assert classificar_magnitude_spearman(-0.95) == "Muito Forte"


def test_calcular_correlacao_spearman_perfeita():
    """Verifica correlação de Spearman perfeita positiva e perfeita negativa."""
    x = [1.0, 2.0, 3.0, 4.0, 5.0]
    y_pos = [10.0, 20.0, 30.0, 40.0, 50.0]
    y_neg = [50.0, 40.0, 30.0, 20.0, 10.0]

    res_pos = calcular_correlacao_spearman(x, y_pos, n_bootstrap=50)
    assert pytest.approx(res_pos.rho, abs=1e-5) == 1.0
    assert res_pos.p_value < 0.01
    assert res_pos.magnitude == "Muito Forte"
    assert res_pos.n == 5

    res_neg = calcular_correlacao_spearman(x, y_neg, n_bootstrap=50)
    assert pytest.approx(res_neg.rho, abs=1e-5) == -1.0
    assert res_neg.p_value < 0.01
    assert res_neg.magnitude == "Muito Forte"


def test_calcular_correlacao_spearman_casos_borda():
    """Garante robustez em arrays constantes, poucos dados ou NaNs."""
    # Menos de 3 dados válidos
    res_small = calcular_correlacao_spearman([1.0, 2.0], [3.0, 4.0])
    assert res_small.rho == 0.0
    assert res_small.p_value == 1.0

    # Array constante
    res_const = calcular_correlacao_spearman([5.0, 5.0, 5.0, 5.0], [1.0, 2.0, 3.0, 4.0])
    assert res_const.rho == 0.0
    assert res_const.p_value == 1.0

    # Com NaNs intercalados
    x = [1.0, np.nan, 3.0, 4.0, 5.0, np.nan]
    y = [2.0, 10.0, 6.0, 8.0, 10.0, 12.0]
    res_nan = calcular_correlacao_spearman(x, y, n_bootstrap=20)
    assert res_nan.n == 4
    assert pytest.approx(res_nan.rho, abs=1e-5) == 1.0


def test_classificar_magnitude_epsilon_quadrado():
    """Valida as faixas de tamanho de efeito do Epsilon ao quadrado."""
    assert classificar_magnitude_epsilon_quadrado(0.005) == "Desprezível"
    assert classificar_magnitude_epsilon_quadrado(0.03) == "Pequeno"
    assert classificar_magnitude_epsilon_quadrado(0.08) == "Médio"
    assert classificar_magnitude_epsilon_quadrado(0.20) == "Grande"


def test_calcular_epsilon_quadrado():
    """Valida a fórmula eps^2 = H / (n - 1) e limitadores [0, 1]."""
    assert calcular_epsilon_quadrado(10.0, 101) == pytest.approx(0.1, abs=1e-5)
    assert calcular_epsilon_quadrado(0.0, 50) == 0.0
    assert calcular_epsilon_quadrado(5.0, 1) == 0.0
    assert calcular_epsilon_quadrado(200.0, 10) == 1.0  # limitador superior


def test_classificar_magnitude_cliffs_delta():
    """Valida as faixas de Romano et al. para Cliff's Delta."""
    assert classificar_magnitude_cliffs_delta(0.10) == "Desprezível"
    assert classificar_magnitude_cliffs_delta(-0.25) == "Pequeno"
    assert classificar_magnitude_cliffs_delta(0.40) == "Médio"
    assert classificar_magnitude_cliffs_delta(-0.60) == "Grande"


def test_calcular_cliffs_delta():
    """Testa cálculo de Cliff's Delta entre grupos idênticos e disjuntos."""
    # Grupos idênticos
    g1 = [1.0, 2.0, 3.0, 4.0, 5.0]
    g2 = [1.0, 2.0, 3.0, 4.0, 5.0]
    res_identicos = calcular_cliffs_delta(g1, g2)
    assert pytest.approx(res_identicos.delta, abs=1e-5) == 0.0
    assert res_identicos.magnitude == "Desprezível"

    # Grupos disjuntos (A estritamente maior que B)
    ga = [100.0, 200.0, 300.0]
    gb = [1.0, 2.0, 3.0]
    res_disj = calcular_cliffs_delta(ga, gb)
    assert pytest.approx(res_disj.delta, abs=1e-5) == 1.0
    assert res_disj.magnitude == "Grande"

    # Caso com grupo vazio
    res_vazio = calcular_cliffs_delta([], [1.0, 2.0])
    assert res_vazio.delta == 0.0


def test_categorizar_por_quartis():
    """Testa partição de série em 4 quartis."""
    s = pd.Series(range(100))
    q = categorizar_por_quartis(s)
    assert q.nunique() == 4
    counts = q.value_counts()
    for c in counts:
        assert c == 25


def test_formatar_p_valor():
    """Verifica a formatação de p-valores."""
    assert formatar_p_valor(0.0001) == "p < 0.001"
    assert formatar_p_valor(0.0423) == "p = 0.042"
    assert formatar_p_valor(0.500) == "p = 0.500"


# ==============================================================================
# TESTES DE KRUSKAL-WALLIS E CORREÇÃO DE HOLM
# ==============================================================================

def test_executar_kruskal_wallis(sample_synthetic_df: pd.DataFrame):
    """Testa Kruskal-Wallis com dados sintéticos com forte efeito."""
    res = executar_kruskal_wallis(sample_synthetic_df, "tipo_projeto", "deployment_frequency_weekly")
    assert res.df == 2  # 3 grupos -> df = 2
    assert res.statistic_h > 15.0
    assert res.p_value_raw < 0.001
    assert res.epsilon_squared > 0.14
    assert res.magnitude == "Grande"
    assert res.n == 30


def test_executar_kruskal_wallis_casos_borda():
    """Testa Kruskal-Wallis com fator único ou dados nulos."""
    df_single = pd.DataFrame({
        "factor": ["A", "A", "A"],
        "metric": [1.0, 2.0, 3.0],
    })
    res = executar_kruskal_wallis(df_single, "factor", "metric")
    assert res.statistic_h == 0.0
    assert res.p_value_raw == 1.0
    assert res.is_significant is False


def test_aplicar_correcao_holm():
    """Garante controle de erro e ajuste não-decrescente de Holm."""
    raw_p = [0.001, 0.01, 0.03, 0.04, 0.50]
    reject, adj_p = aplicar_correcao_holm(raw_p, alpha=0.05)

    assert len(adj_p) == 5
    # Holm é não-decrescente para p-valores ordenados
    for i in range(len(adj_p) - 1):
        assert adj_p[i] <= adj_p[i + 1]
    # Todos p_adj >= p_raw
    for rp, ap in zip(raw_p, adj_p):
        assert ap >= rp

    # Lista vazia
    rej_empty, adj_empty = aplicar_correcao_holm([])
    assert len(rej_empty) == 0


def test_executar_bateria_rq06(sample_synthetic_df: pd.DataFrame):
    """Testa bateria múltipla com cálculo conjunto de Holm."""
    # Adiciona quartis sintéticos
    sample_synthetic_df["stars_quartile"] = categorizar_por_quartis(sample_synthetic_df["stars"])
    factors = ["tipo_projeto", "stars_quartile"]
    metrics = ["deployment_frequency_weekly", "cfr_ci_percentage"]

    results = executar_bateria_rq06(sample_synthetic_df, factors, metrics)
    assert len(results) == 4  # 2 fatores x 2 métricas

    for r in results:
        assert isinstance(r, KruskalResult)
        assert 0.0 <= r.p_value_adj <= 1.0
        assert 0.0 <= r.epsilon_squared <= 1.0


# ==============================================================================
# TESTES DE CARREGAMENTO E INTEGRAÇÃO COM DATASET REAL
# ==============================================================================

def test_carregar_e_preparar_dados():
    """Garante carregamento correto das métricas reais e junção com a amostra-ouro."""
    assert CSV_METRICAS.exists(), f"Arquivo não encontrado: {CSV_METRICAS}"
    df = carregar_e_preparar_dados(CSV_METRICAS, CSV_OURO if CSV_OURO.exists() else None)

    assert len(df) == 310
    assert "deployment_frequency_weekly" in df.columns
    assert "cfr_ci_percentage" in df.columns
    assert "stars_quartile" in df.columns
    assert "age_quartile" in df.columns
    assert "language_group" in df.columns


# ==============================================================================
# TESTES DE GERAÇÃO VISUAL E EXPORTAÇÃO
# ==============================================================================

def test_geracao_figuras_rq05_e_rq06(sample_synthetic_df: pd.DataFrame, tmp_path: Path):
    """Testa geração física e integridade das 6 figuras (PNG 300 DPI e PDF vetorial)."""
    fig_dir = tmp_path / "figuras"
    fig_dir.mkdir(parents=True, exist_ok=True)

    # 1. RQ 05
    res_ci = calcular_correlacao_spearman(
        sample_synthetic_df["deployment_frequency_weekly"],
        sample_synthetic_df["cfr_ci_percentage"],
        n_bootstrap=20,
    )
    res_del = calcular_correlacao_spearman(
        sample_synthetic_df["deployment_frequency_weekly"],
        sample_synthetic_df["cfr_delivery_percentage"],
        n_bootstrap=20,
    )
    p_rq05_png, p_rq05_pdf = gerar_grafico_rq05(
        sample_synthetic_df,
        fig_dir / "rq05.png",
        fig_dir / "rq05.pdf",
        res_ci,
        res_del,
    )
    assert p_rq05_png.exists() and p_rq05_png.stat().st_size > 1000
    assert p_rq05_pdf.exists() and p_rq05_pdf.stat().st_size > 1000

    # 2. RQ 06 Boxplots
    kruskal_res = [
        executar_kruskal_wallis(sample_synthetic_df, "tipo_projeto", "deployment_frequency_weekly"),
        executar_kruskal_wallis(sample_synthetic_df, "tipo_projeto", "lead_time_by_release_days"),
        executar_kruskal_wallis(sample_synthetic_df, "tipo_projeto", "cfr_ci_percentage"),
        executar_kruskal_wallis(sample_synthetic_df, "tipo_projeto", "recovery_time_hours"),
    ]
    p_box_png, p_box_pdf = gerar_grafico_rq06_distribuicoes(
        sample_synthetic_df,
        "tipo_projeto",
        "Tipo de Projeto",
        kruskal_res,
        fig_dir / "rq06_box.png",
        fig_dir / "rq06_box.pdf",
    )
    assert p_box_png.exists() and p_box_png.stat().st_size > 1000
    assert p_box_pdf.exists() and p_box_pdf.stat().st_size > 1000

    # 3. RQ 06 Heatmap
    p_heat_png, p_heat_pdf = gerar_grafico_rq06_heatmap(
        kruskal_res,
        fig_dir / "rq06_heat.png",
        fig_dir / "rq06_heat.pdf",
    )
    assert p_heat_png.exists() and p_heat_png.stat().st_size > 1000
    assert p_heat_pdf.exists() and p_heat_pdf.stat().st_size > 1000


def test_exportar_artefatos_analise(sample_synthetic_df: pd.DataFrame, tmp_path: Path):
    """Testa exportação dos arquivos tabulares CSV, Markdown e LaTeX."""
    res_ci = calcular_correlacao_spearman(
        sample_synthetic_df["deployment_frequency_weekly"],
        sample_synthetic_df["cfr_ci_percentage"],
        n_bootstrap=20,
    )
    res_del = calcular_correlacao_spearman(
        sample_synthetic_df["deployment_frequency_weekly"],
        sample_synthetic_df["cfr_delivery_percentage"],
        n_bootstrap=20,
    )
    k_res = [
        executar_kruskal_wallis(sample_synthetic_df, "tipo_projeto", "deployment_frequency_weekly"),
    ]

    artefatos = exportar_artefatos_analise(res_ci, res_del, k_res, tmp_path)

    assert artefatos["csv_rq05"].exists()
    assert artefatos["csv_rq06"].exists()
    assert artefatos["latex_sbc"].exists()
    assert artefatos["relatorio_md"].exists()

    # Valida conteúdo do LaTeX
    latex_text = artefatos["latex_sbc"].read_text(encoding="utf-8")
    assert "\\begin{table}" in latex_text
    assert "\\caption{Resultados da Correlação de Spearman" in latex_text


def test_pipeline_completo_integrado(tmp_path: Path):
    """Executa o pipeline completo de ponta a ponta e verifica saídas."""
    res = executar_pipeline_analise(
        metricas_path=CSV_METRICAS,
        amostra_ouro_path=CSV_OURO if CSV_OURO.exists() else None,
        output_dir=tmp_path / "data",
        figures_dir=tmp_path / "data" / "figuras",
    )

    assert res["n_repositorios"] == 310
    assert isinstance(res["spearman_ci"], SpearmanResult)
    assert isinstance(res["spearman_delivery"], SpearmanResult)
    assert len(res["kruskal_results"]) > 0
    assert len(res["figuras"]) == 6
    for fig in res["figuras"]:
        assert fig.exists() and fig.stat().st_size > 1000


def test_main_cli_execucao(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Testa execução da função main() via linha de comando simulada."""
    import sys
    from lab03.src.analise_rq05_rq06 import main

    test_args = [
        "analise_rq05_rq06.py",
        "--metricas", str(CSV_METRICAS),
        "--amostra-ouro", str(CSV_OURO) if CSV_OURO.exists() else "",
        "--output-dir", str(tmp_path / "cli_out"),
        "--figures-dir", str(tmp_path / "cli_out" / "figuras"),
    ]
    monkeypatch.setattr(sys, "argv", test_args)
    main()

    assert (tmp_path / "cli_out" / "tabela_estatisticas_rq05.csv").exists()
    assert (tmp_path / "cli_out" / "tabela_estatisticas_rq06.csv").exists()
    assert (tmp_path / "cli_out" / "figuras" / "rq05_dispersao_df_vs_cfr.png").exists()

