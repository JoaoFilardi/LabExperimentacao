"""Simulações de Monte Carlo para violação dos pressupostos estatísticos (Questão Q3).

Issue #55: [ LAB04S02 ] Simular violações dos pressupostos estatísticos (Q3).

Este módulo investiga como o desempenho do Teste t de Welch (paramétrico) e do Teste U de
Mann-Whitney (não-paramétrico) se modifica quando os dados violam severamente os pressupostos
do teste paramétrico, repetindo as análises de:
1. Erro Tipo I (Q1 sob violação — 10.000 simulações com H0 verdadeira, efeito = 0%);
2. Poder Estatístico (Q2 sob violação — 10.000 simulações para cada um dos 6 tamanhos de
   efeito: 0%, 10%, 20%, 30%, 40% e 50% de redução no tempo até o merge).

Condições experimentais comparadas:
- `Q1_Base` / `Q2_Base` (Cenário Original): Distribuição Log-normal calibrada nos dados reais
  (`mu_log = 2.8053`, `sigma_log = 0.9254`, `n = 30` por grupo);
- `Q3_Outliers` (Violação 1 — Outliers Severos): Contaminação de 10% das observações de cada
  amostra (`6` de `60` PRs) por `5x + 50h` (`n = 30` por grupo), representando PRs bloqueados
  por falhas graves de CI, disputas de arquitetura ou dependências externas;
- `Q3_AmostraPequena` (Violação 2 — Tamanho Amostral Pequeno): Redução da amostra para `n = 10`
  PRs por grupo sob a mesma assimetria log-normal, violando a convergência assintótica do
  Teorema Central do Limite (TCL) exigida pelo teste t de Welch.

Uso via linha de comando:
    python -m lab04.src.simulacao_q3
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from lab04.src.cenario import CENARIO
from lab04.src.simulacao import GeradorDadosSimulados
from lab04.src.simulacao_q1 import (
    calcular_intervalo_confianca_wilson,
    classificar_comportamento_erro_tipo_1,
)
from lab04.src.testes_estatisticos import avaliar_matrizes_rapido

CAMINHO_DADOS_DIR = Path(__file__).resolve().parent.parent / "data"
CAMINHO_Q3_ERRO_TIPO_1_CSV = CAMINHO_DADOS_DIR / "resultados_q3_erro_tipo_1.csv"
CAMINHO_Q3_PODER_LARGO_CSV = CAMINHO_DADOS_DIR / "resultados_q3_poder_violacoes.csv"
CAMINHO_Q3_CURVAS_G4_CSV = CAMINHO_DADOS_DIR / "resultados_q3_curvas_g4.csv"
CAMINHO_Q3_IMPACTO_CSV = CAMINHO_DADOS_DIR / "resultados_q3_comparativo_impacto.csv"

# Pelo menos 5 tamanhos de efeito começando em zero (adotamos 6 níveis: 0% a 50%)
EFEITOS_PADRAO_Q3: Tuple[float, ...] = (0.00, 0.10, 0.20, 0.30, 0.40, 0.50)


@dataclass(frozen=True)
class PressupostoViolacaoInfo:
    """Metadados formais sobre os pressupostos dos testes e as violações simuladas em Q3."""

    codigo_violacao: str
    nome_violacao: str
    pressuposto_violado: str
    justificativa_cenario_se: str
    impacto_teorico_welch: str
    impacto_teorico_mann_whitney: str


@dataclass(frozen=True)
class ResultadoSimulacaoQ3:
    """Estrutura consolidada de resultados da Questão Q3 (Erro Tipo I e Poder sob violação)."""

    semente: int
    n_simulacoes: int
    alpha: float
    efeitos_avaliados: Tuple[float, ...]
    pressupostos_e_violacoes: List[PressupostoViolacaoInfo]
    df_erro_tipo_1: pd.DataFrame
    df_poder_largo: pd.DataFrame
    df_curvas_g4: pd.DataFrame
    df_comparativo_impacto: pd.DataFrame
    sintese_interpretativa: str


# ----------------------------------------------------------------------------
# 1. Identificação dos pressupostos e justificativa das violações no cenário
# ----------------------------------------------------------------------------
def obter_pressupostos_e_violacoes() -> List[PressupostoViolacaoInfo]:
    """Retorna a documentação estruturada dos pressupostos violados e sua relevância em SE."""
    return [
        PressupostoViolacaoInfo(
            codigo_violacao="Q3_Outliers",
            nome_violacao="Presença de Outliers Extremos (10% de contaminação: 5x + 50h, n=30)",
            pressuposto_violado=(
                "Normalidade das distribuições populacionais e estabilidade finita da variância "
                "amostral no denominador da estatística t de Welch."
            ),
            justificativa_cenario_se=(
                "Em repositórios reais de software, cerca de 5% a 10% dos Pull Requests sofrem "
                "bloqueios anômalos (espera por revisores seniores em férias, quebras de ambiente "
                "de CI/CD, conflitos complexos de rebase ou discussões arquiteturais prolongadas), "
                "gerando tempos até o merge de centenas de horas que destoam do fluxo normal."
            ),
            impacto_teorico_welch=(
                "Alta sensibilidade: os outliers entram ao quadrado no cálculo da variância amostral "
                "(s²), inflando drasticamente o erro padrão no denominador de t. Sob H0, isso torna "
                "o teste excessivamente conservador (reduz a taxa de rejeição para longe de 5%); sob H1, "
                "destrói a razão sinal-ruído e provoca queda severa no poder estatístico."
            ),
            impacto_teorico_mann_whitney=(
                "Alta robustez: como as observações são convertidas em postos ordenados (1 a N), "
                "um valor extremo recebe apenas o último posto (N), independentemente de sua magnitude "
                "bruta em horas. A taxa de Erro Tipo I permanece próxima a 5% e a perda de poder é mínima."
            ),
        ),
        PressupostoViolacaoInfo(
            codigo_violacao="Q3_AmostraPequena",
            nome_violacao="Tamanho Amostral Pequeno sob Forte Assimetria (Log-normal com n=10 por grupo)",
            pressuposto_violado=(
                "Normalidade assintótica da distribuição amostral das médias via Teorema Central do "
                "Limite (TCL) e adequação da aproximação de Welch-Satterthwaite para graus de liberdade."
            ),
            justificativa_cenario_se=(
                "Em sprints curtas, equipes pequenas ou avaliações piloto de um novo bot de revisão, "
                "frequentemente dispõe-se de apenas 10 Pull Requests por grupo. Com amostras tão "
                "reduzidas e distribuição fortemente assimétrica à direita (skewness > 1,7), o TCL "
                "não consegue normalizar a média amostral."
            ),
            impacto_teorico_welch=(
                "Forte degradação: com n=10 sob distribuição log-normal, a distribuição da estatística t "
                "afasta-se da distribuição t de Student teórica, acentuando o conservadorismo sob H0 "
                "(taxa de Erro Tipo I cai para ~2,9%) e reduzindo o poder de detecção sob H1."
            ),
            impacto_teorico_mann_whitney=(
                "Moderada resiliência: preserva a taxa de Erro Tipo I muito mais próxima de 5% (~4,33%) "
                "e mantém vantagem consistente de poder sobre o teste t de Welch em todos os tamanhos "
                "de efeito, embora o poder absoluto de ambos caia devido ao menor volume de informação (n=10)."
            ),
        ),
    ]


# ----------------------------------------------------------------------------
# 2. Execução de Q1 e Q2 nas condições original e de violação (Q3)
# ----------------------------------------------------------------------------
def _avaliar_condicao_matrizes(
    mat_sem: np.ndarray,
    mat_com: np.ndarray,
    alpha: float = CENARIO.alpha,
    alternativa: str = CENARIO.tipo_teste,
) -> Dict[str, Any]:
    """Executa ambos os testes sobre as matrizes 2D e calcula proporções e ICs de Wilson."""
    n_simulacoes = mat_sem.shape[0]
    res = avaliar_matrizes_rapido(mat_sem, mat_com, alpha=alpha, alternativa=alternativa)

    rej_w = int(np.sum(res["rejeita_welch"]))
    rej_mw = int(np.sum(res["rejeita_mann_whitney"]))

    p_w, inf_w, sup_w = calcular_intervalo_confianca_wilson(rej_w, n_simulacoes)
    p_mw, inf_mw, sup_mw = calcular_intervalo_confianca_wilson(rej_mw, n_simulacoes)

    ks_w = stats.kstest(res["p_welch"], "uniform")
    ks_mw = stats.kstest(res["p_mann_whitney"], "uniform")

    return {
        "n_simulacoes": n_simulacoes,
        "rej_welch": rej_w,
        "taxa_welch": p_w,
        "ic_inf_welch": inf_w,
        "ic_sup_welch": sup_w,
        "ks_p_welch": float(ks_w.pvalue),
        "rej_mw": rej_mw,
        "taxa_mw": p_mw,
        "ic_inf_mw": inf_mw,
        "ic_sup_mw": sup_mw,
        "ks_p_mw": float(ks_mw.pvalue),
    }


def executar_simulacao_q3(
    n_simulacoes: int = 10_000,
    semente: int = 42,
    efeitos: Sequence[float] = EFEITOS_PADRAO_Q3,
    alpha: float = CENARIO.alpha,
    alternativa: str = CENARIO.tipo_teste,
) -> ResultadoSimulacaoQ3:
    """Executa as simulações completas da Questão Q3 (repetindo Q1 e Q2 sob violação de pressupostos).

    Garante que para `efeito == 0.0` (H0 verdadeira) os resultados de Erro Tipo I coincidam
    exatamente bit a bit com as simulações de Q1 e do Gráfico G3.
    """
    efeitos_tupla = tuple(float(e) for e in efeitos)
    if len(efeitos_tupla) < 5 or 0.0 not in efeitos_tupla:
        raise ValueError(
            "A simulação deve conter pelo menos 5 tamanhos de efeito, incluindo 0.0 (H0 verdadeira)."
        )

    gerador = GeradorDadosSimulados(semente=semente)

    configuracoes_cenarios = [
        {
            "cenario_codigo": "Q1_Base",
            "cenario_poder_codigo": "Q2_Base",
            "cenario_rotulo": "Cenário Original (Q1)\nLog-normal (n=30)",
            "cenario_curto": "Cenário Original (n=30)",
            "condicao": "Log-normal realista (n=30)",
            "n_grupo": 30,
            "com_outliers": False,
            "ordem_cenario": 1,
        },
        {
            "cenario_codigo": "Q3_Outliers",
            "cenario_poder_codigo": "Q3_Outliers",
            "cenario_rotulo": "Violação: Outliers (Q3)\n10% contaminação (n=30)",
            "cenario_curto": "Violação: Outliers 10% (n=30)",
            "condicao": "Injeção de 10% de outliers (5x + 50h)",
            "n_grupo": 30,
            "com_outliers": True,
            "ordem_cenario": 2,
        },
        {
            "cenario_codigo": "Q3_AmostraPequena",
            "cenario_poder_codigo": "Q3_AmostraPequena",
            "cenario_rotulo": "Violação: Amostra Pequena (Q3)\nLog-normal (n=10)",
            "cenario_curto": "Violação: Amostra Pequena (n=10)",
            "condicao": "Tamanho amostral reduzido (n=10)",
            "n_grupo": 10,
            "com_outliers": False,
            "ordem_cenario": 3,
        },
    ]

    linhas_erro_tipo_1: List[Dict[str, Any]] = []
    linhas_poder_largo: List[Dict[str, Any]] = []
    linhas_curvas_g4: List[Dict[str, Any]] = []

    for cfg in configuracoes_cenarios:
        n_g = cfg["n_grupo"]
        for delta in efeitos_tupla:
            gerador.redefinir_semente(semente)
            if cfg["com_outliers"]:
                mat_sem, mat_com = gerador.gerar_matrizes_com_outliers(
                    n_simulacoes=n_simulacoes,
                    n_sem_bot=n_g,
                    n_com_bot=n_g,
                    efeito_reducao=delta,
                    prop_outliers=0.10,
                    fator_multiplicador=5.0,
                    deslocamento_aditivo=50.0,
                    arredondar=2,
                )
            else:
                mat_sem, mat_com = gerador.gerar_matrizes_experimento(
                    n_simulacoes=n_simulacoes,
                    n_sem_bot=n_g,
                    n_com_bot=n_g,
                    efeito_reducao=delta,
                    arredondar=2,
                )

            metricas = _avaliar_condicao_matrizes(
                mat_sem, mat_com, alpha=alpha, alternativa=alternativa
            )

            # Se delta == 0.0, H0 é verdadeira -> registra na tabela de Erro Tipo I (Q1 vs Q3)
            if delta == 0.0:
                classe_w, _ = classificar_comportamento_erro_tipo_1(
                    metricas["taxa_welch"], alpha, n_simulacoes
                )
                classe_mw, _ = classificar_comportamento_erro_tipo_1(
                    metricas["taxa_mw"], alpha, n_simulacoes
                )

                for nome_teste, abordagem, rej, taxa, ic_inf, ic_sup, classe, ks_p in [
                    (
                        CENARIO.teste_parametrico,
                        "Paramétrico",
                        metricas["rej_welch"],
                        metricas["taxa_welch"],
                        metricas["ic_inf_welch"],
                        metricas["ic_sup_welch"],
                        classe_w,
                        metricas["ks_p_welch"],
                    ),
                    (
                        CENARIO.teste_nao_parametrico,
                        "Não-paramétrico",
                        metricas["rej_mw"],
                        metricas["taxa_mw"],
                        metricas["ic_inf_mw"],
                        metricas["ic_sup_mw"],
                        classe_mw,
                        metricas["ks_p_mw"],
                    ),
                ]:
                    linhas_erro_tipo_1.append(
                        {
                            "cenario_codigo": cfg["cenario_codigo"],
                            "cenario_rotulo": cfg["cenario_rotulo"],
                            "condicao": cfg["condicao"],
                            "n_por_grupo": n_g,
                            "teste": nome_teste,
                            "abordagem": abordagem,
                            "n_simulacoes": n_simulacoes,
                            "n_rejeicoes": rej,
                            "taxa_empirica": taxa,
                            "taxa_empirica_pct": taxa * 100.0,
                            "taxa_teorica": alpha,
                            "taxa_teorica_pct": alpha * 100.0,
                            "desvio_nominal_pct": (taxa - alpha) * 100.0,
                            "ic_inf": ic_inf,
                            "ic_sup": ic_sup,
                            "ic_inf_pct": ic_inf * 100.0,
                            "ic_sup_pct": ic_sup * 100.0,
                            "comportamento": classe,
                            "bradley_estrito": bool((0.9 * alpha) <= taxa <= (1.1 * alpha)),
                            "ks_pvalor_uniforme": round(ks_p, 6),
                            "ordem_cenario": cfg["ordem_cenario"],
                        }
                    )

            # Registra na tabela larga de Poder (para todos os tamanhos de efeito, incluindo 0%)
            poder_w_pct = metricas["taxa_welch"] * 100.0
            poder_mw_pct = metricas["taxa_mw"] * 100.0
            linhas_poder_largo.append(
                {
                    "cenario_codigo": cfg["cenario_poder_codigo"],
                    "cenario_curto": cfg["cenario_curto"],
                    "condicao": cfg["condicao"],
                    "ordem_cenario": cfg["ordem_cenario"],
                    "n_por_grupo": n_g,
                    "efeito_reducao": delta,
                    "efeito_pct": delta * 100.0,
                    "sob_h0": bool(delta == 0.0),
                    "n_simulacoes": n_simulacoes,
                    "rejeicoes_welch": metricas["rej_welch"],
                    "poder_welch": metricas["taxa_welch"],
                    "poder_welch_pct": poder_w_pct,
                    "ic_inf_welch_pct": metricas["ic_inf_welch"] * 100.0,
                    "ic_sup_welch_pct": metricas["ic_sup_welch"] * 100.0,
                    "rejeicoes_mann_whitney": metricas["rej_mw"],
                    "poder_mann_whitney": metricas["taxa_mw"],
                    "poder_mann_whitney_pct": poder_mw_pct,
                    "ic_inf_mw_pct": metricas["ic_inf_mw"] * 100.0,
                    "ic_sup_mw_pct": metricas["ic_sup_mw"] * 100.0,
                    "vantagem_mw_pp": poder_mw_pct - poder_w_pct,
                }
            )

            # Registra no formato longo/tidy ideal para plotagem direta das curvas no Gráfico G4
            for nome_teste, abordagem, rej, taxa, ic_inf, ic_sup in [
                (
                    CENARIO.teste_parametrico,
                    "Paramétrico",
                    metricas["rej_welch"],
                    metricas["taxa_welch"],
                    metricas["ic_inf_welch"],
                    metricas["ic_sup_welch"],
                ),
                (
                    CENARIO.teste_nao_parametrico,
                    "Não-paramétrico",
                    metricas["rej_mw"],
                    metricas["taxa_mw"],
                    metricas["ic_inf_mw"],
                    metricas["ic_sup_mw"],
                ),
            ]:
                linhas_curvas_g4.append(
                    {
                        "cenario_codigo": cfg["cenario_poder_codigo"],
                        "cenario_curto": cfg["cenario_curto"],
                        "condicao": cfg["condicao"],
                        "ordem_cenario": cfg["ordem_cenario"],
                        "n_por_grupo": n_g,
                        "efeito_reducao": delta,
                        "efeito_pct": delta * 100.0,
                        "sob_h0": bool(delta == 0.0),
                        "teste": nome_teste,
                        "abordagem": abordagem,
                        "n_simulacoes": n_simulacoes,
                        "n_rejeicoes": rej,
                        "proporcao_rejeicoes": taxa,
                        "proporcao_rejeicoes_pct": taxa * 100.0,
                        "ic_inf": ic_inf,
                        "ic_sup": ic_sup,
                        "ic_inf_pct": ic_inf * 100.0,
                        "ic_sup_pct": ic_sup * 100.0,
                    }
                )

    df_erro_tipo_1 = pd.DataFrame(linhas_erro_tipo_1)
    df_poder_largo = pd.DataFrame(linhas_poder_largo)
    df_curvas_g4 = pd.DataFrame(linhas_curvas_g4)

    # Calcula variações frente ao cenário original (Q1_Base / Q2_Base)
    base_t1 = (
        df_erro_tipo_1[df_erro_tipo_1["cenario_codigo"] == "Q1_Base"]
        .set_index("teste")["taxa_empirica_pct"]
        .to_dict()
    )
    df_erro_tipo_1["variacao_vs_base_pp"] = df_erro_tipo_1.apply(
        lambda r: float(r["taxa_empirica_pct"] - base_t1[r["teste"]]), axis=1
    )

    base_poder_w = (
        df_poder_largo[df_poder_largo["cenario_codigo"] == "Q2_Base"]
        .set_index("efeito_reducao")["poder_welch_pct"]
        .to_dict()
    )
    base_poder_mw = (
        df_poder_largo[df_poder_largo["cenario_codigo"] == "Q2_Base"]
        .set_index("efeito_reducao")["poder_mann_whitney_pct"]
        .to_dict()
    )

    df_poder_largo["perda_poder_welch_vs_base_pp"] = df_poder_largo.apply(
        lambda r: float(r["poder_welch_pct"] - base_poder_w[r["efeito_reducao"]]), axis=1
    )
    df_poder_largo["perda_poder_mw_vs_base_pp"] = df_poder_largo.apply(
        lambda r: float(r["poder_mann_whitney_pct"] - base_poder_mw[r["efeito_reducao"]]), axis=1
    )

    df_comparativo_impacto = construir_tabela_comparativa_impacto(df_erro_tipo_1, df_poder_largo)
    sintese = gerar_texto_interpretativo_q3(df_erro_tipo_1, df_poder_largo)

    return ResultadoSimulacaoQ3(
        semente=semente,
        n_simulacoes=n_simulacoes,
        alpha=alpha,
        efeitos_avaliados=efeitos_tupla,
        pressupostos_e_violacoes=obter_pressupostos_e_violacoes(),
        df_erro_tipo_1=df_erro_tipo_1,
        df_poder_largo=df_poder_largo,
        df_curvas_g4=df_curvas_g4,
        df_comparativo_impacto=df_comparativo_impacto,
        sintese_interpretativa=sintese,
    )


def construir_tabela_comparativa_impacto(
    df_erro_tipo_1: pd.DataFrame,
    df_poder_largo: pd.DataFrame,
) -> pd.DataFrame:
    """Constrói tabela comparando o impacto de cada violação sobre o Erro Tipo I e o Poder."""
    linhas = []
    for cenario_cod, rotulo in [
        ("Q3_Outliers", "Violação 1: Outliers Severos (10% contaminação 5x+50h, n=30)"),
        ("Q3_AmostraPequena", "Violação 2: Amostra Pequena (Log-normal n=10)"),
    ]:
        sub_t1 = df_erro_tipo_1[df_erro_tipo_1["cenario_codigo"] == cenario_cod].set_index("teste")
        sub_p = df_poder_largo[
            (df_poder_largo["cenario_codigo"] == cenario_cod) & (~df_poder_largo["sob_h0"])
        ]

        t1_w = float(sub_t1.loc[CENARIO.teste_parametrico, "taxa_empirica_pct"])
        t1_mw = float(sub_t1.loc[CENARIO.teste_nao_parametrico, "taxa_empirica_pct"])
        desvio_w_alpha = float(sub_t1.loc[CENARIO.teste_parametrico, "desvio_nominal_pct"])
        desvio_mw_alpha = float(sub_t1.loc[CENARIO.teste_nao_parametrico, "desvio_nominal_pct"])
        var_t1_w = float(sub_t1.loc[CENARIO.teste_parametrico, "variacao_vs_base_pp"])
        var_t1_mw = float(sub_t1.loc[CENARIO.teste_nao_parametrico, "variacao_vs_base_pp"])

        # Efeito máximo (delta = 50%) e média nos efeitos positivos (10% a 50%)
        linha_base_max = (
            df_poder_largo[df_poder_largo["cenario_codigo"] == "Q2_Base"]
            .sort_values("efeito_reducao")
            .iloc[-1]
        )
        poder_base_max_w = float(linha_base_max["poder_welch_pct"])
        poder_base_max_mw = float(linha_base_max["poder_mann_whitney_pct"])

        linha_max = sub_p.sort_values("efeito_reducao").iloc[-1]
        perda_max_w = float(linha_max["perda_poder_welch_vs_base_pp"])
        perda_max_mw = float(linha_max["perda_poder_mw_vs_base_pp"])
        perda_rel_max_w = (perda_max_w / poder_base_max_w) * 100.0 if poder_base_max_w else 0.0
        perda_rel_max_mw = (perda_max_mw / poder_base_max_mw) * 100.0 if poder_base_max_mw else 0.0
        perda_media_w = float(sub_p["perda_poder_welch_vs_base_pp"].mean())
        perda_media_mw = float(sub_p["perda_poder_mw_vs_base_pp"].mean())
        vantagem_max_mw = float(linha_max["vantagem_mw_pp"])

        teste_mais_afetado_t1 = (
            CENARIO.teste_parametrico
            if abs(desvio_w_alpha) > abs(desvio_mw_alpha)
            else CENARIO.teste_nao_parametrico
        )
        teste_mais_afetado_poder = (
            CENARIO.teste_parametrico
            if abs(perda_rel_max_w) >= abs(perda_rel_max_mw)
            else CENARIO.teste_nao_parametrico
        )

        linhas.append(
            {
                "cenario_codigo": cenario_cod,
                "violacao": rotulo,
                "erro_tipo_1_welch_pct": round(t1_w, 2),
                "erro_tipo_1_mw_pct": round(t1_mw, 2),
                "desvio_alpha_welch_pp": round(desvio_w_alpha, 2),
                "desvio_alpha_mw_pp": round(desvio_mw_alpha, 2),
                "variacao_t1_vs_base_welch_pp": round(var_t1_w, 2),
                "variacao_t1_vs_base_mw_pp": round(var_t1_mw, 2),
                "perda_poder_media_welch_pp": round(perda_media_w, 2),
                "perda_poder_media_mw_pp": round(perda_media_mw, 2),
                "perda_poder_delta50_welch_pp": round(perda_max_w, 2),
                "perda_poder_delta50_mw_pp": round(perda_max_mw, 2),
                "perda_relativa_delta50_welch_pct": round(perda_rel_max_w, 2),
                "perda_relativa_delta50_mw_pct": round(perda_rel_max_mw, 2),
                "vantagem_mw_delta50_pp": round(vantagem_max_mw, 2),
                "teste_maior_alteracao_erro_tipo_1": teste_mais_afetado_t1,
                "teste_maior_alteracao_poder": teste_mais_afetado_poder,
            }
        )
    return pd.DataFrame(linhas)


def gerar_texto_interpretativo_q3(
    df_erro_tipo_1: pd.DataFrame,
    df_poder_largo: pd.DataFrame,
) -> str:
    """Gera síntese interpretativa concisa comparando o cenário original com as violações de Q3."""
    t1_w_base = float(
        df_erro_tipo_1.loc[
            (df_erro_tipo_1["cenario_codigo"] == "Q1_Base")
            & (df_erro_tipo_1["teste"] == CENARIO.teste_parametrico),
            "taxa_empirica_pct",
        ].iloc[0]
    )
    t1_w_out = float(
        df_erro_tipo_1.loc[
            (df_erro_tipo_1["cenario_codigo"] == "Q3_Outliers")
            & (df_erro_tipo_1["teste"] == CENARIO.teste_parametrico),
            "taxa_empirica_pct",
        ].iloc[0]
    )
    t1_w_small = float(
        df_erro_tipo_1.loc[
            (df_erro_tipo_1["cenario_codigo"] == "Q3_AmostraPequena")
            & (df_erro_tipo_1["teste"] == CENARIO.teste_parametrico),
            "taxa_empirica_pct",
        ].iloc[0]
    )
    t1_mw_out = float(
        df_erro_tipo_1.loc[
            (df_erro_tipo_1["cenario_codigo"] == "Q3_Outliers")
            & (df_erro_tipo_1["teste"] == CENARIO.teste_nao_parametrico),
            "taxa_empirica_pct",
        ].iloc[0]
    )
    t1_mw_small = float(
        df_erro_tipo_1.loc[
            (df_erro_tipo_1["cenario_codigo"] == "Q3_AmostraPequena")
            & (df_erro_tipo_1["teste"] == CENARIO.teste_nao_parametrico),
            "taxa_empirica_pct",
        ].iloc[0]
    )

    p50_base = df_poder_largo[
        (df_poder_largo["cenario_codigo"] == "Q2_Base") & (df_poder_largo["efeito_pct"] == 50.0)
    ].iloc[0]
    p50_out = df_poder_largo[
        (df_poder_largo["cenario_codigo"] == "Q3_Outliers")
        & (df_poder_largo["efeito_pct"] == 50.0)
    ].iloc[0]
    p50_small = df_poder_largo[
        (df_poder_largo["cenario_codigo"] == "Q3_AmostraPequena")
        & (df_poder_largo["efeito_pct"] == 50.0)
    ].iloc[0]

    return (
        f"A violação de pressupostos afeta muito mais severamente o teste paramétrico t de Welch do que "
        f"o não-paramétrico U de Mann-Whitney, tanto no Erro Tipo I quanto no Poder Estatístico. "
        f"Sob H₀ verdadeira (Q1 repetida em Q3), a taxa de Erro Tipo I do t de Welch cai de "
        f"{t1_w_base:.2f}% no cenário original para {t1_w_out:.2f}% com outliers severos e {t1_w_small:.2f}% "
        f"com amostra pequena (n=10), tornando-se fortemente conservador, enquanto Mann-Whitney permanece "
        f"estável perto dos 5% nominais ({t1_mw_out:.2f}% e {t1_mw_small:.2f}%). "
        f"Sob H₁ verdadeira (Q2 repetida em Q3 para redução de 50%), a injeção de 10% de outliers derruba "
        f"o poder do t de Welch em {abs(float(p50_out['perda_poder_welch_vs_base_pp'])):.2f} pontos percentuais "
        f"(de {float(p50_base['poder_welch_pct']):.2f}% para {float(p50_out['poder_welch_pct']):.2f}%), "
        f"ao passo que Mann-Whitney retém {float(p50_out['poder_mann_whitney_pct']):.2f}% de poder "
        f"(vantagem de +{float(p50_out['vantagem_mw_pp']):.2f} p.p. sobre Welch). "
        f"Com amostra pequena (n=10), ambos perdem poder pelo menor volume amostral, mas Mann-Whitney "
        f"mantém superioridade consistente em todos os tamanhos de efeito ({float(p50_small['poder_mann_whitney_pct']):.2f}% "
        f"contra {float(p50_small['poder_welch_pct']):.2f}% em δ=50%)."
    )


# ----------------------------------------------------------------------------
# 3. Persistência, carregamento rápido e adaptadores para G3 e G4
# ----------------------------------------------------------------------------
def salvar_resultados_q3(
    resultado: ResultadoSimulacaoQ3,
    caminho_erro_tipo_1: Path | str = CAMINHO_Q3_ERRO_TIPO_1_CSV,
    caminho_poder_largo: Path | str = CAMINHO_Q3_PODER_LARGO_CSV,
    caminho_curvas_g4: Path | str = CAMINHO_Q3_CURVAS_G4_CSV,
    caminho_impacto: Path | str = CAMINHO_Q3_IMPACTO_CSV,
) -> Tuple[Path, Path, Path, Path]:
    """Persiste todas as tabelas resultantes da simulação Q3 em CSV."""
    p_t1 = Path(caminho_erro_tipo_1)
    p_pod = Path(caminho_poder_largo)
    p_g4 = Path(caminho_curvas_g4)
    p_imp = Path(caminho_impacto)

    for p in (p_t1, p_pod, p_g4, p_imp):
        p.parent.mkdir(parents=True, exist_ok=True)

    resultado.df_erro_tipo_1.to_csv(p_t1, index=False)
    resultado.df_poder_largo.to_csv(p_pod, index=False)
    resultado.df_curvas_g4.to_csv(p_g4, index=False)
    resultado.df_comparativo_impacto.to_csv(p_imp, index=False)

    return p_t1, p_pod, p_g4, p_imp


def carregar_ou_executar_q3(
    semente: int = 42,
    n_simulacoes: int = 10_000,
    forcar_reexecucao: bool = False,
    caminho_erro_tipo_1: Path | str = CAMINHO_Q3_ERRO_TIPO_1_CSV,
    caminho_poder_largo: Path | str = CAMINHO_Q3_PODER_LARGO_CSV,
    caminho_curvas_g4: Path | str = CAMINHO_Q3_CURVAS_G4_CSV,
    caminho_impacto: Path | str = CAMINHO_Q3_IMPACTO_CSV,
) -> ResultadoSimulacaoQ3:
    """Carrega os resultados persistidos de Q3 do disco ou executa a simulação caso necessário."""
    p_t1 = Path(caminho_erro_tipo_1)
    p_pod = Path(caminho_poder_largo)
    p_g4 = Path(caminho_curvas_g4)
    p_imp = Path(caminho_impacto)

    if (
        not forcar_reexecucao
        and p_t1.exists()
        and p_pod.exists()
        and p_g4.exists()
        and p_imp.exists()
        and semente == 42
        and n_simulacoes == 10_000
    ):
        df_t1 = pd.read_csv(p_t1)
        df_pod = pd.read_csv(p_pod)
        df_g4 = pd.read_csv(p_g4)
        df_imp = pd.read_csv(p_imp)
        if len(df_t1) == 6 and len(df_pod) == 18 and (df_t1["n_simulacoes"] == 10_000).all():
            return ResultadoSimulacaoQ3(
                semente=semente,
                n_simulacoes=n_simulacoes,
                alpha=CENARIO.alpha,
                efeitos_avaliados=EFEITOS_PADRAO_Q3,
                pressupostos_e_violacoes=obter_pressupostos_e_violacoes(),
                df_erro_tipo_1=df_t1,
                df_poder_largo=df_pod,
                df_curvas_g4=df_g4,
                df_comparativo_impacto=df_imp,
                sintese_interpretativa=gerar_texto_interpretativo_q3(df_t1, df_pod),
            )

    resultado = executar_simulacao_q3(
        n_simulacoes=n_simulacoes,
        semente=semente,
        efeitos=EFEITOS_PADRAO_Q3,
        alpha=CENARIO.alpha,
        alternativa=CENARIO.tipo_teste,
    )
    if semente == 42 and n_simulacoes == 10_000:
        salvar_resultados_q3(
            resultado,
            caminho_erro_tipo_1=p_t1,
            caminho_poder_largo=p_pod,
            caminho_curvas_g4=p_g4,
            caminho_impacto=p_imp,
        )
    return resultado


def obter_dados_q3_para_g3(
    resultado: Optional[ResultadoSimulacaoQ3] = None,
) -> pd.DataFrame:
    """Retorna DataFrame de Erro Tipo I (Q1 e Q3) no formato exato consumido pelo Gráfico G3."""
    res = resultado if resultado is not None else carregar_ou_executar_q3()
    return res.df_erro_tipo_1.copy()


def obter_dados_q3_para_g4(
    resultado: Optional[ResultadoSimulacaoQ3] = None,
) -> pd.DataFrame:
    """Retorna DataFrame das curvas de poder (Q2 e Q3) pronto para construção do Gráfico G4."""
    res = resultado if resultado is not None else carregar_ou_executar_q3()
    return res.df_curvas_g4.copy()


def gerar_relatorio_q3(semente: int = 42, n_simulacoes: int = 10_000) -> str:
    """Gera relatório completo em texto plano com os resultados de Q3."""
    res = carregar_ou_executar_q3(semente=semente, n_simulacoes=n_simulacoes)
    linhas = [
        "=" * 88,
        "LAB04S02 — SIMULAÇÃO DE VIOLAÇÕES DOS PRESSUPOSTOS ESTATÍSTICOS (QUESTÃO Q3)",
        "=" * 88,
        f"Semente: {res.semente} | Simulações por condição: {res.n_simulacoes:,} | Alpha: {res.alpha:.2f}",
        f"Tamanhos de efeito avaliados (%): {[int(e * 100) for e in res.efeitos_avaliados]}",
        "",
        "1. TAXA DE ERRO TIPO I SOB H0 VERDADEIRA (Q1 REPETIDA NAS CONDIÇÕES DE VIOLAÇÃO Q3)",
        "-" * 88,
        res.df_erro_tipo_1[
            [
                "cenario_codigo",
                "condicao",
                "teste",
                "n_rejeicoes",
                "taxa_empirica_pct",
                "desvio_nominal_pct",
                "variacao_vs_base_pp",
                "comportamento",
            ]
        ].to_string(index=False),
        "",
        "2. PODER ESTATÍSTICO POR TAMANHO DE EFEITO (Q2 REPETIDA NAS CONDIÇÕES DE VIOLAÇÃO Q3)",
        "-" * 88,
        res.df_poder_largo[
            [
                "cenario_codigo",
                "efeito_pct",
                "poder_welch_pct",
                "poder_mann_whitney_pct",
                "vantagem_mw_pp",
                "perda_poder_welch_vs_base_pp",
                "perda_poder_mw_vs_base_pp",
            ]
        ].to_string(index=False),
        "",
        "3. DIAGNÓSTICO DE IMPACTO: QUAL TESTE SOFRE MAIOR ALTERAÇÃO?",
        "-" * 88,
        res.df_comparativo_impacto.to_string(index=False),
        "",
        "4. SÍNTESE INTERPRETATIVA:",
        "-" * 88,
        res.sintese_interpretativa,
        "=" * 88,
    ]
    return "\n".join(linhas)


if __name__ == "__main__":  # pragma: no cover
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    res_q3 = carregar_ou_executar_q3(semente=42, n_simulacoes=10_000, forcar_reexecucao=True)
    p1, p2, p3, p4 = salvar_resultados_q3(res_q3)
    print(gerar_relatorio_q3(semente=42, n_simulacoes=10_000))
    print(f"Arquivos CSV gerados:\n  - {p1}\n  - {p2}\n  - {p3}\n  - {p4}")
