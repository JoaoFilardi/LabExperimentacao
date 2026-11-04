"""Testes da análise descritiva e da coleta dos dados reais do LAB04 (LAB04S01)."""

import numpy as np
import pandas as pd
import pytest

from lab04.src import coleta_dados_reais as coleta
from lab04.src.dados_reais import (
    CAMINHO_DADOS_REAIS_PADRAO,
    carregar_dados_reais,
    detectar_outliers_iqr,
    estatisticas_para_dataframe,
    gerar_relatorio,
    obter_resumo_estatistico_reais,
    perfilar_grupo,
    salvar_estatisticas,
    validar_qualidade,
)


def _df_pequeno():
    return pd.DataFrame(
        {
            "pr_id": [1, 2, 3, 4, 5, 6, 7, 8],
            "repositorio": ["o/r"] * 8,
            "grupo": ["sem_bot"] * 4 + ["com_bot"] * 4,
            "bot_presente": [False] * 4 + [True] * 4,
            "nome_bot": ["nenhum"] * 4 + ["codecov[bot]"] * 4,
            "created_at": ["2024-06-01 00:00:00"] * 8,
            "merged_at": [
                "2024-06-01 02:00:00", "2024-06-01 04:00:00", "2024-06-01 08:00:00", "2024-06-03 00:00:00",
                "2024-06-01 01:00:00", "2024-06-01 03:00:00", "2024-06-01 06:00:00", "2024-06-01 12:00:00",
            ],
            "tempo_horas": [2, 4, 8, 48, 1, 3, 6, 12],
        }
    )


# --- CSV real do repositório -------------------------------------------------
def test_csv_existe_com_30_por_grupo_e_sem_problemas():
    df = carregar_dados_reais(CAMINHO_DADOS_REAIS_PADRAO)
    q = validar_qualidade(df)
    assert q["n_por_grupo"] == {"sem_bot": 30, "com_bot": 30}
    assert q["ok"], q["problemas"]


def test_resumo_dos_dois_grupos_e_pooled():
    r = obter_resumo_estatistico_reais()
    assert r["sem_bot"].n == r["com_bot"].n == 30
    assert r["h0_pooled"]["n_total"] == 60
    for g in ("sem_bot", "com_bot"):
        assert r[g].assimetria > 0  # cauda à direita
        assert r[g].media > r[g].mediana
        assert r[g].log_sigma > 0


def test_salvar_estatisticas_gera_csv(tmp_path):
    saida = salvar_estatisticas(caminho_saida=tmp_path / "est.csv")
    out = pd.read_csv(saida)
    assert list(out["grupo"]) == ["sem_bot", "com_bot"]
    assert {"media", "mediana", "desvio_padrao", "minimo", "maximo", "n_outliers_iqr"} <= set(out.columns)


def test_relatorio_contem_secoes():
    txt = gerar_relatorio()
    assert "QUALIDADE DOS DADOS" in txt and "PARÂMETROS POOLED" in txt


# --- Estatísticas em dados conhecidos ----------------------------------------
def test_perfilar_grupo_valores_conhecidos():
    e = perfilar_grupo(_df_pequeno(), "sem_bot")
    assert e.n == 4
    assert e.media == pytest.approx(15.5)
    assert e.mediana == pytest.approx(6.0)
    assert e.minimo == 2 and e.maximo == 48
    assert e.desvio_padrao == pytest.approx(np.std([2, 4, 8, 48], ddof=1))
    assert e.log_mu == pytest.approx(np.mean(np.log([2, 4, 8, 48])))


def test_perfilar_grupo_inexistente():
    with pytest.raises(ValueError):
        perfilar_grupo(_df_pequeno(), "outro")


def test_outliers_iqr_detecta_valor_extremo():
    df = _df_pequeno()
    df.loc[3, "tempo_horas"] = 500
    out = detectar_outliers_iqr(df, "sem_bot")
    assert list(out["pr_id"]) == [4]


def test_estatisticas_para_dataframe_ordem():
    r = obter_resumo_estatistico_reais()
    assert list(estatisticas_para_dataframe(r)["grupo"]) == ["sem_bot", "com_bot"]


# --- Validação de qualidade --------------------------------------------------
def test_qualidade_ok_em_dados_limpos():
    assert validar_qualidade(_df_pequeno())["ok"]


