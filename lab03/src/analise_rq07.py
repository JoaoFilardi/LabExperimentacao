"""Análise de sensibilidade das classificações DORA - RQ07 (LAB03S03, Issue #41).

Pergunta: quanto a classificação DORA dos repositórios muda quando se alteram as
definições operacionais de lead time e de change failure rate, e as conclusões
das RQ01 a RQ06 continuam valendo?

Combinações (C1 é a referência; DF e Recovery Time são idênticos em todas):

    id  Lead Time           CFR            Descrição
    C1  por release (a)     proxy de CI    referência da S02/Issue #39
    C2  por commit  (b)     proxy de CI    só troca o lead time
    C3  por release (a)     proxy entrega  só troca o CFR
    C4  por commit  (b)     proxy entrega  troca as duas definições

Se o dataset tiver a coluna `deployment_frequency_with_prerelease_weekly`
(releases publicadas + pré-releases), a combinação C5 é incluída
automaticamente: igual à C1, mas com essa definição de deploy.

Para cada par de combinações são calculados: % de repositórios que mudaram de
categoria geral, % que melhoraram/pioraram e o kappa de Cohen ponderado
linearmente (`cohen_kappa_score(..., weights='linear')`) sobre a escala
ordinal Low < Medium < High < Elite. A classificação geral segue a regra da C1:
mediana dos 4 scores (Elite=4 ... Low=1) arredondada para baixo.

Uso:
    python -m lab03.src.analise_rq07 \
        --input lab03/data/classificacao_dora_c1.csv \
        --output-dir lab03/data --docs-dir lab03/docs
"""

from __future__ import annotations

import argparse
import itertools
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import cohen_kappa_score

try:
    import matplotlib

    matplotlib.use("Agg")  # execução sem interface gráfica
    import matplotlib.pyplot as plt

    HAS_MATPLOTLIB = True
except ImportError:  # pragma: no cover
    plt = None
    HAS_MATPLOTLIB = False

from .analise_rq01_rq04 import (
    DORA_CATEGORIES,
    DORA_PALETTE,
    classificar_cfr,
    classificar_df,
    classificar_lt,
    classificar_rt,
)

# ==============================================================================
# Constantes
# ==============================================================================

SCORE = {"Elite": 4, "High": 3, "Medium": 2, "Low": 1}
INV_SCORE = {v: k for k, v in SCORE.items()}
ORDEM_ASCENDENTE = ["Low", "Medium", "High", "Elite"]  # ordem ordinal do kappa
LABELS_KAPPA = [1, 2, 3, 4]

# Convenção desta análise para classificar a sensibilidade de uma dimensão
# (% de repositórios que mudam de categoria ao trocar a definição operacional).
LIMIAR_ROBUSTA = 10.0
LIMIAR_SENSIVEL = 30.0

ALPHA = 0.05

REQUIRED_COLUMNS = [
    "full_name",
    "deployment_frequency_weekly",
    "lead_time_by_release_days",
    "lead_time_by_commit_days",
    "cfr_ci_proxy",
    "cfr_delivery_proxy",
    "recovery_time_hours",
]
COL_DF_PRERELEASE = "deployment_frequency_with_prerelease_weekly"


@dataclass(frozen=True)
class Combinacao:
    """Definição operacional de uma combinação (qual coluna alimenta cada métrica)."""

    id: str
    nome: str
    df_col: str
    lt_col: str
    cfr_col: str
    rt_col: str
    descricao: str


C1 = Combinacao(
    "C1", "Referência (release / LT por release / CFR por CI)",
    "deployment_frequency_weekly", "lead_time_by_release_days", "cfr_ci_proxy", "recovery_time_hours",
    "Deploy = release publicada; lead time por release; CFR pelo proxy de CI.",
)
C2 = Combinacao(
    "C2", "Lead time por commit",
    "deployment_frequency_weekly", "lead_time_by_commit_days", "cfr_ci_proxy", "recovery_time_hours",
    "Igual à C1, trocando o lead time por release pelo lead time por commit.",
)
C3 = Combinacao(
    "C3", "CFR por entrega",
    "deployment_frequency_weekly", "lead_time_by_release_days", "cfr_delivery_proxy", "recovery_time_hours",
    "Igual à C1, trocando o CFR por CI pelo CFR por entrega (release seguida de corretiva em 7 dias).",
)
C4 = Combinacao(
    "C4", "Lead time por commit + CFR por entrega",
    "deployment_frequency_weekly", "lead_time_by_commit_days", "cfr_delivery_proxy", "recovery_time_hours",
    "Troca as duas definições de uma vez.",
)
C5 = Combinacao(
    "C5", "Deploy = release + pré-release",
    COL_DF_PRERELEASE, "lead_time_by_release_days", "cfr_ci_proxy", "recovery_time_hours",
    "Igual à C1, contando também pré-releases no Deployment Frequency.",
)
COMBINACOES_PADRAO = [C1, C2, C3, C4]


def combinacoes_disponiveis(df: pd.DataFrame, ids: Optional[Sequence[str]] = None) -> List[Combinacao]:
    """Combinações aplicáveis ao dataset (a C5 só entra se a coluna de pré-release existir)."""
    todas = list(COMBINACOES_PADRAO)
    if COL_DF_PRERELEASE in df.columns:
        todas.append(C5)
    if ids:
        wanted = [i.strip().upper() for i in ids]
        todas = [c for c in todas if c.id in wanted]
    if len(todas) < 3:
        raise ValueError("São necessárias pelo menos 3 combinações de definições operacionais.")
    if todas[0].id != "C1" and ids is not None:
        raise ValueError("A C1 (referência) deve estar entre as combinações selecionadas.")
    return todas


# ==============================================================================
# 1. Classificação por combinação
# ==============================================================================

def _categorizar(series: pd.Series, func) -> pd.Series:
    return series.map(lambda v: func(float(v)) if pd.notna(v) else pd.NA)


