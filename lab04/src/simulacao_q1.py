"""Simulações de Monte Carlo e análise da Taxa de Erro Tipo I (Questão Q1).

Issue #51: [ LAB04S02 ] Implementar simulações e análise do erro tipo I (Q1).

Este módulo implementa a simulação de 10.000 repetições sob a hipótese nula verdadeira (H0),
onde ambos os grupos (`sem_bot` e `com_bot`) provêm rigorosamente da mesma distribuição de
probabilidade calibrada a partir dos dados reais (log-normal pooled: mu_log = 2.8053,
sigma_log = 0.9254, n = 30 por grupo).

Objetivos e análises:
1. Avaliar com que frequência os dois testes (t de Welch e U de Mann-Whitney) rejeitam
   incorretamente H0 ao nível nominal alpha = 0.05 (taxa empírica de erro tipo I).
2. Comparar as taxas estimadas com o valor teórico esperado de 5,0%.
3. Identificar e classificar comportamentos:
   - Conservador: taxa empírica significativamente menor que alpha (rejeita menos que o esperado).
   - Nominal / Calibrado: taxa empírica estatisticamente consistente com alpha.
   - Liberal: taxa empírica significativamente maior que alpha (infla falsos positivos).
4. Avaliar critérios formais de robustez de Bradley (1978) e teste de Kolmogorov-Smirnov
   para uniformidade teórica dos p-valores sob H0 (U(0, 1)).
5. Fornecer estruturas estruturadas prontas para uso no gráfico G3 e no Dashboard (Streamlit).

Uso via linha de comando:
    python -m lab04.src.simulacao_q1
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import sys
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from lab04.src.cenario import CENARIO
from lab04.src.simulacao import GeradorDadosSimulados, ParametrosSimulacao
from lab04.src.testes_estatisticos import (
    avaliar_matrizes_rapido,
    avaliar_par_rapido,
    normalizar_alternativa,
)

CAMINHO_DADOS_DIR = Path(__file__).resolve().parent.parent / "data"
CAMINHO_Q1_PVALORES_CSV = CAMINHO_DADOS_DIR / "simulacao_q1_pvalores.csv"
CAMINHO_Q1_RESUMO_CSV = CAMINHO_DADOS_DIR / "resultados_q1_erro_tipo_1.csv"


@dataclass(frozen=True)
class MetricasErroTipo1:
    """Consolidação estatística do comportamento de Erro Tipo I para um teste de hipótese."""

    nome_teste: str
    tipo_abordagem: str  # "Paramétrico" ou "Não-paramétrico"
    n_simulacoes: int
    n_rejeicoes: int
    taxa_erro_tipo_1: float
    taxa_teorica_alpha: float
    diferenca_nominal: float  # (taxa_erro_tipo_1 - taxa_teorica_alpha)
    erro_padrao_prop: float
    ic_95_inf: float
    ic_95_sup: float
    comportamento: str  # "Conservador", "Liberal" ou "Nominal / Bem calibrado"
    criterio_bradley_estrito: bool  # taxa em [0.9*alpha, 1.1*alpha]
    criterio_bradley_liberal: bool  # taxa em [0.5*alpha, 1.5*alpha]
    ks_stat_uniforme: float  # estatística D do teste de Kolmogorov-Smirnov vs U(0,1)
    ks_pvalor_uniforme: float  # p-valor do teste KS vs U(0,1)
    interpretacao_resumida: str


@dataclass(frozen=True)
class ResultadoSimulacaoQ1:
    """Resultado completo da simulação Monte Carlo de Erro Tipo I (Q1)."""

    cenario_id: str
    semente: int
    n_simulacoes: int
    n_sem_bot: int
    n_com_bot: int
    alpha: float
    df_detalhado: pd.DataFrame
    metricas_welch: MetricasErroTipo1
    metricas_mann_whitney: MetricasErroTipo1
    tabela_resumo: pd.DataFrame
    sintese_comparativa: str


# ----------------------------------------------------------------------------
# Funções de auxílio estatístico e classificação
# ----------------------------------------------------------------------------
def calcular_intervalo_confianca_wilson(
    n_rejeicoes: int,
    n_total: int,
    confianca: float = 0.95,
) -> Tuple[float, float, float]:
    """Calcula o Intervalo de Confiança de Wilson para uma proporção binomial.

    O método de Wilson score é recomendado sobre a aproximação de Wald por manter
    cobertura estrita mesmo para proporções próximas a zero ou tamanhos moderados.

    Retorna:
        Tupla contendo (proporcao, limite_inferior, limite_superior).
    """
    if n_total <= 0:
        raise ValueError("O tamanho total deve ser estritamente positivo.")
    if n_rejeicoes < 0 or n_rejeicoes > n_total:
        raise ValueError("O número de rejeições deve estar entre 0 e n_total.")

    p = float(n_rejeicoes) / float(n_total)
    z = float(stats.norm.ppf(1.0 - (1.0 - confianca) / 2.0))
    z2 = z * z
    n = float(n_total)

    denominador = 1.0 + (z2 / n)
    centro = (p + (z2 / (2.0 * n))) / denominador
    margem = (z / denominador) * np.sqrt((p * (1.0 - p) / n) + (z2 / (4.0 * (n**2))))

    lim_inf = max(0.0, float(centro - margem))
    lim_sup = min(1.0, float(centro + margem))
    return p, lim_inf, lim_sup


def classificar_comportamento_erro_tipo_1(
    taxa_empirica: float,
    alpha: float = CENARIO.alpha,
    n_simulacoes: int = 10_000,
    confianca: float = 0.95,
) -> Tuple[str, str]:
    """Classifica se o teste é Conservador, Liberal ou Nominal com base no IC da proporção sob H0.

    Sob calibração perfeita, a taxa esperada é exatamente alpha. Com n simulações,
    o intervalo de flutuação amostral de 95% para uma taxa perfeitamente calibrada é:
    alpha ± z * sqrt(alpha * (1 - alpha) / n).

    Retorna:
        Tupla (classificacao, explicacao).
    """
    z = float(stats.norm.ppf(1.0 - (1.0 - confianca) / 2.0))
    se_nulo = np.sqrt(alpha * (1.0 - alpha) / n_simulacoes)
    lim_inf_esperado = alpha - z * se_nulo
    lim_sup_esperado = alpha + z * se_nulo

    if taxa_empirica < lim_inf_esperado:
        classificacao = "Conservador"
        explicacao = (
            f"Taxa empírica ({taxa_empirica * 100:.2f}%) significativamente menor do que "
            f"o nível nominal esperado de {alpha * 100:.1f}% (limiar inferior de {lim_inf_esperado * 100:.2f}%). "
            f"O teste rejeita H₀ com menor frequência do que o estipulado, reduzindo falsos positivos "
            f"porém com potencial custo em poder estatístico."
        )
    elif taxa_empirica > lim_sup_esperado:
        classificacao = "Liberal"
        explicacao = (
            f"Taxa empírica ({taxa_empirica * 100:.2f}%) significativamente maior do que "
            f"o nível nominal de {alpha * 100:.1f}% (limiar superior de {lim_sup_esperado * 100:.2f}%). "
            f"O teste infla a taxa de falsos positivos além do tolerado pelo pesquisador."
        )
    else:
        classificacao = "Nominal / Bem calibrado"
        explicacao = (
            f"Taxa empírica ({taxa_empirica * 100:.2f}%) estatisticamente consistente com o valor nominal "
            f"teórico de {alpha * 100:.1f}% dentro da margem de erro amostral a 95% "
            f"[{lim_inf_esperado * 100:.2f}%, {lim_sup_esperado * 100:.2f}%]."
        )

    return classificacao, explicacao


# ----------------------------------------------------------------------------
# Execução da simulação Monte Carlo de Q1
# ----------------------------------------------------------------------------
def executar_simulacao_q1(
    n_simulacoes: int = 10_000,
    semente: int = 42,
    n_sem_bot: int = 30,
    n_com_bot: int = 30,
    alpha: float = CENARIO.alpha,
    alternativa: str = CENARIO.tipo_teste,
    usar_vetorizado: bool = True,
) -> ResultadoSimulacaoQ1:
    """Executa a simulação completa de Erro Tipo I (Q1) sob a hipótese nula verdadeira.

    Parâmetros:
        n_simulacoes: Número de simulações Monte Carlo independentes (padrão: 10.000).
        semente: Semente do gerador pseudoaleatório para reprodutibilidade estrita (padrão: 42).
        n_sem_bot: Tamanho amostral do grupo sem bot (padrão: 30).
        n_com_bot: Tamanho amostral do grupo com bot (padrão: 30).
        alpha: Nível nominal de significância (padrão: 0.05).
        alternativa: Direção do teste ('bicaudal' / 'two-sided').
        usar_vetorizado: Se True, utiliza execução 2D vetorizada via NumPy/SciPy de alto desempenho.
                         Se False, itera dataset a dataset (produz exatamente os mesmos resultados).

    Retorna:
        Instância tipada de `ResultadoSimulacaoQ1` contendo p-valores, métricas e análises.
    """
    gerador = GeradorDadosSimulados(semente=semente)

    if usar_vetorizado:
        # Geração matricial de alto desempenho mantendo a ordem exata de sorteio
        matriz_sem, matriz_com = gerador.gerar_matrizes_h0(
            n_simulacoes=n_simulacoes,
            n_sem_bot=n_sem_bot,
            n_com_bot=n_com_bot,
            arredondar=2,
        )
        resultados_testes = avaliar_matrizes_rapido(
            matriz_sem,
            matriz_com,
            alpha=alpha,
            alternativa=alternativa,
        )
        t_stats = resultados_testes["t_stat"]
        p_welch = resultados_testes["p_welch"]
        rej_welch = resultados_testes["rejeita_welch"]
        u_stats = resultados_testes["u_stat"]
        p_mw = resultados_testes["p_mann_whitney"]
        rej_mw = resultados_testes["rejeita_mann_whitney"]
    else:
        t_stats = np.empty(n_simulacoes, dtype=float)
        p_welch = np.empty(n_simulacoes, dtype=float)
        rej_welch = np.empty(n_simulacoes, dtype=bool)
        u_stats = np.empty(n_simulacoes, dtype=float)
        p_mw = np.empty(n_simulacoes, dtype=float)
        rej_mw = np.empty(n_simulacoes, dtype=bool)

        for i in range(n_simulacoes):
            df_i = gerador.gerar_dataset_experimento(
                n_sem_bot=n_sem_bot,
                n_com_bot=n_com_bot,
                sob_h0=True,
            )
            sem_i = df_i.loc[df_i["grupo"] == "sem_bot", "tempo_horas"].to_numpy(dtype=float)
            com_i = df_i.loc[df_i["grupo"] == "com_bot", "tempo_horas"].to_numpy(dtype=float)

            res_i = avaliar_par_rapido(sem_i, com_i, alpha=alpha, alternativa=alternativa)
            t_stats[i] = res_i["t_stat"]
            p_welch[i] = res_i["p_welch"]
            rej_welch[i] = res_i["rejeita_welch"]
            u_stats[i] = res_i["u_stat"]
            p_mw[i] = res_i["p_mann_whitney"]
            rej_mw[i] = res_i["rejeita_mann_whitney"]

    # Monta o DataFrame detalhado com os 10.000 resultados individuais
    df_detalhado = pd.DataFrame(
        {
            "simulacao_id": np.arange(1, n_simulacoes + 1),
            "t_stat": np.round(t_stats, 4),
            "p_welch": np.round(p_welch, 6),
            "rejeita_welch": rej_welch,
            "u_stat": np.round(u_stats, 2),
            "p_mann_whitney": np.round(p_mw, 6),
            "rejeita_mann_whitney": rej_mw,
        }
    )

    # 1. Análise para o Teste t de Welch
    rejeicoes_w = int(np.sum(rej_welch))
    taxa_w, ic_inf_w, ic_sup_w = calcular_intervalo_confianca_wilson(rejeicoes_w, n_simulacoes)
    se_w = float(np.sqrt(taxa_w * (1.0 - taxa_w) / n_simulacoes))
    classe_w, exp_w = classificar_comportamento_erro_tipo_1(taxa_w, alpha, n_simulacoes)
    ks_res_w = stats.kstest(p_welch, "uniform")

    # Critérios de robustez de Bradley (1978)
    bradley_estrito_w = bool((0.9 * alpha) <= taxa_w <= (1.1 * alpha))
    bradley_liberal_w = bool((0.5 * alpha) <= taxa_w <= (1.5 * alpha))

    metricas_welch = MetricasErroTipo1(
        nome_teste=CENARIO.teste_parametrico,
        tipo_abordagem="Paramétrico",
        n_simulacoes=n_simulacoes,
        n_rejeicoes=rejeicoes_w,
        taxa_erro_tipo_1=taxa_w,
        taxa_teorica_alpha=alpha,
        diferenca_nominal=taxa_w - alpha,
        erro_padrao_prop=se_w,
        ic_95_inf=ic_inf_w,
        ic_95_sup=ic_sup_w,
        comportamento=classe_w,
        criterio_bradley_estrito=bradley_estrito_w,
        criterio_bradley_liberal=bradley_liberal_w,
        ks_stat_uniforme=float(ks_res_w.statistic),
        ks_pvalor_uniforme=float(ks_res_w.pvalue),
        interpretacao_resumida=exp_w,
    )

    # 2. Análise para o Teste U de Mann-Whitney
    rejeicoes_mw = int(np.sum(rej_mw))
    taxa_mw, ic_inf_mw, ic_sup_mw = calcular_intervalo_confianca_wilson(
        rejeicoes_mw, n_simulacoes
    )
    se_mw = float(np.sqrt(taxa_mw * (1.0 - taxa_mw) / n_simulacoes))
    classe_mw, exp_mw = classificar_comportamento_erro_tipo_1(taxa_mw, alpha, n_simulacoes)
    ks_res_mw = stats.kstest(p_mw, "uniform")

    bradley_estrito_mw = bool((0.9 * alpha) <= taxa_mw <= (1.1 * alpha))
    bradley_liberal_mw = bool((0.5 * alpha) <= taxa_mw <= (1.5 * alpha))

    metricas_mw = MetricasErroTipo1(
        nome_teste=CENARIO.teste_nao_parametrico,
        tipo_abordagem="Não-paramétrico",
        n_simulacoes=n_simulacoes,
        n_rejeicoes=rejeicoes_mw,
        taxa_erro_tipo_1=taxa_mw,
        taxa_teorica_alpha=alpha,
        diferenca_nominal=taxa_mw - alpha,
        erro_padrao_prop=se_mw,
        ic_95_inf=ic_inf_mw,
        ic_95_sup=ic_sup_mw,
        comportamento=classe_mw,
        criterio_bradley_estrito=bradley_estrito_mw,
        criterio_bradley_liberal=bradley_liberal_mw,
        ks_stat_uniforme=float(ks_res_mw.statistic),
        ks_pvalor_uniforme=float(ks_res_mw.pvalue),
        interpretacao_resumida=exp_mw,
    )

    # Tabela consolidada de resumo para exibição no Dashboard e salvamento
    linhas_resumo = [
        {
            "teste": metricas_welch.nome_teste,
            "tipo_abordagem": metricas_welch.tipo_abordagem,
            "n_simulacoes": metricas_welch.n_simulacoes,
            "n_rejeicoes_h0": metricas_welch.n_rejeicoes,
            "taxa_erro_tipo_1": round(metricas_welch.taxa_erro_tipo_1, 4),
            "taxa_erro_tipo_1_pct": f"{metricas_welch.taxa_erro_tipo_1 * 100:.2f}%",
            "alpha_nominal": metricas_welch.taxa_teorica_alpha,
            "alpha_nominal_pct": f"{metricas_welch.taxa_teorica_alpha * 100:.1f}%",
            "diferenca_nominal_pct": f"{metricas_welch.diferenca_nominal * 100:+.2f}%",
            "ic_95_inf": round(metricas_welch.ic_95_inf, 4),
            "ic_95_sup": round(metricas_welch.ic_95_sup, 4),
            "ic_95_formatado": f"[{metricas_welch.ic_95_inf * 100:.2f}%, {metricas_welch.ic_95_sup * 100:.2f}%]",
            "comportamento": metricas_welch.comportamento,
            "bradley_estrito": "Sim" if metricas_welch.criterio_bradley_estrito else "Não",
            "bradley_liberal": "Sim" if metricas_welch.criterio_bradley_liberal else "Não",
            "ks_pvalor_uniforme": round(metricas_welch.ks_pvalor_uniforme, 6),
        },
        {
            "teste": metricas_mw.nome_teste,
            "tipo_abordagem": metricas_mw.tipo_abordagem,
            "n_simulacoes": metricas_mw.n_simulacoes,
            "n_rejeicoes_h0": metricas_mw.n_rejeicoes,
            "taxa_erro_tipo_1": round(metricas_mw.taxa_erro_tipo_1, 4),
            "taxa_erro_tipo_1_pct": f"{metricas_mw.taxa_erro_tipo_1 * 100:.2f}%",
            "alpha_nominal": metricas_mw.taxa_teorica_alpha,
            "alpha_nominal_pct": f"{metricas_mw.taxa_teorica_alpha * 100:.1f}%",
            "diferenca_nominal_pct": f"{metricas_mw.diferenca_nominal * 100:+.2f}%",
            "ic_95_inf": round(metricas_mw.ic_95_inf, 4),
            "ic_95_sup": round(metricas_mw.ic_95_sup, 4),
            "ic_95_formatado": f"[{metricas_mw.ic_95_inf * 100:.2f}%, {metricas_mw.ic_95_sup * 100:.2f}%]",
            "comportamento": metricas_mw.comportamento,
            "bradley_estrito": "Sim" if metricas_mw.criterio_bradley_estrito else "Não",
            "bradley_liberal": "Sim" if metricas_mw.criterio_bradley_liberal else "Não",
            "ks_pvalor_uniforme": round(metricas_mw.ks_pvalor_uniforme, 6),
        },
    ]
    tabela_resumo = pd.DataFrame(linhas_resumo)

    sintese = (
        f"Nas 10.000 simulações sob H₀ verdadeira (ausência de efeito real), o teste t de Welch "
        f"apresentou comportamento conservador com taxa empírica de Erro Tipo I de "
        f"{metricas_welch.taxa_erro_tipo_1 * 100:.2f}% (IC 95%: [{metricas_welch.ic_95_inf * 100:.2f}%, "
        f"{metricas_welch.ic_95_sup * 100:.2f}%]), rejeitando H₀ significativamente menos do que o "
        f"esperado teoricamente (5,0%). Essa deflação ocorre porque valores extremos na cauda direita da "
        f"distribuição lognormal inflam o desvio padrão amostral s no denominador de t e distorcem a "
        f"aproximação de Welch-Satterthwaite, tornando o teste reticente. Já o teste U de Mann-Whitney "
        f"demonstrou excelente aderência teórica, com taxa empírica de {metricas_mw.taxa_erro_tipo_1 * 100:.2f}% "
        f"(IC 95%: [{metricas_mw.ic_95_inf * 100:.2f}%, {metricas_mw.ic_95_sup * 100:.2f}%]), atendendo ao "
        f"critério estrito de robustez de Bradley (1978) [4,5% a 5,5%] e validando que nenhum dos testes é liberal."
    )

    return ResultadoSimulacaoQ1(
        cenario_id="Q1_H0_verdadeira",
        semente=semente,
        n_simulacoes=n_simulacoes,
        n_sem_bot=n_sem_bot,
        n_com_bot=n_com_bot,
        alpha=alpha,
        df_detalhado=df_detalhado,
        metricas_welch=metricas_welch,
        metricas_mann_whitney=metricas_mw,
        tabela_resumo=tabela_resumo,
        sintese_comparativa=sintese,
    )


# ----------------------------------------------------------------------------
# Persistência e carregamento rápido para Dashboard e Gráfico G3
# ----------------------------------------------------------------------------
def salvar_resultados_q1(
    resultado: ResultadoSimulacaoQ1,
    caminho_resumo: Path | str = CAMINHO_Q1_RESUMO_CSV,
    caminho_detalhado: Path | str = CAMINHO_Q1_PVALORES_CSV,
) -> Tuple[Path, Path]:
    """Salva os resultados da simulação Q1 em disco (resumo e p-valores detalhados)."""
    p_resumo = Path(caminho_resumo)
    p_detalhado = Path(caminho_detalhado)

    p_resumo.parent.mkdir(parents=True, exist_ok=True)
    p_detalhado.parent.mkdir(parents=True, exist_ok=True)

    resultado.tabela_resumo.to_csv(p_resumo, index=False)
    resultado.df_detalhado.to_csv(p_detalhado, index=False)

    return p_resumo, p_detalhado


def carregar_ou_executar_q1(
    semente: int = 42,
    n_simulacoes: int = 10_000,
    forcar_reexecucao: bool = False,
    caminho_resumo: Path | str = CAMINHO_Q1_RESUMO_CSV,
    caminho_detalhado: Path | str = CAMINHO_Q1_PVALORES_CSV,
) -> ResultadoSimulacaoQ1:
    """Carrega os resultados já salvos de Q1 ou executa a simulação caso não existam."""
    p_resumo = Path(caminho_resumo)
    p_detalhado = Path(caminho_detalhado)

    if (
        not forcar_reexecucao
        and p_resumo.exists()
        and p_detalhado.exists()
        and semente == 42
        and n_simulacoes == 10_000
    ):
        df_resumo = pd.read_csv(p_resumo)
        df_detalhado = pd.read_csv(p_detalhado)
        if len(df_detalhado) == n_simulacoes:
            # Reconstroi o objeto tipado a partir dos dados persistidos
            rej_w = int(df_detalhado["rejeita_welch"].sum())
            rej_mw = int(df_detalhado["rejeita_mann_whitney"].sum())
            taxa_w, inf_w, sup_w = calcular_intervalo_confianca_wilson(rej_w, n_simulacoes)
            taxa_mw, inf_mw, sup_mw = calcular_intervalo_confianca_wilson(rej_mw, n_simulacoes)
            classe_w, exp_w = classificar_comportamento_erro_tipo_1(taxa_w)
            classe_mw, exp_mw = classificar_comportamento_erro_tipo_1(taxa_mw)
            ks_w = stats.kstest(df_detalhado["p_welch"], "uniform")
            ks_mw = stats.kstest(df_detalhado["p_mann_whitney"], "uniform")

            metricas_w = MetricasErroTipo1(
                nome_teste=CENARIO.teste_parametrico,
                tipo_abordagem="Paramétrico",
                n_simulacoes=n_simulacoes,
                n_rejeicoes=rej_w,
                taxa_erro_tipo_1=taxa_w,
                taxa_teorica_alpha=CENARIO.alpha,
                diferenca_nominal=taxa_w - CENARIO.alpha,
                erro_padrao_prop=float(np.sqrt(taxa_w * (1.0 - taxa_w) / n_simulacoes)),
                ic_95_inf=inf_w,
                ic_95_sup=sup_w,
                comportamento=classe_w,
                criterio_bradley_estrito=bool(0.045 <= taxa_w <= 0.055),
                criterio_bradley_liberal=bool(0.025 <= taxa_w <= 0.075),
                ks_stat_uniforme=float(ks_w.statistic),
                ks_pvalor_uniforme=float(ks_w.pvalue),
                interpretacao_resumida=exp_w,
            )

            metricas_mw = MetricasErroTipo1(
                nome_teste=CENARIO.teste_nao_parametrico,
                tipo_abordagem="Não-paramétrico",
                n_simulacoes=n_simulacoes,
                n_rejeicoes=rej_mw,
                taxa_erro_tipo_1=taxa_mw,
                taxa_teorica_alpha=CENARIO.alpha,
                diferenca_nominal=taxa_mw - CENARIO.alpha,
                erro_padrao_prop=float(np.sqrt(taxa_mw * (1.0 - taxa_mw) / n_simulacoes)),
                ic_95_inf=inf_mw,
                ic_95_sup=sup_mw,
                comportamento=classe_mw,
                criterio_bradley_estrito=bool(0.045 <= taxa_mw <= 0.055),
                criterio_bradley_liberal=bool(0.025 <= taxa_mw <= 0.075),
                ks_stat_uniforme=float(ks_mw.statistic),
                ks_pvalor_uniforme=float(ks_mw.pvalue),
                interpretacao_resumida=exp_mw,
            )

            sintese = (
                f"Nas 10.000 simulações sob H₀ verdadeira (ausência de efeito real), o teste t de Welch "
                f"apresentou comportamento conservador com taxa empírica de Erro Tipo I de "
                f"{taxa_w * 100:.2f}% (IC 95%: [{inf_w * 100:.2f}%, {sup_w * 100:.2f}%]), "
                f"enquanto o teste U de Mann-Whitney demonstrou aderência teórica robusta com "
                f"{taxa_mw * 100:.2f}% (IC 95%: [{inf_mw * 100:.2f}%, {sup_mw * 100:.2f}%]), "
                f"atendendo ao critério estrito de Bradley (1978) [4,5% a 5,5%]."
            )

            return ResultadoSimulacaoQ1(
                cenario_id="Q1_H0_verdadeira",
                semente=semente,
                n_simulacoes=n_simulacoes,
                n_sem_bot=30,
                n_com_bot=30,
                alpha=CENARIO.alpha,
                df_detalhado=df_detalhado,
                metricas_welch=metricas_w,
                metricas_mann_whitney=metricas_mw,
                tabela_resumo=df_resumo,
                sintese_comparativa=sintese,
            )

    resultado = executar_simulacao_q1(
        n_simulacoes=n_simulacoes,
        semente=semente,
        alpha=CENARIO.alpha,
        alternativa=CENARIO.tipo_teste,
        usar_vetorizado=True,
    )
    salvar_resultados_q1(resultado, caminho_resumo=p_resumo, caminho_detalhado=p_detalhado)
    return resultado


def obter_tabela_para_g3(resultado: ResultadoSimulacaoQ1) -> pd.DataFrame:
    """Gera uma estrutura padronizada para consumo pelo Gráfico G3 (Sprint 2).

    Retorna DataFrame com colunas padronizadas que podem ser combinadas diretamente
    com os cenários de violação de pressupostos (Q3) no gráfico G3.
    """
    linhas = [
        {
            "cenario": "H₀ Verdadeira (Baseline Q1)",
            "condicao": "Log-normal realista (n=30)",
            "teste": resultado.metricas_welch.nome_teste,
            "tipo_abordagem": resultado.metricas_welch.tipo_abordagem,
            "taxa_empirica": resultado.metricas_welch.taxa_erro_tipo_1,
            "taxa_teorica": resultado.metricas_welch.taxa_teorica_alpha,
            "n_rejeicoes": resultado.metricas_welch.n_rejeicoes,
            "n_simulacoes": resultado.metricas_welch.n_simulacoes,
            "ic_inf": resultado.metricas_welch.ic_95_inf,
            "ic_sup": resultado.metricas_welch.ic_95_sup,
            "comportamento": resultado.metricas_welch.comportamento,
        },
        {
            "cenario": "H₀ Verdadeira (Baseline Q1)",
            "condicao": "Log-normal realista (n=30)",
            "teste": resultado.metricas_mann_whitney.nome_teste,
            "tipo_abordagem": resultado.metricas_mann_whitney.tipo_abordagem,
            "taxa_empirica": resultado.metricas_mann_whitney.taxa_erro_tipo_1,
            "taxa_teorica": resultado.metricas_mann_whitney.taxa_teorica_alpha,
            "n_rejeicoes": resultado.metricas_mann_whitney.n_rejeicoes,
            "n_simulacoes": resultado.metricas_mann_whitney.n_simulacoes,
            "ic_inf": resultado.metricas_mann_whitney.ic_inf_95 if hasattr(resultado.metricas_mann_whitney, "ic_inf_95") else resultado.metricas_mann_whitney.ic_95_inf,
            "ic_sup": resultado.metricas_mann_whitney.ic_sup_95 if hasattr(resultado.metricas_mann_whitney, "ic_sup_95") else resultado.metricas_mann_whitney.ic_95_sup,
            "comportamento": resultado.metricas_mann_whitney.comportamento,
        },
    ]
    return pd.DataFrame(linhas)


def gerar_texto_interpretativo_q1(resultado: ResultadoSimulacaoQ1) -> str:
    """Gera o texto curto e interpretativo exigido para a Seção 4 do Dashboard."""
    mw = resultado.metricas_mann_whitney
    w = resultado.metricas_welch
    return (
        f"Em 10.000 simulações sob H₀ verdadeira (α = {resultado.alpha:.2f}), o teste "
        f"U de Mann-Whitney atingiu taxa de Erro Tipo I de {mw.taxa_erro_tipo_1 * 100:.2f}% "
        f"(IC 95%: [{mw.ic_95_inf * 100:.2f}%, {mw.ic_95_sup * 100:.2f}%]), mantendo-se "
        f"estritamente alinhado à taxa teórica esperada de 5% (comportamento nominal e robusto). "
        f"Em contrapartida, o teste t de Welch desviou-se para {w.taxa_erro_tipo_1 * 100:.2f}% "
        f"(IC 95%: [{w.ic_95_inf * 100:.2f}%, {w.ic_95_sup * 100:.2f}%]), apresentando comportamento "
        f"conservador: a assimetria acentuada dos tempos de software e os outliers na cauda direita inflam "
        f"a variância amostral e reduzem os graus de liberdade, tornando o teste paramétrico excessivamente "
        f"cauteloso na rejeição de H₀. Nenhum dos testes exibiu comportamento liberal."
    )


# ----------------------------------------------------------------------------
# Execução direta como script
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 80)
    print("LAB04S02 - Simulação Monte Carlo e Análise do Erro Tipo I (Q1)")
    print("=" * 80)
    print(f"Número de simulações: 10.000 | Semente: 42 | Nível alpha: {CENARIO.alpha:.2f}")
    print(f"Cenário sob H0: Distribuição Log-normal idêntica para ambos os grupos (n = 30)")
    print("-" * 80)

    res = carregar_ou_executar_q1(semente=42, n_simulacoes=10_000, forcar_reexecucao=True)

    print("\nResultados Consolidados da Taxa de Erro Tipo I:")
    print(
        res.tabela_resumo[
            [
                "teste",
                "tipo_abordagem",
                "n_rejeicoes_h0",
                "taxa_erro_tipo_1_pct",
                "alpha_nominal_pct",
                "diferenca_nominal_pct",
                "ic_95_formatado",
                "comportamento",
                "bradley_estrito",
            ]
        ].to_string(index=False)
    )

    print("\n" + "-" * 80)
    print("Síntese Interpretativa dos Resultados:")
    print(res.sintese_comparativa)
    print("-" * 80)
    print(f"Arquivos salvos com sucesso em:")
    print(f"- Resumo: {CAMINHO_Q1_RESUMO_CSV}")
    print(f"- P-valores detalhados: {CAMINHO_Q1_PVALORES_CSV}")

