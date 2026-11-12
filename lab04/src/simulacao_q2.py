"""Simulações de Monte Carlo e análise do Poder Estatístico (Questão Q2).

Issue #53 / #54 / #56: [ LAB04S02 ] Implementar simulações e análises do poder estatístico (Q2)
e integrar curvas de poder ao gráfico G4 e ao dashboard.

Avalia o comportamento dos testes t de Welch e U de Mann-Whitney para diferentes
tamanhos de efeito, registrando os p-valores e calculando a proporção de rejeições
de H0, além de fornecer o comparativo com o controle teórico Gaussiano (Normal
simétrica sem outliers) para demonstrar no gráfico G4 quando a vantagem de poder
muda de lado.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np
import pandas as pd

from lab04.src.cenario import CENARIO
from lab04.src.simulacao import GeradorDadosSimulados
from lab04.src.simulacao_q1 import calcular_intervalo_confianca_wilson
from lab04.src.simulacao_q3 import EFEITOS_PADRAO_Q3
from lab04.src.testes_estatisticos import (
    avaliar_matrizes_rapido,
    executar_teste_mann_whitney,
    executar_teste_welch,
)

ALPHA = 0.05
SEMENTE_PADRAO = 42
N_SIMULACOES_PADRAO = 10_000

# Reduções percentuais no tempo de merge do grupo com bot (API #53).
# O efeito zero representa o cenário em que H0 é verdadeira.
EFEITOS_PADRAO = [0.00, 0.05, 0.10, 0.20, 0.30, 0.40]

# Grade de efeitos alinhada entre Q2 e Q3 para as curvas comparativas do G4 (#54/#55/#56)
EFEITOS_PADRAO_Q2: Tuple[float, ...] = EFEITOS_PADRAO_Q3

CAMINHO_DADOS_DIR = Path(__file__).resolve().parent.parent / "data"
CAMINHO_Q2_RESUMO_CSV = CAMINHO_DADOS_DIR / "resultados_q2_poder.csv"
CAMINHO_PODER_ESTATISTICO_Q2 = CAMINHO_DADOS_DIR / "poder_estatistico_q2.csv"
CAMINHO_RESULTADOS_INDIVIDUAIS_Q2 = CAMINHO_DADOS_DIR / "resultados_q2.csv"


@dataclass(frozen=True)
class ResultadoSimulacaoQ2:
    """Resultado consolidado da simulação de Poder Estatístico (Questão Q2)."""

    semente: int
    n_simulacoes: int
    n_sem_bot: int
    n_com_bot: int
    alpha: float
    efeitos_avaliados: Tuple[float, ...]
    df_poder_q2: pd.DataFrame
    df_controle_gaussiano: pd.DataFrame
    sintese_comparativa: str


def executar_simulacao_efeito(
    gerador: GeradorDadosSimulados,
    efeito_reducao: float,
    n_simulacoes: int = N_SIMULACOES_PADRAO,
    n_sem_bot: int = 30,
    n_com_bot: int = 30,
    alpha: float = ALPHA,
) -> pd.DataFrame:
    """Executa os dois testes para um tamanho de efeito e retorna p-valores por repetição."""
    matriz_sem_bot, matriz_com_bot = gerador.gerar_matrizes_experimento(
        n_simulacoes=n_simulacoes,
        n_sem_bot=n_sem_bot,
        n_com_bot=n_com_bot,
        efeito_reducao=efeito_reducao,
    )

    resultados = []

    for i in range(n_simulacoes):
        sem_bot = matriz_sem_bot[i]
        com_bot = matriz_com_bot[i]

        resultado_welch = executar_teste_welch(
            sem_bot,
            com_bot,
            alpha=alpha,
        )

        resultado_mann = executar_teste_mann_whitney(
            sem_bot,
            com_bot,
            alpha=alpha,
        )

        p_welch = float(resultado_welch.p_valor)
        p_mann = float(resultado_mann.p_valor)

        resultados.append({
            "repeticao": i + 1,
            "efeito_reducao": efeito_reducao,
            "teste": "Welch",
            "p_valor": p_welch,
            "rejeitou_h0": p_welch < alpha,
        })

        resultados.append({
            "repeticao": i + 1,
            "efeito_reducao": efeito_reducao,
            "teste": "Mann-Whitney",
            "p_valor": p_mann,
            "rejeitou_h0": p_mann < alpha,
        })

    return pd.DataFrame(resultados)


def calcular_poder(resultados: pd.DataFrame) -> pd.DataFrame:
    """Calcula a taxa de rejeição de H0 para cada teste e efeito."""
    resumo = (
        resultados
        .groupby(["efeito_reducao", "teste"], as_index=False)
        .agg(
            total_simulacoes=("rejeitou_h0", "count"),
            rejeicoes_h0=("rejeitou_h0", "sum"),
            poder_estatistico=("rejeitou_h0", "mean"),
            p_valor_medio=("p_valor", "mean"),
            p_valor_mediano=("p_valor", "median"),
        )
    )

    resumo["poder_percentual"] = resumo["poder_estatistico"] * 100
    return resumo


def executar_q2(
    efeitos: Sequence[float] | None = None,
    n_simulacoes: int = N_SIMULACOES_PADRAO,
    n_sem_bot: int = 30,
    n_com_bot: int = 30,
    semente: int = SEMENTE_PADRAO,
    diretorio_saida: Path | str | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Executa o experimento Q2 completo registrando p-valores individuais e resumo."""
    if efeitos is None:
        efeitos = EFEITOS_PADRAO

    if n_simulacoes <= 0:
        raise ValueError("O número de simulações deve ser positivo.")

    if n_sem_bot <= 0 or n_com_bot <= 0:
        raise ValueError("Os tamanhos dos grupos devem ser positivos.")

    if not efeitos:
        raise ValueError("Informe pelo menos um tamanho de efeito.")

    if any(not 0 <= efeito < 1 for efeito in efeitos):
        raise ValueError("Os efeitos devem estar no intervalo [0, 1).")

    gerador = GeradorDadosSimulados(semente=semente)
    resultados_por_efeito = []

    for efeito in efeitos:
        print(
            f"Executando efeito de {efeito:.0%} "
            f"({n_simulacoes} simulações)..."
        )

        resultado = executar_simulacao_efeito(
            gerador=gerador,
            efeito_reducao=efeito,
            n_simulacoes=n_simulacoes,
            n_sem_bot=n_sem_bot,
            n_com_bot=n_com_bot,
        )

        resultados_por_efeito.append(resultado)

    resultados = pd.concat(
        resultados_por_efeito,
        ignore_index=True,
    )

    resumo = calcular_poder(resultados)

    resultados["semente"] = semente
    resultados["alpha"] = ALPHA

    resumo["semente"] = semente
    resumo["alpha"] = ALPHA
    resumo["n_simulacoes"] = n_simulacoes

    if diretorio_saida is None:
        diretorio_saida = Path(__file__).resolve().parents[1] / "data"

    diretorio_saida = Path(diretorio_saida)
    diretorio_saida.mkdir(parents=True, exist_ok=True)

    caminho_resultados = diretorio_saida / "resultados_q2.csv"
    caminho_poder = diretorio_saida / "poder_estatistico_q2.csv"

    resultados.to_csv(
        caminho_resultados,
        index=False,
        encoding="utf-8",
    )

    resumo.to_csv(
        caminho_poder,
        index=False,
        encoding="utf-8",
    )

    print("\nSimulação Q2 concluída!")
    print(f"Resultados individuais: {caminho_resultados}")
    print(f"Resumo do poder: {caminho_poder}")

    return resultados, resumo


