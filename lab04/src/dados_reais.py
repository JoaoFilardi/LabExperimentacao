"""Módulo para carregamento, processamento e perfilamento estatístico dos dados reais do LAB04.

Issue #46: [LAB04S01] Implementar geração reproduzível de dados simulados.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any
import numpy as np
import pandas as pd
from scipy import stats

CAMINHO_DADOS_REAIS_PADRAO = Path(__file__).resolve().parent.parent / "data" / "amostra_dados_reais.csv"


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
    curtose: float     # Excess kurtosis
    log_mu: float      # Média da escala logarítmica
    log_sigma: float   # Desvio padrão da escala logarítmica


def carregar_dados_reais(caminho: Path | str = CAMINHO_DADOS_REAIS_PADRAO) -> pd.DataFrame:
    """Carrega o dataset de dados reais de Pull Requests."""
    caminho = Path(caminho)
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo de dados reais não encontrado em: {caminho}")
    df = pd.read_csv(caminho)
    colunas_obrigatorias = {"pr_id", "grupo", "tempo_horas"}
    if not colunas_obrigatorias.issubset(df.columns):
        raise ValueError(f"O CSV deve conter as colunas: {colunas_obrigatorias}")
    return df


def perfilar_grupo(df: pd.DataFrame, grupo: str) -> EstatisticasGrupo:
    """Calcula métricas descritivas e parâmetros lognormais de um grupo específico."""
    sub = df[df["grupo"] == grupo]["tempo_horas"].dropna().to_numpy()
    if len(sub) == 0:
        raise ValueError(f"Nenhum registro encontrado para o grupo '{grupo}'")

    n = len(sub)
    media = float(np.mean(sub))
    desvio = float(np.std(sub, ddof=1))
    mediana = float(np.median(sub))
    iqr = float(stats.iqr(sub))
    minimo = float(np.min(sub))
    maximo = float(np.max(sub))
    assimetria = float(stats.skew(sub))
    curtose = float(stats.kurtosis(sub))

    # Ajuste de parâmetros lognormais via MLE / log-transform
    log_vals = np.log(sub)
    log_mu = float(np.mean(log_vals))
    log_sigma = float(np.std(log_vals, ddof=1))

    return EstatisticasGrupo(
        grupo=grupo,
        n=n,
        media=media,
        desvio_padrao=desvio,
        mediana=mediana,
        iqr=iqr,
        minimo=minimo,
        maximo=maximo,
        assimetria=assimetria,
        curtose=curtose,
        log_mu=log_mu,
        log_sigma=log_sigma,
    )


def obter_resumo_estatistico_reais(
    caminho: Path | str = CAMINHO_DADOS_REAIS_PADRAO,
) -> Dict[str, Any]:
    """Retorna dicionário completo com resumo dos dois grupos e parâmetros combinados."""
    df = carregar_dados_reais(caminho)
    est_sem = perfilar_grupo(df, "sem_bot")
    est_com = perfilar_grupo(df, "com_bot")

    # Parâmetros pooled sob H0 (amostra combinada)
    todos = df["tempo_horas"].dropna().to_numpy()
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