def classificar_combinacao(df: pd.DataFrame, comb: Combinacao) -> pd.DataFrame:
    """Classifica cada repositório em uma combinação.

    Retorna colunas `<id>_df`, `<id>_lt`, `<id>_cfr`, `<id>_rt` (categorias),
    `<id>_score` e `<id>_categoria` (classificação geral). Se alguma das 4 métricas
    estiver ausente, o repositório não é aplicável à combinação (score/categoria nulos).
    """
    p = comb.id
    out = pd.DataFrame(index=df.index)
    out[f"{p}_df"] = _categorizar(df[comb.df_col], classificar_df)
    out[f"{p}_lt"] = _categorizar(df[comb.lt_col], classificar_lt)
    out[f"{p}_cfr"] = _categorizar(df[comb.cfr_col], classificar_cfr)
    out[f"{p}_rt"] = _categorizar(df[comb.rt_col], classificar_rt)

    parciais = out[[f"{p}_df", f"{p}_lt", f"{p}_cfr", f"{p}_rt"]].apply(lambda s: s.map(SCORE))
    parciais = parciais.astype(float)
    mediana = parciais.median(axis=1, skipna=False)  # NaN se faltar alguma métrica
    score = np.floor(mediana)
    out[f"{p}_score"] = score.astype("Int64")
    out[f"{p}_categoria"] = score.map(lambda v: INV_SCORE[int(v)] if pd.notna(v) else pd.NA)
    return out


def classificar_todas(df: pd.DataFrame, combinacoes: Sequence[Combinacao]) -> pd.DataFrame:
    """Dataset com `full_name` + classificações de todas as combinações."""
    partes = [df[["full_name"]].copy()]
    partes.extend(classificar_combinacao(df, c) for c in combinacoes)
    return pd.concat(partes, axis=1)


# ==============================================================================
# 2. Comparação entre pares de combinações
# ==============================================================================

def interpretar_kappa(k: float) -> str:
    """Faixas de Landis & Koch (1977)."""
    if k != k:
        return "Indefinido"
    if k < 0.0:
        return "Pior que o acaso"
    if k <= 0.20:
        return "Concordância fraca"
    if k <= 0.40:
        return "Concordância razoável"
    if k <= 0.60:
        return "Concordância moderada"
    if k <= 0.80:
        return "Concordância substancial"
    return "Concordância quase perfeita"


def kappa_ponderado_linear(x: Sequence[int], y: Sequence[int]) -> float:
    """Kappa de Cohen ponderado linearmente, na escala ordinal 1..4.

    Quando o kappa é indefinido (as duas classificações são constantes e iguais, logo a
    concordância esperada é total), retorna 1.0 se há concordância plena e 0.0 caso contrário.
    """
    xs, ys = np.asarray(x, dtype=int), np.asarray(y, dtype=int)
    if len(xs) == 0:
        return float("nan")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        k = cohen_kappa_score(xs, ys, labels=LABELS_KAPPA, weights="linear")
    if k != k:
        return 1.0 if bool(np.all(xs == ys)) else 0.0
    return float(k)


def comparar_par(cls: pd.DataFrame, a: str, b: str) -> Dict[str, Any]:
    """Compara a classificação geral de duas combinações nos repositórios aplicáveis às duas."""
    sa, sb = cls[f"{a}_score"], cls[f"{b}_score"]
    mask = sa.notna() & sb.notna()
    x = sa[mask].astype(int).to_numpy()
    y = sb[mask].astype(int).to_numpy()
    n = int(mask.sum())
    mudaram = int((x != y).sum())
    kappa = kappa_ponderado_linear(x, y)
    pct = lambda v: round(100.0 * v / n, 2) if n else float("nan")  # noqa: E731
    return {
        "par": f"{a} x {b}",
        "combinacao_a": a,
        "combinacao_b": b,
        "n_repositorios": n,
        "n_mudaram": mudaram,
        "pct_mudaram": pct(mudaram),
        "pct_melhoraram": pct(int((y > x).sum())),  # b melhor que a
        "pct_pioraram": pct(int((y < x).sum())),
        "delta_medio_score": round(float((y - x).mean()), 4) if n else float("nan"),
        "kappa_ponderado_linear": round(kappa, 4) if kappa == kappa else kappa,
        "interpretacao_kappa": interpretar_kappa(kappa),
    }


def comparar_todos_os_pares(cls: pd.DataFrame, combinacoes: Sequence[Combinacao]) -> pd.DataFrame:
    ids = [c.id for c in combinacoes]
    return pd.DataFrame([comparar_par(cls, a, b) for a, b in itertools.combinations(ids, 2)])


def matriz_transicao(cls: pd.DataFrame, a: str, b: str) -> pd.DataFrame:
    """Matriz de contagem: linhas = categoria em `a`, colunas = categoria em `b`."""
    mask = cls[f"{a}_categoria"].notna() & cls[f"{b}_categoria"].notna()
    ca = pd.Categorical(cls.loc[mask, f"{a}_categoria"], categories=DORA_CATEGORIES)
    cb = pd.Categorical(cls.loc[mask, f"{b}_categoria"], categories=DORA_CATEGORIES)
    return pd.crosstab(ca, cb, dropna=False).reindex(index=DORA_CATEGORIES, columns=DORA_CATEGORIES, fill_value=0)


def matrizes_transicao_longas(cls: pd.DataFrame, combinacoes: Sequence[Combinacao]) -> pd.DataFrame:
    linhas = []
    for a, b in itertools.combinations([c.id for c in combinacoes], 2):
        m = matriz_transicao(cls, a, b)
        for ca in DORA_CATEGORIES:
            for cb in DORA_CATEGORIES:
                linhas.append({"par": f"{a} x {b}", "categoria_a": ca, "categoria_b": cb, "n": int(m.loc[ca, cb])})
    return pd.DataFrame(linhas)


