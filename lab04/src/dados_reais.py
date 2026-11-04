"""Carregamento, validação e perfilamento estatístico dos dados reais do LAB04.

Issue LAB04S01 (coleta e análise de amostra real): este módulo verifica a qualidade
do CSV (ausentes, duplicações, inconsistências), calcula estatísticas descritivas,
analisa a forma das distribuições (assimetria, curtose, outliers, normalidade) e
disponibiliza os parâmetros lognormais usados pela simulação.

Uso como script (a partir da raiz do repositório):
    python -m lab04.src.dados_reais
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from scipy import stats

CAMINHO_DADOS_REAIS_PADRAO = Path(__file__).resolve().parent.parent / "data" / "amostra_dados_reais.csv"
CAMINHO_ESTATISTICAS_PADRAO = (
    Path(__file__).resolve().parent.parent / "data" / "estatisticas_descritivas_reais.csv"
)

GRUPOS = ("sem_bot", "com_bot")
COLUNAS_OBRIGATORIAS = {"pr_id", "grupo", "tempo_horas"}
COLUNAS_COLETA = {"repositorio", "bot_presente", "created_at", "merged_at"}
TOLERANCIA_HORAS = 0.05  # diferença máxima aceita entre tempo_horas e (merged_at - created_at)


@dataclass(frozen=True)
class EstatisticasGrupo:
    """Sumário estatístico descritivo de um grupo."""

    grupo: str
    n: int
    media: float
    desvio_padrao: float
    mediana: float
    iqr: float
    minimo: float
    maximo: float
    assimetria: float  # Skewness
    curtose: float  # Excess kurtosis
    log_mu: float  # Média da escala logarítmica
    log_sigma: float  # Desvio padrão da escala logarítmica
    # Campos adicionados na LAB04S01 (com default para manter compatibilidade)
    q1: float = float("nan")
    q3: float = float("nan")
    coef_variacao: float = float("nan")
    n_outliers_iqr: int = 0
    shapiro_p_bruto: float = float("nan")
    shapiro_p_log: float = float("nan")


# ----------------------------------------------------------------------------
# Carregamento
# ----------------------------------------------------------------------------
def carregar_dados_reais(caminho: Path | str = CAMINHO_DADOS_REAIS_PADRAO) -> pd.DataFrame:
    """Carrega o dataset de dados reais de Pull Requests."""
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo de dados reais não encontrado em: {caminho}")
    df = pd.read_csv(caminho)
    if not COLUNAS_OBRIGATORIAS.issubset(df.columns):
        raise ValueError(f"O CSV deve conter as colunas: {COLUNAS_OBRIGATORIAS}")
    return df


# ----------------------------------------------------------------------------
# Qualidade dos dados
# ----------------------------------------------------------------------------
def validar_qualidade(df: pd.DataFrame) -> Dict[str, Any]:
    """Verifica valores ausentes, duplicações e inconsistências.

    Retorna um dicionário com contagens e uma lista legível de `problemas`.
    `ok` é True quando nenhum problema foi encontrado.
    """
    problemas: List[str] = []

    ausentes = {c: int(v) for c, v in df.isna().sum().items() if v > 0}
    if ausentes:
        problemas.append(f"Valores ausentes: {ausentes}")

    n_dup_id = int(df["pr_id"].duplicated().sum())
    if n_dup_id:
        problemas.append(f"{n_dup_id} pr_id duplicado(s)")
    n_dup_linhas = int(df.duplicated().sum())
    if n_dup_linhas:
        problemas.append(f"{n_dup_linhas} linha(s) totalmente duplicada(s)")

    grupos_invalidos = sorted(set(df["grupo"].dropna()) - set(GRUPOS))
    if grupos_invalidos:
        problemas.append(f"Rótulos de grupo inesperados: {grupos_invalidos}")

    tempo = pd.to_numeric(df["tempo_horas"], errors="coerce")
    n_nao_positivo = int((tempo <= 0).sum())
    if n_nao_positivo:
        problemas.append(f"{n_nao_positivo} tempo(s) <= 0 (inviável para escala log)")

    n_incons_tempo = 0
    n_merge_antes = 0
    n_incons_bot = 0
    if {"created_at", "merged_at"}.issubset(df.columns):
        criado = pd.to_datetime(df["created_at"], errors="coerce")
        mesclado = pd.to_datetime(df["merged_at"], errors="coerce")
        calc = (mesclado - criado).dt.total_seconds() / 3600
        n_merge_antes = int((calc < 0).sum())
        n_incons_tempo = int(((calc - tempo).abs() > TOLERANCIA_HORAS).sum())
        if n_merge_antes:
            problemas.append(f"{n_merge_antes} PR(s) com merged_at anterior a created_at")
        if n_incons_tempo:
            problemas.append(
                f"{n_incons_tempo} PR(s) com tempo_horas diferente de merged_at - created_at"
            )
    if "bot_presente" in df.columns:
        presente = df["bot_presente"].astype(str).str.lower().isin(["true", "1"])
        n_incons_bot = int((presente != (df["grupo"] == "com_bot")).sum())
        if n_incons_bot:
            problemas.append(f"{n_incons_bot} PR(s) com bot_presente incoerente com o grupo")

    return {
        "n_linhas": int(len(df)),
        "n_por_grupo": {g: int((df["grupo"] == g).sum()) for g in GRUPOS},
        "ausentes": ausentes,
        "duplicados_pr_id": n_dup_id,
        "linhas_duplicadas": n_dup_linhas,
        "grupos_invalidos": grupos_invalidos,
        "tempos_nao_positivos": n_nao_positivo,
        "merge_antes_da_criacao": n_merge_antes,
        "inconsistencia_tempo": n_incons_tempo,
        "inconsistencia_bot": n_incons_bot,
        "problemas": problemas,
        "ok": not problemas,
    }


def sinais_de_amostra_nao_aleatoria(df: pd.DataFrame) -> List[str]:
    """Alertas heurísticos sobre a forma como a amostra foi organizada.

    Não são erros de dados, mas pontos que devem ser explicados na documentação
    (ex.: linhas ordenadas por tempo, pr_id sequencial, ciclo fixo de bots).
    """
    alertas: List[str] = []
    for g in GRUPOS:
        sub = df[df["grupo"] == g]
        if len(sub) > 2 and sub["tempo_horas"].is_monotonic_increasing:
            alertas.append(f"Grupo '{g}': linhas ordenadas por tempo_horas (ordem não é a de coleta).")
    ids = np.sort(df["pr_id"].to_numpy())
    if len(ids) > 2 and np.all(np.diff(ids) == 1):
        alertas.append(
            "pr_id forma uma sequência contínua sem lacunas; PRs reais de um repositório "
            "ativo raramente são consecutivos (issues e PRs compartilham a numeração)."
        )
    if "nome_bot" in df.columns:
        bots = df.loc[df["grupo"] == "com_bot", "nome_bot"].tolist()
        for p in (2, 3, 4):
            if len(bots) >= 2 * p and all(bots[i] == bots[i % p] for i in range(len(bots))):
                alertas.append(f"Coluna nome_bot repete um ciclo fixo de {p} valores.")
                break
    return alertas


# ----------------------------------------------------------------------------
# Estatísticas descritivas e forma da distribuição
# ----------------------------------------------------------------------------
def limites_outliers_iqr(valores: np.ndarray, k: float = 1.5) -> tuple[float, float]:
    """Cercas de Tukey: [Q1 - k*IQR, Q3 + k*IQR]."""
    q1, q3 = np.percentile(valores, [25, 75])
    iqr = q3 - q1
    return float(q1 - k * iqr), float(q3 + k * iqr)


def detectar_outliers_iqr(df: pd.DataFrame, grupo: str, k: float = 1.5) -> pd.DataFrame:
    """Retorna as linhas do grupo que ficam fora das cercas de Tukey."""
    sub = df[df["grupo"] == grupo]
    inf, sup = limites_outliers_iqr(sub["tempo_horas"].to_numpy(), k)
    return sub[(sub["tempo_horas"] < inf) | (sub["tempo_horas"] > sup)]


def perfilar_grupo(df: pd.DataFrame, grupo: str) -> EstatisticasGrupo:
    """Calcula métricas descritivas e parâmetros lognormais de um grupo específico."""
    sub = df[df["grupo"] == grupo]["tempo_horas"].dropna().to_numpy(dtype=float)
    if len(sub) == 0:
        raise ValueError(f"Nenhum registro encontrado para o grupo '{grupo}'")

    n = len(sub)
    media = float(np.mean(sub))
    desvio = float(np.std(sub, ddof=1)) if n > 1 else float("nan")
    q1, q3 = (float(x) for x in np.percentile(sub, [25, 75]))

    log_vals = np.log(sub)  # exige tempos > 0 (ver validar_qualidade)
    shapiro_bruto = float(stats.shapiro(sub).pvalue) if n >= 3 else float("nan")
    shapiro_log = float(stats.shapiro(log_vals).pvalue) if n >= 3 else float("nan")
    inf, sup = limites_outliers_iqr(sub)

    return EstatisticasGrupo(
        grupo=grupo,
        n=n,
        media=media,
        desvio_padrao=desvio,
        mediana=float(np.median(sub)),
        iqr=float(stats.iqr(sub)),
        minimo=float(np.min(sub)),
        maximo=float(np.max(sub)),
        assimetria=float(stats.skew(sub)),
        curtose=float(stats.kurtosis(sub)),
        log_mu=float(np.mean(log_vals)),
        log_sigma=float(np.std(log_vals, ddof=1)) if n > 1 else float("nan"),
        q1=q1,
        q3=q3,
        coef_variacao=desvio / media if media else float("nan"),
        n_outliers_iqr=int(np.sum((sub < inf) | (sub > sup))),
        shapiro_p_bruto=shapiro_bruto,
        shapiro_p_log=shapiro_log,
    )


def obter_resumo_estatistico_reais(
    caminho: Path | str = CAMINHO_DADOS_REAIS_PADRAO,
) -> Dict[str, Any]:
    """Retorna dicionário completo com resumo dos dois grupos e parâmetros combinados."""
    df = carregar_dados_reais(caminho)
    est_sem = perfilar_grupo(df, "sem_bot")
    est_com = perfilar_grupo(df, "com_bot")

    # Parâmetros pooled sob H0 (amostra combinada)
    todos = df["tempo_horas"].dropna().to_numpy(dtype=float)
    log_todos = np.log(todos)

    return {
        "sem_bot": est_sem,
        "com_bot": est_com,
        "h0_pooled": {
            "n_total": len(todos),
            "mediana_pooled": float(np.median(todos)),
            "media_pooled": float(np.mean(todos)),
            "log_mu_pooled": float(np.mean(log_todos)),
            "log_sigma_pooled": float(np.std(log_todos, ddof=1)),
        },
    }


def estatisticas_para_dataframe(resumo: Dict[str, Any]) -> pd.DataFrame:
    """Tabela (uma linha por grupo) pronta para CSV/dashboard."""
    return pd.DataFrame([asdict(resumo[g]) for g in GRUPOS])


def salvar_estatisticas(
    caminho_dados: Path | str = CAMINHO_DADOS_REAIS_PADRAO,
    caminho_saida: Path | str = CAMINHO_ESTATISTICAS_PADRAO,
) -> Path:
    """Calcula e grava as estatísticas descritivas em CSV."""
    resumo = obter_resumo_estatistico_reais(caminho_dados)
    saida = Path(caminho_saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    estatisticas_para_dataframe(resumo).to_csv(saida, index=False, float_format="%.6g")
    return saida


def interpretar_forma(est: EstatisticasGrupo) -> List[str]:
    """Frases curtas descrevendo a forma da distribuição, úteis para o dashboard."""
    notas = []
    if est.assimetria > 1:
        notas.append(f"assimetria forte à direita (skew = {est.assimetria:.2f})")
    elif est.assimetria > 0.5:
        notas.append(f"assimetria moderada à direita (skew = {est.assimetria:.2f})")
    else:
        notas.append(f"aproximadamente simétrica (skew = {est.assimetria:.2f})")
    notas.append(f"média ({est.media:.1f} h) {'>' if est.media > est.mediana else '<='} mediana ({est.mediana:.1f} h)")
    notas.append(f"{est.n_outliers_iqr} outlier(s) pelo critério de Tukey (1,5·IQR)")
    if est.shapiro_p_bruto < 0.05:
        notas.append(f"normalidade rejeitada na escala original (Shapiro p = {est.shapiro_p_bruto:.3g})")
    else:
        notas.append(f"normalidade não rejeitada na escala original (Shapiro p = {est.shapiro_p_bruto:.3g})")
    if est.shapiro_p_log >= 0.05:
        notas.append(f"escala log compatível com normal (Shapiro p = {est.shapiro_p_log:.3g}) → lognormal plausível")
    else:
        notas.append(f"escala log também rejeita normalidade (Shapiro p = {est.shapiro_p_log:.3g})")
    return notas


def gerar_relatorio(caminho: Path | str = CAMINHO_DADOS_REAIS_PADRAO) -> str:
    """Relatório textual da análise descritiva (qualidade + estatísticas + forma)."""
    df = carregar_dados_reais(caminho)
    q = validar_qualidade(df)
    resumo = obter_resumo_estatistico_reais(caminho)
    linhas = ["=== QUALIDADE DOS DADOS ===", f"Linhas: {q['n_linhas']}  Por grupo: {q['n_por_grupo']}"]
    linhas.append("Nenhum problema encontrado." if q["ok"] else "Problemas: " + "; ".join(q["problemas"]))
    for alerta in sinais_de_amostra_nao_aleatoria(df):
        linhas.append(f"ATENÇÃO: {alerta}")
    for g in GRUPOS:
        e = resumo[g]
        linhas += [
            "",
            f"=== {g} (n={e.n}) ===",
            f"média={e.media:.2f}  dp={e.desvio_padrao:.2f}  CV={e.coef_variacao:.2f}",
            f"min={e.minimo:.2f}  Q1={e.q1:.2f}  mediana={e.mediana:.2f}  Q3={e.q3:.2f}  max={e.maximo:.2f}  IQR={e.iqr:.2f}",
            f"skew={e.assimetria:.2f}  curtose={e.curtose:.2f}  outliers(IQR)={e.n_outliers_iqr}",
            f"lognormal: mu={e.log_mu:.3f}  sigma={e.log_sigma:.3f}",
        ]
        linhas += [f"- {n}" for n in interpretar_forma(e)]
    h = resumo["h0_pooled"]
    linhas += [
        "",
        "=== PARÂMETROS POOLED (H0) ===",
        f"n={h['n_total']}  mediana={h['mediana_pooled']:.2f}  média={h['media_pooled']:.2f}  "
        f"mu_log={h['log_mu_pooled']:.3f}  sigma_log={h['log_sigma_pooled']:.3f}",
    ]
    return "\n".join(linhas)


if __name__ == "__main__":  # pragma: no cover
    print(gerar_relatorio())
    print(f"\nEstatísticas gravadas em: {salvar_estatisticas()}")