"""Módulo de geração reproduzível de dados simulados para o LAB04.

Issue #46: [LAB04S01] Implementar geração reproduzível de dados simulados.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple
import numpy as np
import pandas as pd

from lab04.src.dados_reais import CAMINHO_DADOS_REAIS_PADRAO, obter_resumo_estatistico_reais

CAMINHO_DADOS_SIMULADOS_S01 = (
    Path(__file__).resolve().parent.parent / "data" / "dados_simulados_s01.csv"
)


@dataclass
class ParametrosSimulacao:
    """Parâmetros fundamentados nos dados reais para as simulações do LAB04."""

    # Tamanho amostral padrão por grupo (S01: n=30)
    n_sem_bot: int = 30
    n_com_bot: int = 30

    # Parâmetros sob H1 observados nos dados reais (escala log-normal)
    # Grupo sem_bot: Mediana ~ 18.9h, log_mu ~ 2.97, log_sigma ~ 0.87
    mu_log_sem_bot: float = 2.9721
    sigma_log_sem_bot: float = 0.8670

    # Grupo com_bot: Mediana ~ 13.6h, log_mu ~ 2.64, log_sigma ~ 0.96
    mu_log_com_bot: float = 2.6385
    sigma_log_com_bot: float = 0.9632

    # Parâmetros baseline comuns sob H0 (distribuição idêntica para ambos os grupos)
    # Mediana combinada ~ 15.4h, log_mu ~ 2.80, log_sigma ~ 0.90
    mu_log_h0: float = 2.8053
    sigma_log_h0: float = 0.9254

    # Semente pseudoaleatória padrão para reprodutibilidade
    semente_padrao: int = 42


class GeradorDadosSimulados:
    """Gerador reproduzível de dados simulados para testes de hipótese e simulações Monte Carlo."""

    def __init__(
        self,
        semente: int = 42,
        parametros: Optional[ParametrosSimulacao] = None,
    ):
        """Inicializa o gerador com uma semente fixa e parâmetros configuráveis."""
        self.semente = semente
        self.rng = np.random.default_rng(semente)
        self.parametros = parametros or ParametrosSimulacao(semente_padrao=semente)

    def redefinir_semente(self, semente: int) -> None:
        """Reinicia o gerador com uma nova semente."""
        self.semente = semente
        self.rng = np.random.default_rng(semente)

    def gerar_vetor_lognormal(
        self,
        tamanho: int,
        mu_log: float,
        sigma_log: float,
        arredondar: int = 2,
    ) -> np.ndarray:
        """Gera um vetor unidimensional de observações sob distribuição Lognormal."""
        if tamanho <= 0:
            raise ValueError("O tamanho amostral deve ser um inteiro positivo.")
        if sigma_log <= 0:
            raise ValueError("O desvio padrão na escala logarítmica deve ser estritamente positivo.")

        amostra = self.rng.lognormal(mean=mu_log, sigma=sigma_log, size=tamanho)
        return np.round(amostra, arredondar)

    def gerar_dataset_experimento(
        self,
        n_sem_bot: Optional[int] = None,
        n_com_bot: Optional[int] = None,
        sob_h0: bool = False,
        efeito_reducao: float = 0.0,
        mu_log_base: Optional[float] = None,
        sigma_log_base: Optional[float] = None,
        sigma_log_com_bot: Optional[float] = None,
        inicio_pr_id: int = 1,
    ) -> pd.DataFrame:
        """Gera um DataFrame com dois grupos independentes (sem_bot e com_bot).

        Parâmetros:
            n_sem_bot: Tamanho amostral do grupo controle (padrão: 30).
            n_com_bot: Tamanho amostral do grupo tratamento (padrão: 30).
            sob_h0: Se True, ambos os grupos seguem parâmetros estritamente idênticos.
            efeito_reducao: Redução percentual esperada no tempo do grupo com_bot (ex.: 0.20 = 20%).
            mu_log_base: Parâmetro mu_log de referência para o grupo sem_bot.
            sigma_log_base: Parâmetro sigma_log para o grupo sem_bot.
            sigma_log_com_bot: Parâmetro sigma_log específico para o grupo com_bot.
            inicio_pr_id: ID inicial dos PRs gerados.

        Retorna:
            pd.DataFrame contendo colunas ['pr_id', 'grupo', 'tempo_horas'].
        """
        n_sem = n_sem_bot if n_sem_bot is not None else self.parametros.n_sem_bot
        n_com = n_com_bot if n_com_bot is not None else self.parametros.n_com_bot

        if sob_h0:
            # Sob H0 verdadeira: ambos os grupos compartilham a mesma distribuição
            mu_sem = mu_log_base if mu_log_base is not None else self.parametros.mu_log_h0
            sig_sem = sigma_log_base if sigma_log_base is not None else self.parametros.sigma_log_h0
            mu_com = mu_sem
            sig_com = sig_sem
        else:
            # Sob H1: parâmetros reais ou deslocados por um efeito_reducao
            mu_sem = mu_log_base if mu_log_base is not None else self.parametros.mu_log_sem_bot
            sig_sem = sigma_log_base if sigma_log_base is not None else self.parametros.sigma_log_sem_bot

            if efeito_reducao > 0.0:
                # Efeito multiplicativo: tempo_com = tempo_sem * (1 - delta)
                # Na escala logarítmica: mu_log_com = mu_log_sem + ln(1 - delta)
                if efeito_reducao >= 1.0:
                    raise ValueError("efeito_reducao deve ser menor que 1.0 (100%).")
                delta_log = np.log(1.0 - efeito_reducao)
                mu_com = mu_sem + delta_log
                sig_com = sigma_log_com_bot if sigma_log_com_bot is not None else sig_sem
            else:
                mu_com = (
                    self.parametros.mu_log_com_bot
                    if mu_log_base is None
                    else mu_sem - 0.3336  # diferença empírica padrão
                )
                sig_com = (
                    sigma_log_com_bot
                    if sigma_log_com_bot is not None
                    else self.parametros.sigma_log_com_bot
                )

        tempos_sem = self.gerar_vetor_lognormal(n_sem, mu_sem, sig_sem)
        tempos_com = self.gerar_vetor_lognormal(n_com, mu_com, sig_com)

        dados_sem = [
            {"pr_id": inicio_pr_id + i, "grupo": "sem_bot", "tempo_horas": t}
            for i, t in enumerate(tempos_sem)
        ]
        dados_com = [
            {"pr_id": inicio_pr_id + n_sem + i, "grupo": "com_bot", "tempo_horas": t}
            for i, t in enumerate(tempos_com)
        ]

        df = pd.DataFrame(dados_sem + dados_com)
        return df

    def gerar_matrizes_h0(
        self,
        n_simulacoes: int = 10_000,
        n_sem_bot: Optional[int] = None,
        n_com_bot: Optional[int] = None,
        mu_log_base: Optional[float] = None,
        sigma_log_base: Optional[float] = None,
        arredondar: int = 2,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Gera duas matrizes 2D (n_simulacoes, n_sem) e (n_simulacoes, n_com) sob H0 verdadeira.

        Sob H0 verdadeira, ambos os grupos compartilham rigorosamente os mesmos parâmetros populacionais,
        garantindo ausência de efeito investigado. O sorteio sequencial por simulação preserva equivalência
        estrita com a geração iterativa dataset por dataset.

        Retorna:
            Tupla contendo (matriz_sem_bot, matriz_com_bot).
        """
        n_sem = n_sem_bot if n_sem_bot is not None else self.parametros.n_sem_bot
        n_com = n_com_bot if n_com_bot is not None else self.parametros.n_com_bot
        mu = mu_log_base if mu_log_base is not None else self.parametros.mu_log_h0
        sig = sigma_log_base if sigma_log_base is not None else self.parametros.sigma_log_h0

        if n_simulacoes <= 0:
            raise ValueError("O número de simulações deve ser um inteiro positivo.")
        if n_sem <= 0 or n_com <= 0:
            raise ValueError("Os tamanhos amostrais devem ser inteiros positivos.")
        if sig <= 0:
            raise ValueError("O desvio padrão sigma_log deve ser estritamente positivo.")

        amostras = self.rng.lognormal(mean=mu, sigma=sig, size=(n_simulacoes, n_sem + n_com))
        if arredondar is not None:
            amostras = np.round(amostras, arredondar)

        return amostras[:, :n_sem], amostras[:, n_sem:]

    def gerar_dataset_com_outliers(
        self,
        n_sem_bot: int = 30,
        n_com_bot: int = 30,
        prop_outliers: float = 0.10,
        fator_multiplicador: float = 5.0,
        sob_h0: bool = True,
    ) -> Tuple[pd.DataFrame, np.ndarray]:
        """Gera dataset com injeção proposital de outliers para a Questão Q3 (violação de pressupostos).

        Retorna:
            Tupla (df, indices_outliers) onde indices_outliers são os índices contaminados.
        """
        df = self.gerar_dataset_experimento(
            n_sem_bot=n_sem_bot,
            n_com_bot=n_com_bot,
            sob_h0=sob_h0,
        )

        n_total = len(df)
        n_outliers = max(1, int(n_total * prop_outliers))
        indices_outliers = self.rng.choice(df.index, size=n_outliers, replace=False)

        tempos_modificados = df["tempo_horas"].copy()
        # Injeta valores anômalos extremos multiplicando pelo fator e adicionando deslocamento
        tempos_modificados.loc[indices_outliers] = np.round(
            tempos_modificados.loc[indices_outliers] * fator_multiplicador + 50.0, 2
        )
        df["tempo_horas"] = tempos_modificados
        return df, indices_outliers

    def gerar_dataset_gaussiano(
        self,
        n_sem_bot: int = 30,
        n_com_bot: int = 30,
        media: float = 25.0,
        desvio: float = 8.0,
        delta_media: float = 0.0,
    ) -> pd.DataFrame:
        """Gera dataset com distribuição Normal pura para análise comparativa de controle teórico."""
        sem = self.rng.normal(loc=media, scale=desvio, size=n_sem_bot)
        com = self.rng.normal(loc=media - delta_media, scale=desvio, size=n_com_bot)

        dados_sem = [
            {"pr_id": 1 + i, "grupo": "sem_bot", "tempo_horas": round(max(0.1, t), 2)}
            for i, t in enumerate(sem)
        ]
        dados_com = [
            {"pr_id": 1 + n_sem_bot + i, "grupo": "com_bot", "tempo_horas": round(max(0.1, t), 2)}
            for i, t in enumerate(com)
        ]
        return pd.DataFrame(dados_sem + dados_com)


def gerar_e_salvar_dataset_s01(
    semente: int = 42,
    caminho_saida: Path | str = CAMINHO_DADOS_SIMULADOS_S01,
) -> pd.DataFrame:
    """Gera o dataset simulado representativo da Sprint 01 e o persiste em formato CSV."""
    gerador = GeradorDadosSimulados(semente=semente)
    # Para o dataset inicial da S01, geramos dados sob H1 observada (com efeito empírico)
    df = gerador.gerar_dataset_experimento(
        n_sem_bot=30,
        n_com_bot=30,
        sob_h0=False,
    )
    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho_saida, index=False)
    return df


if __name__ == "__main__":
    df_sim = gerar_e_salvar_dataset_s01()
    print(f"Dataset simulado gerado com sucesso em: {CAMINHO_DADOS_SIMULADOS_S01}")
    print(f"Total de observações: {len(df_sim)}")
    print(df_sim.groupby("grupo")["tempo_horas"].describe())
