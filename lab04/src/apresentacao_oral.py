"""Preparação e suporte interativo para a Apresentação Oral — Perguntas 11 a 15.

Issue #62: [ LAB04FINAL ] Preparar apresentação oral das perguntas 11 a 15.

Este módulo estrutura as respostas diretas (roteiro de ~30 segundos por pergunta),
as referências visuais exatas no dashboard (onde apontar na tela durante a arguição)
e os cálculos empíricos de suporte para as perguntas 11, 12, 13, 14 e 15 da
apresentação oral do Laboratório 04:

- Pergunta 11: Violação de pressupostos simulada (Q3) e por que afeta mais um teste que o outro;
- Pergunta 12: O que mudaria no G3 e no G4 se usássemos α = 0,01 em vez de α = 0,05;
- Pergunta 13: Confirmação da expectativa inicial do grupo pela simulação + análise de
  detecção para efeito verdadeiro de 5% com amostra pequena (n = 15);
- Pergunta 14: Comparação das conclusões nos dados reais (tiangolo/fastapi) e importância
  prática do tamanho do efeito;
- Pergunta 15: Recomendação oficial de teste para o cenário, quando a escolha mudaria
  e principal limitação do estudo.

Uso via linha de comando:
    python -m lab04.src.apresentacao_oral
"""

from __future__ import annotations

from dataclasses import dataclass
import sys
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from lab04.src.cenario import CENARIO
from lab04.src.simulacao import GeradorDadosSimulados
from lab04.src.testes_estatisticos import avaliar_matrizes_rapido


@dataclass(frozen=True)
class PerguntaApresentacaoOral:
    """Estrutura de uma pergunta da apresentação oral com roteiro de 30s e apoio visual."""

    numero: int
    titulo_curto: str
    pergunta_oficial: str
    pergunta_variante: Optional[str]
    secao_dashboard: str
    onde_apontar_no_dashboard: str
    fala_30_segundos: str
    fala_variante_30_segundos: Optional[str]
    pontos_chave_argicao: Tuple[str, ...]


def avaliar_impacto_alpha_001(
    semente: int = 42,
    n_simulacoes: int = 10_000,
    n_sem_bot: int = 30,
    n_com_bot: int = 30,
    efeitos: Tuple[float, ...] = (0.00, 0.10, 0.20, 0.30, 0.40, 0.50),
) -> pd.DataFrame:
    """Compara empiricamente o Erro Tipo I (δ=0%) e o Poder (δ>0%) sob α = 0,05 vs. α = 0,01.

    Sustenta com números exatos a resposta da Pergunta 12 sobre o deslocamento de G3 e G4
    ao adotar um nível de significância mais rigoroso (α = 0,01).
    """
    gerador = GeradorDadosSimulados(semente=semente)
    linhas: List[Dict[str, object]] = []

    for delta in efeitos:
        gerador.redefinir_semente(semente)
        mat_sem, mat_com = gerador.gerar_matrizes_experimento(
            n_simulacoes=n_simulacoes,
            n_sem_bot=n_sem_bot,
            n_com_bot=n_com_bot,
            efeito_reducao=delta,
            arredondar=2,
        )
        res_005 = avaliar_matrizes_rapido(
            mat_sem, mat_com, alpha=0.05, alternativa=CENARIO.tipo_teste
        )
        res_001 = avaliar_matrizes_rapido(
            mat_sem, mat_com, alpha=0.01, alternativa=CENARIO.tipo_teste
        )

        poder_w_005 = float(np.mean(res_005["rejeita_welch"])) * 100.0
        poder_mw_005 = float(np.mean(res_005["rejeita_mann_whitney"])) * 100.0
        poder_w_001 = float(np.mean(res_001["rejeita_welch"])) * 100.0
        poder_mw_001 = float(np.mean(res_001["rejeita_mann_whitney"])) * 100.0

        linhas.append(
            {
                "efeito_reducao": float(delta),
                "efeito_pct": float(delta) * 100.0,
                "papel_estatistico": "Erro Tipo I (G3)" if delta == 0.0 else "Poder Estatístico (G4)",
                "welch_alpha_005_pct": poder_w_005,
                "welch_alpha_001_pct": poder_w_001,
                "reducao_welch_pp": poder_w_001 - poder_w_005,
                "mw_alpha_005_pct": poder_mw_005,
                "mw_alpha_001_pct": poder_mw_001,
                "reducao_mw_pp": poder_mw_001 - poder_mw_005,
            }
        )

    return pd.DataFrame(linhas)