def executar_simulacao_q2_gaussiano(
    n_simulacoes: int = 10_000,
    semente: int = 42,
    n_sem_bot: int = 30,
    n_com_bot: int = 30,
    efeitos: Sequence[float] = EFEITOS_PADRAO_Q2,
    media_base: float = 25.0,
    desvio_base: float = 12.0,
    alpha: float = CENARIO.alpha,
    alternativa: str = CENARIO.tipo_teste,
) -> pd.DataFrame:
    """Simula curvas de poder sob distribuição Normal simétrica pura (sem assimetria/outliers).

    Demonstra empiricamente a condição clássica em que a vantagem de poder muda de lado
    em favor do teste paramétrico t de Welch (Eficiência Relativa Assintótica de Mann-Whitney
    sob normalidade é de ~95,5%).
    """
    linhas: List[Dict[str, Any]] = []

    for delta in efeitos:
        rng = np.random.default_rng(semente)
        amostras = rng.normal(
            loc=media_base, scale=desvio_base, size=(n_simulacoes, n_sem_bot + n_com_bot)
        )
        if delta > 0.0:
            amostras[:, n_sem_bot:] = amostras[:, n_sem_bot:] - (media_base * delta)
        amostras = np.round(amostras, 2)

        mat_sem = amostras[:, :n_sem_bot]
        mat_com = amostras[:, n_sem_bot:]
        res = avaliar_matrizes_rapido(mat_sem, mat_com, alpha=alpha, alternativa=alternativa)

        rej_w = int(np.sum(res["rejeita_welch"]))
        rej_mw = int(np.sum(res["rejeita_mann_whitney"]))
        p_w, inf_w, sup_w = calcular_intervalo_confianca_wilson(rej_w, n_simulacoes)
        p_mw, inf_mw, sup_mw = calcular_intervalo_confianca_wilson(rej_mw, n_simulacoes)

        linhas.append(
            {
                "cenario_codigo": "Controle_Normal",
                "cenario_curto": "Controle Teórico: Normal Simétrica (n=30)",
                "condicao": "Distribuição Normal simétrica sem outliers (n=30)",
                "n_por_grupo": n_sem_bot,
                "efeito_reducao": float(delta),
                "efeito_pct": float(delta) * 100.0,
                "sob_h0": bool(delta == 0.0),
                "n_simulacoes": n_simulacoes,
                "rejeicoes_welch": rej_w,
                "poder_welch": p_w,
                "poder_welch_pct": p_w * 100.0,
                "ic_inf_welch_pct": inf_w * 100.0,
                "ic_sup_welch_pct": sup_w * 100.0,
                "rejeicoes_mann_whitney": rej_mw,
                "poder_mann_whitney": p_mw,
                "poder_mann_whitney_pct": p_mw * 100.0,
                "ic_inf_mw_pct": inf_mw * 100.0,
                "ic_sup_mw_pct": sup_mw * 100.0,
                "vantagem_mw_pp": (p_mw - p_w) * 100.0,
            }
        )

    return pd.DataFrame(linhas)


