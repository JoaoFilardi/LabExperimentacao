"""Testes da orquestração, integração com o pipeline e exportação."""

import csv

import pandas as pd

from lab03.src.coleta_lead_time import (
    COMMITS_CSV,
    RELEASES_CSV,
    SUMMARY_CSV,
    collect_repositories,
    collect_repository,
    export_results,
    load_selected_repositories,
    run_lead_time_collection,
)
from lab03.tests.fakes import FakeClient, make_commit, make_compare_page, make_release


def _client_cenario():
    """Janela: 2024-03-01 a 2025-02-28.

    v1.0 (2024-02-01) fora da janela, serve de base para v1.1.
    """
    releases = [
        make_release(1, "v1.0", "2024-02-01T00:00:00Z"),
        make_release(2, "v1.1", "2024-04-01T00:00:00Z"),
        make_release(3, "v1.2", "2024-05-01T00:00:00Z"),
        make_release(4, "v1.3", "2024-06-01T00:00:00Z"),
        make_release(5, "v2.0-rc", "2024-06-15T00:00:00Z", prerelease=True),
        make_release(6, "v2.0-draft", "2024-06-20T00:00:00Z", draft=True),
        make_release(7, "v0.1", "2023-01-01T00:00:00Z"),  # fora da janela
    ]
    compares = {
        ("v1.0", "v1.1"): [
            make_compare_page(
                [
                    make_commit("a1", "2024-03-25T00:00:00Z", committer_date="2024-03-31T00:00:00Z"),
                    make_commit("a2", "2024-03-30T12:00:00Z"),
                ]
            )
        ],
        ("v1.1", "v1.2"): [
            make_compare_page(
                [make_commit("b1", "2024-04-20T00:00:00Z"), make_commit("b2", "2024-04-30T00:00:00Z")]
            )
        ],
        ("v1.2", "v1.3"): [make_compare_page([])],  # releases consecutivas sem commits
    }
    return FakeClient(releases=releases, compares=compares)


def test_collect_repository_fim_a_fim(sample_config):
    result = collect_repository(_client_cenario(), "o", "r", sample_config)
    s = result.summary
    assert s.repo == "o/r"
    assert s.releases_na_janela == 3  # v1.1, v1.2, v1.3
    assert s.releases_calculadas == 2
    assert s.commits_usados == 4
    assert s.releases_sem_commits == 1
    assert s.releases_sem_release_anterior == 0
    assert s.mediana_lead_time_release_horas == 216.0
    assert s.mediana_lead_time_commit_horas == 102.0
    assert [r.tag_name for r in result.releases] == ["v1.1", "v1.2", "v1.3"]
    assert {c.sha for c in result.commits} == {"a1", "a2", "b1", "b2"}


def test_collect_repository_sem_release_anterior_mantem_repositorio(sample_config):
    client = FakeClient(releases=[make_release(1, "v1", "2024-04-01T00:00:00Z")])
    result = collect_repository(client, "o", "r", sample_config)
    assert result.summary.releases_na_janela == 1
    assert result.summary.releases_sem_release_anterior == 1
    assert result.summary.releases_calculadas == 0
    assert result.summary.mediana_lead_time_release_horas is None
    assert not result.summary.erro


def test_collect_repository_comparacao_404_nao_derruba_repositorio(sample_config):
    client = FakeClient(
        releases=[
            make_release(1, "v1", "2024-04-01T00:00:00Z"),
            make_release(2, "v2", "2024-05-01T00:00:00Z"),
        ]
    )  # sem compares => 404
    result = collect_repository(client, "o", "r", sample_config)
    assert result.summary.releases_comparacao_indisponivel == 1
    assert result.summary.releases_sem_release_anterior == 1


def test_collect_repository_falha_ao_listar_releases(sample_config):
    client = FakeClient(fail_releases=True)
    result = collect_repository(client, "o", "r", sample_config)
    assert "falha persistente" in result.summary.erro
    assert result.releases == []


def test_collect_repositories_processa_varios_repos_de_forma_independente(sample_config):
    client = _client_cenario()
    results = collect_repositories(client, [("o", "r"), ("o", "r")], sample_config)
    assert len(results) == 2
    # seen_shas é por repositório: o segundo repo não perde commits do primeiro
    assert results[1].summary.commits_usados == 4


def test_load_selected_repositories(tmp_path):
    path = tmp_path / "sel.csv"
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["owner", "name", "full_name"])
        w.writerow(["react", "react", "react/react"])
        w.writerow(["", "sem-owner", "x"])
        w.writerow(["n8n-io", "n8n", "n8n-io/n8n"])
    assert load_selected_repositories(path) == [("react", "react"), ("n8n-io", "n8n")]


def test_export_results_gera_tres_csvs(sample_config, tmp_path):
    result = collect_repository(_client_cenario(), "o", "r", sample_config)
    out = tmp_path / "saida"
    releases_p, commits_p, summary_p = export_results([result], out)
    assert releases_p.name == RELEASES_CSV
    assert commits_p.name == COMMITS_CSV
    assert summary_p.name == SUMMARY_CSV

    releases = pd.read_csv(releases_p)
    commits = pd.read_csv(commits_p)
    summary = pd.read_csv(summary_p)
    assert len(releases) == 3
    assert len(commits) == 4
    assert summary.loc[0, "mediana_lead_time_release_horas"] == 216.0
    assert summary.loc[0, "mediana_lead_time_commit_horas"] == 102.0
    assert set(releases["status"]) == {"OK", "SEM_COMMITS"}


def test_export_results_vazio_mantem_cabecalhos(tmp_path):
    releases_p, commits_p, summary_p = export_results([], tmp_path)
    assert "repo" in pd.read_csv(releases_p).columns
    assert "sha" in pd.read_csv(commits_p).columns
    assert len(pd.read_csv(summary_p)) == 0


def test_run_lead_time_collection_com_lista_e_limite(sample_config):
    results = run_lead_time_collection(
        sample_config,
        client=_client_cenario(),
        repositories=[("o", "r"), ("o", "r")],
        limit=1,
    )
    assert len(results) == 1
    assert (sample_config.output.data_dir / SUMMARY_CSV).is_file()
