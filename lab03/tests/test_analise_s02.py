import math

import numpy as np
import pandas as pd
import pytest
from statsmodels.stats.inter_rater import aggregate_raters, fleiss_kappa

from lab03.src.concordancia import (
    calcular_concordancia, divergencias, fleiss, interpretar_kappa, matriz_avaliacoes, verificar_amostra,
)
from lab03.src.consenso import PENDENTE, construir_consenso
from lab03.src.heuristica_corretiva import avaliar_versoes, metricas, v1_palavras_chave, v2_palavras_e_semver


def _base() -> pd.DataFrame:
    linhas = []
    for repo_id in range(1, 61):
        for num in range(1, 6):
            linhas.append({
                "repo_id": repo_id, "full_name": f"org/repo{repo_id}",
                "repo_url": f"https://github.com/org/repo{repo_id}", "primary_language": "Python",
                "release_num": num, "tag_name": f"v1.{num}.0", "release_name": f"v1.{num}.0",
                "published_at": "2025-01-01T00:00:00Z",
                "release_url": f"https://github.com/org/repo{repo_id}/releases/tag/v1.{num}.{repo_id}",
                "tipo_projeto": "CLI", "entrega_real": "sim",
                "is_corretiva": "sim" if num in (2, 4) else "não", "justificativa": "",
            })
    return pd.DataFrame(linhas)


def _tres(altera=None):
    a, b, c = _base(), _base(), _base()
    if altera:
        altera(a, b, c)
    return {"kayque": a, "joao": b, "tiago": c}


def test_fleiss_exemplo_da_literatura():
    # Exemplo clássico (Wikipedia): 10 sujeitos, 14 avaliadores, 5 categorias, kappa ~ 0,210
    tabela = np.array([
        [0, 0, 0, 0, 14], [0, 2, 6, 4, 2], [0, 0, 3, 5, 6], [0, 3, 9, 2, 0], [2, 2, 8, 1, 1],
        [7, 7, 0, 0, 0], [3, 2, 6, 3, 0], [2, 5, 3, 2, 2], [6, 5, 2, 1, 0], [0, 2, 2, 3, 7],
    ])
    assert fleiss_kappa(tabela, method="fleiss") == pytest.approx(0.210, abs=0.001)


def test_concordancia_perfeita_com_duas_categorias():
    r = calcular_concordancia(_tres())
    linha = r[r["dimensao"] == "is_corretiva"].iloc[0]
    assert linha["fleiss_kappa"] == 1.0 and linha["concordancia_total_pct"] == 100.0


def test_categoria_unica_gera_kappa_indefinido():
    r = calcular_concordancia(_tres())
    linha = r[r["dimensao"] == "tipo_projeto"].iloc[0]
    assert pd.isna(linha["fleiss_kappa"]) and linha["interpretacao"] == "indefinido"


def test_kappa_cai_com_discordancia():
    def altera(a, b, c):
        b.loc[b["release_num"] == 1, "is_corretiva"] = "sim"
    k = calcular_concordancia(_tres(altera)).set_index("dimensao").loc["is_corretiva", "fleiss_kappa"]
    assert 0 < k < 1


def test_matriz_por_repo_e_por_release():
    dfs = _tres()
    assert len(matriz_avaliacoes(dfs, "tipo_projeto")) == 60
    assert len(matriz_avaliacoes(dfs, "is_corretiva")) == 300


def test_divergencias_listadas():
    def altera(a, b, c):
        a.loc[(a["repo_id"] == 3) & (a["release_num"] == 2), "is_corretiva"] = "não"
    d = divergencias(_tres(altera))
    assert len(d) == 1 and d.iloc[0]["dimensao"] == "is_corretiva" and d.iloc[0]["repo_id"] == 3


def test_verificar_amostra_detecta_amostra_diferente():
    dfs = _tres()
    dfs["joao"].loc[0, "release_url"] = "https://github.com/outro"
    assert any("mesma amostra" in e for e in verificar_amostra(dfs))


def test_verificar_amostra_ok():
    assert verificar_amostra(_tres()) == []