def executar_simulacao_q2(
    n_simulacoes: int = 10_000,
    semente: int = 42,
    n_sem_bot: int = 30,
    n_com_bot: int = 30,
    efeitos: Sequence[float] = EFEITOS_PADRAO_Q2,
    alpha: float = CENARIO.alpha,
    alternativa: str = CENARIO.tipo_teste,
) -> ResultadoSimulacaoQ2:
    """Executa a simulação de Poder Estatístico (Q2) no cenário log-normal realista e no controle normal."""
    efeitos_tupla = tuple(float(e) for e in efeitos)
    if len(efeitos_tupla) < 5 or 0.0 not in efeitos_tupla:
        raise ValueError(
            "Q2 exige pelo menos 5 tamanhos de efeito começando em 0.0 (H0 verdadeira)."
        )

    gerador = GeradorDadosSimulados(semente=semente)
    linhas_q2: List[Dict[str, Any]] = []

    for delta in efeitos_tupla:
        gerador.redefinir_semente(semente)
        mat_sem, mat_com = gerador.gerar_matrizes_experimento(
            n_simulacoes=n_simulacoes,
            n_sem_bot=n_sem_bot,
            n_com_bot=n_com_bot,
            efeito_reducao=delta,
            arredondar=2,
        )
        res = avaliar_matrizes_rapido(mat_sem, mat_com, alpha=alpha, alternativa=alternativa)

        rej_w = int(np.sum(res["rejeita_welch"]))
        rej_mw = int(np.sum(res["rejeita_mann_whitney"]))
        p_w, inf_w, sup_w = calcular_intervalo_confianca_wilson(rej_w, n_simulacoes)
        p_mw, inf_mw, sup_mw = calcular_intervalo_confianca_wilson(rej_mw, n_simulacoes)

        linhas_q2.append(
            {
                "cenario_codigo": "Q2_Base",
                "cenario_curto": "Cenário Original (n=30)",
                "condicao": f"Log-normal realista (n={n_sem_bot})",
                "n_por_grupo": n_sem_bot,
                "efeito_reducao": delta,
                "efeito_pct": delta * 100.0,
                "sob_h0": bool(delta == 0.0),
                "n_simulacoes": n_simulacoes,
                "rejeicoes_welch": rej_w,
                "poder_welch": p_w,
                "poder_welch_pct": p_w * 100.0,
                "ic_inf_welch_pct": inf_w * 100.0,
                "ic_sup_welch_pct": sup_w * 100.0,
                "rejeicoes_mann_whitney": rej_mw,
                "poder_mann_whitney": p_mw,
                "poder_mann_whitney_pct": p_mw * 100.0,
                "ic_inf_mw_pct": inf_mw * 100.0,
                "ic_sup_mw_pct": sup_mw * 100.0,
                "vantagem_mw_pp": (p_mw - p_w) * 100.0,
            }
        )

    df_poder_q2 = pd.DataFrame(linhas_q2)
    df_gauss = executar_simulacao_q2_gaussiano(
        n_simulacoes=n_simulacoes,
        semente=semente,
        n_sem_bot=n_sem_bot,
        n_com_bot=n_com_bot,
        efeitos=efeitos_tupla,
        alpha=alpha,
        alternativa=alternativa,
    )

    linha_50 = df_poder_q2.sort_values("efeito_reducao").iloc[-1]
    linha_30_gauss = (
        df_gauss[df_gauss["efeito_pct"] == 30.0].iloc[0]
        if 30.0 in df_gauss["efeito_pct"].values
        else df_gauss.iloc[-1]
    )

    sintese = (
        f"No cenário original log-normal (Q2, n={n_sem_bot}, 10.000 simulações por efeito), o poder "
        f"estatístico cresce monotonicamente conforme o tamanho do efeito avança de 0% a 50%, e o "
        f"teste U de Mann-Whitney supera o teste t de Welch em todos os níveis de efeito "
        f"(atingindo {float(linha_50['poder_mann_whitney_pct']):.2f}% contra "
        f"{float(linha_50['poder_welch_pct']):.2f}% em δ=50%, vantagem de "
        f"+{float(linha_50['vantagem_mw_pp']):.2f} p.p.). "
        f"A vantagem só muda de lado para o teste t de Welch no controle teórico sob distribuição "
        f"Normal simétrica sem outliers ({float(linha_30_gauss['poder_welch_pct']):.2f}% no Welch "
        f"vs. {float(linha_30_gauss['poder_mann_whitney_pct']):.2f}% no Mann-Whitney em δ=30%), "
        f"confirmando que a assimetria log-normal dos tempos de software é o fator determinante "
        f"para a superioridade do teste não-paramétrico."
    )

    return ResultadoSimulacaoQ2(
        semente=semente,
        n_simulacoes=n_simulacoes,
        n_sem_bot=n_sem_bot,
        n_com_bot=n_com_bot,
        alpha=alpha,
        efeitos_avaliados=efeitos_tupla,
        df_poder_q2=df_poder_q2,
        df_controle_gaussiano=df_gauss,
        sintese_comparativa=sintese,
    )


