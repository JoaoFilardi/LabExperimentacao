"""G1: comparação entre dados reais e simulados (histogramas lado a lado).

Issue: [LAB04S01] Implementar gráfico G1 de comparação entre dados reais e simulados.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from lab04.src.dados_reais import CAMINHO_DADOS_REAIS_PADRAO
from lab04.src.simulacao import GeradorDadosSimulados, ParametrosSimulacao

COL_GRUPO = "grupo"
COL_VALOR = "tempo_horas"
UNIDADE = "horas"
GRUPOS = ["sem_bot", "com_bot"]
ROTULO_GRUPO = {"sem_bot": "Sem bot (controle)", "com_bot": "Com bot (tratamento)"}
COR_REAL = "#1f77b4"
COR_SIM = "#ff7f0e"
COR_OUTLIER = "#d62728"


def carregar_reais(caminho: Path | str = CAMINHO_DADOS_REAIS_PADRAO) -> pd.DataFrame:
    return pd.read_csv(caminho)


def carregar_simulados(semente: int = 42) -> pd.DataFrame:
    """Gera em memória o mesmo dataset da S01 (H1 observada, n=30 por grupo)."""
    gerador = GeradorDadosSimulados(semente=semente)
    return gerador.gerar_dataset_experimento(n_sem_bot=30, n_com_bot=30, sob_h0=False)


def _limite_outlier(serie: pd.Series) -> float:
    """Cerca superior de Tukey: Q3 + 1,5 * IQR."""
    q1, q3 = serie.quantile([0.25, 0.75])
    return q3 + 1.5 * (q3 - q1)


def _resumo(serie: pd.Series) -> dict:
    return {
        "n": len(serie),
        "media": serie.mean(),
        "mediana": serie.median(),
        "dp": serie.std(),
        "assimetria": serie.skew(),
        "n_outliers": int((serie > _limite_outlier(serie)).sum()),
    }


def obter_tabela_comparativa_g1(reais: pd.DataFrame, simulados: pd.DataFrame) -> pd.DataFrame:
    """Gera tabela comparativa com estatísticas descritivas dos dados reais e simulados."""
    linhas = []
    fontes = [
        ("Dados Reais (tiangolo/fastapi)", reais),
        ("Dados Simulados S01 (semente = 42)", simulados),
    ]
    for nome_fonte, df in fontes:
        for g in GRUPOS:
            serie = df.loc[df[COL_GRUPO] == g, COL_VALOR].dropna()
            r = _resumo(serie)
            q1, q3 = serie.quantile([0.25, 0.75])
            linhas.append(
                {
                    "Origem": nome_fonte,
                    "Grupo": ROTULO_GRUPO[g],
                    "n": r["n"],
                    "Média (h)": round(r["media"], 2),
                    "Mediana (h)": round(r["mediana"], 2),
                    "DP (h)": round(r["dp"], 2),
                    "IQR (h)": round(q3 - q1, 2),
                    "Assimetria": round(r["assimetria"], 2),
                    "Outliers (Tukey)": r["n_outliers"],
                    "Máximo (h)": round(float(serie.max()), 2),
                }
            )
    return pd.DataFrame(linhas)


def gerar_g1(reais: pd.DataFrame, simulados: pd.DataFrame, n_bins: int = 15):
    """Retorna uma Figure 2x2: linhas = grupos, colunas = (reais, simulados)."""
    todos = np.concatenate([reais[COL_VALOR].to_numpy(), simulados[COL_VALOR].to_numpy()])
    bins = np.histogram_bin_edges(todos, bins=n_bins)  # mesmos intervalos em todos os painéis

    fig, eixos = plt.subplots(2, 2, figsize=(11, 7), sharex=True, sharey=True)

    for i, grupo in enumerate(GRUPOS):
        fontes = [
            ("Reais", COR_REAL, reais),
            ("Simulados", COR_SIM, simulados),
        ]
        for j, (nome, cor, df) in enumerate(fontes):
            ax = eixos[i][j]
            serie = df.loc[df[COL_GRUPO] == grupo, COL_VALOR].dropna()
            r = _resumo(serie)

            ax.hist(serie, bins=bins, color=cor, alpha=0.85, edgecolor="white")
            ax.axvline(r["mediana"], color="black", ls="--", lw=1.2,
                       label=f"Mediana = {r['mediana']:.1f} h")
            ax.axvline(r["media"], color="gray", ls=":", lw=1.5,
                       label=f"Média = {r['media']:.1f} h")

            outliers = serie[serie > _limite_outlier(serie)]
            if len(outliers):
                ax.plot(outliers, np.full(len(outliers), 0.15), "v",
                        color=COR_OUTLIER, markersize=7, label="Outlier (Tukey)")

            ax.set_title(f"{ROTULO_GRUPO[grupo]} – {nome} (n = {r['n']})", fontsize=11)
            ax.text(0.97, 0.60,
                    f"DP = {r['dp']:.1f} h\nAssimetria = {r['assimetria']:.2f}\n"
                    f"Outliers = {r['n_outliers']}",
                    transform=ax.transAxes, ha="right", va="top", fontsize=9,
                    bbox=dict(boxstyle="round", fc="white", ec="lightgray", alpha=0.9))
            ax.legend(loc="upper right", fontsize=8)
            ax.grid(axis="y", alpha=0.25)

            if j == 0:
                ax.set_ylabel("Frequência (nº de PRs)")
            if i == 1:
                ax.set_xlabel(f"Tempo até o merge ({UNIDADE})")

    fig.suptitle("G1 – Tempo até o merge de PRs: dados reais vs. simulados", fontsize=14)
    fig.tight_layout()
    return fig


def texto_interpretativo(reais: pd.DataFrame, simulados: pd.DataFrame) -> str:
    """Texto de 4 frases gerado a partir dos próprios dados (sempre consistente com o gráfico)."""
    def stats(df, g):
        return _resumo(df.loc[df[COL_GRUPO] == g, COL_VALOR])

    rs, rc = stats(reais, "sem_bot"), stats(reais, "com_bot")
    ss, sc = stats(simulados, "sem_bot"), stats(simulados, "com_bot")
    p = ParametrosSimulacao()

    texto = (
        f"Nos dados reais, a mediana do tempo até o merge é {rs['mediana']:.1f} h sem bot e "
        f"{rc['mediana']:.1f} h com bot, com assimetria positiva "
        f"({rs['assimetria']:.2f} e {rc['assimetria']:.2f}) e cauda longa à direita. "
        f"Os dados simulados (n = {ss['n']} por grupo) reproduzem esse formato, com medianas de "
        f"{ss['mediana']:.1f} h e {sc['mediana']:.1f} h e assimetria positiva. "
        f"Os parâmetros log-normais usados (μ = {p.mu_log_sem_bot:.2f} e σ = {p.sigma_log_sem_bot:.2f} sem bot; "
        f"μ = {p.mu_log_com_bot:.2f} e σ = {p.sigma_log_com_bot:.2f} com bot) foram ajustados às "
        f"medianas e à dispersão logarítmica da amostra real. "
        f"Os outliers (reais: {rs['n_outliers']} e {rc['n_outliers']}; simulados: "
        f"{ss['n_outliers']} e {sc['n_outliers']}) ficam na cauda direita, como esperado para tempos de processo."
    )
    return texto.replace(".", ",", 0)  # mantém como está; ajuste de vírgula decimal opcional


if __name__ == "__main__":
    reais, simulados = carregar_reais(), carregar_simulados()
    fig = gerar_g1(reais, simulados)
    saida = Path(__file__).resolve().parent.parent / "data" / "g1_reais_vs_simulados.png"
    fig.savefig(saida, dpi=150, bbox_inches="tight")
    print(f"G1 salvo em: {saida}")
    print(texto_interpretativo(reais, simulados))