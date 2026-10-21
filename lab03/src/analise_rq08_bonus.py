"""Bônus RQ08, opção A: Deployment rework rate (LAB03S03).

Fórmula (por repositório, dentro da janela de observação do config.yaml):

    rework_rate = releases corretivas / releases válidas na janela

- Release válida: draft=false e prerelease=false (mesmo critério de releases.py).
- Release corretiva: classificação da heurística validada na S02
  (heuristica_corretiva.py, versão v1_palavras_chave por padrão: F1 = 0,8764 >= 0,70).

Comparação com o CFR da variante (b) (cfr_delivery_proxy do metricas_dora.csv):

    CFR(b) = releases seguidas por release corretiva em até 7 dias / releases avaliadas
    (releases dos últimos 7 dias da janela são censuradas e saem do denominador)

O rework rate conta a release que CORRIGE; o CFR(b) conta a release que FALHOU.
Para auditar a consistência, o CFR(b) é recalculado aqui a partir das mesmas releases
e confrontado com o valor do CSV (colunas `cfr_confere` e `contagem_confere`).

Uso (a partir da raiz do repositório):
    python -m lab03.src.analise_rq08_bonus --coletar   # baixa/lê do cache as releases e salva o CSV
    python -m lab03.src.analise_rq08_bonus             # roda a análise a partir do CSV versionado
"""

from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from .heuristica_corretiva import HEURISTICAS

logger = logging.getLogger(__name__)

VERSAO_HEURISTICA_PADRAO = "v1_palavras_chave"
JANELA_CFR_DIAS = 7
TOLERANCIA_CFR_CSV = 1e-3  # o CSV guarda o CFR com 4 casas decimais

DATA_DIR = Path("lab03/data")
CONFIG_PATH = Path("lab03/config.yaml")
METRICAS_CSV = DATA_DIR / "metricas_dora.csv"
RELEASES_CSV = DATA_DIR / "releases_rework.csv.gz"  # .gz: o CSV puro passa de 100 MB (limite do GitHub)
FIGURAS_DIR = DATA_DIR / "figuras"

_SEMVER = re.compile(r"(\d+)\.(\d+)\.(\d+)")


def semver_patch(row: pd.Series) -> str:
    """Classificador alternativo: bump de patch (x.y.Z, Z > 0) na tag => corretiva.

    Limitação: versionamento por calendário (ex.: 2026.1.5) gera falsos positivos.
    """
    m = _SEMVER.search(str(row.get("tag_name", "")))
    return "sim" if m and int(m.group(3)) > 0 else "não"


CLASSIFICADORES = {**HEURISTICAS, "semver_patch": semver_patch}

COLUNAS_RELEASES = ["full_name", "release_id", "tag_name", "release_name", "release_body", "published_at"]


# ---------------------------------------------------------------------------
# Janela e coleta
# ---------------------------------------------------------------------------
def _utc(valor) -> pd.Timestamp:
    ts = pd.Timestamp(valor)
    return ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")


