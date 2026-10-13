"""Testes automatizados de validação e integridade da Amostra-Ouro (LAB03S02).

Valida a integridade do sorteio reproduzível dos 60 repositórios, a completude
das 300 avaliações de releases, o vocabulário controlado das três dimensões
e a consistência e independência dos dados preenchidos pelos avaliadores João e Tiago.
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd
import pytest

from lab03.src.gerar_amostra_ouro import (
    REPOSITORIOS_AMOSTRA_OURO,
    SEED,
    build_gold_sample_base,
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CSV_BASE_PATH = DATA_DIR / "amostra_ouro_base.csv"
CSV_JOAO_PATH = DATA_DIR / "rotulagem_amostra_ouro_joao.csv"
CSV_TIAGO_PATH = DATA_DIR / "rotulagem_amostra_ouro_tiago.csv"

COLUNAS_ESPERADAS = [
    "repo_id",
    "full_name",
    "repo_url",
    "primary_language",
    "release_num",
    "tag_name",
    "release_name",
    "published_at",
    "release_url",
    "tipo_projeto",
    "entrega_real",
    "is_corretiva",
    "justificativa",
]

VALORES_TIPO_PROJETO = {
    "biblioteca/framework",
    "aplicação/serviço",
    "CLI",
    "outro",
}

VALORES_ENTREGA_REAL = {
    "sim",
    "não",
    "incerto",
}

VALORES_IS_CORRETIVA = {
    "sim",
    "não",
}


@pytest.fixture(scope="module")
def df_amostra_base() -> pd.DataFrame:
    """Carrega o DataFrame base gerado deterministicamente."""
    assert CSV_BASE_PATH.exists(), f"Arquivo não encontrado: {CSV_BASE_PATH}"
    df = pd.read_csv(CSV_BASE_PATH, encoding="utf-8")
    return df


@pytest.fixture(scope="module")
def df_rotulagem_joao() -> pd.DataFrame:
    """Carrega o DataFrame com as rotulações de João."""
    assert CSV_JOAO_PATH.exists(), f"Arquivo não encontrado: {CSV_JOAO_PATH}"
    df = pd.read_csv(CSV_JOAO_PATH, encoding="utf-8")
    return df


@pytest.fixture(scope="module")
def df_rotulagem_tiago() -> pd.DataFrame:
    """Carrega o DataFrame com as rotulações de Tiago."""
    assert CSV_TIAGO_PATH.exists(), f"Arquivo não encontrado: {CSV_TIAGO_PATH}"
    df = pd.read_csv(CSV_TIAGO_PATH, encoding="utf-8")
    return df


def test_arquivos_amostra_ouro_existem():
    """Garante que a base e as rotulagens de João e Tiago estão no diretório lab03/data."""
    assert CSV_BASE_PATH.exists(), "amostra_ouro_base.csv não encontrado"
    assert CSV_JOAO_PATH.exists(), "rotulagem_amostra_ouro_joao.csv não encontrado"
    assert CSV_TIAGO_PATH.exists(), "rotulagem_amostra_ouro_tiago.csv não encontrado"


# -------------------------------------------------------------------------
# Testes da Rotulagem de João
# -------------------------------------------------------------------------

def test_estrutura_colunas(df_rotulagem_joao: pd.DataFrame):
    """Verifica se todas as colunas obrigatórias estão presentes e na ordem esperada."""
    assert list(df_rotulagem_joao.columns) == COLUNAS_ESPERADAS


def test_contagem_total_linhas_e_repositorios(df_rotulagem_joao: pd.DataFrame):
    """Garante que a amostra-ouro possui exatamente 300 linhas (60 repositórios x 5 releases)."""
    assert len(df_rotulagem_joao) == 300, f"Esperado 300 linhas, obtido {len(df_rotulagem_joao)}"
    
    unique_repos = df_rotulagem_joao["full_name"].nunique()
    assert unique_repos == 60, f"Esperado 60 repositórios únicos, obtido {unique_repos}"
    
    unique_ids = df_rotulagem_joao["repo_id"].nunique()
    assert unique_ids == 60, f"Esperado 60 IDs únicos, obtido {unique_ids}"
    assert sorted(df_rotulagem_joao["repo_id"].unique()) == list(range(1, 61))


def test_exatamente_5_releases_por_repositorio(df_rotulagem_joao: pd.DataFrame):
    """Garante que cada repositório possui exatamente 5 releases indexadas de 1 a 5."""
    contagem_por_repo = df_rotulagem_joao.groupby("full_name")["release_num"].apply(list)
    for repo, releases in contagem_por_repo.items():
        assert len(releases) == 5, f"Repositório {repo} não tem 5 releases: {releases}"
        assert sorted(releases) == [1, 2, 3, 4, 5], f"Repositório {repo} com numeração inválida: {releases}"


def test_vocabulario_tipo_projeto(df_rotulagem_joao: pd.DataFrame):
    """Garante adesão estrita ao vocabulário controlado para tipo_projeto."""
    valores_obtidos = set(df_rotulagem_joao["tipo_projeto"].unique())
    invalidos = valores_obtidos - VALORES_TIPO_PROJETO
    assert not invalidos, f"Valores não permitidos em tipo_projeto: {invalidos}"
    assert "biblioteca/framework" in valores_obtidos
    assert "aplicação/serviço" in valores_obtidos
    assert "CLI" in valores_obtidos
    assert "outro" in valores_obtidos


def test_vocabulario_entrega_real(df_rotulagem_joao: pd.DataFrame):
    """Garante adesão estrita ao vocabulário controlado para entrega_real."""
    valores_obtidos = set(df_rotulagem_joao["entrega_real"].unique())
    invalidos = valores_obtidos - VALORES_ENTREGA_REAL
    assert not invalidos, f"Valores não permitidos em entrega_real: {invalidos}"
    assert "sim" in valores_obtidos


def test_vocabulario_is_corretiva(df_rotulagem_joao: pd.DataFrame):
    """Garante adesão estrita ao vocabulário controlado para is_corretiva."""
    valores_obtidos = set(df_rotulagem_joao["is_corretiva"].unique())
    invalidos = valores_obtidos - VALORES_IS_CORRETIVA
    assert not invalidos, f"Valores não permitidos em is_corretiva: {invalidos}"
    assert "sim" in valores_obtidos
    assert "não" in valores_obtidos


def test_sem_valores_nulos_ou_vazios(df_rotulagem_joao: pd.DataFrame):
    """Garante que não existem valores nulos (NaN) ou strings compostas só de espaços."""
    assert df_rotulagem_joao.isna().sum().sum() == 0, "Encontrados valores NaN no dataframe"

    for col in ["full_name", "repo_url", "primary_language", "tag_name", "release_url", "justificativa"]:
        empty_mask = df_rotulagem_joao[col].astype(str).str.strip() == ""
        assert not empty_mask.any(), f"Coluna {col} contém valores vazios ou em branco"


def test_integridade_urls_github(df_rotulagem_joao: pd.DataFrame):
    """Verifica formato das URLs dos repositórios e das releases."""
    for _, row in df_rotulagem_joao.iterrows():
        assert row["repo_url"].startswith("https://github.com/"), f"URL inválida: {row['repo_url']}"
        assert row["release_url"].startswith(f"https://github.com/{row['full_name']}/releases/tag/"), (
            f"Release URL incorreta para {row['full_name']}: {row['release_url']}"
        )


def test_consistencia_atributos_por_repositorio(df_rotulagem_joao: pd.DataFrame):
    """Garante que tipo_projeto e entrega_real são invariantes para o mesmo repositório."""
    tipo_divergencias = df_rotulagem_joao.groupby("full_name")["tipo_projeto"].nunique()
    assert (tipo_divergencias == 1).all(), "tipo_projeto diverge entre releases do mesmo repositório"

    entrega_divergencias = df_rotulagem_joao.groupby("full_name")["entrega_real"].nunique()
    assert (entrega_divergencias == 1).all(), "entrega_real diverge entre releases do mesmo repositório"


def test_alinhamento_entre_base_e_rotulagem(df_amostra_base: pd.DataFrame, df_rotulagem_joao: pd.DataFrame):
    """Garante que a rotulagem de João preservou perfeitamente as chaves e metadados da base."""
    cols_base = [
        "repo_id",
        "full_name",
        "repo_url",
        "primary_language",
        "release_num",
        "tag_name",
        "release_name",
        "published_at",
        "release_url",
    ]
    pd.testing.assert_frame_equal(df_amostra_base[cols_base], df_rotulagem_joao[cols_base])


# -------------------------------------------------------------------------
# Testes da Rotulagem Independente de Tiago
# -------------------------------------------------------------------------

def test_estrutura_colunas_tiago(df_rotulagem_tiago: pd.DataFrame):
    """Verifica se todas as colunas obrigatórias estão presentes na rotulagem de Tiago."""
    assert list(df_rotulagem_tiago.columns) == COLUNAS_ESPERADAS


def test_contagem_total_linhas_e_repositorios_tiago(df_rotulagem_tiago: pd.DataFrame):
    """Garante exatamente 300 linhas e 60 repositórios únicos na rotulagem de Tiago."""
    assert len(df_rotulagem_tiago) == 300, f"Esperado 300 linhas, obtido {len(df_rotulagem_tiago)}"
    assert df_rotulagem_tiago["full_name"].nunique() == 60
    assert df_rotulagem_tiago["repo_id"].nunique() == 60
    assert sorted(df_rotulagem_tiago["repo_id"].unique()) == list(range(1, 61))


def test_exatamente_5_releases_por_repositorio_tiago(df_rotulagem_tiago: pd.DataFrame):
    """Garante que cada repositório possui exatamente 5 releases indexadas de 1 a 5 na rotulagem de Tiago."""
    contagem_por_repo = df_rotulagem_tiago.groupby("full_name")["release_num"].apply(list)
    for repo, releases in contagem_por_repo.items():
        assert len(releases) == 5, f"Repositório {repo} não tem 5 releases: {releases}"
        assert sorted(releases) == [1, 2, 3, 4, 5]


def test_vocabulario_tipo_projeto_tiago(df_rotulagem_tiago: pd.DataFrame):
    """Garante adesão estrita ao vocabulário de tipo_projeto por Tiago."""
    valores_obtidos = set(df_rotulagem_tiago["tipo_projeto"].unique())
    invalidos = valores_obtidos - VALORES_TIPO_PROJETO
    assert not invalidos, f"Valores não permitidos em tipo_projeto: {invalidos}"
    assert "biblioteca/framework" in valores_obtidos
    assert "aplicação/serviço" in valores_obtidos
    assert "CLI" in valores_obtidos
    assert "outro" in valores_obtidos


def test_vocabulario_entrega_real_tiago(df_rotulagem_tiago: pd.DataFrame):
    """Garante adesão estrita ao vocabulário de entrega_real por Tiago."""
    valores_obtidos = set(df_rotulagem_tiago["entrega_real"].unique())
    invalidos = valores_obtidos - VALORES_ENTREGA_REAL
    assert not invalidos, f"Valores não permitidos em entrega_real: {invalidos}"
    assert "sim" in valores_obtidos
    assert "não" in valores_obtidos


def test_vocabulario_is_corretiva_tiago(df_rotulagem_tiago: pd.DataFrame):
    """Garante adesão estrita ao vocabulário de is_corretiva por Tiago."""
    valores_obtidos = set(df_rotulagem_tiago["is_corretiva"].unique())
    invalidos = valores_obtidos - VALORES_IS_CORRETIVA
    assert not invalidos, f"Valores não permitidos em is_corretiva: {invalidos}"
    assert "sim" in valores_obtidos
    assert "não" in valores_obtidos


def test_sem_valores_nulos_ou_vazios_tiago(df_rotulagem_tiago: pd.DataFrame):
    """Garante que a rotulagem de Tiago não contém NaN ou strings em branco."""
    assert df_rotulagem_tiago.isna().sum().sum() == 0, "Encontrados valores NaN na rotulagem de Tiago"

    for col in ["full_name", "repo_url", "primary_language", "tag_name", "release_url", "justificativa"]:
        empty_mask = df_rotulagem_tiago[col].astype(str).str.strip() == ""
        assert not empty_mask.any(), f"Coluna {col} contém valores vazios na rotulagem de Tiago"


def test_consistencia_atributos_por_repositorio_tiago(df_rotulagem_tiago: pd.DataFrame):
    """Garante invariância de tipo_projeto e entrega_real por repositório na rotulagem de Tiago."""
    tipo_div = df_rotulagem_tiago.groupby("full_name")["tipo_projeto"].nunique()
    assert (tipo_div == 1).all(), "tipo_projeto diverge entre releases do mesmo repositório"

    entrega_div = df_rotulagem_tiago.groupby("full_name")["entrega_real"].nunique()
    assert (entrega_div == 1).all(), "entrega_real diverge entre releases do mesmo repositório"


def test_alinhamento_entre_base_e_rotulagem_tiago(
    df_amostra_base: pd.DataFrame,
    df_rotulagem_tiago: pd.DataFrame,
):
    """Garante alinhamento perfeito entre as chaves da base e a rotulagem de Tiago."""
    cols_base = [
        "repo_id",
        "full_name",
        "repo_url",
        "primary_language",
        "release_num",
        "tag_name",
        "release_name",
        "published_at",
        "release_url",
    ]
    pd.testing.assert_frame_equal(df_amostra_base[cols_base], df_rotulagem_tiago[cols_base])


def test_independencia_rotulagem_joao_tiago(
    df_rotulagem_joao: pd.DataFrame,
    df_rotulagem_tiago: pd.DataFrame,
):
    """Verifica que a rotulagem de Tiago é independente e não uma cópia idêntica da de João."""
    # As justificativas foram formuladas de maneira independente
    assert not (df_rotulagem_joao["justificativa"] == df_rotulagem_tiago["justificativa"]).all(), (
        "As justificativas são idênticas, indicando dependência indevida entre avaliadores"
    )


# -------------------------------------------------------------------------
# Teste de Reprodutibilidade da Amostra-Ouro
# -------------------------------------------------------------------------

def test_reprodutibilidade_gerador_amostra_ouro():
    """Garante que o gerador reproduz fielmente as 300 releases com semente 42."""
    df_gerado_1 = build_gold_sample_base(random_state=SEED)
    df_gerado_2 = build_gold_sample_base(random_state=SEED)

    assert df_gerado_1.equals(df_gerado_2), "Gerador não é determinístico para a mesma semente"
    assert len(df_gerado_1) == 300
    assert len(REPOSITORIOS_AMOSTRA_OURO) == 60