def distribuicao_por_combinacao(cls: pd.DataFrame, combinacoes: Sequence[Combinacao]) -> pd.DataFrame:
    """Contagem e percentual de repositórios por categoria geral, por combinação."""
    linhas = []
    for c in combinacoes:
        col = cls[f"{c.id}_categoria"].dropna()
        n = len(col)
        linha: Dict[str, Any] = {"combinacao": c.id, "n": n}
        for cat in DORA_CATEGORIES:
            k = int((col == cat).sum())
            linha[cat] = k
            linha[f"{cat}_pct"] = round(100.0 * k / n, 2) if n else float("nan")
        linhas.append(linha)
    return pd.DataFrame(linhas)


def sensibilidade_por_dimensao(cls: pd.DataFrame, combinacoes: Sequence[Combinacao]) -> pd.DataFrame:
    """% de repositórios cuja categoria muda em cada métrica (DF, LT, CFR, RT) por par."""
    linhas = []
    for a, b in itertools.combinations([c.id for c in combinacoes], 2):
        linha: Dict[str, Any] = {"par": f"{a} x {b}"}
        for dim in ("df", "lt", "cfr", "rt"):
            ca, cb = cls[f"{a}_{dim}"], cls[f"{b}_{dim}"]
            mask = ca.notna() & cb.notna()
            n = int(mask.sum())
            linha[f"pct_mudou_{dim}"] = round(100.0 * float((ca[mask] != cb[mask]).sum()) / n, 2) if n else float("nan")
        linhas.append(linha)
    return pd.DataFrame(linhas)


# ==============================================================================
# 3. Robustez das conclusões das RQ01 a RQ06
# ==============================================================================

def veredito_sensibilidade(pct_mudou: float) -> str:
    if pct_mudou != pct_mudou:
        return "indefinido"
    if pct_mudou < LIMIAR_ROBUSTA:
        return "robusta"
    if pct_mudou <= LIMIAR_SENSIVEL:
        return "parcialmente sensível"
    return "sensível"


def comparar_variantes(df: pd.DataFrame, col_a: str, col_b: str, cat_fn, nome: str) -> Dict[str, Any]:
    """Compara duas variantes de uma métrica (RQ02: lead time; RQ03: CFR)."""
    sub = df[[col_a, col_b]].dropna()
    n = len(sub)
    if n == 0:
        return {"metrica": nome, "n": 0}
    a, b = sub[col_a].astype(float), sub[col_b].astype(float)
    dif = a - b
    if (dif == 0).all():
        p_wilcoxon = 1.0
    else:
        p_wilcoxon = float(stats.wilcoxon(a, b).pvalue)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        rho = float(stats.spearmanr(a, b).statistic) if n >= 3 else float("nan")
    pct_cat = 100.0 * float((a.map(cat_fn) != b.map(cat_fn)).mean())
    return {
        "metrica": nome,
        "n": n,
        "mediana_variante_a": round(float(a.median()), 4),
        "mediana_variante_b": round(float(b.median()), 4),
        "mediana_diferenca_a_menos_b": round(float(dif.median()), 4),
        "p_wilcoxon_pareado": round(p_wilcoxon, 6),
        "spearman_entre_variantes": round(rho, 4) if rho == rho else rho,
        "pct_mudou_categoria": round(pct_cat, 2),
        "veredito": veredito_sensibilidade(pct_cat),
    }


def magnitude_spearman(rho: float) -> str:
    """Dancey & Reidy, como na RQ05."""
    v = abs(rho)
    if v < 0.10:
        return "Desprezível"
    if v < 0.30:
        return "Fraca"
    if v < 0.50:
        return "Moderada"
    if v < 0.70:
        return "Forte"
    return "Muito Forte"


def rq05_por_variante_cfr(df: pd.DataFrame, combinacoes: Sequence[Combinacao]) -> pd.DataFrame:
    """Spearman entre Deployment Frequency e cada definição de CFR usada nas combinações."""
    linhas = []
    vistos = set()
    for c in combinacoes:
        chave = (c.df_col, c.cfr_col)
        if chave in vistos:
            continue
        vistos.add(chave)
        sub = df[[c.df_col, c.cfr_col]].dropna()
        n = len(sub)
        if n >= 3 and sub[c.df_col].nunique() > 1 and sub[c.cfr_col].nunique() > 1:
            res = stats.spearmanr(sub[c.df_col], sub[c.cfr_col])
            rho, p = float(res.statistic), float(res.pvalue)
        else:
            rho, p = 0.0, 1.0
        linhas.append({
            "combinacoes": ",".join(x.id for x in combinacoes if (x.df_col, x.cfr_col) == chave),
            "metrica_df": c.df_col, "metrica_cfr": c.cfr_col, "n": n,
            "rho": round(rho, 4), "p_valor": round(p, 6),
            "sinal": "positivo" if rho > 0 else ("negativo" if rho < 0 else "nulo"),
            "magnitude": magnitude_spearman(rho),
            "significativo": bool(p < ALPHA),
        })
    return pd.DataFrame(linhas)


def ajustar_holm(p_values: Sequence[float]) -> np.ndarray:
    """p-valores ajustados pelo método de Holm-Bonferroni."""
    p = np.asarray(p_values, dtype=float)
    m = len(p)
    ajustado = np.empty(m)
    maximo = 0.0
    for pos, idx in enumerate(np.argsort(p)):
        maximo = max(maximo, min(1.0, (m - pos) * p[idx]))
        ajustado[idx] = maximo
    return ajustado


def _quartis(s: pd.Series) -> pd.Series:
    r = pd.to_numeric(s, errors="coerce").rank(method="first")
    return pd.qcut(r, q=4, labels=["Q1", "Q2", "Q3", "Q4"])


