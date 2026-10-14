import pandas as pd
import pytest

from lab03.src.validar_rotulagem import validar


def _df_valido() -> pd.DataFrame:
    linhas = []
    for repo_id in range(1, 61):
        for num in range(1, 6):
            linhas.append({
                "repo_id": repo_id,
                "full_name": f"org/repo{repo_id}",
                "repo_url": f"https://github.com/org/repo{repo_id}",
                "primary_language": "Python",
                "release_num": num,
                "tag_name": f"v1.{num}.0",
                "release_name": f"v1.{num}.0",
                "published_at": "2025-01-01T00:00:00Z",
                "release_url": f"https://github.com/org/repo{repo_id}/releases/tag/v1.{num}.0",
                "tipo_projeto": "CLI",
                "entrega_real": "sim",
                "is_corretiva": "não",
                "justificativa": "",
            })
    return pd.DataFrame(linhas)


def test_arquivo_valido():
    df = _df_valido()
    assert validar(df, base=df.copy()) == []


def test_celula_vazia():
    df = _df_valido()
    df.loc[0, "is_corretiva"] = ""
    assert any("is_corretiva" in e and "vazias" in e for e in validar(df))


def test_valor_fora_do_vocabulario():
    df = _df_valido()
    df.loc[0, "tipo_projeto"] = "biblioteca"
    assert any("fora do vocabulário" in e for e in validar(df))


def test_tipo_varia_dentro_do_repositorio():
    df = _df_valido()
    df.loc[0, "tipo_projeto"] = "outro"
    assert any("mesmo repositório" in e for e in validar(df))


def test_linhas_faltando():
    df = _df_valido().iloc[:-1]
    assert any("Esperadas 300" in e for e in validar(df))


def test_incerto_exige_justificativa():
    df = _df_valido()
    df.loc[df["repo_id"] == 1, "entrega_real"] = "incerto"
    assert any("sem justificativa" in e for e in validar(df))


def test_amostra_diferente_da_base():
    df = _df_valido()
    base = df.copy()
    df.loc[0, "tag_name"] = "v9.9.9"
    assert any("mesma amostra" in e for e in validar(df, base))


def test_coluna_ausente():
    df = _df_valido().drop(columns=["justificativa"])
    assert validar(df) == ["Colunas ausentes: ['justificativa']"]