def test_consenso_maioria_e_unanimidade():
    def altera(a, b, c):
        a.loc[(a["repo_id"] == 1) & (a["release_num"] == 1), "is_corretiva"] = "sim"
    final, pend = construir_consenso(_tres(altera))
    linha = final[(final["repo_id"] == 1) & (final["release_num"] == 1)].iloc[0]
    assert linha["is_corretiva"] == "não" and linha["metodo_is_corretiva"] == "maioria"
    assert final["metodo_tipo_projeto"].eq("unanimidade").all()
    assert pend.empty and len(final) == 300


def test_consenso_sem_maioria_fica_pendente_e_desempate_resolve():
    def altera(a, b, c):
        a.loc[a["repo_id"] == 5, "tipo_projeto"] = "CLI"
        b.loc[b["repo_id"] == 5, "tipo_projeto"] = "outro"
        c.loc[c["repo_id"] == 5, "tipo_projeto"] = "biblioteca/framework"
    dfs = _tres(altera)
    final, pend = construir_consenso(dfs)
    assert len(pend) == 1 and pend.iloc[0]["repo_id"] == 5
    assert (final.loc[final["repo_id"] == 5, "tipo_projeto"] == PENDENTE).all()

    des = pd.DataFrame([{"dimensao": "tipo_projeto", "repo_id": 5, "release_num": 0,
                         "valor_final": "biblioteca/framework", "motivo": "decisão em grupo"}])
    final2, pend2 = construir_consenso(dfs, des)
    assert pend2.empty
    assert (final2.loc[final2["repo_id"] == 5, "tipo_projeto"] == "biblioteca/framework").all()
    assert (final2.loc[final2["repo_id"] == 5, "metodo_tipo_projeto"] == "desempate_grupo").all()


def test_metricas_precisao_recall_f1():
    m = metricas(["sim", "sim", "não", "não"], ["sim", "não", "sim", "não"])
    assert (m["tp"], m["fp"], m["fn"], m["tn"]) == (1, 1, 1, 1)
    assert m["precisao"] == m["recall"] == m["f1"] == 0.5


def test_metricas_sem_positivos_nao_divide_por_zero():
    assert metricas(["não", "não"], ["não", "não"])["f1"] == 0.0


def test_v1_e_v2():
    assert v1_palavras_chave(pd.Series({"release_name": "Fix crash on startup"})) == "sim"
    assert v1_palavras_chave(pd.Series({"release_name": "New features"})) == "não"
    assert v2_palavras_e_semver(pd.Series({"release_name": "Add support", "tag_name": "v1.2.3"})) == "não"
    assert v2_palavras_e_semver(pd.Series({"release_name": "Release", "tag_name": "v1.2.3"})) == "sim"
    assert v2_palavras_e_semver(pd.Series({"release_name": "Release", "tag_name": "v1.2.0"})) == "não"


def test_avaliar_versoes_registra_refinamento_quando_f1_baixo():
    # títulos neutros: v1 não detecta nada (F1=0); v2 usa semver de patch e acerta
    df = pd.DataFrame({
        "release_name": ["Release a", "Release b", "Release c", "Release d"],
        "tag_name": ["v1.0.1", "v1.0.2", "v1.1.0", "v1.2.0"],
        "is_corretiva": ["sim", "sim", "não", "não"],
    })
    r = avaliar_versoes(df)
    assert list(r["versao"]) == ["v1_palavras_chave", "v2_palavras_e_semver"]
    assert r.iloc[0]["f1"] < 0.70 and r.iloc[1]["f1"] >= 0.70


def test_avaliar_versoes_para_na_primeira_que_atinge_limiar():
    df = pd.DataFrame({
        "release_name": ["Bugfix release", "New features"], "tag_name": ["v1.0.1", "v1.1.0"],
        "is_corretiva": ["sim", "não"],
    })
    assert len(avaliar_versoes(df)) == 1


@pytest.mark.parametrize("k,esperado", [(0.1, "leve"), (0.3, "razoável"), (0.5, "moderada"),
                                        (0.7, "substancial"), (0.9, "quase perfeita"),
                                        (-0.1, "pior que o acaso"), (float("nan"), "indefinido")])
def test_interpretacao_kappa(k, esperado):
    assert interpretar_kappa(k) == esperado