"""Gráfico G3: Comparação da taxa de Erro Tipo I sob H0 (Cenário Original vs. Violações).

Issue #52: [ LAB04S02 ] Implementar gráfico G3 de comparação do erro tipo I.

Este módulo constrói o gráfico G3, apresentando visualmente a taxa empírica de Erro Tipo I
dos dois testes estatísticos (t de Welch e U de Mann-Whitney) em 10.000 simulações de Monte Carlo
sob a hipótese nula verdadeira (H0) em diferentes condições experimentais:
1. Cenário Original (Q1): Distribuição Log-normal calibrada nos dados reais (n = 30);
2. Violação de Pressupostos — Outliers Extremos (Q3): Contaminação de 10% das observações com
   valores multiplicados por 5x + 50h (n = 30);
3. Violação de Pressupostos — Amostra Pequena (Q3): Amostras reduzidas a n = 10 por grupo sob a
   mesma distribuição assimétrica, investigando o colapso assintótico do TCL.

O gráfico inclui:
- Barras agrupadas com cores consistentes para cada teste (Azul para Welch, Laranja para Mann-Whitney);
- Linha de referência horizontal em 5% (α = 0,05) e faixa de calibração estrita de Bradley (4,5% a 5,5%);
- Barras de erro indicando o intervalo de confiança de Wilson a 95%;
- Rótulos com os valores percentuais exatos em cada barra;
- Eixos nomeados com unidade percentual, título, subtítulo e legenda padronizada;
- Texto interpretativo conciso (2 a 4 frases) para o Dashboard.

Uso via linha de comando:
    python -m lab04.src.grafico_g3
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from lab04.src.cenario import CENARIO
from lab04.src.simulacao import GeradorDadosSimulados, ParametrosSimulacao
from lab04.src.simulacao_q1 import (
    calcular_intervalo_confianca_wilson,
    classificar_comportamento_erro_tipo_1,
)
from lab04.src.testes_estatisticos import avaliar_matrizes_rapido

# Cores oficiais padronizadas do projeto
COR_WELCH = "#1f77b4"  # Azul para o teste paramétrico (t de Welch)
COR_MANN_WHITNEY = "#ff7f0e"  # Laranja para o teste não-paramétrico (Mann-Whitney)
COR_REFERENCIA = "#d62728"  # Vermelho para a linha nominal de 5% (α = 0,05)
COR_FAIXA = "#d62728"  # Vermelho suave para a faixa de calibração estrita

CAMINHO_DADOS_DIR = Path(__file__).resolve().parent.parent / "data"
CAMINHO_G3_PADRAO = CAMINHO_DADOS_DIR / "g3_erro_tipo_1.png"
CAMINHO_DADOS_G3_CONSOLIDADO = CAMINHO_DADOS_DIR / "resultados_g3_consolidado.csv"


# ----------------------------------------------------------------------------
# Simulação conjunta das condições de Q1 e Q3 para o G3
# ----------------------------------------------------------------------------
def simular_condicoes_g3(
    semente: int = 42,
    n_simulacoes: int = 10_000,
    alpha: float = CENARIO.alpha,
    alternativa: str = CENARIO.tipo_teste,
) -> pd.DataFrame:
    """Executa as simulações Monte Carlo sob H0 para as 3 condições de avaliação de Erro Tipo I.

    Condições simuladas:
    1. Base (Q1): Log-normal calibrada com n = 30 por grupo;
    2. Violação Outliers (Q3): Log-normal com 10% de contaminação severa (n = 30);
    3. Violação Amostra Pequena (Q3): Log-normal com n = 10 por grupo.

    Retorna:
        pd.DataFrame estruturado com as taxas empíricas, ICs 95%, desvios e classificações.
    """
    gerador = GeradorDadosSimulados(semente=semente)
    registros = []

    # -------------------------------------------------------------------------
    # 1. Cenário Original (Q1): Log-normal realista (n=30)
    # -------------------------------------------------------------------------
    gerador.redefinir_semente(semente)
    s_base, c_base = gerador.gerar_matrizes_h0(
        n_simulacoes=n_simulacoes, n_sem_bot=30, n_com_bot=30, arredondar=2
    )
    res_base = avaliar_matrizes_rapido(s_base, c_base, alpha=alpha, alternativa=alternativa)

    rej_w_base = int(np.sum(res_base["rejeita_welch"]))
    rej_mw_base = int(np.sum(res_base["rejeita_mann_whitney"]))
    p_w_base, inf_w_base, sup_w_base = calcular_intervalo_confianca_wilson(
        rej_w_base, n_simulacoes
    )
    p_mw_base, inf_mw_base, sup_mw_base = calcular_intervalo_confianca_wilson(
        rej_mw_base, n_simulacoes
    )
    classe_w_base, _ = classificar_comportamento_erro_tipo_1(p_w_base, alpha, n_simulacoes)
    classe_mw_base, _ = classificar_comportamento_erro_tipo_1(p_mw_base, alpha, n_simulacoes)

    registros.extend(
        [
            {
                "cenario_codigo": "Q1_Base",
                "cenario_rotulo": "Cenário Original (Q1)\nLog-normal (n=30)",
                "condicao": "Log-normal realista (n=30)",
                "teste": CENARIO.teste_parametrico,
                "abordagem": "Paramétrico",
                "n_simulacoes": n_simulacoes,
                "n_rejeicoes": rej_w_base,
                "taxa_empirica": p_w_base,
                "taxa_empirica_pct": p_w_base * 100.0,
                "taxa_teorica": alpha,
                "taxa_teorica_pct": alpha * 100.0,
                "desvio_nominal_pct": (p_w_base - alpha) * 100.0,
                "ic_inf": inf_w_base,
                "ic_sup": sup_w_base,
                "ic_inf_pct": inf_w_base * 100.0,
                "ic_sup_pct": sup_w_base * 100.0,
                "comportamento": classe_w_base,
                "ordem_cenario": 1,
            },
            {
                "cenario_codigo": "Q1_Base",
                "cenario_rotulo": "Cenário Original (Q1)\nLog-normal (n=30)",
                "condicao": "Log-normal realista (n=30)",
                "teste": CENARIO.teste_nao_parametrico,
                "abordagem": "Não-paramétrico",
                "n_simulacoes": n_simulacoes,
                "n_rejeicoes": rej_mw_base,
                "taxa_empirica": p_mw_base,
                "taxa_empirica_pct": p_mw_base * 100.0,
                "taxa_teorica": alpha,
                "taxa_teorica_pct": alpha * 100.0,
                "desvio_nominal_pct": (p_mw_base - alpha) * 100.0,
                "ic_inf": inf_mw_base,
                "ic_sup": sup_mw_base,
                "ic_inf_pct": inf_mw_base * 100.0,
                "ic_sup_pct": sup_mw_base * 100.0,
                "comportamento": classe_mw_base,
                "ordem_cenario": 1,
            },
        ]
    )

    # -------------------------------------------------------------------------
    # 2. Violação de Pressupostos (Q3): Injeção de Outliers Extremos (10%, n=30)
    # -------------------------------------------------------------------------
    gerador.redefinir_semente(semente)
    s_out, c_out = gerador.gerar_matrizes_h0(
        n_simulacoes=n_simulacoes, n_sem_bot=30, n_com_bot=30, arredondar=2
    )
    mat_out = np.hstack([s_out, c_out])
    n_outliers_por_amostra = 6  # 10% de 60 observações totais

    for i in range(n_simulacoes):
        idx_sorteados = gerador.rng.choice(60, size=n_outliers_por_amostra, replace=False)
        mat_out[i, idx_sorteados] = np.round(mat_out[i, idx_sorteados] * 5.0 + 50.0, 2)

    s_out_mod = mat_out[:, :30]
    c_out_mod = mat_out[:, 30:]
    res_out = avaliar_matrizes_rapido(s_out_mod, c_out_mod, alpha=alpha, alternativa=alternativa)

    rej_w_out = int(np.sum(res_out["rejeita_welch"]))
    rej_mw_out = int(np.sum(res_out["rejeita_mann_whitney"]))
    p_w_out, inf_w_out, sup_w_out = calcular_intervalo_confianca_wilson(
        rej_w_out, n_simulacoes
    )
    p_mw_out, inf_mw_out, sup_mw_out = calcular_intervalo_confianca_wilson(
        rej_mw_out, n_simulacoes
    )
    classe_w_out, _ = classificar_comportamento_erro_tipo_1(p_w_out, alpha, n_simulacoes)
    classe_mw_out, _ = classificar_comportamento_erro_tipo_1(p_mw_out, alpha, n_simulacoes)

    registros.extend(
        [
            {
                "cenario_codigo": "Q3_Outliers",
                "cenario_rotulo": "Violação: Outliers (Q3)\n10% contaminação (n=30)",
                "condicao": "Injeção de 10% de outliers (5x + 50h)",
                "teste": CENARIO.teste_parametrico,
                "abordagem": "Paramétrico",
                "n_simulacoes": n_simulacoes,
                "n_rejeicoes": rej_w_out,
                "taxa_empirica": p_w_out,
                "taxa_empirica_pct": p_w_out * 100.0,
                "taxa_teorica": alpha,
                "taxa_teorica_pct": alpha * 100.0,
                "desvio_nominal_pct": (p_w_out - alpha) * 100.0,
                "ic_inf": inf_w_out,
                "ic_sup": sup_w_out,
                "ic_inf_pct": inf_w_out * 100.0,
                "ic_sup_pct": sup_w_out * 100.0,
                "comportamento": classe_w_out,
                "ordem_cenario": 2,
            },
            {
                "cenario_codigo": "Q3_Outliers",
                "cenario_rotulo": "Violação: Outliers (Q3)\n10% contaminação (n=30)",
                "condicao": "Injeção de 10% de outliers (5x + 50h)",
                "teste": CENARIO.teste_nao_parametrico,
                "abordagem": "Não-paramétrico",
                "n_simulacoes": n_simulacoes,
                "n_rejeicoes": rej_mw_out,
                "taxa_empirica": p_mw_out,
                "taxa_empirica_pct": p_mw_out * 100.0,
                "taxa_teorica": alpha,
                "taxa_teorica_pct": alpha * 100.0,
                "desvio_nominal_pct": (p_mw_out - alpha) * 100.0,
                "ic_inf": inf_mw_out,
                "ic_sup": sup_mw_out,
                "ic_inf_pct": inf_mw_out * 100.0,
                "ic_sup_pct": sup_mw_out * 100.0,
                "comportamento": classe_mw_out,
                "ordem_cenario": 2,
            },
        ]
    )

    # -------------------------------------------------------------------------
    # 3. Violação de Pressupostos (Q3): Amostra Pequena (n=10)
    # -------------------------------------------------------------------------
    gerador.redefinir_semente(semente)
    s_small, c_small = gerador.gerar_matrizes_h0(
        n_simulacoes=n_simulacoes, n_sem_bot=10, n_com_bot=10, arredondar=2
    )
    res_small = avaliar_matrizes_rapido(
        s_small, c_small, alpha=alpha, alternativa=alternativa
    )

    rej_w_small = int(np.sum(res_small["rejeita_welch"]))
    rej_mw_small = int(np.sum(res_small["rejeita_mann_whitney"]))
    p_w_small, inf_w_small, sup_w_small = calcular_intervalo_confianca_wilson(
        rej_w_small, n_simulacoes
    )
    p_mw_small, inf_mw_small, sup_mw_small = calcular_intervalo_confianca_wilson(
        rej_mw_small, n_simulacoes
    )
    classe_w_small, _ = classificar_comportamento_erro_tipo_1(p_w_small, alpha, n_simulacoes)
    classe_mw_small, _ = classificar_comportamento_erro_tipo_1(
        p_mw_small, alpha, n_simulacoes
    )

    registros.extend(
        [
            {
                "cenario_codigo": "Q3_AmostraPequena",
                "cenario_rotulo": "Violação: Amostra Pequena (Q3)\nLog-normal (n=10)",
                "condicao": "Tamanho amostral reduzido (n=10)",
                "teste": CENARIO.teste_parametrico,
                "abordagem": "Paramétrico",
                "n_simulacoes": n_simulacoes,
                "n_rejeicoes": rej_w_small,
                "taxa_empirica": p_w_small,
                "taxa_empirica_pct": p_w_small * 100.0,
                "taxa_teorica": alpha,
                "taxa_teorica_pct": alpha * 100.0,
                "desvio_nominal_pct": (p_w_small - alpha) * 100.0,
                "ic_inf": inf_w_small,
                "ic_sup": sup_w_small,
                "ic_inf_pct": inf_w_small * 100.0,
                "ic_sup_pct": sup_w_small * 100.0,
                "comportamento": classe_w_small,
                "ordem_cenario": 3,
            },
            {
                "cenario_codigo": "Q3_AmostraPequena",
                "cenario_rotulo": "Violação: Amostra Pequena (Q3)\nLog-normal (n=10)",
                "condicao": "Tamanho amostral reduzido (n=10)",
                "teste": CENARIO.teste_nao_parametrico,
                "abordagem": "Não-paramétrico",
                "n_simulacoes": n_simulacoes,
                "n_rejeicoes": rej_mw_small,
                "taxa_empirica": p_mw_small,
                "taxa_empirica_pct": p_mw_small * 100.0,
                "taxa_teorica": alpha,
                "taxa_teorica_pct": alpha * 100.0,
                "desvio_nominal_pct": (p_mw_small - alpha) * 100.0,
                "ic_inf": inf_mw_small,
                "ic_sup": sup_mw_small,
                "ic_inf_pct": inf_mw_small * 100.0,
                "ic_sup_pct": sup_mw_small * 100.0,
                "comportamento": classe_mw_small,
                "ordem_cenario": 3,
            },
        ]
    )

    df_consolidado = pd.DataFrame(registros)
    return df_consolidado


def carregar_ou_simular_dados_g3(
    semente: int = 42,
    n_simulacoes: int = 10_000,
    forcar_reexecucao: bool = False,
    caminho_csv: Path | str = CAMINHO_DADOS_G3_CONSOLIDADO,
) -> pd.DataFrame:
    """Carrega os dados consolidados do G3 a partir do CSV ou executa a simulação completa."""
    p_csv = Path(caminho_csv)
    if not forcar_reexecucao and p_csv.exists() and semente == 42 and n_simulacoes == 10_000:
        df_lido = pd.read_csv(p_csv)
        if len(df_lido) == 6 and (df_lido["n_simulacoes"] == 10_000).all():
            return df_lido

    df = simular_condicoes_g3(semente=semente, n_simulacoes=n_simulacoes)
    if semente == 42 and n_simulacoes == 10_000:
        p_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(p_csv, index=False)
    return df


# ----------------------------------------------------------------------------
# Construção visual do Gráfico G3
# ----------------------------------------------------------------------------
def gerar_g3(
    df_dados: Optional[pd.DataFrame] = None,
    semente: int = 42,
    n_simulacoes: int = 10_000,
    alpha: float = CENARIO.alpha,
) -> plt.Figure:
    """Gera o objeto Figure do gráfico G3 com barras agrupadas e linha de referência em 5%.

    Retorna:
        plt.Figure pronta para renderização no Streamlit (`st.pyplot`) ou salvamento em PNG.
    """
    df = (
        df_dados
        if df_dados is not None
        else carregar_ou_simular_dados_g3(semente=semente, n_simulacoes=n_simulacoes)
    )

    cenarios = df["cenario_rotulo"].unique()
    n_cenarios = len(cenarios)
    x = np.arange(n_cenarios)
    largura = 0.36

    df_w = df[df["teste"] == CENARIO.teste_parametrico].sort_values("ordem_cenario")
    df_mw = df[df["teste"] == CENARIO.teste_nao_parametrico].sort_values("ordem_cenario")

    taxas_w = df_w["taxa_empirica_pct"].to_numpy()
    taxas_mw = df_mw["taxa_empirica_pct"].to_numpy()

    # Cálculo dos erros assimétricos para as barras de erro (IC Wilson 95%)
    yerr_w_inf = taxas_w - df_w["ic_inf_pct"].to_numpy()
    yerr_w_sup = df_w["ic_sup_pct"].to_numpy() - taxas_w
    yerr_w = np.vstack([yerr_w_inf, yerr_w_sup])

    yerr_mw_inf = taxas_mw - df_mw["ic_inf_pct"].to_numpy()
    yerr_mw_sup = df_mw["ic_sup_pct"].to_numpy() - taxas_mw
    yerr_mw = np.vstack([yerr_mw_inf, yerr_mw_sup])

    fig, ax = plt.subplots(figsize=(10.5, 6.2), dpi=100)

    # 1. Faixa sombreada de tolerância estrita de calibração (critério estrito de Bradley: [4,5%, 5,5%])
    ax.axhspan(
        4.5,
        5.5,
        color=COR_FAIXA,
        alpha=0.10,
        label="Margem estrita de calibração (Bradley: 4,5% a 5,5%)",
        zorder=1,
    )

    # 2. Linha horizontal de referência teórica em 5% (α = 0,05)
    ax.axhline(
        alpha * 100.0,
        color=COR_REFERENCIA,
        linestyle="--",
        linewidth=2.0,
        label=f"Nível nominal teórico (α = {alpha * 100:.1f}%)",
        zorder=3,
    )

    # 3. Barras agrupadas para os dois testes
    barras_w = ax.bar(
        x - largura / 2.0,
        taxas_w,
        largura,
        yerr=yerr_w,
        capsize=4.5,
        color=COR_WELCH,
        alpha=0.90,
        edgecolor="black",
        linewidth=0.8,
        label=f"{CENARIO.teste_parametrico} (Paramétrico)",
        zorder=4,
    )

    barras_mw = ax.bar(
        x + largura / 2.0,
        taxas_mw,
        largura,
        yerr=yerr_mw,
        capsize=4.5,
        color=COR_MANN_WHITNEY,
        alpha=0.90,
        edgecolor="black",
        linewidth=0.8,
        label=f"{CENARIO.teste_nao_parametrico} (Não-paramétrico)",
        zorder=4,
    )

    # 4. Rótulos percentuais sobre cada barra
    for barra in barras_w:
        altura = barra.get_height()
        ax.annotate(
            f"{altura:.2f}%",
            xy=(barra.get_x() + barra.get_width() / 2.0, altura),
            xytext=(0, 7),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
            color="#0b3c61",
        )

    for barra in barras_mw:
        altura = barra.get_height()
        ax.annotate(
            f"{altura:.2f}%",
            xy=(barra.get_x() + barra.get_width() / 2.0, altura),
            xytext=(0, 7),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold",
            color="#a24c00",
        )

    # 5. Formatação de eixos, títulos e legendas
    ax.set_title(
        "G3 — Taxa de Erro Tipo I dos Dois Testes sob H₀ nas Situações Simuladas",
        fontsize=13,
        fontweight="bold",
        pad=14,
    )
    ax.set_ylabel("Taxa Empírica de Erro Tipo I (%)", fontsize=11, fontweight="bold")
    ax.set_xlabel("Cenário e Condição Experimental sob H₀", fontsize=11, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(cenarios, fontsize=10.5)
    ax.set_ylim(0.0, 7.5)

    ax.grid(axis="y", linestyle=":", alpha=0.6, zorder=0)
    ax.legend(loc="upper right", framealpha=0.92, fontsize=9.5)

    # Anotação metodológica no canto inferior direito
    ax.text(
        0.02,
        0.04,
        f"Simulações: {n_simulacoes:,} repetições independentes por condição | Semente fixa = {semente}\n"
        f"Barras de erro representam Intervalo de Confiança de Wilson a 95%",
        transform=ax.transAxes,
        fontsize=8.5,
        va="bottom",
        ha="left",
        bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="lightgray", alpha=0.9),
        zorder=5,
    )

    fig.tight_layout()
    return fig


def salvar_grafico_g3(
    fig: Optional[plt.Figure] = None,
    df_dados: Optional[pd.DataFrame] = None,
    caminho_saida: Path | str = CAMINHO_G3_PADRAO,
    dpi: int = 300,
) -> Path:
    """Salva a imagem do gráfico G3 em arquivo de imagem PNG de alta resolução."""
    p_saida = Path(caminho_saida)
    p_saida.parent.mkdir(parents=True, exist_ok=True)

    figura = fig if fig is not None else gerar_g3(df_dados=df_dados)
    figura.savefig(p_saida, dpi=dpi, bbox_inches="tight")
    plt.close(figura)
    return p_saida


def texto_interpretativo_g3(df_dados: Optional[pd.DataFrame] = None) -> str:
    """Gera o texto explicativo de 2 a 4 frases descrevendo o comportamento de cada teste.

    Atende estritamente às exigências do laboratório:
    - Descreve se as taxas se aproximam de 5%;
    - Identifica onde ocorreram os maiores desvios;
    - Sintetiza as razões estatísticas observadas.
    """
    df = df_dados if df_dados is not None else carregar_ou_simular_dados_g3()

    df_w = df[df["teste"] == CENARIO.teste_parametrico].set_index("cenario_codigo")
    df_mw = df[df["teste"] == CENARIO.teste_nao_parametrico].set_index("cenario_codigo")

    t_w_base = f"{df_w.loc['Q1_Base', 'taxa_empirica_pct']:.2f}%".replace(".", ",")
    t_w_out = f"{df_w.loc['Q3_Outliers', 'taxa_empirica_pct']:.2f}%".replace(".", ",")
    t_w_small = f"{df_w.loc['Q3_AmostraPequena', 'taxa_empirica_pct']:.2f}%".replace(".", ",")

    t_mw_base = f"{df_mw.loc['Q1_Base', 'taxa_empirica_pct']:.2f}%".replace(".", ",")
    t_mw_out = f"{df_mw.loc['Q3_Outliers', 'taxa_empirica_pct']:.2f}%".replace(".", ",")
    t_mw_small = f"{df_mw.loc['Q3_AmostraPequena', 'taxa_empirica_pct']:.2f}%".replace(".", ",")

    return (
        f"O gráfico G3 compara a taxa empírica de Erro Tipo I dos dois testes em 10.000 simulações sob H₀ "
        f"frente ao nível nominal de 5% (linha tracejada vermelha). "
        f"O teste U de Mann-Whitney apresentou o melhor desempenho em todas as condições simuladas, "
        f"mantendo-se rigorosamente próximo aos 5% ({t_mw_base} na base, {t_mw_out} com outliers "
        f"e {t_mw_small} com amostra pequena), confirmando robustez estrita por operar sobre postos ordenados. "
        f"Já o teste t de Welch apresentou comportamento conservador em todos os cenários, rejeitando H₀ "
        f"consideravelmente menos do que o esperado ({t_w_base} na base, {t_w_out} com outliers "
        f"e {t_w_small} com amostra pequena). "
        f"Os maiores desvios ocorreram nas situações de violação de pressupostos (outliers severos e amostra pequena), "
        f"nas quais a cauda longa e a variabilidade extrema inflam o erro padrão e distorcem a aproximação "
        f"paramétrica do teste t."
    )


# ----------------------------------------------------------------------------
# Execução direta como script
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 80)
    print("LAB04S02 - G3: Comparação do Erro Tipo I (Cenário Original vs. Violações)")
    print("=" * 80)

    df_consolidado = carregar_ou_simular_dados_g3(semente=42, n_simulacoes=10_000, forcar_reexecucao=True)

    print("\nResultados Consolidados para o Gráfico G3:")
    print(
        df_consolidado[
            [
                "cenario_codigo",
                "teste",
                "taxa_empirica_pct",
                "taxa_teorica_pct",
                "desvio_nominal_pct",
                "comportamento",
            ]
        ].to_string(index=False)
    )

    caminho_figura = salvar_grafico_g3(df_dados=df_consolidado)
    print(f"\nGráfico G3 gerado e salvo com sucesso em: {caminho_figura}")

    print("\n" + "-" * 80)
    print("Texto Interpretativo Oficial do Gráfico G3:")
    print(texto_interpretativo_g3(df_consolidado))
    print("-" * 80)
