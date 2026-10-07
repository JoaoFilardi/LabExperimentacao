"""Testes da coleta de releases e de commits entre releases."""

from lab03.src.releases import (
    MAX_COMPARE_COMMITS,
    build_release_pairs,
    fetch_commits_between,
    fetch_valid_releases,
    parse_release,
)
from lab03.tests.fakes import FakeClient, make_commit, make_compare_page, make_release


def _commits(n, prefix="c", date="2024-04-10T00:00:00Z"):
    return [make_commit(f"{prefix}{i:04d}", date) for i in range(n)]


# ---------------------------------------------------------------- releases


def test_parse_release_valida():
    rel = parse_release(make_release(1, "v1.0", "2024-04-01T10:00:00Z"))
    assert rel is not None
    assert rel.release_id == 1
    assert rel.tag_name == "v1.0"
    assert rel.name == "Release v1.0"
    assert rel.published_at.isoformat() == "2024-04-01T10:00:00+00:00"


def test_parse_release_descarta_draft():
    assert parse_release(make_release(1, "v1", "2024-04-01T10:00:00Z", draft=True)) is None


def test_parse_release_descarta_prerelease():
    assert parse_release(make_release(1, "v1", "2024-04-01T10:00:00Z", prerelease=True)) is None


def test_parse_release_descarta_sem_published_at_ou_tag():
    assert parse_release(make_release(1, "v1", None)) is None
    assert parse_release(make_release(1, "", "2024-04-01T10:00:00Z")) is None
    assert parse_release(make_release(1, "v1", "data-invalida")) is None
    assert parse_release("nao e dict") is None


def test_parse_release_usa_tag_quando_nome_vazio():
    rel = parse_release(make_release(1, "v1", "2024-04-01T10:00:00Z", name=""))
    assert rel.name == "v1"


def test_fetch_valid_releases_filtra_e_ordena():
    client = FakeClient(
        releases=[
            make_release(3, "v3", "2024-06-01T00:00:00Z"),
            make_release(9, "v9-draft", "2024-07-01T00:00:00Z", draft=True),
            make_release(1, "v1", "2024-04-01T00:00:00Z"),
            make_release(8, "v8-rc", "2024-05-15T00:00:00Z", prerelease=True),
            make_release(2, "v2", "2024-05-01T00:00:00Z"),
            make_release(2, "v2", "2024-05-01T00:00:00Z"),  # duplicada
        ]
    )
    releases = fetch_valid_releases(client, "o", "r")
    assert [r.tag_name for r in releases] == ["v1", "v2", "v3"]
    call = client.calls[0]
    assert call["endpoint"] == "repos/o/r/releases"
    assert call["cache_category"] == "releases"  # camada de cache compartilhada
    assert call["cache_key_prefix"] == "releases_o_r"


def test_build_release_pairs_respeita_janela(sample_window_config):
    client = FakeClient(
        releases=[
            make_release(1, "v1", "2023-01-01T00:00:00Z"),  # antes da janela
            make_release(2, "v2", "2024-04-01T00:00:00Z"),
            make_release(3, "v3", "2024-05-01T00:00:00Z"),
            make_release(4, "v4", "2025-06-01T00:00:00Z"),  # depois da janela
        ]
    )
    pairs = build_release_pairs(fetch_valid_releases(client, "o", "r"), sample_window_config)
    assert [(r.tag_name, p.tag_name if p else None) for r, p in pairs] == [
        ("v2", "v1"),  # anterior fora da janela é usada como base
        ("v3", "v2"),
    ]


def test_build_release_pairs_sem_release_anterior(sample_window_config):
    client = FakeClient(releases=[make_release(1, "v1", "2024-04-01T00:00:00Z")])
    pairs = build_release_pairs(fetch_valid_releases(client, "o", "r"), sample_window_config)
    assert len(pairs) == 1
    assert pairs[0][0].tag_name == "v1"
    assert pairs[0][1] is None


def test_build_release_pairs_todas_fora_da_janela(sample_window_config):
    client = FakeClient(releases=[make_release(1, "v1", "2020-01-01T00:00:00Z")])
    assert build_release_pairs(fetch_valid_releases(client, "o", "r"), sample_window_config) == []


# ----------------------------------------------------------------- compare


def test_compare_pagina_unica():
    key = ("v1", "v2")
    client = FakeClient(compares={key: [make_compare_page(_commits(3))]})
    result = fetch_commits_between(client, "o", "r", "v1", "v2")
    assert result.available
    assert len(result.commits) == 3
    assert result.total_commits == 3
    assert not result.truncated
    call = client.calls[0]
    assert call["endpoint"] == "repos/o/r/compare/v1...v2"
    assert call["cache_category"] == "compare"


def test_compare_com_paginacao_junta_paginas():
    pages = [
        make_compare_page(_commits(100, "a"), total_commits=250),
        make_compare_page(_commits(100, "b"), total_commits=250),
        make_compare_page(_commits(50, "c"), total_commits=250),
    ]
    client = FakeClient(compares={("v1", "v2"): pages})
    result = fetch_commits_between(client, "o", "r", "v1", "v2")
    assert len(result.commits) == 250
    assert result.total_commits == 250
    assert not result.truncated  # exatamente no limite de 250: nada perdido


def test_compare_mais_de_250_commits_marca_truncada():
    pages = [
        make_compare_page(_commits(100, "a"), total_commits=420),
        make_compare_page(_commits(100, "b"), total_commits=420),
        make_compare_page(_commits(50, "c"), total_commits=420),
    ]
    client = FakeClient(compares={("v1", "v2"): pages})
    result = fetch_commits_between(client, "o", "r", "v1", "v2")
    assert MAX_COMPARE_COMMITS == 250
    assert len(result.commits) == 250
    assert result.total_commits == 420
    assert result.truncated


def test_compare_ignora_sha_repetido_entre_paginas():
    pages = [
        make_compare_page([make_commit("x1", "2024-04-01T00:00:00Z")], total_commits=2),
        make_compare_page(
            [make_commit("x1", "2024-04-01T00:00:00Z"), make_commit("x2", "2024-04-02T00:00:00Z")],
            total_commits=2,
        ),
    ]
    client = FakeClient(compares={("v1", "v2"): pages})
    result = fetch_commits_between(client, "o", "r", "v1", "v2")
    assert [c["sha"] for c in result.commits] == ["x1", "x2"]
    assert not result.truncated


def test_compare_404_indisponivel():
    client = FakeClient(compares={})  # [] = 404 no client
    result = fetch_commits_between(client, "o", "r", "v1", "v2")
    assert not result.available
    assert result.commits == []
    assert "404" in result.error


def test_compare_falha_do_client_nao_propaga():
    client = FakeClient(fail_compares=(("v1", "v2"),))
    result = fetch_commits_between(client, "o", "r", "v1", "v2")
    assert not result.available
    assert "falha persistente" in result.error


def test_compare_total_ausente_usa_quantidade_retornada():
    page = {"commits": _commits(2)}  # sem total_commits
    client = FakeClient(compares={("v1", "v2"): [page]})
    result = fetch_commits_between(client, "o", "r", "v1", "v2")
    assert result.total_commits == 2
    assert not result.truncated


def test_compare_codifica_tags_especiais():
    client = FakeClient(compares={("rel/1.0+b", "rel/1.1"): [make_compare_page(_commits(1))]})
    result = fetch_commits_between(client, "o", "r", "rel/1.0+b", "rel/1.1")
    assert result.available
    assert client.calls[0]["endpoint"] == "repos/o/r/compare/rel/1.0%2Bb...rel/1.1"