def preparar_fatores(df: pd.DataFrame) -> Dict[str, pd.Series]:
    """Fatores estruturais da RQ06 disponíveis no dataset."""
    fatores: Dict[str, pd.Series] = {}
    if "stars" in df.columns:
        fatores["stars_quartile"] = _quartis(df["stars"])
    if "age_years" in df.columns:
        fatores["age_quartile"] = _quartis(df["age_years"])
    if "contributors_count" in df.columns:
        fatores["contributors_quartile"] = _quartis(df["contributors_count"])
    if "primary_language" in df.columns:
        top = df["primary_language"].value_counts().head(5).index
        fatores["language_group"] = df["primary_language"].map(lambda v: v if v in top else "Outras")
    return fatores


def rq06_por_combinacao(
    df: pd.DataFrame, cls: pd.DataFrame, combinacoes: Sequence[Combinacao]
) -> pd.DataFrame:
    """Kruskal-Wallis do score DORA geral de cada combinação contra cada fator da RQ06 (Holm global)."""
    fatores = preparar_fatores(df)
    linhas = []
    for c in combinacoes:
        score = cls[f"{c.id}_score"].astype(float)
        for nome, fator in fatores.items():
            base = pd.DataFrame({"s": score, "f": fator}).dropna()
            grupos = [g["s"].to_numpy() for _, g in base.groupby("f", observed=True) if len(g) > 0]
            n = len(base)
            if len(grupos) < 2 or n < 3:
                h, p = 0.0, 1.0
            else:
                try:
                    res = stats.kruskal(*grupos)
                    h, p = float(res.statistic), float(res.pvalue)
                except ValueError:  # todos os valores idênticos
                    h, p = 0.0, 1.0
            eps2 = max(0.0, min(1.0, h / (n - 1))) if n > 1 else 0.0
            linhas.append({
                "combinacao": c.id, "fator": nome, "n": n, "H": round(h, 4),
                "gl": max(0, len(grupos) - 1), "p_bruto": p, "epsilon2": round(eps2, 4),
            })
    out = pd.DataFrame(linhas)
    if out.empty:
        return out
    out["p_holm"] = ajustar_holm(out["p_bruto"].to_numpy())
    out["significativo"] = out["p_holm"] < ALPHA
    out["p_bruto"] = out["p_bruto"].round(6)
    out["p_holm"] = out["p_holm"].round(6)
    return out


def resumir_robustez(
    sens_dim: pd.DataFrame,
    rq02: Dict[str, Any],
    rq03: Dict[str, Any],
    rq05: pd.DataFrame,
    rq06: pd.DataFrame,
    pares: pd.DataFrame,
) -> pd.DataFrame:
    """Tabela-síntese: uma linha por RQ com evidência e veredito de robustez."""
    linhas: List[Dict[str, str]] = []

    linhas.append({
        "rq": "RQ01", "pergunta": "Deployment Frequency",
        "evidencia": "Todas as combinações usam a mesma definição de deploy (release publicada).",
        "veredito": "invariante por construção",
    })
    linhas.append({
        "rq": "RQ02", "pergunta": "Lead Time (por release x por commit)",
        "evidencia": (
            f"{rq02.get('pct_mudou_categoria', float('nan')):.1f}% dos repositórios mudam de categoria de LT; "
            f"Spearman entre variantes = {rq02.get('spearman_entre_variantes', float('nan'))}; "
            f"Wilcoxon pareado p = {rq02.get('p_wilcoxon_pareado', float('nan'))}."
        ),
        "veredito": rq02.get("veredito", "indefinido"),
    })
    linhas.append({
        "rq": "RQ03", "pergunta": "CFR (CI x entrega)",
        "evidencia": (
            f"{rq03.get('pct_mudou_categoria', float('nan')):.1f}% dos repositórios mudam de categoria de CFR; "
            f"Spearman entre variantes = {rq03.get('spearman_entre_variantes', float('nan'))}; "
            f"Wilcoxon pareado p = {rq03.get('p_wilcoxon_pareado', float('nan'))}."
        ),
        "veredito": rq03.get("veredito", "indefinido"),
    })
    linhas.append({
        "rq": "RQ04", "pergunta": "Recovery Time",
        "evidencia": "Todas as combinações usam o mesmo tempo de recuperação (episódios por workflow, com censura).",
        "veredito": "invariante por construção",
    })

    if len(rq05) >= 2:
        sinais = set(rq05["sinal"])
        mags = set(rq05["magnitude"])
        sig = set(rq05["significativo"])
        if len(sinais) == 1 and len(mags) == 1 and len(sig) == 1:
            v5 = "robusta"
        elif len(sinais) == 1:
            v5 = "parcialmente sensível"
        else:
            v5 = "sensível"
        ev5 = "; ".join(
            f"{r.metrica_cfr}: rho={r.rho:.3f} ({r.magnitude}, p={r.p_valor:.4f})" for r in rq05.itertuples()
        )
    else:
        v5, ev5 = "indefinido", "Menos de duas definições de CFR disponíveis."
    linhas.append({"rq": "RQ05", "pergunta": "DF x CFR (Spearman)", "evidencia": ev5, "veredito": v5})

    if not rq06.empty:
        partes, veredictos = [], []
        for fator, g in rq06.groupby("fator", sort=False):
            sigs = set(g["significativo"])
            veredictos.append("robusta" if len(sigs) == 1 else "sensível")
            quais = ",".join(g.loc[g["significativo"], "combinacao"]) or "nenhuma"
            partes.append(f"{fator}: significativo em {quais}")
        v6 = "robusta" if all(v == "robusta" for v in veredictos) else (
            "parcialmente sensível" if any(v == "robusta" for v in veredictos) else "sensível")
        ev6 = "; ".join(partes)
    else:
        v6, ev6 = "indefinido", "Dataset sem fatores estruturais (stars, idade, contribuidores, linguagem)."
    linhas.append({"rq": "RQ06", "pergunta": "Fatores associados ao desempenho DORA", "evidencia": ev6, "veredito": v6})

    ref = pares[pares["combinacao_a"] == "C1"] if not pares.empty else pares
    if not ref.empty:
        linhas.append({
            "rq": "Geral", "pergunta": "Classificação DORA geral (C1 x demais)",
            "evidencia": (
                f"% que muda de categoria: {ref['pct_mudaram'].min():.1f}% a {ref['pct_mudaram'].max():.1f}%; "
                f"kappa linear: {ref['kappa_ponderado_linear'].min():.3f} a {ref['kappa_ponderado_linear'].max():.3f}."
            ),
            "veredito": veredito_sensibilidade(float(ref["pct_mudaram"].max())),
        })
    return pd.DataFrame(linhas)


