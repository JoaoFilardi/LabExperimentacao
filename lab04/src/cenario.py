"""Definições e metadados do cenário, hipóteses e testes estatísticos do LAB04.

Issue #45: [LAB04S01] Definir cenário, testes estatísticos e hipóteses.
"""

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class DefinicaoCenario:
    """Configurações e definições formais do experimento."""

    par_id: str = "P1"
    nome_par: str = "t de Welch × Mann-Whitney"
    teste_parametrico: str = "t de Welch"
    teste_nao_parametrico: str = "Mann-Whitney (Wilcoxon rank-sum)"
    tipo_teste: str = "bicaudal"  # two-tailed
    alpha: float = 0.05
    nivel_confianca: float = 0.95

    # Cenário de Engenharia de Software
    titulo_cenario: str = (
        "Impacto do uso de bots de revisão automatizada no tempo até o merge (lead time to merge) de Pull Requests"
    )
    grupo_tratamento: str = "com_bot"
    grupo_controle: str = "sem_bot"
    unidade_medida: str = "horas"
    origem_dados_reais: str = "Repositório público open-source no GitHub: tiangolo/fastapi"
    n_observacoes_reais_total: int = 60
    n_observacoes_reais_por_grupo: int = 30
    variavel_dependente: str = (
        "tempo_horas (lead time to merge: tempo decorrido entre a abertura e o merge do PR, em horas)"
    )
    criterio_selecao_prs: str = (
        "30 Pull Requests com assistência de bots de automação (FastAPI Bot, GitHub Actions) e "
        "30 Pull Requests revisados exclusivamente por humanos minerados do histórico oficial."
    )

    # Pergunta de Pesquisa em frase única e objetiva
    pergunta_pesquisa: str = (
        "A utilização de bots de revisão automatizada altera o tempo decorrido até o merge de "
        "Pull Requests em projetos de Engenharia de Software?"
    )

    # Hipóteses Conceituais
    h0_conceitual: str = (
        "Não há diferença no tempo até o merge de Pull Requests entre o grupo assistido por bots "
        "e o grupo revisado exclusivamente por humanos."
    )
    h1_conceitual: str = (
        "Há diferença significativa no tempo até o merge de Pull Requests entre o grupo assistido por bots "
        "e o grupo revisado exclusivamente por humanos."
    )

    # Hipóteses Operacionais - Teste t de Welch (médias)
    h0_welch: str = "μ_com_bot = μ_sem_bot (diferença de médias igual a zero)"
    h1_welch: str = "μ_com_bot ≠ μ_sem_bot (diferença de médias diferente de zero)"

    # Hipóteses Operacionais - Teste U de Mann-Whitney (distribuições / postos / medianas)
    h0_mann_whitney: str = (
        "P(X_com_bot > Y_sem_bot) = 0.5 (distribuições estocasticamente equivalentes / medianas iguais)"
    )
    h1_mann_whitney: str = (
        "P(X_com_bot > Y_sem_bot) ≠ 0.5 (dominância estocástica / medianas distintas)"
    )

    # Previsão Inicial Pré-Simulação
    teste_esperado_melhor_desempenho: str = "Mann-Whitney (Wilcoxon rank-sum)"
    justificativa_previsao: str = (
        "Em Engenharia de Software, tempos de processo (como lead time de PRs) apresentam distribuição "
        "acentuadamente assimétrica à direita (right-skewed) com presença recorrente de outliers severos. "
        "O teste paramétrico t de Welch tem sua média e variância infladas por esses valores extremos, "
        "perdendo poder estatístico de detecção (maior Erro Tipo II) e sofrendo instabilidade teórica com "
        "amostras moderadas. O teste U de Mann-Whitney baseia-se em postos ordenados, sendo robusto contra "
        "assimetria e caudas pesadas, mantendo taxa de Erro Tipo I controlada próxima a 5% e maior poder de "
        "detecção nas condições realistas do cenário."
    )

    # Resumo para a Seção 1 ("Cenário") do Dashboard
    texto_dashboard_cenario: str = (
        "Investigamos se a utilização de bots de revisão automatizada altera o tempo decorrido até o merge "
        "de Pull Requests em projetos de Engenharia de Software. Comparamos o teste paramétrico t de Welch com "
        "o não-paramétrico U de Mann-Whitney a um nível de significância de α = 0,05 em teste bicaudal, "
        "investigando as hipóteses H₀ (ausência de efeito no tempo de integração) e H₁ (presença de diferença significativa). "
        "A amostra empírica é composta por 60 Pull Requests (30 revisados com assistência de bots e 30 revisados de "
        "forma puramente manual) minerados do histórico de repositório open-source no GitHub. Nossa hipótese preliminar "
        "sustenta que o teste de Mann-Whitney apresentará superioridade de poder e robustez diante da assimetria acentuada "
        "e dos outliers inerentes a tempos de processo de software."
    )


# Instância padrão para importação no projeto
CENARIO = DefinicaoCenario()


def get_info_cenario() -> Dict[str, str | float | int]:
    """Retorna dicionário estruturado com as informações principais do cenário para o Dashboard."""
    return {
        "par_id": CENARIO.par_id,
        "nome_par": CENARIO.nome_par,
        "pergunta_pesquisa": CENARIO.pergunta_pesquisa,
        "h0": CENARIO.h0_conceitual,
        "h1": CENARIO.h1_conceitual,
        "tipo_teste": CENARIO.tipo_teste,
        "alpha": CENARIO.alpha,
        "teste_esperado": CENARIO.teste_esperado_melhor_desempenho,
        "origem_dados": CENARIO.origem_dados_reais,
        "n_observacoes_total": CENARIO.n_observacoes_reais_total,
        "n_por_grupo": CENARIO.n_observacoes_reais_por_grupo,
        "variavel": CENARIO.variavel_dependente,
        "texto_dashboard": CENARIO.texto_dashboard_cenario,
    }

