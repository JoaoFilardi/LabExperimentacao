
"""
LAB04 - Q2
Simulação do poder estatístico dos testes t de Welch e Mann-Whitney.

Avalia o comportamento dos testes para diferentes tamanhos de efeito,
registrando os p-valores e calculando a proporção de rejeições de H0.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from lab04.src.simulacao import GeradorDadosSimulados
from lab04.src.testes_estatisticos import (
    executar_teste_welch,
    executar_teste_mann_whitney,
)


ALPHA = 0.05
SEMENTE_PADRAO = 42
N_SIMULACOES_PADRAO = 10_000

# Reduções percentuais no tempo de merge do grupo com bot.
# O efeito zero representa o cenário em que H0 é verdadeira.
EFEITOS_PADRAO = [0.00, 0.05, 0.10, 0.20, 0.30, 0.40]


def executar_simulacao_efeito(
    gerador,
    efeito_reducao,
    n_simulacoes=N_SIMULACOES_PADRAO,
    n_sem_bot=30,
    n_com_bot=30,
    alpha=ALPHA,
):
    """Executa os dois testes para um tamanho de efeito."""

    matriz_sem_bot, matriz_com_bot = (
        gerador.gerar_matrizes_experimento(
            n_simulacoes=n_simulacoes,
            n_sem_bot=n_sem_bot,
            n_com_bot=n_com_bot,
            efeito_reducao=efeito_reducao,
        )
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


def calcular_poder(resultados):
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

    resumo["poder_percentual"] = (
        resumo["poder_estatistico"] * 100
    )

    return resumo


def executar_q2(
    efeitos=None,
    n_simulacoes=N_SIMULACOES_PADRAO,
    n_sem_bot=30,
    n_com_bot=30,
    semente=SEMENTE_PADRAO,
    diretorio_saida=None,
):
    """
    Executa o experimento Q2 completo.

    Retorna:
        resultados: p-valores individuais de cada repetição.
        resumo: poder estatístico por teste e tamanho de efeito.
    """

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

    # Identificação do cenário e da semente utilizada.
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


if __name__ == "__main__":
    resultados, resumo = executar_q2()

    print("\nPoder estatístico encontrado:")
    print(
        resumo[
            [
                "efeito_reducao",
                "teste",
                "poder_percentual",
                "p_valor_medio",
            ]
        ].to_string(index=False)
    )
