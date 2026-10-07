"""Testes do cálculo das duas variantes de Lead Time e das medianas."""

from lab03.src.lead_time import (
    STATUS_COMPARACAO_INDISPONIVEL,
    STATUS_OK,
    STATUS_SEM_COMMITS,
    STATUS_SEM_DATA_COMMIT,
    STATUS_SEM_RELEASE_ANTERIOR,
    compute_release_lead_time,
    extract_commit_date,
    hours_between,
    median_or_none,
    summarize_repository,
)
from lab03.src.releases import CompareResult, parse_release
from lab03.tests.fakes import make_commit, make_release


def _rel(rid, tag, published):
    return parse_release(make_release(rid, tag, published))


def _compare(commits, total=None, truncated=False):
    return CompareResult(
        available=True,
        commits=commits,
        total_commits=len(commits) if total is None else total,
        truncated=truncated,
    )


PREV = _rel(1, "v1", "2024-04-01T00:00:00Z")
CUR = _rel(2, "v2", "2024-05-01T00:00:00Z")


def test_hours_between_e_mediana():
    assert hours_between(CUR.published_at, PREV.published_at) == 30 * 24
    assert median_or_none([3.0, 1.0, 2.0]) == 2.0
    assert median_or_none([1.0, 2.0, 3.0, 10.0]) == 2.5
    assert median_or_none([]) is None


def test_extract_commit_date_usa_author_e_nao_committer():
    commit = make_commit("a", "2024-04-10T00:00:00Z", committer_date="2024-04-25T00:00:00Z")
    assert extract_commit_date(commit).isoformat() == "2024-04-10T00:00:00+00:00"


def test_extract_commit_date_ausente_ou_invalida():
    assert extract_commit_date({}) is None
    assert extract_commit_date(None) is None
    assert extract_commit_date(make_commit("a", None)) is None
    assert extract_commit_date(make_commit("a", "nao-e-data")) is None


def test_lead_time_por_release_usa_commit_mais_antigo():
    commits = [
        make_commit("new", "2024-04-30T00:00:00Z"),
        make_commit("old", "2024-04-20T00:00:00Z"),  # 11 dias = 264 h
        make_commit("mid", "2024-04-25T00:00:00Z"),
    ]
    row, _ = compute_release_lead_time("o/r", CUR, PREV, _compare(commits), set())
    assert row.status == STATUS_OK
    assert row.commit_mais_antigo_sha == "old"
    assert row.lead_time_release_horas == 264.0
    assert row.release_anterior_tag == "v1"
    assert row.commits_coletados == 3


def test_lead_time_por_release_ignora_committer_date():
    # author em 04-20 (264 h); committer em 04-30 (24 h): vale o author
    commits = [make_commit("a", "2024-04-20T00:00:00Z", committer_date="2024-04-30T00:00:00Z")]
    row, _ = compute_release_lead_time("o/r", CUR, PREV, _compare(commits), set())
    assert row.lead_time_release_horas == 264.0


def test_lead_time_por_commit_um_por_commit():
    commits = [
        make_commit("c1", "2024-04-20T00:00:00Z"),  # 264 h
        make_commit("c2", "2024-04-30T00:00:00Z"),  # 24 h
        make_commit("c3", "2024-04-29T12:00:00Z"),  # 36 h
    ]
    _, rows = compute_release_lead_time("o/r", CUR, PREV, _compare(commits), set())
    assert {r.sha: r.lead_time_commit_horas for r in rows} == {"c1": 264.0, "c2": 24.0, "c3": 36.0}
    assert all(r.release_tag == "v2" for r in rows)


def test_sem_release_anterior():
    row, commits = compute_release_lead_time("o/r", CUR, None, None, set())
    assert row.status == STATUS_SEM_RELEASE_ANTERIOR
    assert row.lead_time_release_horas is None
    assert row.release_anterior_tag == ""
    assert commits == []


def test_comparacao_indisponivel_registra_motivo():
    cmp404 = CompareResult(available=False, error="comparacao_inexistente_404")
    row, commits = compute_release_lead_time("o/r", CUR, PREV, cmp404, set())
    assert row.status == STATUS_COMPARACAO_INDISPONIVEL
    assert row.observacao == "comparacao_inexistente_404"
    assert commits == []

    row, _ = compute_release_lead_time("o/r", CUR, PREV, None, set())
    assert row.status == STATUS_COMPARACAO_INDISPONIVEL


def test_releases_consecutivas_sem_commits():
    row, commits = compute_release_lead_time("o/r", CUR, PREV, _compare([]), set())
    assert row.status == STATUS_SEM_COMMITS
    assert row.lead_time_release_horas is None
    assert commits == []


