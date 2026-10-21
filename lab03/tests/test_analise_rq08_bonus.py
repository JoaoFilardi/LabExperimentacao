"""Testes da análise bônus RQ08 (deployment rework rate)."""

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from lab03.src.analise_rq08_bonus import (
    calcular_cfr_b,
    calcular_rework,
    classificar_releases,
    comparar,
    executar,
    filtrar_janela,
    montar_tabela,
)

INICIO = pd.Timestamp("2025-10-01T00:00:00Z")
FIM = pd.Timestamp("2026-09-30T23:59:59Z")


def _rel(repo, tag, nome, data, corpo=""):
    return {"full_name": repo, "release_id": hash((repo, tag)) % 10**6, "tag_name": tag,
            "release_name": nome, "release_body": corpo, "published_at": data}


def _releases_basicas():
    return pd.DataFrame([
        _rel("a/x", "v1.0.0", "Features", "2026-01-01T00:00:00Z"),
        _rel("a/x", "v1.0.1", "Bug fixes", "2026-01-03T00:00:00Z"),     # corretiva, <=7d da anterior
        _rel("a/x", "v1.1.0", "New features", "2026-03-01T00:00:00Z"),
        _rel("a/x", "v1.1.1", "Hotfix crash", "2026-09-29T00:00:00Z"),  # corretiva, censurada
        _rel("b/y", "v2.0.0", "Improvements", "2026-02-01T00:00:00Z"),
        _rel("b/y", "v3.0.0", "Support new API", "2026-04-01T00:00:00Z"),
    ])


def test_classificacao_usa_heuristica_validada():
    df = classificar_releases(_releases_basicas())
    esperado = {"v1.0.0": False, "v1.0.1": True, "v1.1.0": False, "v1.1.1": True,
                "v2.0.0": False, "v3.0.0": False}
    assert dict(zip(df["tag_name"], df["is_corretiva"])) == esperado


def test_rework_rate_por_repositorio():
    df = classificar_releases(_releases_basicas())
    rw = calcular_rework(df).set_index("full_name")
    assert rw.loc["a/x", "total_releases"] == 4
    assert rw.loc["a/x", "releases_corretivas"] == 2
    assert abs(rw.loc["a/x", "rework_rate"] - 0.5) < 1e-12
    assert rw.loc["b/y", "rework_rate"] == 0.0


def test_filtro_de_janela_exclui_releases_fora():
    df = classificar_releases(pd.concat([
        _releases_basicas(),
        pd.DataFrame([_rel("a/x", "v0.9.0", "Fix", "2025-01-01T00:00:00Z")]),  # antes da janela
    ], ignore_index=True))
    assert len(filtrar_janela(df, INICIO, FIM)) == 6


def test_cfr_b_censura_ultimos_7_dias_e_conta_falhas():
    df = classificar_releases(_releases_basicas())
    cfr = calcular_cfr_b(df, FIM, 7).set_index("full_name")
    # a/x: v1.1.1 censurada (29/09); v1.0.0 falha (corretiva 2 dias depois); v1.0.1 e v1.1.0 não.
    assert cfr.loc["a/x", "releases_censuradas"] == 1
    assert cfr.loc["a/x", "releases_avaliadas_cfr"] == 3
    assert cfr.loc["a/x", "releases_com_falha"] == 1
    assert abs(cfr.loc["a/x", "cfr_b_recalculado"] - 1 / 3) < 1e-12
    assert cfr.loc["b/y", "cfr_b_recalculado"] == 0.0


def test_tabela_sinaliza_inconsistencia_com_csv():
    df = classificar_releases(_releases_basicas())
    metricas = pd.DataFrame({
        "full_name": ["a/x", "b/y"],
        "valid_releases_count": [4, 5],              # b/y diverge (6 coletadas)
        "cfr_delivery_proxy": [0.3333, 0.25],        # b/y diverge (recalculado = 0)
    })
    tab = montar_tabela(calcular_rework(df), calcular_cfr_b(df, FIM), metricas).set_index("full_name")
    assert bool(tab.loc["a/x", "contagem_confere"]) and bool(tab.loc["a/x", "cfr_confere"])
    assert not bool(tab.loc["b/y", "contagem_confere"])
    assert not bool(tab.loc["b/y", "cfr_confere"])


def test_comparar_casos_degenerados_nao_quebram():
    tab = pd.DataFrame({"rework_rate": [0.2, 0.2, 0.2], "cfr_b_recalculado": [0.2, 0.2, 0.2]})
    res = comparar(tab)
    assert res["repos_iguais"] == 3
    assert np.isnan(res["wilcoxon_p"]) and np.isnan(res["spearman_rho"])


def test_comparar_conta_direcao():
    tab = pd.DataFrame({"rework_rate": [0.1, 0.5, 0.3, 0.4],
                        "cfr_b_recalculado": [0.2, 0.4, 0.3, 0.9]})
    res = comparar(tab)
    assert (res["repos_rework_menor_que_cfr"], res["repos_rework_maior_que_cfr"], res["repos_iguais"]) == (2, 1, 1)


def test_executar_gera_artefatos():
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        _releases_basicas().to_csv(tmp / "releases.csv", index=False)
        pd.DataFrame({"full_name": ["a/x", "b/y"], "valid_releases_count": [4, 2],
                      "cfr_delivery_proxy": [0.3333, 0.0]}).to_csv(tmp / "metricas.csv", index=False)
        r = executar(tmp / "releases.csv", tmp / "metricas.csv", tmp / "out", tmp / "out" / "fig",
                     janela=(INICIO, FIM))
        for nome in ("rework_rate_por_repo.csv", "rework_rate_resumo.csv",
                     "rework_rate_comparacao_cfr.csv", "tabela_rework_rate.md"):
            assert (tmp / "out" / nome).exists(), nome
        assert (tmp / "out" / "fig" / "rework_vs_cfr_b.png").exists()
        assert len(r["tabela"]) == 2