def carregar_janela(config_path: Path = CONFIG_PATH) -> Tuple[pd.Timestamp, pd.Timestamp]:
    """Lê window.start_date / window.end_date do config.yaml."""
    import yaml

    from .config import parse_iso_datetime

    with open(config_path, encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    janela = cfg["window"]
    return _utc(parse_iso_datetime(janela["start_date"])), _utc(parse_iso_datetime(janela["end_date"]))


def _criar_client():
    """Instancia o GitHubClient compartilhado (ajuste se o construtor exigir argumentos)."""
    from .github_client import GitHubClient

    return GitHubClient()


def coletar_releases_repo(client, full_name: str) -> pd.DataFrame:
    """Releases válidas de um repositório, incluindo o corpo (release_body).

    Usa o mesmo endpoint, parâmetros e cache_key_prefix de releases.fetch_valid_releases,
    portanto reaproveita as páginas já guardadas em lab03/data/cache.
    """
    from .releases import MAX_RELEASE_PAGES, parse_release

    owner, repo = full_name.split("/", 1)
    brutas = client.paginate(
        endpoint=f"repos/{owner}/{repo}/releases",
        params={"per_page": 100},
        max_pages=MAX_RELEASE_PAGES,
        cache_category="releases",
        cache_key_prefix=f"releases_{owner}_{repo}",
    )
    linhas, vistos = [], set()
    for raw in brutas:
        release = parse_release(raw)
        if release is None or (release.release_id and release.release_id in vistos):
            continue
        vistos.add(release.release_id)
        linhas.append({
            "full_name": full_name,
            "release_id": release.release_id,
            "tag_name": release.tag_name,
            "release_name": release.name,
            "release_body": raw.get("body") or "",
            "published_at": release.published_at.isoformat(),
        })
    return pd.DataFrame(linhas, columns=COLUNAS_RELEASES)


def coletar_releases(metricas: pd.DataFrame, client=None) -> pd.DataFrame:
    client = client or _criar_client()
    partes = []
    for full_name in metricas["full_name"]:
        try:
            partes.append(coletar_releases_repo(client, full_name))
        except Exception as err:  # noqa: BLE001 - segue para o próximo repositório
            logger.warning("Falha ao coletar releases de %s: %s", full_name, err)
    return pd.concat(partes, ignore_index=True) if partes else pd.DataFrame(columns=COLUNAS_RELEASES)


def _ler_token() -> str:
    """Token do ambiente (GITHUB_TOKEN) ou do .env (lab03/.env, depois .env na raiz)."""
    import os

    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        return token
    for caminho in (Path("lab03/.env"), Path(".env")):
        if caminho.exists():
            for linha in caminho.read_text(encoding="utf-8").splitlines():
                if linha.strip().startswith("GITHUB_TOKEN="):
                    return linha.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def _get_json(url: str, token: str):
    import json
    import urllib.request

    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "lab03-rq08",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def coletar_releases_direto(full_names, token: str, max_paginas: int = 10) -> pd.DataFrame:
    """Coleta as releases válidas chamando a API com o token, sem passar pelo GitHubClient.

    Usada quando o client não carrega o token (cota anônima de 60 req/h).
    Não usa o cache em disco; o resultado fica em releases_rework.csv.
    """
    from .releases import parse_release

    if not token:
        raise SystemExit("GITHUB_TOKEN não encontrado (ambiente, lab03/.env ou .env).")
    linhas = []
    for i, full_name in enumerate(full_names, 1):
        logger.info("Coletando %d/%d: %s", i, len(full_names), full_name)
        vistos = set()
        for pagina in range(1, max_paginas + 1):
            url = f"https://api.github.com/repos/{full_name}/releases?per_page=100&page={pagina}"
            try:
                brutas = _get_json(url, token)
            except Exception as err:  # noqa: BLE001 - segue para o próximo repositório
                logger.warning("Falha em %s (página %d): %s", full_name, pagina, err)
                break
            if not brutas:
                break
            for raw in brutas:
                release = parse_release(raw)
                if release is None or (release.release_id and release.release_id in vistos):
                    continue
                vistos.add(release.release_id)
                linhas.append({
                    "full_name": full_name,
                    "release_id": release.release_id,
                    "tag_name": release.tag_name,
                    "release_name": release.name,
                    "release_body": raw.get("body") or "",
                    "published_at": release.published_at.isoformat(),
                })
            if len(brutas) < 100:
                break
    return pd.DataFrame(linhas, columns=COLUNAS_RELEASES)


# ---------------------------------------------------------------------------
# Cálculo
# ---------------------------------------------------------------------------
def classificar_releases(
    releases: pd.DataFrame, versao: str = VERSAO_HEURISTICA_PADRAO, usar_corpo: bool = True
) -> pd.DataFrame:
    """Adiciona `is_corretiva` (bool) usando a heurística validada na S02.

    usar_corpo=False ignora o release_body (classifica só por título/tag): análise de
    sensibilidade, pois corpos de changelog real citam "fix"/"bug" em quase toda release.
    """
    if versao not in CLASSIFICADORES:
        raise ValueError(f"Classificador desconhecido: {versao}. Opções: {list(CLASSIFICADORES)}")
    df = releases.copy()
    for col in ("tag_name", "release_name", "release_body"):
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str)
    df["published_at"] = pd.to_datetime(df["published_at"], utc=True)
    if not usar_corpo:
        df["release_body"] = ""
    if df.empty:
        df["is_corretiva"] = pd.Series(dtype=bool)
        return df
    df["is_corretiva"] = df.apply(CLASSIFICADORES[versao], axis=1).eq("sim")
    return df