def test_commits_sem_data_sao_contados_e_ignorados():
    commits = [make_commit("ok", "2024-04-30T00:00:00Z"), make_commit("sem", None)]
    row, rows = compute_release_lead_time("o/r", CUR, PREV, _compare(commits), set())
    assert row.status == STATUS_OK
    assert row.commits_sem_data == 1
    assert [r.sha for r in rows] == ["ok"]


def test_todos_commits_sem_data():
    row, rows = compute_release_lead_time("o/r", CUR, PREV, _compare([make_commit("x", None)]), set())
    assert row.status == STATUS_SEM_DATA_COMMIT
    assert row.commits_sem_data == 1
    assert rows == []


def test_comparacao_truncada_e_sinalizada():
    commits = [make_commit("a", "2024-04-30T00:00:00Z")]
    row, _ = compute_release_lead_time(
        "o/r", CUR, PREV, _compare(commits, total=300, truncated=True), set()
    )
    assert row.status == STATUS_OK
    assert row.comparacao_truncada
    assert row.total_commits_api == 300
    assert row.commits_coletados == 1
    assert "1 de 300" in row.observacao


def test_commit_repetido_entre_releases_conta_uma_vez_na_variante_por_commit():
    seen = set()
    shared = make_commit("shared", "2024-04-20T00:00:00Z")
    row1, rows1 = compute_release_lead_time("o/r", CUR, PREV, _compare([shared]), seen)
    nxt = _rel(3, "v3", "2024-06-01T00:00:00Z")
    row2, rows2 = compute_release_lead_time("o/r", nxt, CUR, _compare([shared]), seen)
    assert len(rows1) == 1
    assert rows2 == []
    assert row2.commits_duplicados_ignorados == 1
    # A variante por release continua usando todos os commits do intervalo
    assert row2.lead_time_release_horas == hours_between(nxt.published_at, shared_date())


def shared_date():
    return extract_commit_date(make_commit("s", "2024-04-20T00:00:00Z"))


def test_summarize_medianas_e_contagens_das_duas_variantes():
    seen = set()
    c1 = [make_commit("a", "2024-03-25T00:00:00Z"), make_commit("b", "2024-03-30T12:00:00Z")]
    c2 = [make_commit("c", "2024-04-20T00:00:00Z"), make_commit("d", "2024-04-30T00:00:00Z")]
    r1 = _rel(1, "v1", "2024-03-10T00:00:00Z")
    r2 = _rel(2, "v2", "2024-04-01T00:00:00Z")
    r3 = _rel(3, "v3", "2024-05-01T00:00:00Z")
    r4 = _rel(4, "v4", "2024-06-01T00:00:00Z")
    rows, commits = [], []
    for rel, prev, cmp_ in [
        (r1, None, None),
        (r2, r1, _compare(c1)),  # release: 168 h | commits: 168 h e 36 h
        (r3, r2, _compare(c2)),  # release: 264 h | commits: 264 h e 24 h
        (r4, r3, _compare([])),  # sem commits
    ]:
        row, cr = compute_release_lead_time("o/r", rel, prev, cmp_, seen)
        rows.append(row)
        commits.extend(cr)

    s = summarize_repository("o/r", rows, commits)
    assert s.releases_na_janela == 4
    assert s.releases_calculadas == 2
    assert s.commits_usados == 4
    assert s.releases_sem_release_anterior == 1
    assert s.releases_sem_commits == 1
    assert s.releases_comparacao_indisponivel == 0
    assert s.mediana_lead_time_release_horas == 216.0  # mediana de [168, 264]
    assert s.mediana_lead_time_commit_horas == 102.0  # mediana de [24, 36, 168, 264]
    # as duas variantes têm n de observações diferentes e permanecem separadas
    assert s.releases_calculadas != s.commits_usados


def test_summarize_sem_dados_mantem_repositorio():
    s = summarize_repository("o/r", [], [])
    assert s.releases_na_janela == 0
    assert s.mediana_lead_time_release_horas is None
    assert s.mediana_lead_time_commit_horas is None


def test_summarize_conta_indisponiveis_truncadas_e_sem_data():
    rows = []
    r, _ = compute_release_lead_time("o/r", CUR, PREV, CompareResult(available=False, error="x"), set())
    rows.append(r)
    r, _ = compute_release_lead_time(
        "o/r", CUR, PREV, _compare([make_commit("a", "2024-04-30T00:00:00Z")], total=999, truncated=True), set()
    )
    rows.append(r)
    r, _ = compute_release_lead_time("o/r", CUR, PREV, _compare([make_commit("a", None)]), set())
    rows.append(r)
    s = summarize_repository("o/r", rows, [])
    assert s.releases_comparacao_indisponivel == 1
    assert s.releases_truncadas == 1
    assert s.releases_sem_data_commit == 1
    assert s.commits_sem_data == 1