def test_qualidade_detecta_ausente_duplicado_e_inconsistencia():
    df = _df_pequeno()
    df.loc[0, "tempo_horas"] = np.nan
    df.loc[1, "pr_id"] = 1  # duplicado
    df.loc[2, "tempo_horas"] = 99  # difere de merged_at - created_at
    df.loc[5, "bot_presente"] = False  # incoerente com grupo
    q = validar_qualidade(df)
    assert not q["ok"]
    assert q["ausentes"] == {"tempo_horas": 1}
    assert q["duplicados_pr_id"] == 1
    assert q["inconsistencia_tempo"] >= 1
    assert q["inconsistencia_bot"] == 1


def test_qualidade_detecta_merge_antes_da_criacao_e_tempo_nao_positivo():
    df = _df_pequeno()
    df.loc[0, "merged_at"] = "2024-05-31 00:00:00"
    df.loc[1, "tempo_horas"] = 0
    q = validar_qualidade(df)
    assert q["merge_antes_da_criacao"] == 1
    assert q["tempos_nao_positivos"] == 1


def test_carregar_arquivo_inexistente_e_colunas_faltando(tmp_path):
    with pytest.raises(FileNotFoundError):
        carregar_dados_reais(tmp_path / "nao_existe.csv")
    ruim = tmp_path / "ruim.csv"
    ruim.write_text("a,b\n1,2\n")
    with pytest.raises(ValueError):
        carregar_dados_reais(ruim)


# --- Coleta (funções puras, sem rede) ----------------------------------------
def _pr(n=1, autor="alice", tipo="User", criado="2024-06-01T10:00:00Z", mesclado="2024-06-01T12:30:00Z"):
    return {"number": n, "user": {"login": autor, "type": tipo}, "created_at": criado, "merged_at": mesclado}


def test_eh_bot():
    assert coleta.eh_bot({"login": "codecov[bot]", "type": "Bot"})
    assert coleta.eh_bot({"login": "x[bot]", "type": "User"})
    assert not coleta.eh_bot({"login": "alice", "type": "User"})
    assert not coleta.eh_bot(None)


def test_calcular_tempo_horas():
    assert coleta.calcular_tempo_horas("2024-06-01T10:00:00Z", "2024-06-01T12:30:00Z") == 2.5


def test_montar_registro_com_e_sem_bot():
    com = coleta.montar_registro("o/r", _pr(), [{"user": {"login": "codecov[bot]", "type": "Bot"}}])
    assert com["grupo"] == "com_bot" and com["bot_presente"] and com["nome_bot"] == "codecov[bot]"
    assert com["tempo_horas"] == 2.5
    sem = coleta.montar_registro("o/r", _pr(2), [{"user": {"login": "bob", "type": "User"}}])
    assert sem["grupo"] == "sem_bot" and sem["nome_bot"] == "nenhum"


def test_montar_registro_exclui_nao_elegiveis():
    assert coleta.montar_registro("o/r", _pr(autor="dependabot[bot]", tipo="Bot"), []) is None
    assert coleta.montar_registro("o/r", _pr(mesclado=None), []) is None
    assert coleta.montar_registro("o/r", _pr(mesclado="2024-06-01T10:00:00Z"), []) is None


def _registros(n_cada=40):
    regs = []
    for i in range(n_cada):
        for g in ("sem_bot", "com_bot"):
            regs.append({"pr_id": i * 2 + (g == "com_bot"), "repositorio": "o/r", "grupo": g,
                         "bot_presente": g == "com_bot", "nome_bot": "x[bot]" if g == "com_bot" else "nenhum",
                         "created_at": "2024-06-01 00:00:00", "merged_at": "2024-06-01 05:00:00", "tempo_horas": 5.0})
    return regs


def test_amostragem_reprodutivel_e_balanceada():
    a = coleta.amostrar_por_grupo(_registros(), n=30, seed=1)
    b = coleta.amostrar_por_grupo(_registros(), n=30, seed=1)
    c = coleta.amostrar_por_grupo(_registros(), n=30, seed=2)
    assert a.equals(b) and not a.equals(c)
    assert a["grupo"].value_counts().to_dict() == {"sem_bot": 30, "com_bot": 30}


def test_amostragem_falha_com_poucos_elegiveis():
    with pytest.raises(ValueError):
        coleta.amostrar_por_grupo(_registros(10), n=30)