def filtrar_janela(releases: pd.DataFrame, inicio: pd.Timestamp, fim: pd.Timestamp) -> pd.DataFrame:
    mask = (releases["published_at"] >= inicio) & (releases["published_at"] <= fim)
    return releases[mask].copy()


def calcular_rework(releases: pd.DataFrame) -> pd.DataFrame:
    """rework_rate = releases corretivas / releases válidas, por repositório."""
    out = (
        releases.groupby("full_name")["is_corretiva"]
        .agg(total_releases="size", releases_corretivas="sum")
        .reset_index()
    )
    out["releases_corretivas"] = out["releases_corretivas"].astype(int)
    out["rework_rate"] = out["releases_corretivas"] / out["total_releases"]
    return out


def calcular_cfr_b(releases: pd.DataFrame, fim: pd.Timestamp, janela_dias: int = JANELA_CFR_DIAS) -> pd.DataFrame:
    """CFR variante (b) recalculado: release falha se há corretiva em (t, t + janela_dias].

    Releases publicadas nos últimos `janela_dias` dias da janela são censuradas
    (excluídas do denominador), como em cfr_delivery_censored_count.
    """
    delta = pd.Timedelta(days=janela_dias)
    limite_censura = fim - delta
    linhas = []
    for full_name, g in releases.groupby("full_name"):
        datas = sorted(g["published_at"])
        corretivas = list(g.loc[g["is_corretiva"], "published_at"])
        avaliadas = [d for d in datas if d <= limite_censura]
        falhas = sum(any(d < c <= d + delta for c in corretivas) for d in avaliadas)
        linhas.append({
            "full_name": full_name,
            "releases_avaliadas_cfr": len(avaliadas),
            "releases_com_falha": falhas,
            "releases_censuradas": len(datas) - len(avaliadas),
            "cfr_b_recalculado": falhas / len(avaliadas) if avaliadas else np.nan,
        })
    return pd.DataFrame(linhas)


def montar_tabela(rework: pd.DataFrame, cfr: pd.DataFrame, metricas: pd.DataFrame) -> pd.DataFrame:
    """Une rework, CFR recalculado e os valores do metricas_dora.csv, com colunas de auditoria."""
    base = metricas[["full_name", "valid_releases_count", "cfr_delivery_proxy"]].copy()
    tab = base.merge(rework, on="full_name", how="left").merge(cfr, on="full_name", how="left")
    tab["contagem_confere"] = tab["total_releases"] == tab["valid_releases_count"]
    tab["cfr_confere"] = np.isclose(
        tab["cfr_b_recalculado"], tab["cfr_delivery_proxy"], atol=TOLERANCIA_CFR_CSV, equal_nan=False
    )
    tab["diferenca_rework_menos_cfr"] = tab["rework_rate"] - tab["cfr_b_recalculado"]
    return tab


# ---------------------------------------------------------------------------
# Estatística
# ---------------------------------------------------------------------------
def resumir(tab: pd.DataFrame) -> pd.DataFrame:
    linhas = {}
    for col in ("rework_rate", "cfr_b_recalculado", "cfr_delivery_proxy"):
        s = tab[col].dropna()
        linhas[col] = {
            "n": len(s),
            "média": s.mean(), "mediana": s.median(),
            "Q1": s.quantile(0.25), "Q3": s.quantile(0.75),
            "mín": s.min(), "máx": s.max(),
        } if len(s) else {k: np.nan for k in ("n", "média", "mediana", "Q1", "Q3", "mín", "máx")}
    return pd.DataFrame(linhas).T