# ==============================================================================
# 4. Figuras
# ==============================================================================

def _heatmap(ax, matriz: np.ndarray, rotulos_x, rotulos_y, fmt: str, cmap: str, titulo: str,
             vmin: Optional[float] = None, vmax: Optional[float] = None) -> None:
    im = ax.imshow(matriz, cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_xticks(range(len(rotulos_x)))
    ax.set_xticklabels(rotulos_x)
    ax.set_yticks(range(len(rotulos_y)))
    ax.set_yticklabels(rotulos_y)
    ax.set_title(titulo, fontsize=11, fontweight="bold")
    lim_cor = np.nanmax(matriz) / 2.0 if np.isfinite(matriz).any() else 0.0
    for i in range(matriz.shape[0]):
        for j in range(matriz.shape[1]):
            v = matriz[i, j]
            if v != v:
                texto, cor = "—", "#555555"
            else:
                texto = format(v, fmt)
                cor = "white" if (vmin is None and v > lim_cor and lim_cor > 0) else "black"
            ax.text(j, i, texto, ha="center", va="center", fontsize=10, color=cor)
    ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)


def _salvar(fig, figures_dir: Path, nome: str) -> List[Path]:
    figures_dir.mkdir(parents=True, exist_ok=True)
    png, pdf = figures_dir / f"{nome}.png", figures_dir / f"{nome}.pdf"
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(pdf, format="pdf", bbox_inches="tight")
    plt.close(fig)
    return [png, pdf]