def avaliar_cenario_subdimensionado_n15_efeito_5pct(
    semente: int = 42,
    n_simulacoes: int = 10_000,
    alpha: float = CENARIO.alpha,
) -> Dict[str, float]:
    """Avalia o poder empírico quando o efeito verdadeiro é de 5% e a amostra tem n = 15 por grupo.

    Sustenta com números exatos a discussão de tamanho amostral e a variante da Pergunta 13.
    """
    gerador = GeradorDadosSimulados(semente=semente)
    mat_sem, mat_com = gerador.gerar_matrizes_experimento(
        n_simulacoes=n_simulacoes,
        n_sem_bot=15,
        n_com_bot=15,
        efeito_reducao=0.05,
        arredondar=2,
    )
    res = avaliar_matrizes_rapido(mat_sem, mat_com, alpha=alpha, alternativa=CENARIO.tipo_teste)
    poder_welch_pct = float(np.mean(res["rejeita_welch"])) * 100.0
    poder_mw_pct = float(np.mean(res["rejeita_mann_whitney"])) * 100.0
    return {
        "n_por_grupo": 15.0,
        "efeito_pct": 5.0,
        "alpha_pct": alpha * 100.0,
        "poder_welch_pct": poder_welch_pct,
        "erro_tipo_2_welch_pct": 100.0 - poder_welch_pct,
        "poder_mann_whitney_pct": poder_mw_pct,
        "erro_tipo_2_mw_pct": 100.0 - poder_mw_pct,
    }


