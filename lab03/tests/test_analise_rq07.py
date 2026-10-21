"""Testes da análise de sensibilidade RQ07 (LAB03S03, Issue #41)."""

from __future__ import annotations

import math
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from lab03.src import analise_rq07 as m
except ModuleNotFoundError:  # execução a partir de lab03/
    from src import analise_rq07 as m


def _df(linhas):
    base = {
        "full_name": "o/r", "stars": 1000, "primary_language": "Python", "age_years": 3.0,
        "contributors_count": 10, "deployment_frequency_weekly": 0.5,
        "lead_time_by_release_days": 3.0, "lead_time_by_commit_days": 2.0,
        "cfr_ci_proxy": 0.10, "cfr_delivery_proxy": 0.50, "recovery_time_hours": 0.5,
    }
    rows = []
    for i, linha in enumerate(linhas):
        r = dict(base)
        r["full_name"] = f"o/r{i}"
        r.update(linha)
        rows.append(r)
    return pd.DataFrame(rows)


def test_classificacao_c1_segue_a_regra_da_mediana():
    # DF 0.5 -> Medium(2), LT 3 -> High(3), CFR 0.10 -> Elite(4), RT 0.5 -> Elite(4): mediana 3.5 -> 3
    cls = m.classificar_combinacao(_df([{}]), m.C1)
    assert cls.loc[0, "C1_df"] == "Medium"
    assert cls.loc[0, "C1_lt"] == "High"
    assert cls.loc[0, "C1_cfr"] == "Elite"
    assert cls.loc[0, "C1_rt"] == "Elite"
    assert cls.loc[0, "C1_score"] == 3
    assert cls.loc[0, "C1_categoria"] == "High"


def test_mediana_e_arredondada_para_baixo():
    # scores 4,3,2,1 -> mediana 2.5 -> 2 (Medium)
    df = _df([{
        "deployment_frequency_weekly": 8.0,   # Elite
        "lead_time_by_release_days": 3.0,     # High
        "cfr_ci_proxy": 0.40,                 # Medium
        "recovery_time_hours": 200.0,         # Low
    }])
    assert m.classificar_combinacao(df, m.C1).loc[0, "C1_categoria"] == "Medium"


def test_combinacoes_usam_as_colunas_certas():
    df = _df([{"lead_time_by_release_days": 40.0, "lead_time_by_commit_days": 0.5,
               "cfr_ci_proxy": 0.05, "cfr_delivery_proxy": 0.50}])
    assert m.classificar_combinacao(df, m.C1).loc[0, "C1_lt"] == "Low"
    assert m.classificar_combinacao(df, m.C2).loc[0, "C2_lt"] == "Elite"
    assert m.classificar_combinacao(df, m.C3).loc[0, "C3_cfr"] == "Low"
    assert m.classificar_combinacao(df, m.C1).loc[0, "C1_cfr"] == "Elite"
    c4 = m.classificar_combinacao(df, m.C4)
    assert c4.loc[0, "C4_lt"] == "Elite" and c4.loc[0, "C4_cfr"] == "Low"


def test_metrica_ausente_deixa_repositorio_nao_aplicavel():
    df = _df([{}, {"lead_time_by_commit_days": np.nan}])
    cls = m.classificar_combinacao(df, m.C2)
    assert cls.loc[0, "C2_categoria"] == "High"
    assert pd.isna(cls.loc[1, "C2_categoria"])
    assert pd.isna(cls.loc[1, "C2_score"])


def test_kappa_identico_e_1():
    assert m.kappa_ponderado_linear([1, 2, 3, 4, 2], [1, 2, 3, 4, 2]) == 1.0


def test_kappa_constante_igual_retorna_1():
    assert m.kappa_ponderado_linear([3, 3, 3], [3, 3, 3]) == 1.0


def test_kappa_ponderado_linear_valor_conhecido():
    # Calculado à mão: 1 - (1/12) / 0.375 = 7/9
    k = m.kappa_ponderado_linear([1, 2, 3, 4], [1, 2, 3, 3])
    assert math.isclose(k, 7 / 9, rel_tol=1e-9)


def test_kappa_linear_penaliza_menos_erro_de_um_degrau_que_de_tres():
    perto = m.kappa_ponderado_linear([1, 2, 3, 4, 1, 4], [2, 2, 3, 4, 1, 4])
    longe = m.kappa_ponderado_linear([1, 2, 3, 4, 1, 4], [4, 2, 3, 4, 1, 4])
    assert perto > longe


def test_comparar_par_conta_mudancas_e_direcao():
    df = _df([
        {},  # C1 High
        {"lead_time_by_commit_days": 0.5},          # C2 melhora: LT Elite -> scores 2,4,4,4 -> 4 Elite (C1 High)
        {"lead_time_by_commit_days": 40.0},         # C2 piora: LT Low -> scores 2,1,4,4 -> 3 High (C1 High)
        {"deployment_frequency_weekly": 8.0,
         "lead_time_by_release_days": 3.0, "lead_time_by_commit_days": 40.0,
         "cfr_ci_proxy": 0.40, "recovery_time_hours": 200.0},  # C1 Medium; C2 scores 4,1,2,1 -> 1.5 -> Low
    ])
    cls = m.classificar_todas(df, [m.C1, m.C2, m.C3])
    r = m.comparar_par(cls, "C1", "C2")
    assert r["n_repositorios"] == 4
    assert r["n_mudaram"] == 2
    assert r["pct_mudaram"] == 50.0
    assert r["pct_melhoraram"] == 25.0
    assert r["pct_pioraram"] == 25.0
    assert 0.0 <= r["kappa_ponderado_linear"] <= 1.0