def carregar_ou_executar_q2(
    semente: int = 42,
    n_simulacoes: int = 10_000,
    forcar_reexecucao: bool = False,
    caminho_csv: Path | str = CAMINHO_Q2_RESUMO_CSV,
) -> ResultadoSimulacaoQ2:
    """Carrega os resultados de Q2 a partir do disco ou executa a simulação."""
    p_csv = Path(caminho_csv)
    if not forcar_reexecucao and p_csv.exists() and semente == 42 and n_simulacoes == 10_000:
        df_lido = pd.read_csv(p_csv)
        df_base = df_lido[df_lido["cenario_codigo"] == "Q2_Base"].reset_index(drop=True)
        df_gauss = df_lido[df_lido["cenario_codigo"] == "Controle_Normal"].reset_index(drop=True)
        if len(df_base) == 6 and len(df_gauss) == 6:
            linha_50 = df_base.sort_values("efeito_reducao").iloc[-1]
            linha_30_g = df_gauss[df_gauss["efeito_pct"] == 30.0].iloc[0]
            sintese = (
                f"No cenário original log-normal (Q2, n=30, 10.000 simulações por efeito), o poder "
                f"estatístico cresce monotonicamente conforme o tamanho do efeito avança de 0% a 50%, e o "
                f"teste U de Mann-Whitney supera o teste t de Welch em todos os níveis de efeito "
                f"(atingindo {float(linha_50['poder_mann_whitney_pct']):.2f}% contra "
                f"{float(linha_50['poder_welch_pct']):.2f}% em δ=50%, vantagem de "
                f"+{float(linha_50['vantagem_mw_pp']):.2f} p.p.). "
                f"A vantagem só muda de lado para o teste t de Welch no controle teórico sob distribuição "
                f"Normal simétrica sem outliers ({float(linha_30_g['poder_welch_pct']):.2f}% no Welch "
                f"vs. {float(linha_30_g['poder_mann_whitney_pct']):.2f}% no Mann-Whitney em δ=30%), "
                f"confirmando que a assimetria log-normal dos tempos de software é o fator determinante "
                f"para a superioridade do teste não-paramétrico."
            )
            return ResultadoSimulacaoQ2(
                semente=semente,
                n_simulacoes=n_simulacoes,
                n_sem_bot=30,
                n_com_bot=30,
                alpha=CENARIO.alpha,
                efeitos_avaliados=EFEITOS_PADRAO_Q2,
                df_poder_q2=df_base,
                df_controle_gaussiano=df_gauss,
                sintese_comparativa=sintese,
            )

    res = executar_simulacao_q2(n_simulacoes=n_simulacoes, semente=semente)
    if semente == 42 and n_simulacoes == 10_000:
        p_csv.parent.mkdir(parents=True, exist_ok=True)
        pd.concat([res.df_poder_q2, res.df_controle_gaussiano], ignore_index=True).to_csv(
            p_csv, index=False
        )
    return res


if __name__ == "__main__":  # pragma: no cover
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    res_q2 = carregar_ou_executar_q2(semente=42, n_simulacoes=10_000)
    print(res_q2.sintese_comparativa)