def comparar(tab: pd.DataFrame, coluna_cfr: str = "cfr_b_recalculado") -> Dict[str, float]:
    """Spearman, Wilcoxon pareado e contagens de qual métrica é maior, por repositório."""
    d = tab[["rework_rate", coluna_cfr]].dropna()
    dif = d["rework_rate"] - d[coluna_cfr]
    res: Dict[str, float] = {
        "cfr_usado": coluna_cfr,
        "n_repos": len(d),
        "mediana_diferenca_rework_menos_cfr": float(dif.median()) if len(d) else np.nan,
        "repos_rework_menor_que_cfr": int((dif < 0).sum()),
        "repos_rework_maior_que_cfr": int((dif > 0).sum()),
        "repos_iguais": int((dif == 0).sum()),
        "spearman_rho": np.nan, "spearman_p": np.nan,
        "wilcoxon_stat": np.nan, "wilcoxon_p": np.nan,
    }
    if len(d) >= 3 and d["rework_rate"].nunique() > 1 and d[coluna_cfr].nunique() > 1:
        rho, p = stats.spearmanr(d["rework_rate"], d[coluna_cfr])
        res["spearman_rho"], res["spearman_p"] = float(rho), float(p)
    if (dif != 0).any():
        try:
            w, p = stats.wilcoxon(dif)
            res["wilcoxon_stat"], res["wilcoxon_p"] = float(w), float(p)
        except ValueError:
            pass
    return res


def rework_agregado(tab: pd.DataFrame) -> float:
    ok = tab.dropna(subset=["total_releases"])
    return float(ok["releases_corretivas"].sum() / ok["total_releases"].sum()) if len(ok) else np.nan


# ---------------------------------------------------------------------------
# Saídas
# ---------------------------------------------------------------------------
def _md(df: pd.DataFrame, casas: int = 4) -> str:
    """Tabela em Markdown (índice vira a primeira coluna)."""
    def fmt(v):
        if isinstance(v, (float, np.floating)):
            return "" if np.isnan(v) else f"{v:.{casas}f}"
        return str(v)

    cab = [df.index.name or ""] + [str(c) for c in df.columns]
    linhas = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    for idx, row in df.iterrows():
        cels = [str(int(v)) if c == "n" and not np.isnan(v) else fmt(v) for c, v in row.items()]
        linhas.append("| " + " | ".join([str(idx)] + cels) + " |")
    return "\n".join(linhas)


def gerar_figura(tab: pd.DataFrame, caminho: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    d = tab.dropna(subset=["rework_rate", "cfr_b_recalculado"])
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.5))
    ax[0].boxplot([d["rework_rate"], d["cfr_b_recalculado"]])
    ax[0].set_xticklabels(["Rework rate", "CFR (b)"])
    ax[0].set_ylabel("Proporção de releases")
    ax[0].set_title("Distribuição por repositório")
    ax[1].scatter(d["cfr_b_recalculado"], d["rework_rate"], alpha=0.7)
    lim = max(d["cfr_b_recalculado"].max(), d["rework_rate"].max(), 0.01) * 1.05
    ax[1].plot([0, lim], [0, lim], "k--", lw=1)
    ax[1].set_xlabel("CFR (b), recalculado")
    ax[1].set_ylabel("Rework rate")
    ax[1].set_title("Rework rate vs CFR (b)")
    fig.tight_layout()
    caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho, dpi=150)
    plt.close(fig)