def obter_perguntas_11_a_15() -> List[PerguntaApresentacaoOral]:
    """Retorna a lista estruturada das Perguntas 11 a 15 para a apresentação oral."""
    return [
        PerguntaApresentacaoOral(
            numero=11,
            titulo_curto="Violação de Pressupostos (Q3) e Sensibilidade Diferencial",
            pergunta_oficial=(
                "Que violação de pressuposto vocês simularam, e por que ela afeta mais "
                "um teste do que o outro?"
            ),
            pergunta_variante=None,
            secao_dashboard="Seção 4 (G3 — Erro Tipo I) e Seção 5 (G4 — Poder)",
            onde_apontar_no_dashboard=(
                "Apontar para os grupos 2 e 3 de barras no Gráfico G3 (Outliers 10% e Amostra "
                "Pequena n=10) e para as curvas tracejadas e pontilhadas no Gráfico G4."
            ),
            fala_30_segundos=(
                "Simulamos duas violações severas na Q3: primeiro, a injeção de 10% de outliers "
                "extremos multiplicando o tempo por 5 vezes mais 50 horas; segundo, a redução da "
                "amostra para n = 10 PRs por grupo sob forte assimetria log-normal. "
                "Elas afetam drasticamente o teste t de Welch porque os outliers entram elevados "
                "ao quadrado no cálculo da variância amostral, inflando o erro padrão no denominador "
                "e derrubando seu poder em δ = 50% de 64,20% para apenas 22,62% (-41,58 p.p.), além "
                "de n = 10 inviabilizar o Teorema Central do Limite. Já o teste U de Mann-Whitney "
                "converte os dados em postos ordenados de 1 a 60, limitando qualquer valor extremo "
                "ao posto máximo e mantendo 62,30% de poder mesmo sob outliers severos."
            ),
            fala_variante_30_segundos=None,
            pontos_chave_argicao=(
                "Violação 1 (Q3_Outliers): 10% de contaminação (6 de 60 observações) por 5x + 50h (representando bloqueios de CI/arquitetura).",
                "Violação 2 (Q3_AmostraPequena): Redução de n=30 para n=10 por grupo sob assimetria log-normal (σ_log = 0,9254).",
                "No G3 (Erro Tipo I): Welch cai para 3,28% com outliers e 2,90% com n=10 (conservadorismo severo); Mann-Whitney permanece estável em 4,52% e 4,33%.",
                "No G4 (Poder em δ=50%): Welch perde 41,58 p.p. com outliers (64,20% → 22,62%), enquanto Mann-Whitney mantém 62,30% (vantagem de +39,68 p.p.).",
            ),
        ),
        PerguntaApresentacaoOral(
            numero=12,
            titulo_curto="Mudança do Nível de Significância de α = 0,05 para α = 0,01",
            pergunta_oficial=(
                "Se vocês usassem α = 0,01 em vez de 0,05, o que mudaria no G3 e no G4?"
            ),
            pergunta_variante=None,
            secao_dashboard="Seção 4 (G3 — Erro Tipo I) e Seção 5 (G4 — Poder)",
            onde_apontar_no_dashboard=(
                "Apontar para a linha horizontal vermelha de 5% no Gráfico G3 e para a altura "
                "das curvas de poder no painel esquerdo do Gráfico G4."
            ),
            fala_30_segundos=(
                "Se reduzíssemos α de 0,05 para 0,01, exigiríamos evidência muito mais forte "
                "(p < 0,01) para rejeitar H0. No gráfico G3, a linha horizontal de referência "
                "desceria de 5% para 1%, e as barras empíricas de Erro Tipo I cairiam "
                "proporcionalmente: no cenário base, Mann-Whitney cairia de 4,58% para 0,81% e "
                "Welch de 3,93% para 0,42%, mantendo o perfil conservador do teste t. "
                "Já no gráfico G4, como o limiar crítico fica mais rigoroso, todas as curvas de "
                "poder se deslocariam para baixo e para a direita: em δ = 50%, o poder de "
                "Mann-Whitney cairia de 79,08% para 55,47% e o de Welch de 64,20% para 34,14%, "
                "aumentando o Erro Tipo II em troca de menos falsos positivos."
            ),
            fala_variante_30_segundos=None,
            pontos_chave_argicao=(
                "Trade-off clássico entre Erro Tipo I (α) e Erro Tipo II (β): reduzir α de 5% para 1% diminui falsos positivos, mas reduz o poder (1 - β).",
                "No G3 (Cenário Base sob H0): Mann-Whitney passa de 4,58% (α=5%) para 0,81% (α=1%); Welch passa de 3,93% (α=5%) para 0,42% (α=1%).",
                "No G4 (Poder em δ=30%): Mann-Whitney cai de 29,59% para 11,91% (-17,68 p.p.); Welch cai de 22,49% para 6,39% (-16,10 p.p.).",
                "No G4 (Poder em δ=50%): Mann-Whitney cai de 79,08% para 55,47% (-23,61 p.p.); Welch cai de 64,20% para 34,14% (-30,06 p.p.).",
            ),
        ),
        PerguntaApresentacaoOral(
            numero=13,
            titulo_curto="Expectativa Pré-Simulação vs. Resultados (e Subdimensionamento n=15, δ=5%)",
            pergunta_oficial=(
                "A simulação confirmou o que o grupo esperava antes de simular? "
                "Se não, o que explica a diferença?"
            ),
            pergunta_variante=(
                "Se o efeito verdadeiro é de 5%, mas a amostra tem n = 15, vocês esperam "
                "que os testes o detectem? Onde isso aparece nos gráficos?"
            ),
            secao_dashboard="Seção 1 (Cenário), Seção 5 (G4 — Poder) e Seção 7 (Conclusão)",
            onde_apontar_no_dashboard=(
                "Apontar para a hipótese pré-simulação na Seção 1/Seção 7 e para a abertura entre "
                "as curvas laranja e azul no Gráfico G4 (incluindo o canto inferior esquerdo em δ ≤ 10%)."
            ),
            fala_30_segundos=(
                "Sim, a simulação confirmou integralmente nossa expectativa teórica prévia: "
                "esperávamos que o teste U de Mann-Whitney superasse o teste t de Welch porque os "
                "tempos de merge seguem uma distribuição log-normal fortemente assimétrica à direita "
                "(assimetria acima de 1,45 e razão média/mediana de 1,45x). "
                "O ponto mais revelador que a simulação esclareceu na prática foi a direção do "
                "desvio do teste t no G3: em vez de ficar liberal, o teste t de Welch ficou "
                "sistematicamente conservador (rejeitando apenas 3,93% na base e 3,28% com outliers), "
                "pois os valores extremos da cauda direita entram ao quadrado no denominador da "
                "estatística t, freando tanto os falsos positivos quanto o poder estatístico."
            ),
            fala_variante_30_segundos=(
                "Se o efeito verdadeiro for de apenas 5% com n = 15 observações por grupo, não "
                "esperamos que nenhum dos dois testes o detecte. Isso aparece claramente no canto "
                "inferior esquerdo do gráfico G4: mesmo com n = 30, para efeitos de 5% a 10% as "
                "curvas ficam entre 4,4% e 7,1%, coladas na linha vermelha de ruído nominal de 5%; "
                "e na curva pontilhada de amostra pequena (n = 10) o poder em 10% é de apenas 3,41% "
                "a 5,13%. Simulando especificamente n = 15 e efeito de 5%, Mann-Whitney tem apenas "
                "4,45% de poder e Welch 3,35%, ou seja, mais de 95% de probabilidade de Erro Tipo II."
            ),
            pontos_chave_argicao=(
                "Expectativa prévia confirmada: Mann-Whitney liderou em precisão de α (4,58% vs. 3,93%) e em poder em todos os níveis de efeito (79,08% vs. 64,20% em δ=50%).",
                "Nuance estatística explicada pela simulação: outliers simétricos nos dois grupos tornam Welch conservador (e não liberal) devido à inflação quadrática de s² no denominador.",
                "Para a pergunta variante (δ=5%, n=15): Poder empírico é de apenas 4,45% (Mann-Whitney) e 3,35% (Welch) — experimento severamente subdimensionado (Erro Tipo II > 95%).",
            ),
        ),
        PerguntaApresentacaoOral(
            numero=14,
            titulo_curto="Conclusão nos Dados Reais (tiangolo/fastapi) e Importância Prática",
            pergunta_oficial=(
                "Nos dados reais, os dois testes chegaram à mesma conclusão? "
                "O tamanho do efeito tem importância prática?"
            ),
            pergunta_variante=None,
            secao_dashboard="Seção 6 (Dados reais) e Seção 2 (G1 — Os dados)",
            onde_apontar_no_dashboard=(
                "Apontar para a Tabela da Seção 6 (Dados reais) destacando os dois p-valores "
                "(0,0969 vs. 0,0446) e as medianas (16,49h vs. 8,54h)."
            ),
            fala_30_segundos=(
                "Não, nos dados reais minerados do repositório FastAPI (n = 30 por grupo) os dois "
                "testes chegaram a decisões opostas a α = 5%: o teste U de Mann-Whitney rejeitou H0 "
                "(U = 577,5; p = 0,0446), enquanto o teste t de Welch não rejeitou H0 (t = 1,688; "
                "p = 0,0969). Isso ocorreu porque os 3 outliers severos do grupo com bot (PRs de "
                "53h a 70h) inflaram o desvio padrão para 19,21h, mascarando o efeito paramétrico — "
                "exatamente o fenômeno previsto pelas nossas curvas do G4. "
                "E sim, o tamanho do efeito tem alta importância prática: a mediana caiu 48,2% "
                "(de 16,49h para 8,54h, economizando quase 8 horas de espera por PR), com r "
                "rank-biserial de +0,2833 e d de Cohen de +0,4358."
            ),
            fala_variante_30_segundos=None,
            pontos_chave_argicao=(
                "Divergência real em α = 0,05: Mann-Whitney detecta o efeito (p = 0,0446 < 0,05), enquanto Welch falha em detectar (p = 0,0969 ≥ 0,05).",
                "Conexão direta com o G4: com n=30 e redução real próxima de 34% a 48% sob outliers, o G4 já previa que Welch teria baixo poder por perda de eficiência na cauda.",
                "Importância prática substancial: redução de 34,3% na média (25,75h → 16,92h, -8,83h) e de 48,2% na mediana (16,49h → 8,54h, -7,95h), acelerando o ciclo de CI/CD em quase um dia útil de trabalho.",
            ),
        ),
        PerguntaApresentacaoOral(
            numero=15,
            titulo_curto="Recomendação Oficial, Quando Mudar de Teste e Principal Limitação",
            pergunta_oficial=(
                "Qual teste vocês recomendam para o cenário, em que situação mudariam a "
                "recomendação, e qual é a principal limitação do estudo?"
            ),
            pergunta_variante=None,
            secao_dashboard="Seção 7 (Conclusão) e Painel Direito da Seção 5 (G4)",
            onde_apontar_no_dashboard=(
                "Apontar para a Seção 7 (Conclusão) e para a curva azul traço-ponto (Controle "
                "Normal Simétrico) na zona inferior (Δ < 0) do painel direito do Gráfico G4."
            ),
            fala_30_segundos=(
                "Recomendamos o teste U de Mann-Whitney para avaliar o tempo de merge de Pull "
                "Requests e métricas de engenharia de software assimétricas, pois ele mantém o "
                "Erro Tipo I calibrado perto de 5% (4,58%) e entrega até +39,68 pontos percentuais "
                "a mais de poder que Welch quando há outliers. "
                "Mudaríamos a recomendação para o teste t de Welch se a métrica seguisse uma "
                "distribuição Normal simétrica sem outliers — situação mostrada na zona azul do "
                "painel direito do G4, onde Welch supera Mann-Whitney (65,73% vs. 63,03% em δ=30% "
                "pela eficiência assintótica de 95,5% dos postos) — ou se a decisão exigisse "
                "estritamente a média em grande amostra. "
                "A principal limitação do estudo é ser observacional em um único repositório "
                "(FastAPI, n=30), sujeito a confundidores como tamanho do PR e complexidade do código."
            ),
            fala_variante_30_segundos=None,
            pontos_chave_argicao=(
                "Recomendação principal: Teste U de Mann-Whitney (robusto no Erro Tipo I em G3 e dominante em poder nas curvas log-normais de G4).",
                "Quando mudar para t de Welch: (1) Distribuição aproximadamente simétrica/Normal e livre de outliers (onde Welch tem vantagem de ~2,7 p.p. em δ=30% devido à ARE = 3/π ≈ 95,5%), ou (2) análise sobre dados log-transformados validados sem caudas extremas.",
                "Principal limitação do estudo: Coleta real observacional (não-randomizada) restrita a um único projeto (tiangolo/fastapi) com n=30 por grupo, sem controle multivariado para linhas alteradas (LOC), número de revisores humanos ou fuso horário.",
            ),
        ),
    ]


