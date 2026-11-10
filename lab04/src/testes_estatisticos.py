"""Aplicação e interpretação dos dois testes estatísticos do LAB04 (Par P1).

Issue #49: [LAB04S01] Implementar aplicação e interpretação dos dois testes estatísticos.

Este módulo implementa a execução, o cálculo de tamanho de efeito e a interpretação
automatizada dos dois testes selecionados para o Par P1:
1. Teste t de Welch (paramétrico, comparação de médias com variâncias desiguais).
2. Teste U de Mann-Whitney / Wilcoxon rank-sum (não-paramétrico, comparação de postos /
   dominância estocástica / medianas).

As funções foram projetadas de forma modular tanto para a análise detalhada de um único
conjunto de dados (S01 e dados reais) quanto para a execução vetorizada/rápida nas
10.000 repetições de Monte Carlo das questões Q1, Q2 e Q3 na Sprint 02 (LAB04S02).

Uso como script (a partir da raiz do repositório):
    python -m lab04.src.testes_estatisticos
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import sys
from typing import Any, Dict, List, Literal, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from lab04.src.cenario import CENARIO
from lab04.src.dados_reais import CAMINHO_DADOS_REAIS_PADRAO, carregar_dados_reais
from lab04.src.simulacao import CAMINHO_DADOS_SIMULADOS_S01, GeradorDadosSimulados

CAMINHO_RESULTADOS_TESTES_S01 = (
    Path(__file__).resolve().parent.parent / "data" / "resultados_testes_s01.csv"
)

DirecaoAlternativa = Literal["two-sided", "less", "greater"]

MAPA_ALTERNATIVA_SCIPY: Dict[str, DirecaoAlternativa] = {
    "bicaudal": "two-sided",
    "two-sided": "two-sided",
    "menor": "less",
    "less": "less",
    "maior": "greater",
    "greater": "greater",
}


@dataclass(frozen=True)
class ResultadoTesteIndividual:
    """Resultado detalhado da aplicação de um teste de hipótese sobre dois grupos."""

    nome_teste: str
    tipo_abordagem: str  # "Paramétrico" ou "Não-paramétrico"
    o_que_compara: str
    h0_operacional: str
    h1_operacional: str
    direcao_teste: str  # "bicaudal" ("two-sided")
    alpha: float
    n_sem_bot: int
    n_com_bot: int
    medida_central_sem_bot: float
    medida_central_com_bot: float
    diferenca_central: float  # (com_bot - sem_bot)
    dispersao_sem_bot: float
    dispersao_com_bot: float
    nome_estatistica: str  # "t" ou "U"
    estatistica: float
    graus_liberdade_ou_auxiliar: float  # df (Welch) ou z aproximado (Mann-Whitney)
    nome_auxiliar: str  # "gl (Welch-Satterthwaite)" ou "z (aprox. normal)"
    p_valor: float
    rejeitar_h0: bool
    decisao_estatistica: str
    nome_tamanho_efeito: str  # "d de Cohen (Welch)" ou "r rank-biserial"
    tamanho_efeito: float
    interpretacao_efeito: str
    interpretacao_linguagem_simples: str


@dataclass(frozen=True)
class ComparacaoTestes:
    """Consolidação comparativa dos dois testes aplicados ao mesmo conjunto de dados."""

    origem_dados: str
    semente: int | None
    alpha: float
    direcao_teste: str
    welch: ResultadoTesteIndividual
    mann_whitney: ResultadoTesteIndividual
    concordam_decisao: bool
    resumo_comparativo: str
    explicacao_diferencas: str


# ----------------------------------------------------------------------------
# Funções utilitárias de preparação e validação
# ----------------------------------------------------------------------------
def normalizar_alternativa(alternativa: str = CENARIO.tipo_teste) -> DirecaoAlternativa:
    """Converte o rótulo de direção do teste ('bicaudal', 'two-sided', etc.) para o padrão SciPy."""
    chave = alternativa.strip().lower()
    if chave not in MAPA_ALTERNATIVA_SCIPY:
        raise ValueError(
            f"Direção de teste inválida: '{alternativa}'. "
            f"Opções válidas: {list(MAPA_ALTERNATIVA_SCIPY.keys())}"
        )
    return MAPA_ALTERNATIVA_SCIPY[chave]


def extrair_grupos_dataframe(
    df: pd.DataFrame,
    coluna_grupo: str = "grupo",
    coluna_valor: str = "tempo_horas",
    grupo_controle: str = CENARIO.grupo_controle,
    grupo_tratamento: str = CENARIO.grupo_tratamento,
) -> Tuple[np.ndarray, np.ndarray]:
    """Extrai os vetores numéricos (sem_bot, com_bot) a partir de um DataFrame padronizado."""
    if coluna_grupo not in df.columns or coluna_valor not in df.columns:
        raise ValueError(
            f"O DataFrame deve conter as colunas '{coluna_grupo}' e '{coluna_valor}'."
        )

    sem_bot = (
        df.loc[df[coluna_grupo] == grupo_controle, coluna_valor]
        .dropna()
        .to_numpy(dtype=float)
    )
    com_bot = (
        df.loc[df[coluna_grupo] == grupo_tratamento, coluna_valor]
        .dropna()
        .to_numpy(dtype=float)
    )

    validar_amostras(sem_bot, com_bot)
    return sem_bot, com_bot


def validar_amostras(sem_bot: np.ndarray, com_bot: np.ndarray) -> None:
    """Valida se ambos os grupos possuem observações suficientes e valores finitos."""
    if len(sem_bot) < 2 or len(com_bot) < 2:
        raise ValueError(
            "Cada grupo comparado deve conter pelo menos 2 observações válidas."
        )
    if not (np.all(np.isfinite(sem_bot)) and np.all(np.isfinite(com_bot))):
        raise ValueError("As amostras não podem conter valores NaN ou infinitos.")


# ----------------------------------------------------------------------------
# Cálculos de tamanhos de efeito e estatísticas auxiliares
# ----------------------------------------------------------------------------
def calcular_graus_liberdade_welch(sem_bot: np.ndarray, com_bot: np.ndarray) -> float:
    """Calcula os graus de liberdade pela equação de Welch-Satterthwaite."""
    n1, n2 = len(com_bot), len(sem_bot)
    v1 = float(np.var(com_bot, ddof=1)) / n1
    v2 = float(np.var(sem_bot, ddof=1)) / n2
    numerador = (v1 + v2) ** 2
    denominador = ((v1**2) / (n1 - 1)) + ((v2**2) / (n2 - 1))
    if denominador == 0.0:
        return float(n1 + n2 - 2)
    return float(numerador / denominador)


def calcular_d_cohen_welch(sem_bot: np.ndarray, com_bot: np.ndarray) -> float:
    """Calcula o d de Cohen usando o desvio padrão quadrático médio (não-agrupado de Welch).

    Sinal negativo indica que o grupo com_bot teve média menor que o grupo sem_bot.
    """
    media_sem = float(np.mean(sem_bot))
    media_com = float(np.mean(com_bot))
    var_sem = float(np.var(sem_bot, ddof=1))
    var_com = float(np.var(com_bot, ddof=1))
    dp_combinado = float(np.sqrt((var_sem + var_com) / 2.0))
    if dp_combinado == 0.0:
        return 0.0
    return float((media_com - media_sem) / dp_combinado)


def classificar_d_cohen(d: float) -> str:
    """Classifica a magnitude do d de Cohen segundo as convenções de Cohen (1988)."""
    mag = abs(d)
    if mag < 0.20:
        return "trivial / desprezível (|d| < 0,20)"
    if mag < 0.50:
        return "pequeno (0,20 ≤ |d| < 0,50)"
    if mag < 0.80:
        return "médio (0,50 ≤ |d| < 0,80)"
    return "grande (|d| ≥ 0,80)"


def calcular_correlacao_rank_biserial(
    estatistica_u: float, n_com_bot: int, n_sem_bot: int
) -> float:
    """Calcula a correlação rank-biserial (r_rb = 2*(U / (n1*n2)) - 1).

    Como U é calculado para com_bot em relação a sem_bot:
    - r_rb < 0 indica que com_bot tende a ter tempos menores (postos menores) que sem_bot.
    - r_rb = 0 indica equivalência estocástica (P(X > Y) = 0,5).
    - r_rb > 0 indica que com_bot tende a ter tempos maiores que sem_bot.
    """
    total_pares = float(n_com_bot * n_sem_bot)
    if total_pares == 0.0:
        return 0.0
    return float((2.0 * estatistica_u / total_pares) - 1.0)


def classificar_rank_biserial(r_rb: float) -> str:
    """Classifica a magnitude da correlação rank-biserial / delta de Cliff."""
    mag = abs(r_rb)
    if mag < 0.147:
        return "trivial / desprezível (|r_rb| < 0,15)"
    if mag < 0.330:
        return "pequeno (0,15 ≤ |r_rb| < 0,33)"
    if mag < 0.474:
        return "médio (0,33 ≤ |r_rb| < 0,47)"
    return "grande (|r_rb| ≥ 0,47)"


def calcular_z_mann_whitney(
    estatistica_u: float, n_com_bot: int, n_sem_bot: int
) -> float:
    """Calcula a estatística padronizada Z da aproximação normal de Mann-Whitney sob H0."""
    mu_u = (n_com_bot * n_sem_bot) / 2.0
    sigma_u = float(np.sqrt((n_com_bot * n_sem_bot * (n_com_bot + n_sem_bot + 1)) / 12.0))
    if sigma_u == 0.0:
        return 0.0
    return float((estatistica_u - mu_u) / sigma_u)


# ----------------------------------------------------------------------------
# Implementação dos dois testes estatísticos (Par P1)
# ----------------------------------------------------------------------------
def executar_teste_welch(
    sem_bot: np.ndarray,
    com_bot: np.ndarray,
    alpha: float = CENARIO.alpha,
    alternativa: str = CENARIO.tipo_teste,
) -> ResultadoTesteIndividual:
    """Executa o Teste t de Welch para duas amostras independentes (com_bot vs. sem_bot).

    Condições de aplicação:
        - Observações independentes dentro dos grupos e entre os grupos;
        - Variável contínua medida em escala intervalar ou de razão;
        - Normalidade aproximada das médias amostrais (não exige variâncias iguais).
    """
    sem_arr = np.asarray(sem_bot, dtype=float)
    com_arr = np.asarray(com_bot, dtype=float)
    validar_amostras(sem_arr, com_arr)

    alt_scipy = normalizar_alternativa(alternativa)
    res = stats.ttest_ind(com_arr, sem_arr, equal_var=False, alternative=alt_scipy)

    t_stat = float(res.statistic)
    p_val = float(res.pvalue)
    gl = float(getattr(res, "df", calcular_graus_liberdade_welch(sem_arr, com_arr)))

    media_sem = float(np.mean(sem_arr))
    media_com = float(np.mean(com_arr))
    dif_media = media_com - media_sem
    dp_sem = float(np.std(sem_arr, ddof=1))
    dp_com = float(np.std(com_arr, ddof=1))

    rejeitar = bool(p_val < alpha)
    d_cohen = calcular_d_cohen_welch(sem_arr, com_arr)
    classe_d = classificar_d_cohen(d_cohen)

    if rejeitar:
        decisao = (
            f"Rejeitar H₀ (p = {p_val:.4f} < α = {alpha:.2f}): há diferença estatisticamente "
            f"significativa entre as médias."
        )
        interpretacao = (
            f"O teste t de Welch identificou diferença estatisticamente significativa entre o tempo "
            f"médio até o merge com bot ({media_com:.2f} h) e sem bot ({media_sem:.2f} h), com "
            f"t({gl:.1f}) = {t_stat:.4f} e p = {p_val:.4f} (< {alpha:.2f}). "
            f"Portanto, sob a ótica das médias, há evidência de que o uso de bots de revisão altera o "
            f"tempo médio de integração de Pull Requests."
        )
    else:
        decisao = (
            f"Não rejeitar H₀ (p = {p_val:.4f} ≥ α = {alpha:.2f}): não há evidência suficiente "
            f"de diferença entre as médias."
        )
        interpretacao = (
            f"O teste t de Welch não detectou diferença estatisticamente significativa entre o tempo "
            f"médio até o merge com bot ({media_com:.2f} h) e sem bot ({media_sem:.2f} h), resultando "
            f"em t({gl:.1f}) = {t_stat:.4f} e p = {p_val:.4f} (≥ {alpha:.2f}). "
            f"Em linguagem simples: a redução observada de {abs(dif_media):.2f} h na média é pequena "
            f"frente à alta variabilidade dos dados (DP de {dp_com:.2f} h com bot e {dp_sem:.2f} h sem bot), "
            f"não permitindo afirmar, por este teste, que os bots alteram o tempo médio até o merge."
        )

    return ResultadoTesteIndividual(
        nome_teste=CENARIO.teste_parametrico,
        tipo_abordagem="Paramétrico",
        o_que_compara=(
            "Médias aritméticas populacionais (μ_com_bot vs. μ_sem_bot), ponderando a diferença "
            "pelo erro padrão combinado sem exigir igualdade de variâncias (ajuste de Welch-Satterthwaite)."
        ),
        h0_operacional=CENARIO.h0_welch,
        h1_operacional=CENARIO.h1_welch,
        direcao_teste=CENARIO.tipo_teste if alt_scipy == "two-sided" else alt_scipy,
        alpha=alpha,
        n_sem_bot=len(sem_arr),
        n_com_bot=len(com_arr),
        medida_central_sem_bot=media_sem,
        medida_central_com_bot=media_com,
        diferenca_central=dif_media,
        dispersao_sem_bot=dp_sem,
        dispersao_com_bot=dp_com,
        nome_estatistica="t",
        estatistica=t_stat,
        graus_liberdade_ou_auxiliar=gl,
        nome_auxiliar="gl (Welch-Satterthwaite)",
        p_valor=p_val,
        rejeitar_h0=rejeitar,
        decisao_estatistica=decisao,
        nome_tamanho_efeito="d de Cohen (Welch)",
        tamanho_efeito=d_cohen,
        interpretacao_efeito=classe_d,
        interpretacao_linguagem_simples=interpretacao,
    )


def executar_teste_mann_whitney(
    sem_bot: np.ndarray,
    com_bot: np.ndarray,
    alpha: float = CENARIO.alpha,
    alternativa: str = CENARIO.tipo_teste,
) -> ResultadoTesteIndividual:
    """Executa o Teste U de Mann-Whitney / Soma de Postos de Wilcoxon (com_bot vs. sem_bot).

    Condições de aplicação:
        - Observações independentes dentro dos grupos e entre os grupos;
        - Variável contínua ou ordinal que permita ranqueamento conjunto consistente;
        - Livre de distribuição (não exige normalidade e é robusto a outliers de cauda).
    """
    sem_arr = np.asarray(sem_bot, dtype=float)
    com_arr = np.asarray(com_bot, dtype=float)
    validar_amostras(sem_arr, com_arr)

    alt_scipy = normalizar_alternativa(alternativa)
    res = stats.mannwhitneyu(com_arr, sem_arr, alternative=alt_scipy, method="auto")

    u_stat = float(res.statistic)
    p_val = float(res.pvalue)
    z_stat = calcular_z_mann_whitney(u_stat, len(com_arr), len(sem_arr))

    mediana_sem = float(np.median(sem_arr))
    mediana_com = float(np.median(com_arr))
    dif_mediana = mediana_com - mediana_sem
    iqr_sem = float(stats.iqr(sem_arr))
    iqr_com = float(stats.iqr(com_arr))

    rejeitar = bool(p_val < alpha)
    r_rb = calcular_correlacao_rank_biserial(u_stat, len(com_arr), len(sem_arr))
    classe_r = classificar_rank_biserial(r_rb)
    prob_menor = 1.0 - (u_stat / (len(com_arr) * len(sem_arr)))

    if rejeitar:
        decisao = (
            f"Rejeitar H₀ (p = {p_val:.4f} < α = {alpha:.2f}): há diferença estatisticamente "
            f"significativa na ordenação de postos / medianas."
        )
        interpretacao = (
            f"O teste U de Mann-Whitney detectou diferença estatisticamente significativa na distribuição "
            f"dos tempos até o merge entre os grupos com bot (mediana = {mediana_com:.2f} h) e sem bot "
            f"(mediana = {mediana_sem:.2f} h), com U = {u_stat:.1f} (z = {z_stat:.4f}) e p = {p_val:.4f} "
            f"(< {alpha:.2f}). Em {prob_menor * 100:.1f}% dos pares comparados, um PR com bot foi mesclado "
            f"mais rapidamente do que um PR sem bot, indicando que a automação altera o tempo até o merge."
        )
    else:
        decisao = (
            f"Não rejeitar H₀ (p = {p_val:.4f} ≥ α = {alpha:.2f}): não há evidência suficiente "
            f"de dominância estocástica / diferença entre as medianas."
        )
        interpretacao = (
            f"O teste U de Mann-Whitney não rejeitou a hipótese nula ao comparar os postos do grupo "
            f"com bot (mediana = {mediana_com:.2f} h, IQR = {iqr_com:.2f} h) e do grupo sem bot "
            f"(mediana = {mediana_sem:.2f} h, IQR = {iqr_sem:.2f} h), obtendo U = {u_stat:.1f} "
            f"(z = {z_stat:.4f}) e p = {p_val:.4f} (≥ {alpha:.2f}). "
            f"Em linguagem simples: embora a mediana com bot seja {abs(dif_mediana):.2f} h menor e "
            f"um PR com bot vença em {prob_menor * 100:.1f}% dos pares (r_rb = {r_rb:.3f}), essa "
            f"vantagem nos postos ainda pode ocorrer por acaso em amostras de n = {len(sem_arr)}."
        )

    return ResultadoTesteIndividual(
        nome_teste=CENARIO.teste_nao_parametrico,
        tipo_abordagem="Não-paramétrico",
        o_que_compara=(
            "Ordenação conjunta de postos (ranks) e dominância estocástica P(X_com_bot > Y_sem_bot) "
            "(equivalente à comparação de medianas quando as distribuições têm formato semelhante)."
        ),
        h0_operacional=CENARIO.h0_mann_whitney,
        h1_operacional=CENARIO.h1_mann_whitney,
        direcao_teste=CENARIO.tipo_teste if alt_scipy == "two-sided" else alt_scipy,
        alpha=alpha,
        n_sem_bot=len(sem_arr),
        n_com_bot=len(com_arr),
        medida_central_sem_bot=mediana_sem,
        medida_central_com_bot=mediana_com,
        diferenca_central=dif_mediana,
        dispersao_sem_bot=iqr_sem,
        dispersao_com_bot=iqr_com,
        nome_estatistica="U",
        estatistica=u_stat,
        graus_liberdade_ou_auxiliar=z_stat,
        nome_auxiliar="z (aprox. normal)",
        p_valor=p_val,
        rejeitar_h0=rejeitar,
        decisao_estatistica=decisao,
        nome_tamanho_efeito="r rank-biserial",
        tamanho_efeito=r_rb,
        interpretacao_efeito=classe_r,
        interpretacao_linguagem_simples=interpretacao,
    )


# ----------------------------------------------------------------------------
# Aplicação conjunta e interpretação comparativa
# ----------------------------------------------------------------------------
def aplicar_ambos_testes(
    df: pd.DataFrame,
    alpha: float = CENARIO.alpha,
    alternativa: str = CENARIO.tipo_teste,
    origem_dados: str = "Dados simulados S01 (semente = 42)",
    semente: int | None = 42,
) -> ComparacaoTestes:
    """Aplica o teste t de Welch e o teste U de Mann-Whitney ao mesmo DataFrame e compara os resultados."""
    sem_bot, com_bot = extrair_grupos_dataframe(df)

    res_welch = executar_teste_welch(sem_bot, com_bot, alpha=alpha, alternativa=alternativa)
    res_mw = executar_teste_mann_whitney(sem_bot, com_bot, alpha=alpha, alternativa=alternativa)

    concordam = res_welch.rejeitar_h0 == res_mw.rejeitar_h0
    dif_p = abs(res_welch.p_valor - res_mw.p_valor)
    teste_menor_p = (
        res_mw.nome_teste if res_mw.p_valor < res_welch.p_valor else res_welch.nome_teste
    )

    max_com = float(np.max(com_bot))
    max_sem = float(np.max(sem_bot))

    if concordam and not res_welch.rejeitar_h0:
        resumo = (
            f"Ambos os testes convergem para a NÃO rejeição de H₀ ao nível α = {alpha:.2f} "
            f"(Welch: t = {res_welch.estatistica:.4f}, p = {res_welch.p_valor:.4f}; "
            f"Mann-Whitney: U = {res_mw.estatistica:.1f}, p = {res_mw.p_valor:.4f}). "
            f"Neste conjunto de dados ({origem_dados}), não há evidência estatística suficiente para "
            f"afirmar que o uso de bots de revisão altera o tempo até o merge de Pull Requests."
        )
    elif concordam and res_welch.rejeitar_h0:
        resumo = (
            f"Ambos os testes convergem para a REJEIÇÃO de H₀ ao nível α = {alpha:.2f} "
            f"(Welch: t = {res_welch.estatistica:.4f}, p = {res_welch.p_valor:.4f}; "
            f"Mann-Whitney: U = {res_mw.estatistica:.1f}, p = {res_mw.p_valor:.4f}), "
            f"confirmando que o uso de bots de revisão altera significativamente o tempo até o merge."
        )
    else:
        vencedor = res_mw if res_mw.rejeitar_h0 else res_welch
        perdedor = res_welch if res_mw.rejeitar_h0 else res_mw
        resumo = (
            f"Os testes divergiram na decisão para α = {alpha:.2f}: {vencedor.nome_teste} rejeitou H₀ "
            f"(p = {vencedor.p_valor:.4f} < {alpha:.2f}), enquanto {perdedor.nome_teste} não rejeitou H₀ "
            f"(p = {perdedor.p_valor:.4f} ≥ {alpha:.2f})."
        )

    explicacao_diferencas = (
        f"Embora aplicados exatamente às mesmas {res_welch.n_sem_bot + res_welch.n_com_bot} observações, "
        f"o teste {teste_menor_p} produziu um p-valor menor (Δp = {dif_p:.4f}: "
        f"p_Mann-Whitney = {res_mw.p_valor:.4f} vs. p_Welch = {res_welch.p_valor:.4f}). "
        f"A razão estatística reside na natureza assimétrica e nos valores extremos da amostra "
        f"(máximo de {max_com:.2f} h no grupo com_bot e {max_sem:.2f} h no grupo sem_bot): "
        f"no teste t de Welch, observações extremas na cauda direita puxam a média aritmética para cima "
        f"(reduzindo a diferença entre médias para {res_welch.diferenca_central:.2f} h) e inflam o desvio "
        f"padrão amostral ({res_welch.dispersao_com_bot:.2f} h e {res_welch.dispersao_sem_bot:.2f} h), "
        f"aumentando o denominador da estatística t e reduzindo sua sensibilidade. "
        f"Já o teste U de Mann-Whitney converte os tempos em postos ordenados (1 a "
        f"{res_mw.n_sem_bot + res_mw.n_com_bot}), limitando o peso de qualquer outlier ao último posto "
        f"e preservando maior sensibilidade ao deslocamento das medianas ({res_mw.medida_central_com_bot:.2f} h "
        f"vs. {res_mw.medida_central_sem_bot:.2f} h, diferença de {res_mw.diferenca_central:.2f} h)."
    )

    return ComparacaoTestes(
        origem_dados=origem_dados,
        semente=semente,
        alpha=alpha,
        direcao_teste=res_welch.direcao_teste,
        welch=res_welch,
        mann_whitney=res_mw,
        concordam_decisao=concordam,
        resumo_comparativo=resumo,
        explicacao_diferencas=explicacao_diferencas,
    )


# ----------------------------------------------------------------------------
# Funções enxutas de alto desempenho para reutilização na S02 (Q1, Q2 e Q3)
# ----------------------------------------------------------------------------
def avaliar_par_rapido(
    sem_bot: np.ndarray,
    com_bot: np.ndarray,
    alpha: float = CENARIO.alpha,
    alternativa: str = CENARIO.tipo_teste,
) -> Dict[str, float | bool]:
    """Executa ambos os testes de forma enxuta para loops de Monte Carlo (10.000 repetições na S02).

    Evita formatação de strings e cálculos descritivos redundantes para maximizar a velocidade
    nas simulações de Erro Tipo I (Q1), Poder (Q2) e Violação de Pressupostos (Q3).
    """
    alt_scipy = normalizar_alternativa(alternativa)
    res_t = stats.ttest_ind(com_bot, sem_bot, equal_var=False, alternative=alt_scipy)
    res_u = stats.mannwhitneyu(com_bot, sem_bot, alternative=alt_scipy, method="asymptotic")

    p_welch = float(res_t.pvalue)
    p_mw = float(res_u.pvalue)

    return {
        "t_stat": float(res_t.statistic),
        "p_welch": p_welch,
        "rejeita_welch": bool(p_welch < alpha),
        "u_stat": float(res_u.statistic),
        "p_mann_whitney": p_mw,
        "rejeita_mann_whitney": bool(p_mw < alpha),
    }


def avaliar_dataframe_rapido(
    df: pd.DataFrame,
    alpha: float = CENARIO.alpha,
    alternativa: str = CENARIO.tipo_teste,
) -> Dict[str, float | bool]:
    """Wrapper enxuto de `avaliar_par_rapido` que recebe diretamente um DataFrame simulado."""
    sem_bot, com_bot = extrair_grupos_dataframe(df)
    return avaliar_par_rapido(sem_bot, com_bot, alpha=alpha, alternativa=alternativa)


def avaliar_matrizes_rapido(
    sem_bot_matriz: np.ndarray,
    com_bot_matriz: np.ndarray,
    alpha: float = CENARIO.alpha,
    alternativa: str = CENARIO.tipo_teste,
) -> Dict[str, np.ndarray]:
    """Executa ambos os testes vetorizados (ao longo do axis=1) para matrizes de Monte Carlo.

    Parâmetros:
        sem_bot_matriz: Matriz 2D de formato (n_simulacoes, n_sem_bot).
        com_bot_matriz: Matriz 2D de formato (n_simulacoes, n_com_bot).
        alpha: Nível de significância (padrão: 0.05).
        alternativa: Direção do teste ('bicaudal', 'two-sided', etc.).

    Retorna:
        Dicionário com arrays 1D contendo estatísticas, p-valores e booleanos de rejeição
        para as n_simulacoes.
    """
    alt_scipy = normalizar_alternativa(alternativa)
    res_t = stats.ttest_ind(
        com_bot_matriz, sem_bot_matriz, axis=1, equal_var=False, alternative=alt_scipy
    )
    res_u = stats.mannwhitneyu(
        com_bot_matriz, sem_bot_matriz, axis=1, alternative=alt_scipy, method="asymptotic"
    )

    p_welch = np.asarray(res_t.pvalue, dtype=float)
    p_mw = np.asarray(res_u.pvalue, dtype=float)

    return {
        "t_stat": np.asarray(res_t.statistic, dtype=float),
        "p_welch": p_welch,
        "rejeita_welch": np.asarray(p_welch < alpha, dtype=bool),
        "u_stat": np.asarray(res_u.statistic, dtype=float),
        "p_mann_whitney": p_mw,
        "rejeita_mann_whitney": np.asarray(p_mw < alpha, dtype=bool),
    }


# ----------------------------------------------------------------------------
# Execução sobre os datasets oficiais (Simulado S01 e Reais) e exportação
# ----------------------------------------------------------------------------
def carregar_ou_gerar_simulados_s01(
    semente: int = 42,
    caminho_csv: Path | str = CAMINHO_DADOS_SIMULADOS_S01,
) -> pd.DataFrame:
    """Carrega o CSV de dados simulados da S01 ou gera com a semente fixa se necessário."""
    caminho = Path(caminho_csv)
    if caminho.exists() and semente == 42:
        return pd.read_csv(caminho)
    gerador = GeradorDadosSimulados(semente=semente)
    return gerador.gerar_dataset_experimento(n_sem_bot=30, n_com_bot=30, sob_h0=False)


def executar_analise_simulados_s01(
    semente: int = 42,
    alpha: float = CENARIO.alpha,
) -> ComparacaoTestes:
    """Executa os dois testes estatísticos sobre o conjunto de dados simulado oficial da S01."""
    df_sim = carregar_ou_gerar_simulados_s01(semente=semente)
    return aplicar_ambos_testes(
        df=df_sim,
        alpha=alpha,
        alternativa=CENARIO.tipo_teste,
        origem_dados=f"Dados Simulados S01 (semente = {semente})",
        semente=semente,
    )


def executar_analise_dados_reais(
    caminho: Path | str = CAMINHO_DADOS_REAIS_PADRAO,
    alpha: float = CENARIO.alpha,
) -> ComparacaoTestes:
    """Executa os dois testes estatísticos sobre a amostra de dados reais coletada."""
    df_reais = carregar_dados_reais(caminho)
    return aplicar_ambos_testes(
        df=df_reais,
        alpha=alpha,
        alternativa=CENARIO.tipo_teste,
        origem_dados="Amostra de Dados Reais (tiangolo/fastapi)",
        semente=None,
    )


def comparacao_para_dataframe(comparacao: ComparacaoTestes) -> pd.DataFrame:
    """Converte o objeto `ComparacaoTestes` em uma tabela padronizada para CSV e Dashboard."""
    linhas = []
    for res in (comparacao.welch, comparacao.mann_whitney):
        rotulo_central = "Média (h)" if res.tipo_abordagem == "Paramétrico" else "Mediana (h)"
        rotulo_disp = "DP (h)" if res.tipo_abordagem == "Paramétrico" else "IQR (h)"
        linhas.append(
            {
                "origem_dados": comparacao.origem_dados,
                "teste": res.nome_teste,
                "abordagem": res.tipo_abordagem,
                "direcao": res.direcao_teste,
                "alpha": res.alpha,
                "n_sem_bot": res.n_sem_bot,
                "n_com_bot": res.n_com_bot,
                "tipo_medida_central": rotulo_central,
                "central_sem_bot_h": round(res.medida_central_sem_bot, 4),
                "central_com_bot_h": round(res.medida_central_com_bot, 4),
                "diferenca_central_h": round(res.diferenca_central, 4),
                "tipo_dispersao": rotulo_disp,
                "dispersao_sem_bot_h": round(res.dispersao_sem_bot, 4),
                "dispersao_com_bot_h": round(res.dispersao_com_bot, 4),
                "nome_estatistica": res.nome_estatistica,
                "estatistica": round(res.estatistica, 4),
                "nome_auxiliar": res.nome_auxiliar,
                "valor_auxiliar": round(res.graus_liberdade_ou_auxiliar, 4),
                "p_valor": round(res.p_valor, 6),
                "rejeitar_h0": res.rejeitar_h0,
                "decisao_estatistica": res.decisao_estatistica,
                "nome_tamanho_efeito": res.nome_tamanho_efeito,
                "tamanho_efeito": round(res.tamanho_efeito, 4),
                "magnitude_efeito": res.interpretacao_efeito,
                "o_que_compara": res.o_que_compara,
                "interpretacao": res.interpretacao_linguagem_simples,
            }
        )
    return pd.DataFrame(linhas)


def salvar_resultados_testes_s01(
    caminho_saida: Path | str = CAMINHO_RESULTADOS_TESTES_S01,
    semente: int = 42,
) -> Path:
    """Executa os testes nos dados simulados (S01) e nos dados reais e salva o CSV consolidado."""
    comp_sim = executar_analise_simulados_s01(semente=semente)
    comp_reais = executar_analise_dados_reais()

    df_out = pd.concat(
        [comparacao_para_dataframe(comp_sim), comparacao_para_dataframe(comp_reais)],
        ignore_index=True,
    )
    saida = Path(caminho_saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(saida, index=False)
    return saida


def gerar_relatorio_testes_s01(semente: int = 42) -> str:
    """Gera relatório textual completo com a aplicação e interpretação dos dois testes."""
    comp_sim = executar_analise_simulados_s01(semente=semente)
    comp_reais = executar_analise_dados_reais()

    blocos: List[str] = [
        "================================================================================",
        "LAB04S01 — APLICAÇÃO E INTERPRETAÇÃO DOS DOIS TESTES ESTATÍSTICOS (PAR P1)",
        "================================================================================",
        f"Pergunta de pesquisa: {CENARIO.pergunta_pesquisa}",
        f"H0 conceitual: {CENARIO.h0_conceitual}",
        f"H1 conceitual: {CENARIO.h1_conceitual}",
        f"Direção do teste: {CENARIO.tipo_teste} | Nível de significância: α = {CENARIO.alpha:.2f}",
        "",
    ]

    for titulo, comp in [
        ("1. RESULTADOS NOS DADOS SIMULADOS (S01 — SEMENTE FIXA 42)", comp_sim),
        ("2. RESULTADOS NA AMOSTRA DE DADOS REAIS (tiangolo/fastapi)", comp_reais),
    ]:
        blocos.append(titulo)
        blocos.append("-" * len(titulo))
        for res in (comp.welch, comp.mann_whitney):
            blocos.extend(
                [
                    f"[{res.nome_teste} ({res.tipo_abordagem})]",
                    f"  • O que compara: {res.o_que_compara}",
                    f"  • H0 operacional: {res.h0_operacional}",
                    f"  • H1 operacional: {res.h1_operacional}",
                    f"  • Amostras: n_sem_bot = {res.n_sem_bot}, n_com_bot = {res.n_com_bot}",
                    f"  • Tendência central (sem_bot vs com_bot): "
                    f"{res.medida_central_sem_bot:.2f} h vs {res.medida_central_com_bot:.2f} h "
                    f"(Δ = {res.diferenca_central:+.2f} h)",
                    f"  • Dispersão (sem_bot vs com_bot): "
                    f"{res.dispersao_sem_bot:.2f} h vs {res.dispersao_com_bot:.2f} h",
                    f"  • Estatística: {res.nome_estatistica} = {res.estatistica:.4f} "
                    f"({res.nome_auxiliar} = {res.graus_liberdade_ou_auxiliar:.4f})",
                    f"  • p-valor: {res.p_valor:.6f}",
                    f"  • Tamanho do efeito ({res.nome_tamanho_efeito}): "
                    f"{res.tamanho_efeito:.4f} — {res.interpretacao_efeito}",
                    f"  • Decisão (α = {res.alpha:.2f}): {res.decisao_estatistica}",
                    f"  • Interpretação: {res.interpretacao_linguagem_simples}",
                    "",
                ]
            )
        blocos.extend(
            [
                f"Resumo comparativo ({comp.origem_dados}):",
                f"  {comp.resumo_comparativo}",
                "",
                "Diferenças observadas e razões estatísticas:",
                f"  {comp.explicacao_diferencas}",
                "",
            ]
        )

    return "\n".join(blocos)


if __name__ == "__main__":  # pragma: no cover
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    caminho_salvo = salvar_resultados_testes_s01()
    print(gerar_relatorio_testes_s01())
    print(f"Resultados salvos em: {caminho_salvo}")