def gerar_figuras(
    cls: pd.DataFrame, combinacoes: Sequence[Combinacao], pares: pd.DataFrame,
    distribuicao: pd.DataFrame, figures_dir: Path,
) -> List[Path]:
    if not HAS_MATPLOTLIB:
        raise RuntimeError(
            "matplotlib não está instalado: as figuras da RQ07 não podem ser geradas. "
            "Instale com `python -m pip install matplotlib`."
        )
    ids = [c.id for c in combinacoes]
    caminhos: List[Path] = []

    # Figura 1: distribuição da classificação geral por combinação
    fig, ax = plt.subplots(figsize=(10, 5.5))
    largura = 0.8 / len(ids)
    x = np.arange(len(DORA_CATEGORIES))
    for k, cid in enumerate(ids):
        linha = distribuicao[distribuicao["combinacao"] == cid].iloc[0]
        valores = [linha[f"{cat}_pct"] for cat in DORA_CATEGORIES]
        barras = ax.bar(x + (k - (len(ids) - 1) / 2) * largura, valores, largura, label=cid, edgecolor="#2c3e50")
        for b, v in zip(barras, valores):
            ax.annotate(f"{v:.0f}%", (b.get_x() + b.get_width() / 2, b.get_height()),
                        xytext=(0, 3), textcoords="offset points", ha="center", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(DORA_CATEGORIES)
    ax.set_ylabel("Repositórios (%)")
    ax.set_xlabel("Categoria DORA geral")
    ax.set_title("RQ07: distribuição da classificação DORA por combinação", fontweight="bold")
    ax.legend(title="Combinação")
    fig.tight_layout()
    caminhos += _salvar(fig, figures_dir, "rq07_distribuicao_combinacoes")

    # Figura 2: matrizes de % de mudança e de kappa entre todos os pares
    k = len(ids)
    pct_m = np.full((k, k), np.nan)
    kap_m = np.full((k, k), np.nan)
    for r in pares.itertuples():
        i, j = ids.index(r.combinacao_a), ids.index(r.combinacao_b)
        pct_m[i, j] = pct_m[j, i] = r.pct_mudaram
        kap_m[i, j] = kap_m[j, i] = r.kappa_ponderado_linear
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    _heatmap(ax1, pct_m, ids, ids, ".1f", "YlOrRd", "% de repositórios que mudaram de categoria", 0, 100)
    _heatmap(ax2, kap_m, ids, ids, ".2f", "YlGnBu", "Kappa de Cohen ponderado (linear)", 0, 1)
    fig.suptitle("RQ07: sensibilidade da classificação DORA entre combinações", fontweight="bold")
    fig.tight_layout()
    caminhos += _salvar(fig, figures_dir, "rq07_matriz_mudanca_kappa")

    # Figura 3: matrizes de transição C1 x demais
    outros = ids[1:]
    fig, axes = plt.subplots(1, len(outros), figsize=(5 * len(outros), 4.6), squeeze=False)
    for ax, oid in zip(axes[0], outros):
        m = matriz_transicao(cls, ids[0], oid)
        _heatmap(ax, m.to_numpy(dtype=float), DORA_CATEGORIES, DORA_CATEGORIES, ".0f", "Blues", f"{ids[0]} (linhas) x {oid} (colunas)")
        ax.set_xlabel(oid)
        ax.set_ylabel(ids[0])
    fig.suptitle("RQ07: transição de categoria em relação à referência", fontweight="bold")
    fig.tight_layout()
    caminhos += _salvar(fig, figures_dir, "rq07_transicoes_c1")
    return caminhos


# ==============================================================================
# 5. Exportação e relatório
# ==============================================================================

def _md(df: pd.DataFrame) -> str:
    cab = [str(c) for c in df.columns]
    linhas = ["| " + " | ".join(cab) + " |", "| " + " | ".join(["---"] * len(cab)) + " |"]
    for _, row in df.iterrows():
        linhas.append("| " + " | ".join(str(row[c]) for c in df.columns) + " |")
    return "\n".join(linhas)


def _latex_escape(s: Any) -> str:
    return str(s).replace("_", r"\_").replace("%", r"\%").replace("&", r"\&")


def exportar_latex(pares: pd.DataFrame, distribuicao: pd.DataFrame, path: Path) -> Path:
    linhas = [
        "% Tabelas geradas automaticamente - RQ07 (Issue #41)\n",
        "\\begin{table}[htbp]\n\\centering\n"
        "\\caption{Sensibilidade da classificação DORA entre combinações (RQ 07)}\n"
        "\\label{tab:rq07_pares}\n\\begin{tabular}{|l|r|r|r|r|r|l|}\n\\hline\n"
        "\\textbf{Par} & \\textbf{N} & \\textbf{\\% mudaram} & \\textbf{\\% melhoraram} & "
        "\\textbf{\\% pioraram} & \\textbf{$\\kappa_w$} & \\textbf{Interpretação} \\\\\n\\hline\n",
    ]
    for r in pares.itertuples():
        linhas.append(
            f"{r.par.replace(' x ', ' $\\times$ ')} & {r.n_repositorios} & {r.pct_mudaram:.1f} & "
            f"{r.pct_melhoraram:.1f} & {r.pct_pioraram:.1f} & {r.kappa_ponderado_linear:.3f} & "
            f"{_latex_escape(r.interpretacao_kappa)} \\\\\n"
        )
    linhas.append("\\hline\n\\end{tabular}\n\\end{table}\n\n")
    linhas.append(
        "\\begin{table}[htbp]\n\\centering\n"
        "\\caption{Distribuição da classificação DORA geral por combinação}\n"
        "\\label{tab:rq07_distribuicao}\n\\begin{tabular}{|l|r|r|r|r|}\n\\hline\n"
        "\\textbf{Combinação} & \\textbf{Elite} & \\textbf{High} & \\textbf{Medium} & \\textbf{Low} \\\\\n\\hline\n"
    )
    for r in distribuicao.itertuples():
        linhas.append(
            f"{r.combinacao} & {r.Elite} ({r.Elite_pct:.1f}\\%) & {r.High} ({r.High_pct:.1f}\\%) & "
            f"{r.Medium} ({r.Medium_pct:.1f}\\%) & {r.Low} ({r.Low_pct:.1f}\\%) \\\\\n"
        )
    linhas.append("\\hline\n\\end{tabular}\n\\end{table}\n")
    path.write_text("".join(linhas), encoding="utf-8")
    return path


def gerar_discussao(
    pares: pd.DataFrame, sens_dim: pd.DataFrame, robustez: pd.DataFrame, combinacoes: Sequence[Combinacao]
) -> str:
    """Texto de discussão derivado dos números; deve ser revisado antes de entrar no artigo."""
    ref = pares[pares["combinacao_a"] == "C1"]
    dim_cols = ["pct_mudou_df", "pct_mudou_lt", "pct_mudou_cfr", "pct_mudou_rt"]
    nomes = {"pct_mudou_df": "Deployment Frequency", "pct_mudou_lt": "Lead Time",
             "pct_mudou_cfr": "CFR", "pct_mudou_rt": "Recovery Time"}
    medias = sens_dim[dim_cols].mean()
    dim_top = medias.idxmax()

    par_max = pares.loc[pares["pct_mudaram"].idxmax()]
    par_min = pares.loc[pares["pct_mudaram"].idxmin()]
    kmin, kmax = pares["kappa_ponderado_linear"].min(), pares["kappa_ponderado_linear"].max()

    paragrafos = [
        (
            f"Foram comparadas {len(combinacoes)} combinações ({', '.join(c.id for c in combinacoes)}) em "
            f"{len(pares)} pares. A porcentagem de repositórios que mudam de categoria DORA geral varia de "
            f"{par_min['pct_mudaram']:.1f}% ({par_min['par']}) a {par_max['pct_mudaram']:.1f}% ({par_max['par']}), e o "
            f"kappa de Cohen ponderado linearmente varia de {kmin:.3f} a {kmax:.3f}."
        ),
        (
            f"A dimensão que mais contribui para a instabilidade é {nomes[dim_top]} (média de "
            f"{medias[dim_top]:.1f}% de repositórios mudando de categoria por par). Deployment Frequency e Recovery Time "
            f"não são alterados pelas combinações C1 a C4; a variação vem exclusivamente das trocas de definição de "
            f"lead time e de CFR."
        ),
    ]
    if not ref.empty:
        sentido = []
        for r in ref.itertuples():
            if r.delta_medio_score > 0:
                sentido.append(f"{r.combinacao_b} tende a classificar melhor que C1 (delta médio de score {r.delta_medio_score:+.2f})")
            elif r.delta_medio_score < 0:
                sentido.append(f"{r.combinacao_b} tende a classificar pior que C1 (delta médio de score {r.delta_medio_score:+.2f})")
            else:
                sentido.append(f"{r.combinacao_b} não desloca a média de C1")
        paragrafos.append("Sentido da mudança em relação à referência: " + "; ".join(sentido) + ".")

    for r in robustez.itertuples():
        if r.rq in ("RQ02", "RQ03", "RQ05", "RQ06"):
            paragrafos.append(f"**{r.rq}** ({r.pergunta}): conclusão **{r.veredito}**. {r.evidencia}")
    paragrafos.append(
        "**RQ01 e RQ04** usam a mesma definição em todas as combinações; suas conclusões são invariantes a estas "
        "escolhas, mas continuam dependentes das definições de deploy (release publicada) e de recuperação (episódios "
        "por workflow com censura), que não foram variadas aqui."
    )
    paragrafos.append(
        f"Convenção de leitura: uma dimensão é considerada robusta quando menos de {LIMIAR_ROBUSTA:.0f}% dos "
        f"repositórios mudam de categoria, parcialmente sensível entre {LIMIAR_ROBUSTA:.0f}% e {LIMIAR_SENSIVEL:.0f}% "
        f"e sensível acima disso. Os limiares são uma escolha desta análise, não do enunciado."
    )
    return "\n\n".join(paragrafos)


def gerar_relatorio(
    path: Path, combinacoes: Sequence[Combinacao], n_repos: int, distribuicao: pd.DataFrame, pares: pd.DataFrame,
    sens_dim: pd.DataFrame, rq05: pd.DataFrame, rq06: pd.DataFrame, robustez: pd.DataFrame,
    rq02: Dict[str, Any], rq03: Dict[str, Any], figuras: Sequence[Path], input_csv: Path,
) -> Path:
    defs = pd.DataFrame([{
        "Combinação": c.id, "Deploy": c.df_col, "Lead time": c.lt_col, "CFR": c.cfr_col,
        "Recovery": c.rt_col, "Descrição": c.descricao,
    } for c in combinacoes])
    pares_tab = pares[[
        "par", "n_repositorios", "n_mudaram", "pct_mudaram", "pct_melhoraram", "pct_pioraram",
        "delta_medio_score", "kappa_ponderado_linear", "interpretacao_kappa",
    ]]
    dist_tab = distribuicao[["combinacao", "n"] + DORA_CATEGORIES]
    texto = [
        "# RQ07: Sensibilidade das classificações DORA (Sprint 03, Issue #41)\n",
        "## 1. Objetivo\n",
        "Medir quanto a classificação DORA muda quando se alteram as definições operacionais de lead time e de "
        "change failure rate, e verificar se as conclusões das RQ01 a RQ06 permanecem.\n",
        "## 2. Combinações de definições operacionais\n",
        "C1 é a referência. Em todas as combinações a classificação geral é a mediana dos 4 scores "
        "(Elite=4, High=3, Medium=2, Low=1) arredondada para baixo, com os mesmos cortes da Seção 5.\n",
        _md(defs) + "\n",
        "## 3. Reprodução\n",
        f"```\npython -m lab03.src.analise_rq07 --input {input_csv.as_posix()}\n```\n",
        f"Entrada: `{input_csv.name}` ({n_repos} repositórios). Saídas: `classificacao_dora_combinacoes.csv`, "
        "`rq07_*.csv`, `tabelas_artigo_sbc_rq07.tex` e as figuras `rq07_*.png/.pdf`.\n",
        "## 4. Resultados\n",
        "### 4.1 Distribuição da classificação geral por combinação\n",
        _md(dist_tab) + "\n",
        "### 4.2 Mudança de categoria e kappa ponderado por par\n",
        "`pct_melhoraram`/`pct_pioraram` são relativos à segunda combinação do par. O kappa usa pesos lineares na "
        "escala Low < Medium < High < Elite.\n",
        _md(pares_tab) + "\n",
        "### 4.3 Onde a mudança acontece (por métrica)\n",
        _md(sens_dim) + "\n",
        "### 4.4 RQ05 por definição de CFR\n",
        _md(rq05) + "\n",
        "### 4.5 RQ06 por combinação (Kruskal-Wallis do score geral, Holm global)\n",
        (_md(rq06[["combinacao", "fator", "n", "H", "gl", "p_bruto", "p_holm", "epsilon2", "significativo"]])
         if not rq06.empty else "Sem fatores estruturais disponíveis.") + "\n",
        "### 4.6 Figuras\n",
        "\n".join(f"- `{p.name}`" for p in figuras if p.suffix == ".png") + "\n",
        "## 5. Robustez das conclusões das RQ01 a RQ06\n",
        _md(robustez) + "\n",
        gerar_discussao(pares, sens_dim, robustez, combinacoes) + "\n",
        "## 6. Limitações\n",
        "- As combinações variam apenas lead time e CFR; a variante \"release publicada x release + pré-release\" só "
        "entra se o dataset tiver a coluna `deployment_frequency_with_prerelease_weekly` (C5).\n"
        "- Os cortes DORA e a regra da mediana com arredondamento para baixo são os mesmos em todas as combinações; "
        "mudar a regra de agregação poderia alterar a sensibilidade.\n"
        "- As variantes de lead time e de CFR são proxies de entrega e CI, não medidas diretas de deploy em produção.\n",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(texto), encoding="utf-8")
    return path


# ==============================================================================
# 6. Pipeline
# ==============================================================================

def verificar_colunas(df: pd.DataFrame) -> None:
    faltando = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if faltando:
        raise ValueError(f"Colunas obrigatórias ausentes no dataset: {faltando}")
    if len(df) == 0:
        raise ValueError("Dataset vazio.")
    if df["full_name"].duplicated().any():
        raise ValueError("Há repositórios duplicados em `full_name`.")


def conferir_c1_exportada(df: pd.DataFrame, cls: pd.DataFrame) -> Optional[int]:
    """Compara a C1 recalculada com `c1_overall_category` do CSV da Issue #39 (nº de divergências)."""
    if "c1_overall_category" not in df.columns:
        return None
    a = cls["C1_categoria"].astype(object).where(cls["C1_categoria"].notna(), None)
    b = df["c1_overall_category"].astype(object).where(df["c1_overall_category"].notna(), None)
    return int((a != b).sum())


def executar_pipeline_rq07(
    input_csv_path: Path,
    output_dir: Path,
    docs_dir: Optional[Path] = None,
    figures_dir: Optional[Path] = None,
    combinacoes_ids: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    """Executa a análise completa da RQ07 e grava tabelas, figuras e relatório."""
    if not input_csv_path.exists():
        raise FileNotFoundError(f"Arquivo CSV de entrada não encontrado: {input_csv_path}")
    output_dir.mkdir(parents=True, exist_ok=True)
    docs_dir = docs_dir or output_dir.parent / "docs"
    figures_dir = figures_dir or output_dir / "figuras"

    df = pd.read_csv(input_csv_path, encoding="utf-8")
    verificar_colunas(df)
    combinacoes = combinacoes_disponiveis(df, combinacoes_ids)

    cls = classificar_todas(df, combinacoes)
    divergencias_c1 = conferir_c1_exportada(df, cls)
    pares = comparar_todos_os_pares(cls, combinacoes)
    transicoes = matrizes_transicao_longas(cls, combinacoes)
    distribuicao = distribuicao_por_combinacao(cls, combinacoes)
    sens_dim = sensibilidade_por_dimensao(cls, combinacoes)

    rq02 = comparar_variantes(df, "lead_time_by_release_days", "lead_time_by_commit_days", classificar_lt, "Lead Time")
    rq03 = comparar_variantes(df, "cfr_ci_proxy", "cfr_delivery_proxy", classificar_cfr, "CFR")
    rq05 = rq05_por_variante_cfr(df, combinacoes)
    rq06 = rq06_por_combinacao(df, cls, combinacoes)
    robustez = resumir_robustez(sens_dim, rq02, rq03, rq05, rq06, pares)

    saidas = {
        "classificacao": output_dir / "classificacao_dora_combinacoes.csv",
        "pares": output_dir / "rq07_comparacao_pares.csv",
        "transicoes": output_dir / "rq07_matrizes_transicao.csv",
        "distribuicao": output_dir / "rq07_distribuicao_combinacoes.csv",
        "dimensoes": output_dir / "rq07_sensibilidade_dimensoes.csv",
        "rq05": output_dir / "rq07_rq05_por_cfr.csv",
        "rq06": output_dir / "rq07_rq06_por_combinacao.csv",
        "robustez": output_dir / "rq07_robustez_conclusoes.csv",
        "latex": output_dir / "tabelas_artigo_sbc_rq07.tex",
    }
    cls.to_csv(saidas["classificacao"], index=False, encoding="utf-8")
    pares.to_csv(saidas["pares"], index=False, encoding="utf-8")
    transicoes.to_csv(saidas["transicoes"], index=False, encoding="utf-8")
    distribuicao.to_csv(saidas["distribuicao"], index=False, encoding="utf-8")
    sens_dim.to_csv(saidas["dimensoes"], index=False, encoding="utf-8")
    rq05.to_csv(saidas["rq05"], index=False, encoding="utf-8")
    rq06.to_csv(saidas["rq06"], index=False, encoding="utf-8")
    robustez.to_csv(saidas["robustez"], index=False, encoding="utf-8")
    exportar_latex(pares, distribuicao, saidas["latex"])

    figuras = gerar_figuras(cls, combinacoes, pares, distribuicao, figures_dir)
    saidas["relatorio"] = gerar_relatorio(
        docs_dir / "analise_rq07.md", combinacoes, len(df), distribuicao, pares, sens_dim,
        rq05, rq06, robustez, rq02, rq03, figuras, input_csv_path,
    )

    return {
        "n_repositorios": len(df),
        "combinacoes": [c.id for c in combinacoes],
        "divergencias_c1_vs_csv": divergencias_c1,
        "classificacoes": cls,
        "pares": pares,
        "distribuicao": distribuicao,
        "sensibilidade_dimensoes": sens_dim,
        "rq02": rq02,
        "rq03": rq03,
        "rq05": rq05,
        "rq06": rq06,
        "robustez": robustez,
        "artefatos": saidas,
        "figuras": figuras,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="RQ07: sensibilidade das classificações DORA (LAB03S03 - Issue #41)")
    parser.add_argument("--input", default="lab03/data/classificacao_dora_c1.csv",
                        help="CSV com as métricas por repositório (saída da Issue #39)")
    parser.add_argument("--output-dir", default="lab03/data", help="Diretório das tabelas CSV/LaTeX")
    parser.add_argument("--docs-dir", default="lab03/docs", help="Diretório do relatório em Markdown")
    parser.add_argument("--figures-dir", default=None, help="Diretório das figuras (padrão: output-dir/figuras)")
    parser.add_argument("--combinacoes", default=None, help="Lista separada por vírgula, ex.: C1,C2,C3,C4")
    args = parser.parse_args()

    res = executar_pipeline_rq07(
        input_csv_path=Path(args.input),
        output_dir=Path(args.output_dir),
        docs_dir=Path(args.docs_dir),
        figures_dir=Path(args.figures_dir) if args.figures_dir else None,
        combinacoes_ids=args.combinacoes.split(",") if args.combinacoes else None,
    )

    print("=" * 80)
    print("RQ07 - SENSIBILIDADE DAS CLASSIFICAÇÕES DORA CONCLUÍDA")
    print("=" * 80)
    print(f"Repositórios: {res['n_repositorios']} | Combinações: {', '.join(res['combinacoes'])}")
    if res["divergencias_c1_vs_csv"] is not None:
        print(f"Divergências entre C1 recalculada e c1_overall_category do CSV: {res['divergencias_c1_vs_csv']}")
    for r in res["pares"].itertuples():
        print(f"  {r.par}: {r.pct_mudaram:5.1f}% mudaram | kappa_w = {r.kappa_ponderado_linear:.3f} ({r.interpretacao_kappa})")
    print("\nRobustez:")
    for r in res["robustez"].itertuples():
        print(f"  {r.rq}: {r.veredito}")
    print(f"\nRelatório: {res['artefatos']['relatorio']}")


if __name__ == "__main__":
    main()