def construir_tabela_resumo_perguntas_11_a_15() -> pd.DataFrame:
    """Retorna um DataFrame resumindo as Perguntas 11 a 15, onde apontar e a resposta-síntese."""
    perguntas = obter_perguntas_11_a_15()
    return pd.DataFrame(
        [
            {
                "Nº": f"Pergunta {p.numero}",
                "Tema": p.titulo_curto,
                "Pergunta": p.pergunta_oficial,
                "Onde Apontar no Dashboard": p.secao_dashboard,
                "Síntese Direta (30s)": p.fala_30_segundos,
            }
            for p in perguntas
        ]
    )


def gerar_roteiro_markdown_perguntas_11_a_15() -> str:
    """Gera o relatório completo em Markdown das Perguntas 11 a 15 com tabelas empíricas."""
    perguntas = obter_perguntas_11_a_15()
    df_alpha = avaliar_impacto_alpha_001(semente=42, n_simulacoes=10_000)
    sub_n15 = avaliar_cenario_subdimensionado_n15_efeito_5pct(semente=42, n_simulacoes=10_000)

    linhas: List[str] = [
        "# Roteiro da Apresentação Oral — Perguntas 11 a 15 (Issue #62)",
        "",
        "**Tempo estimado por resposta:** ~30 segundos (curta, direta e apoiada visualmente no Dashboard).",
        "",
    ]
    for p in perguntas:
        linhas.append(f"## Pergunta {p.numero} — {p.titulo_curto}")
        linhas.append(f"- **Enunciado:** *\"{p.pergunta_oficial}\"*")
        linhas.append(f"- **Seção do Dashboard:** `{p.secao_dashboard}`")
        linhas.append(f"- **Onde apontar na tela:** {p.onde_apontar_no_dashboard}")
        linhas.append(f"- **Fala direta (30s):**\n  > \"{p.fala_30_segundos}\"")
        if p.pergunta_variante and p.fala_variante_30_segundos:
            linhas.append(f"- **Variante de arguição (Tamanho amostral / G4):** *\"{p.pergunta_variante}\"*")
            linhas.append(f"- **Fala direta para a variante (30s):**\n  > \"{p.fala_variante_30_segundos}\"")
        linhas.append("- **Números-chave para arguição do professor:**")
        for pt in p.pontos_chave_argicao:
            linhas.append(f"  - {pt}")
        linhas.append("")

    linhas.append("## Evidência Empírica Auxiliar — Pergunta 12 (α = 0,05 vs. α = 0,01)")
    linhas.append(df_alpha.to_string(index=False))
    linhas.append("")
    linhas.append("## Evidência Empírica Auxiliar — Subdimensionamento (n = 15, δ = 5%)")
    linhas.append(
        f"- Poder t de Welch: {sub_n15['poder_welch_pct']:.2f}% "
        f"(Erro Tipo II β = {sub_n15['erro_tipo_2_welch_pct']:.2f}%)\n"
        f"- Poder U de Mann-Whitney: {sub_n15['poder_mann_whitney_pct']:.2f}% "
        f"(Erro Tipo II β = {sub_n15['erro_tipo_2_mw_pct']:.2f}%)"
    )
    return "\n".join(linhas)


if __name__ == "__main__":  # pragma: no cover
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(gerar_roteiro_markdown_perguntas_11_a_15())