def test_comparar_par_ignora_repositorios_nao_aplicaveis():
    df = _df([{}, {"lead_time_by_commit_days": np.nan}])
    cls = m.classificar_todas(df, [m.C1, m.C2, m.C3])
    r = m.comparar_par(cls, "C1", "C2")
    assert r["n_repositorios"] == 1


def test_pares_cobrem_todas_as_combinacoes():
    df = _df([{}, {"cfr_ci_proxy": 0.4}])
    pares = m.comparar_todos_os_pares(m.classificar_todas(df, [m.C1, m.C2, m.C3]), [m.C1, m.C2, m.C3])
    assert list(pares["par"]) == ["C1 x C2", "C1 x C3", "C2 x C3"]


def test_matriz_transicao_soma_n():
    df = _df([{}, {"cfr_ci_proxy": 0.4}, {"deployment_frequency_weekly": 8.0}])
    cls = m.classificar_todas(df, [m.C1, m.C2, m.C3])
    mat = m.matriz_transicao(cls, "C1", "C3")
    assert int(mat.to_numpy().sum()) == 3
    assert list(mat.index) == m.DORA_CATEGORIES


def test_interpretacao_kappa_faixas():
    assert m.interpretar_kappa(0.85) == "Concordância quase perfeita"
    assert m.interpretar_kappa(0.70) == "Concordância substancial"
    assert m.interpretar_kappa(0.50) == "Concordância moderada"
    assert m.interpretar_kappa(0.30) == "Concordância razoável"
    assert m.interpretar_kappa(0.10) == "Concordância fraca"
    assert m.interpretar_kappa(-0.1) == "Pior que o acaso"


def test_holm_conhecido():
    adj = m.ajustar_holm([0.01, 0.04, 0.03])
    assert np.allclose(adj, [0.03, 0.06, 0.06])


def test_veredito_sensibilidade():
    assert m.veredito_sensibilidade(5.0) == "robusta"
    assert m.veredito_sensibilidade(20.0) == "parcialmente sensível"
    assert m.veredito_sensibilidade(45.0) == "sensível"


def test_combinacoes_exige_pelo_menos_tres():
    df = _df([{}])
    try:
        m.combinacoes_disponiveis(df, ["C1", "C2"])
    except ValueError:
        return
    raise AssertionError("deveria exigir 3 combinações")


def test_c5_entra_quando_ha_coluna_de_prerelease():
    df = _df([{}])
    assert [c.id for c in m.combinacoes_disponiveis(df)] == ["C1", "C2", "C3", "C4"]
    df[m.COL_DF_PRERELEASE] = 2.0
    assert [c.id for c in m.combinacoes_disponiveis(df)][-1] == "C5"


def test_verificar_colunas_rejeita_dataset_incompleto():
    df = _df([{}]).drop(columns=["cfr_delivery_proxy"])
    try:
        m.verificar_colunas(df)
    except ValueError:
        return
    raise AssertionError("deveria rejeitar dataset sem coluna obrigatória")


def _dataset_sintetico(n=60, seed=7):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "full_name": [f"org/repo{i}" for i in range(n)],
        "stars": rng.integers(1000, 90000, n),
        "primary_language": rng.choice(["Python", "Go", "Java", "Rust", "C++", "Ruby", "PHP"], n),
        "age_years": rng.uniform(1, 12, n).round(2),
        "contributors_count": rng.integers(3, 800, n),
        "deployment_frequency_weekly": rng.lognormal(-1.0, 1.0, n).round(4),
        "lead_time_by_release_days": rng.lognormal(2.0, 1.0, n).round(3),
        "lead_time_by_commit_days": rng.lognormal(1.5, 1.0, n).round(3),
        "cfr_ci_proxy": rng.beta(2, 8, n).round(4),
        "cfr_delivery_proxy": rng.beta(3, 7, n).round(4),
        "recovery_time_hours": rng.lognormal(2.0, 1.2, n).round(3),
    })
    return df


def test_pipeline_ponta_a_ponta_gera_todos_os_artefatos():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        csv = tmp / "entrada.csv"
        df = _dataset_sintetico()
        df["c1_overall_category"] = m.classificar_combinacao(df, m.C1)["C1_categoria"]
        df.to_csv(csv, index=False)
        res = m.executar_pipeline_rq07(csv, tmp / "data", tmp / "docs")

        assert res["n_repositorios"] == 60
        assert res["divergencias_c1_vs_csv"] == 0
        assert len(res["pares"]) == 6  # C(4,2)
        for nome, caminho in res["artefatos"].items():
            assert Path(caminho).exists(), nome
        assert any(p.suffix == ".png" for p in res["figuras"])
        k = res["pares"]["kappa_ponderado_linear"]
        assert ((k >= -1.0) & (k <= 1.0)).all()
        texto = (tmp / "docs" / "analise_rq07.md").read_text(encoding="utf-8")
        assert "Robustez das conclusões das RQ01 a RQ06" in texto
        assert "C1 x C2" in texto
        cls = pd.read_csv(tmp / "data" / "classificacao_dora_combinacoes.csv")
        assert len(cls) == 60
        for cid in ["C1", "C2", "C3", "C4"]:
            assert cls[f"{cid}_categoria"].notna().all()


def test_pipeline_e_reproduzivel():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        csv = tmp / "entrada.csv"
        _dataset_sintetico().to_csv(csv, index=False)
        r1 = m.executar_pipeline_rq07(csv, tmp / "a", tmp / "docs_a")
        r2 = m.executar_pipeline_rq07(csv, tmp / "b", tmp / "docs_b")
        pd.testing.assert_frame_equal(r1["pares"], r2["pares"])
        pd.testing.assert_frame_equal(r1["rq06"], r2["rq06"])