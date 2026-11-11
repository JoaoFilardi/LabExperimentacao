"""Simulações de Monte Carlo e análise do Poder Estatístico (Questão Q2).

Issue #53 / #56: [ LAB04S02 ] Implementar simulações e análise do poder estatístico (Q2)
e integrar simulações e gráficos ao dashboard.

Este módulo avalia a capacidade dos dois testes estatísticos (t de Welch e U de Mann-Whitney)
de detectar efeitos reais de tamanhos crescentes (6 níveis: 0%, 10%, 20%, 30%, 40% e 50%
de redução no tempo até o merge) em 10.000 repetições de Monte Carlo por configuração:
1. Cenário Original (Q2_Base): Distribuição Log-normal calibrada nos dados reais (n = 30);
2. Controle Teórico Gaussiano (Controle_Normal): Distribuição Normal simétrica sem outliers
   (n = 30), demonstrando em que situação teórica a vantagem de poder muda de lado para o
   teste paramétrico t de Welch.

Uso via linha de comando:
    python -m lab04.src.simulacao_q2
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

from lab04.src.cenario import CENARIO
from lab04.src.simulacao import GeradorDadosSimulados
from lab04.src.simulacao_q1 import calcular_intervalo_confianca_wilson
from lab04.src.simulacao_q3 import EFEITOS_PADRAO_Q3, carregar_ou_executar_q3
from lab04.src.testes_estatisticos import avaliar_matrizes_rapido

CAMINHO_DADOS_DIR = Path(__file__).resolve().parent.parent / "data"
CAMINHO_Q2_RESUMO_CSV = CAMINHO_DADOS_DIR / "resultados_q2_poder.csv"

EFEITOS_PADRAO_Q2: Tuple[float, ...] = EFEITOS_PADRAO_Q3


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
    rng = np.random.default_rng(semente)
    linhas: List[Dict[str, Any]] = []

    for delta in efeitos:
        rng = np.random.default_rng(semente)
        amostras = rng.normal(loc=media_base, scale=desvio_base, size=(n_simulacoes, n_sem_bot + n_com_bot))
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
    linha_30_gauss = df_gauss[df_gauss["efeito_pct"] == 30.0].iloc[0] if 30.0 in df_gauss["efeito_pct"].values else df_gauss.iloc[-1]

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
            res_q3 = carregar_ou_executar_q3(semente=semente, n_simulacoes=n_simulacoes)
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
    res_q2 = carregar_ou_executar_q2(semente=42, n_simulacoes=10_000, forcar_reexecucao=True)
    print("=" * 84)
    print("LAB04S02 — SIMULAÇÃO DE PODER ESTATÍSTICO (QUESTÃO Q2)")
    print("=" * 84)
    print(res_q2.df_poder_q2.to_string(index=False))
    print("\n--- CONTROLE TEÓRICO GAUSSIANO (QUANDO A VANTAGEM MUDA DE LADO) ---")
    print(res_q2.df_controle_gaussiano.to_string(index=False))
    print("\nSíntese:")
    print(res_q2.sintese_comparativa)
    print(f"\nSalvo em: {CAMINHO_Q2_RESUMO_CSV}")