def executar(
    releases_csv: Path = RELEASES_CSV,
    metricas_csv: Path = METRICAS_CSV,
    saida_dir: Path = DATA_DIR,
    figuras_dir: Path = FIGURAS_DIR,
    versao: str = VERSAO_HEURISTICA_PADRAO,
    janela_cfr_dias: int = JANELA_CFR_DIAS,
    janela: Optional[Tuple[pd.Timestamp, pd.Timestamp]] = None,
    usar_corpo: bool = True,
) -> Dict[str, object]:
    metricas = pd.read_csv(metricas_csv)
    inicio, fim = janela or carregar_janela()
    releases = classificar_releases(pd.read_csv(releases_csv), versao, usar_corpo)
    releases = filtrar_janela(releases, inicio, fim)

    rework = calcular_rework(releases)
    cfr = calcular_cfr_b(releases, fim, janela_cfr_dias)
    tab = montar_tabela(rework, cfr, metricas)
    resumo = resumir(tab)
    comp = comparar(tab, "cfr_b_recalculado")
    comp_csv = comparar(tab[tab["cfr_confere"]], "cfr_delivery_proxy")

    saida_dir.mkdir(parents=True, exist_ok=True)
    tab.to_csv(saida_dir / "rework_rate_por_repo.csv", index=False)
    resumo.to_csv(saida_dir / "rework_rate_resumo.csv")
    pd.DataFrame([comp, {**comp_csv, "cfr_usado": "cfr_delivery_proxy (somente linhas consistentes)"}]).to_csv(
        saida_dir / "rework_rate_comparacao_cfr.csv", index=False
    )
    (saida_dir / "tabela_rework_rate.md").write_text(
        "# Deployment rework rate vs CFR (b)\n\n"
        f"Heurística: `{versao}` ({'título+corpo' if usar_corpo else 'somente título/tag'}). Janela: {inicio.date()} a {fim.date()}. "
        f"Rework rate agregado: {rework_agregado(tab):.4f}.\n\n"
        "## Resumo\n\n" + _md(resumo) + "\n\n"
        "## Por repositório\n\n" + _md(tab[[
            "full_name", "total_releases", "releases_corretivas", "rework_rate",
            "cfr_b_recalculado", "cfr_delivery_proxy", "contagem_confere", "cfr_confere"]].set_index("full_name")) + "\n",
        encoding="utf-8",
    )
    gerar_figura(tab, figuras_dir / "rework_vs_cfr_b.png")

    n_inc = int((~tab["cfr_confere"]).sum())
    logger.info("Repositórios: %d | CFR(b) do CSV inconsistente com as releases: %d", len(tab), n_inc)
    return {"tabela": tab, "resumo": resumo, "comparacao": comp, "comparacao_csv": comp_csv}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--coletar", action="store_true", help="coleta as releases (usa o cache) e salva releases_rework.csv")
    p.add_argument("--direto", action="store_true",
                   help="com --coletar: chama a API com o token do .env, sem usar o GitHubClient")
    p.add_argument("--sem-corpo", action="store_true",
                   help="classifica só por título/tag (sensibilidade); saídas em lab03/data/rq08_sem_corpo/")
    p.add_argument("--heuristica", default=VERSAO_HEURISTICA_PADRAO, choices=list(CLASSIFICADORES))
    p.add_argument("--janela-cfr-dias", type=int, default=JANELA_CFR_DIAS)
    args = p.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    if args.coletar:
        metricas = pd.read_csv(METRICAS_CSV)
        if args.direto:
            coletadas = coletar_releases_direto(list(metricas["full_name"]), _ler_token())
        else:
            coletadas = coletar_releases(metricas)
        coletadas.to_csv(RELEASES_CSV, index=False)
        logger.info("Releases salvas em %s (%d linhas)", RELEASES_CSV, len(coletadas))

    if not RELEASES_CSV.exists():
        raise SystemExit(f"{RELEASES_CSV} não encontrado. Rode primeiro com --coletar.")
    sufixos = ([args.heuristica] if args.heuristica != VERSAO_HEURISTICA_PADRAO else []) + (
        ["sem_corpo"] if args.sem_corpo else [])
    if sufixos:
        destino = DATA_DIR / ("rq08_" + "_".join(sufixos))
        r = executar(saida_dir=destino, figuras_dir=destino, versao=args.heuristica,
                     janela_cfr_dias=args.janela_cfr_dias, usar_corpo=not args.sem_corpo)
    else:
        r = executar(versao=args.heuristica, janela_cfr_dias=args.janela_cfr_dias)
    print(r["resumo"].round(4).to_string())
    print()
    for chave, valor in r["comparacao"].items():
        print(f"{chave}: {valor}")


if __name__ == "__main__":
    main()