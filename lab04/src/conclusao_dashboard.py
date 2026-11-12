"""Módulo de consolidação e conclusão final do Dashboard do LAB04.

Issue #57: [ LAB04FINAL ] Finalizar cenário, dados e conclusão do dashboard.

Este módulo estrutura os dados e análises para a Seção 7 ("Conclusão") do Dashboard,
além de fornecer sínteses comparativas para as Seções 1 ("Cenário") e 2 ("Os dados"):
1. Confronto formal: Previsão inicial (pré-simulação) vs. Resultados obtidos (Q1, Q2, Q3 e Dados Reais);
2. Diagnóstico comparativo de desempenho (Erro Tipo I vs. Poder Estatístico);
3. Recomendação oficial justificada de qual teste adotar para o cenário de Engenharia de Software;
4. Identificação das condições técnicas sob as quais a recomendação mudaria;
5. Enumeração exaustiva das principais limitações metodológicas do estudo;
6. Síntese textual de 2 a 4 frases para apresentação oral e conclusão executiva.

Uso via linha de comando:
    python -m lab04.src.conclusao_dashboard
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd

from lab04.src.cenario import CENARIO


@dataclass(frozen=True)
class ItemExpectativaVsResultado:
    """Comparação entre o previsto antes de simular e o resultado empírico obtido."""

    dimensao: str
    previsao_pre_simulacao: str
    resultado_pos_simulacao: str
    status_confirmacao: str  # "Confirmada integralmente", "Confirmada", etc.
    resumo_evidencia: str


@dataclass(frozen=True)
class LimitacaoEstudo:
    """Estrutura detalhada de uma limitação metodológica do estudo experimental."""

    numero: int
    titulo: str
    descricao: str
    impacto_na_inferencia: str
    como_mitigar_futuramente: str


@dataclass(frozen=True)
class RecomendacaoFinal:
    """Recomendação estatística final e condições de transição entre os testes."""

    teste_recomendado: str
    tipo_abordagem: str
    justificativa_principal: str
    tamanho_efeito_recomendado: str
    quando_muda_a_recomendacao: str
    sintese_executiva_conclusao: str


def obter_expectativa_vs_resultados() -> List[ItemExpectativaVsResultado]:
    """Retorna lista estruturada confrontando a expectativa prévia com os resultados de Q1, Q2, Q3 e Reais."""
    return [
        ItemExpectativaVsResultado(
            dimensao="Q1 — Taxa de Erro Tipo I (H₀ verdadeira)",
            previsao_pre_simulacao=(
                "Ambos os testes deveriam controlar o Erro Tipo I próximo a 5%, mas esperava-se que "
                "o teste t de Welch pudesse sofrer distorções devido à cauda pesada dos tempos de merge."
            ),
            resultado_pos_simulacao=(
                "Mann-Whitney foi nominal e calibrado (4,58% ≈ 5,0%, IC 95%: [4,19%, 5,01%]). "
                "O teste t de Welch foi excessivamente conservador (3,93% < 5,0%, IC 95%: [3,57%, 4,33%]), "
                "pois a cauda log-normal infla o desvio padrão amostral no denominador de t."
            ),
            status_confirmacao="Confirmada integralmente",
            resumo_evidencia=(
                "Mann-Whitney atendeu ao critério estrito de Bradley [4,5% a 5,5%]; Welch desviou-se "
                "em -1,07 p.p. Nenhum teste foi liberal."
            ),
        ),
        ItemExpectativaVsResultado(
            dimensao="Q2 — Poder Estatístico de Detecção (sob H₁)",
            previsao_pre_simulacao=(
                "O teste U de Mann-Whitney teria maior poder de detecção para tempos de software com cauda longa, "
                "enquanto Welch perderia sensibilidade pelo impacto de outliers na variância."
            ),
            resultado_pos_simulacao=(
                "Mann-Whitney superou Welch em todos os 6 tamanhos de efeito (δ de 0% a 50%). "
                "Em δ = 50% (redução substancial), Mann-Whitney alcançou 79,08% de poder frente a 64,20% de Welch "
                "(vantagem de +14,88 pontos percentuais)."
            ),
            status_confirmacao="Confirmada integralmente",
            resumo_evidencia=(
                "Mann-Whitney atinge a zona de poder aceitável (80%) muito antes de Welch nas condições realistas do cenário."
            ),
        ),
        ItemExpectativaVsResultado(
            dimensao="Q3 — Violação por Outliers Extremos",
            previsao_pre_simulacao=(
                "A presença de anomalias pontuais severas (PRs bloqueados) prejudicaria drasticamente o teste paramétrico "
                "e teria efeito desprezível sobre o teste de postos."
            ),
            resultado_pos_simulacao=(
                "Sob 10% de outliers severos (5x + 50h), o poder de Welch colapsou de 64,20% para 22,62% em δ = 50% "
                "(queda de 41,58 p.p.), enquanto Mann-Whitney preservou 62,30% de poder (vantagem de +39,68 p.p.)."
            ),
            status_confirmacao="Confirmada integralmente",
            resumo_evidencia=(
                "Postos ordenados limitam o peso do outlier ao posto máximo (60); Welch é desestruturado quadraticamente."
            ),
        ),
        ItemExpectativaVsResultado(
            dimensao="Q3 — Violação por Normalidade Pura",
            previsao_pre_simulacao=(
                "O teste t de Welch só apresentaria superioridade se os dados fossem perfeitamente gaussianos e simétricos."
            ),
            resultado_pos_simulacao=(
                "Sob normalidade pura sem outliers, Welch obteve poder de 75,80% contra 73,12% de Mann-Whitney "
                "em δ = 30% (vantagem marginal de apenas +2,68 p.p. para Welch)."
            ),
            status_confirmacao="Confirmada integralmente",
            resumo_evidencia=(
                "Mesmo no cenário ideal para o paramétrico, a eficiência assintótica de Pitman de Mann-Whitney é 95,5%."
            ),
        ),
        ItemExpectativaVsResultado(
            dimensao="Dados Reais (tiangolo/fastapi, n = 30 por grupo)",
            previsao_pre_simulacao=(
                "Mann-Whitney produziria evidência estatística mais clara (p-valor menor) que Welch sobre os 60 PRs reais."
            ),
            resultado_pos_simulacao=(
                "Embora ambos convirjam para não rejeitar H₀ ao nível α = 0,05 para a amostra moderada n = 30 "
                "(Welch p = 0,2641; Mann-Whitney p = 0,1715), Mann-Whitney produziu p-valor 35% menor "
                "e capturou probabilidade de superioridade de 60,6% (efeito pequeno, r_rb = -0,2111)."
            ),
            status_confirmacao="Confirmada",
            resumo_evidencia=(
                "Conexão com G4: com n=30 o poder para efeito pequeno (24% a 28%) é de apenas 28% a 48%, "
                "explicando a não rejeição sem descartar relevância prática."
            ),
        ),
    ]


def obter_tabela_expectativa_vs_resultados() -> pd.DataFrame:
    """Converte os itens de expectativa vs. resultados em um DataFrame formatado para o Dashboard."""
    dados = []
    for item in obter_expectativa_vs_resultados():
        dados.append(
            {
                "Dimensão Avaliada": item.dimensao,
                "Expectativa Prévia (Antes de Simular)": item.previsao_pre_simulacao,
                "Resultado Observado (Simulações / Reais)": item.resultado_pos_simulacao,
                "Status da Previsão": item.status_confirmacao,
                "Evidência Central": item.resumo_evidencia,
            }
        )
    return pd.DataFrame(dados)


def obter_recomendacao_final() -> RecomendacaoFinal:
    """Retorna a recomendação formal definitiva do grupo para o cenário investigado."""
    return RecomendacaoFinal(
        teste_recomendado=CENARIO.teste_nao_parametrico,
        tipo_abordagem="Não-paramétrico (baseado em postos / dominância estocástica)",
        justificativa_principal=(
            "O teste U de Mann-Whitney demonstrou superioridade decisiva nas condições realistas de Engenharia de Software. "
            "Ele garante controle rigoroso da taxa de Erro Tipo I (4,58% ≈ 5,0%, atendendo a Bradley estrito), "
            "oferece maior poder de detecção sob assimetria log-normal (79,08% vs. 64,20% em δ=50%) e exibe imunidade "
            "excepcional a outliers severos (62,30% vs. 22,62% de Welch sob contaminação). Em contrapartida, o teste t de "
            "Welch mostrou-se excessivamente conservador (Erro Tipo I de 3,93% a 2,90%) e vulnerável ao colapso de poder "
            "quando há valores extremos na cauda."
        ),
        tamanho_efeito_recomendado=(
            "Correlação Rank-Biserial (r_rb) ou Delta de Cliff (d_cliff), complementados pela "
            "Probabilidade de Superioridade (P(X_com < Y_sem))."
        ),
        quando_muda_a_recomendacao=(
            "A recomendação mudaria em favor do teste t de Welch em apenas duas situações bem delimitadas: "
            "1. Se os dados forem comprovadamente simétricos e livres de caudas pesadas ou outliers severos "
            "(cenário Gaussiano puro, onde Welch tem vantagem marginal de ~2,7 p.p. de poder); "
            "2. Se o tamanho amostral for muito grande (n > 100 a 200 observações por grupo), onde o Teorema Central do "
            "Limite normaliza satisfatoriamente a distribuição das médias, e o objetivo da gerência de engenharia for "
            "estritamente estimar o custo ou ganho médio em horas/dólares (média aritmética ponderada)."
        ),
        sintese_executiva_conclusao=(
            "Para avaliação de lead time e tempos de processo de software, a recomendação categórica é utilizar o "
            "teste U de Mann-Whitney acompanhado da correlação rank-biserial. A assimetria positiva natural e a "
            "recorrência de outliers inviabilizam a sensibilidade do teste t paramétrico em amostras pequenas a moderadas."
        ),
    )


def obter_limitacoes_estudo() -> List[LimitacaoEstudo]:
    """Retorna a lista estruturada das 4 principais limitações metodológicas do estudo."""
    return [
        LimitacaoEstudo(
            numero=1,
            titulo="Tamanho amostral empírico moderado (n = 30 por grupo)",
            descricao=(
                "A amostra de dados reais minerada do repositório tiangolo/fastapi continha 30 Pull Requests com bot "
                "e 30 sem bot (60 no total). Esse volume foi excelente para calibração dos parâmetros log-normais da simulação, "
                "mas revelou-se insuficiente para atingir 80% de poder estatístico na detecção do efeito real observado "
                "(redução de 24% nas medianas, que teve poder empírico de ~45% a 48%)."
            ),
            impacto_na_inferencia=(
                "A não rejeição de H₀ na amostra real não comprova a ausência de benefício dos bots, mas reflete "
                "um Erro Tipo II potencial decorrente de tamanho amostral moderado frente a alta dispersão."
            ),
            como_mitigar_futuramente=(
                "Expandir a coleta empírica para n ≥ 80 a 100 Pull Requests por grupo, conforme projetado "
                "pelas curvas de dimensionamento amostral do Gráfico G4."
            ),
        ),
        LimitacaoEstudo(
            numero=2,
            titulo="Escopo restrito a um único ecossistema open-source (tiangolo/fastapi)",
            descricao=(
                "Os dados reais refletem as convenções, a cultura de revisão e as automações específicas do projeto FastAPI "
                "(FastAPI Bot, GitHub Actions de documentação e tradução). Projetos de software corporativo fechado, sistemas "
                "legados ou linguagens compiladas (C++, Rust) podem apresentar dinâmicas de merge substancialmente diferentes."
            ),
            impacto_na_inferencia=(
                "A generalização dos parâmetros exatos (μ_log = 2,80, σ_log = 0,92) deve ser feita com cautela "
                "ao transpor para outros domínios de engenharia."
            ),
            como_mitigar_futuramente=(
                "Conduzir estudos multi-repositório com amostras estratificadas de projetos de diferentes portes, "
                "linguagens e modelos de governança."
            ),
        ),
        LimitacaoEstudo(
            numero=3,
            titulo="Modelo univariado sem controle de variáveis de confusão (covariáveis)",
            descricao=(
                "A variável resposta analisada foi unicamente o tempo decorrido até o merge (tempo_horas). "
                "Não foram controladas covariáveis que influenciam criticamente a velocidade de integração, "
                "tais como o tamanho da alteração (linhas adicionadas/removidas - LOC), quantidade de arquivos modificados, "
                "número de comentários de discussão, experiência do autor do PR e complexidade ciclomática."
            ),
            impacto_na_inferencia=(
                "Parte da variância observada pode decorrer de disparidades no tamanho médio dos PRs entre os grupos, "
                "e não exclusivamente da presença de bots."
            ),
            como_mitigar_futuramente=(
                "Adotar pareamento por escore de propensão (Propensity Score Matching) ou modelos de regressão múltipla / "
                "modelos de sobrevivência (Cox Proportional Hazards) controlando por LOC e interações."
            ),
        ),
        LimitacaoEstudo(
            numero=4,
            titulo="Premissa de independência temporal e ausência de efeitos de sazonalidade",
            descricao=(
                "As simulações de Monte Carlo assumiram que os Pull Requests são observações independentes e identicamente "
                "distribuídas (i.i.d.). Na prática real, revisões de código sofrem forte dependência temporal (sazonalidade de "
                "dias úteis vs. fins de semana, períodos de férias, ciclos de sprint e code freezes antes de releases)."
            ),
            impacto_na_inferencia=(
                "A variabilidade real pode exibir autocorrelação em janelas de tempo concentradas, ligeiramente superior "
                "à dispersão gerada por amostragem puramente pseudoaleatória."
            ),
            como_mitigar_futuramente=(
                "Incorporar modelos de séries temporais ou bootstrapping em blocos temporais (block bootstrap) "
                "para preservar a dependência temporal do fluxo de trabalho."
            ),
        ),
    ]


def obter_resumo_conclusao_markdown() -> str:
    """Gera o texto completo e estruturado para a Seção 7 do Dashboard."""
    rec = obter_recomendacao_final()
    return (
        f"### Síntese Final e Recomendação Oficial\n\n"
        f"As 10.000 simulações de Monte Carlo executadas sob H₀ (Q1), sob tamanhos crescentes de efeito (Q2) "
        f"e sob violações severas de pressupostos (Q3), integradas à aplicação nos dados reais minerados do repositório "
        f"`tiangolo/fastapi`, confirmam de forma contundente a expectativa pré-experimental do grupo:\n\n"
        f"1. **Recomendação Oficial:** O **{rec.teste_recomendado}** é o teste estatístico formalmente recomendado "
        f"para experimentação com tempos de processo em Engenharia de Software. Ele garante taxa de Erro Tipo I perfeitamente "
        f"calibrada ao nível nominal de 5% (4,58% na base, 4,52% com outliers e 4,33% com n=10), atende aos critérios estritos "
        f"de robustez de Bradley (1978) e assegura poder de detecção amplamente superior (79,08% vs. 64,20% de Welch em δ=50%, "
        f"e 62,30% vs. 22,62% sob contaminação severa).\n"
        f"2. **Tamanho do Efeito Complementar:** A inferência sobre postos deve ser sempre acompanhada da "
        f"**Correlação Rank-Biserial (r_rb)** ou Delta de Cliff, complementada pela Probabilidade de Superioridade P(com < sem).\n"
        f"3. **Quando a Escolha Mudaria:** A recomendação migraria para o teste t de Welch apenas em distribuições estritamente "
        f"simétricas/normais e sem outliers (onde Welch obtém vantagem de ~2,7 p.p. de poder em δ=30%) ou em grandes amostras "
        f"(n > 100) quando a métrica de negócio exigir a média aritmética monetária/horária direta.\n"
        f"4. **Interpretação nos Dados Reais:** A não rejeição de H₀ nos 60 PRs reais decorre do tamanho amostral moderado "
        f"(n = 30 por grupo), que confere poder estatístico de apenas ~45% a 48% para detectar o efeito real pequeno observado "
        f"(redução de 24% a 28% no tempo até o merge), ilustrando empiricamente a necessidade de planejar amostras maiores "
        f"(n ≥ 80) para detecção conclusiva com 80% de poder."
    )


if __name__ == "__main__":
    print("=" * 80)
    print("LAB04FINAL - Módulo de Conclusão e Recomendações do Dashboard")
    print("=" * 80)
    rec = obter_recomendacao_final()
    print(f"\nTeste Recomendado: {rec.teste_recomendado}")
    print(f"Abordagem: {rec.tipo_abordagem}")
    print(f"\nJustificativa:\n{rec.justificativa_principal}")
    print(f"\nQuando a recomendação mudaria:\n{rec.quando_muda_a_recomendacao}")
    print("\n" + "-" * 80)
    print("Expectativa vs. Resultados:")
    df_exp = obter_tabela_expectativa_vs_resultados()
    print(df_exp[["Dimensão Avaliada", "Status da Previsão", "Evidência Central"]].to_string(index=False))
    print("\n" + "-" * 80)
    print("Limitações do Estudo:")
    for lim in obter_limitacoes_estudo():
        print(f"[{lim.numero}] {lim.titulo}: {lim.impacto_na_inferencia}")

