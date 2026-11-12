"""Preparação e suporte interativo para a Apresentação Oral — Perguntas 1 a 15.

Issues correspondentes:
- Issue #58: [ LAB04FINAL ] Preparar apresentação oral das perguntas 1 a 5.
- Issue #60: [ LAB04FINAL ] Preparar apresentação oral das perguntas 6 a 10.
- Issue #62: [ LAB04FINAL ] Preparar apresentação oral das perguntas 11 a 15.

Este módulo estrutura as respostas diretas (roteiro de ~30 segundos por pergunta),
as referências visuais exatas no dashboard (onde apontar na tela durante a arguição),
as respostas para perguntas variantes da banca e os cálculos empíricos de suporte.

Bloco 0 — Perguntas 1 a 5 (Issue #58):
- Pergunta 1: Cenário investigado e significado de H₀ e H₁ em palavras simples;
- Pergunta 2: Direcionalidade do teste (bicaudal) e justificativa metodológica;
- Pergunta 3: Coleta dos dados reais (FastAPI) e características da distribuição;
- Pergunta 4: Uso dos dados reais para calibrar parâmetros log-normais na simulação;
- Pergunta 5: O que cada teste compara de fato (médias aritméticas vs. postos ordenados).

Bloco 1 — Perguntas 6 a 10 (Issue #60):
- Pergunta 6: Distribuição da estatística sob H₀ e região de rejeição no G2;
- Pergunta 7: Significado e equívocos conceituais do p-valor no exemplo do G2;
- Pergunta 8: Erro Tipo I vs. Erro Tipo II no cenário e análise de gravidade;
- Pergunta 9: Comportamento de Erro Tipo I no G3 (liberal vs. conservador);
- Pergunta 10: Poder estatístico no G4 e evolução da vantagem com o efeito.

Bloco 2 — Perguntas 11 a 15 (Issue #62):
- Pergunta 11: Violação de pressupostos simulada (Q3) e sensibilidade diferencial;
- Pergunta 12: Mudança do nível de significância de α = 0,05 para α = 0,01 no G3 e G4;
- Pergunta 13: Confirmação da expectativa inicial + análise de subdimensionamento (n = 15, δ = 5%);
- Pergunta 14: Comparação das conclusões nos dados reais (tiangolo/fastapi) e importância prática;
- Pergunta 15: Recomendação oficial de teste, quando mudar de teste e principal limitação.

Uso via linha de comando:
    python -m lab04.src.apresentacao_oral
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
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


# ----------------------------------------------------------------------------
# Perguntas 1 a 5 (Issue #58)
# ----------------------------------------------------------------------------
def obter_perguntas_1_a_5() -> List[PerguntaApresentacaoOral]:
    """Retorna a lista estruturada das Perguntas 1 a 5 para a apresentação oral (Issue #58)."""
    return [
        PerguntaApresentacaoOral(
            numero=1,
            titulo_curto="Cenário de Pesquisa e Significado de H₀ e H₁",
            pergunta_oficial=(
                "Qual é o cenário de vocês e o que H₀ e H₁ afirmam, em palavras simples?"
            ),
            pergunta_variante=(
                "Se o p-valor for maior que 0,05, isso prova que H₀ é verdadeira ou apenas não temos evidências para rejeitá-la?"
            ),
            secao_dashboard="Seção 1 (Cenário)",
            onde_apontar_no_dashboard=(
                "Apontar para a Seção 1 do Dashboard: no card esquerdo (Pergunta de Pesquisa em destaque), "
                "no card central (definições conceituais de H₀ e H₁ e operacionalizações para Welch e Mann-Whitney) "
                "e no card direito (origem dos dados no repositório tiangolo/fastapi)."
            ),
            fala_30_segundos=(
                "Nosso cenário investiga se a adoção de bots de automação em Pull Requests acelera ou atrasa "
                "o tempo até o merge no repositório open-source FastAPI. Em palavras simples, a hipótese nula H₀ afirma "
                "que os bots não fazem qualquer diferença no tempo de merge: a distribuição dos tempos com e sem bot é a mesma "
                "e qualquer oscilação observada decorre de mero acaso amostral. Já a hipótese alternativa H₁ afirma que existe "
                "uma diferença sistemática no tempo de processo entre os grupos, seja acelerando o fluxo de integração contínua "
                "ou gerando overhead e atraso."
            ),
            fala_variante_30_segundos=(
                "Apenas indica ausência de evidência suficiente para rejeitar. Em inferência frequentista, não rejeitar H₀ "
                "jamais prova que ela seja verdadeira; significa apenas que, dado o ruído e a dispersão amostral com n = 30, "
                "o teste não acumulou poder estatístico suficiente para descartar a hipótese de igualdade (risco de Erro Tipo II)."
            ),
            pontos_chave_argicao=(
                "Cenário investigado: Par 3 — Efeito do uso de bots de automação sobre o lead time até o merge de PRs.",
                "H₀ conceitual: O tempo até o merge é identicamente distribuído entre PRs com e sem bot (efeito nulo).",
                "H₁ conceitual: O tempo até o merge difere sistematicamente entre PRs com e sem bot (efeito bicaudal).",
                "Operacionalização estatística: Welch testa μ_sem = μ_com; Mann-Whitney testa P(X_com > Y_sem) = 0,50.",
                "Não rejeição ≠ Prova de H₀: Ausência de significância com amostras moderadas decorre do poder estatístico limitado.",
            ),
        ),
        PerguntaApresentacaoOral(
            numero=2,
            titulo_curto="Direcionalidade do Teste: Unicaudal vs. Bicaudal",
            pergunta_oficial=(
                "O teste de vocês é unicaudal ou bicaudal? Por quê?"
            ),
            pergunta_variante=(
                "Por que não adotar teste unicaudal à esquerda já que o interesse prático da equipe é exclusivamente acelerar o merge?"
            ),
            secao_dashboard="Seção 1 (Cenário) e Seção 3 (Como os testes funcionam — G2)",
            onde_apontar_no_dashboard=(
                "Apontar para o card 'Pergunta de Pesquisa' na Seção 1 onde consta explicitamente 'Tipo de teste: bicaudal / two-sided', "
                "e para as duas áreas vermelhas sombreadas de 2,5% em cada extremidade da distribuição nula no Gráfico G2."
            ),
            fala_30_segundos=(
                "Nosso teste é estritamente bicaudal (two-sided). Embora a expectativa teórica inicial fosse de aceleração, "
                "a literatura empírica de Engenharia de Software documenta que bots com falhas, conflitos de dependências, "
                "notificações excessivas ou testes frágeis podem paradoxalmente atrasar as aprovações. Como um atraso nas "
                "integrações representaria um impacto organizacional negativo relevante que precisamos ser capazes de detectar, "
                "não podemos descartar essa direção a priori, repartindo o risco α = 5% em 2,5% para aceleração e 2,5% para atraso."
            ),
            fala_variante_30_segundos=(
                "Adotar um teste unicaudal inflaria o poder estatístico na direção desejada mas tornaria o teste cego a qualquer "
                "atraso provocado pelo bot. Se a automação na prática gerasse gargalos severos e aumentasse o lead time, o teste "
                "unicaudal à esquerda falharia em acusar qualquer significância, induzindo a gestão a um falso senso de segurança."
            ),
            pontos_chave_argicao=(
                "Classificação formal: Teste bicaudal (two-sided / bilateral) com nível de significância α = 0,05.",
                "Divisão do erro α: α/2 = 0,025 alocado na cauda inferior (aceleração) e 0,025 na cauda superior (atraso).",
                "Limites críticos no G2: t = ±2,0085 (Welch) e z = ±1,9600 (Mann-Whitney).",
                "Justificativa metodológica: Evitar viés confirmatório; bots podem gerar retrabalho e overhead de CI na prática.",
            ),
        ),
        PerguntaApresentacaoOral(
            numero=3,
            titulo_curto="Coleta dos Dados Reais e Formato da Distribuição",
            pergunta_oficial=(
                "Como os dados reais foram coletados, e o que eles mostraram sobre a forma da distribuição?"
            ),
            pergunta_variante=(
                "Quais evidências estatísticas confirmam que os dados reais violam a suposição de normalidade?"
            ),
            secao_dashboard="Seção 1 (Origem dos Dados Reais) e Seção 2 (G1 — Os dados)",
            onde_apontar_no_dashboard=(
                "Apontar para a Seção 1 no card 'Origem dos Dados Reais' (60 PRs do tiangolo/fastapi), para os dois histogramas "
                "superiores do Gráfico G1 e para a Tabela Comparativa Descritiva destacando os valores de assimetria (1,72 e 2,17) "
                "e os outliers na cauda direita (até 105,5h)."
            ),
            fala_30_segundos=(
                "Os dados foram minerados via GitHub REST API do repositório fastapi (tiangolo/fastapi), selecionando 60 Pull Requests "
                "mergeados com tamanho moderado entre 10 e 500 linhas: 30 interagindo com bots e 30 sem bots. Os dados revelaram "
                "que a distribuição é fortemente assimétrica à direita, contínua estritamente positiva e com caudas longas: "
                "a assimetria calculada é de 1,72 sem bot e 2,17 com bot, com presença de outliers extremos de até 105,5 horas. "
                "O teste de Shapiro-Wilk rejeita a normalidade com p < 0,001."
            ),
            fala_variante_30_segundos=(
                "A forte assimetria positiva, o teste de Shapiro-Wilk altamente significativo (p = 0,00015) e a grande "
                "discrepância entre médias (27,3h e 20,8h) e medianas (18,9h e 13,6h) comprovam a não-normalidade. "
                "Além disso, o desvio padrão é da mesma ordem de grandeza da média (23,2h e 22,6h), violando totalmente o "
                "pressuposto de simetria do teste t clássico."
            ),
            pontos_chave_argicao=(
                "Fonte empírica: GitHub API v3, repositório tiangolo/fastapi, n = 30 por grupo (N = 60 PRs mergeados).",
                "Filtros de controle: PRs aceitos com 10 a 500 linhas modificadas (LOC) para homogeneizar complexidade.",
                "Assimetria acentuada: 1,72 (sem_bot) e 2,17 (com_bot); cauda longa estritamente positiva (Y > 0).",
                "Presença de outliers: 4 outliers em sem_bot (máx 105,50h) e 2 em com_bot (máx 88,00h) pelo critério IQR 1,5x.",
                "Rejeição de normalidade: Shapiro-Wilk W = 0,805 (p = 0,00015), inviabilizando a suposição gaussiana estrita.",
            ),
        ),
        PerguntaApresentacaoOral(
            numero=4,
            titulo_curto="Calibração dos Parâmetros da Simulação com os Dados Reais",
            pergunta_oficial=(
                "Como os dados reais ajudaram a escolher os parâmetros da simulação?"
            ),
            pergunta_variante=(
                "Por que uma distribuição Normal não seria adequada para modelar os tempos na simulação de Monte Carlo?"
            ),
            secao_dashboard="Seção 2 (Os dados — Expander de Justificativa e Calibração) e Gráfico G1",
            onde_apontar_no_dashboard=(
                "Apontar para o expander 'Justificativa das Distribuições e Calibração dos Parâmetros' na Seção 2 e para os "
                "histogramas inferiores de G1 (dados simulados), mostrando como a distribuição simulada replica a forma e a dispersão dos dados reais superiores."
            ),
            fala_30_segundos=(
                "Como os tempos reais exibiram suporte positivo e assimetria multiplicativa, adotamos a distribuição Log-normal. "
                "Os dados reais forneceram a calibração direta na escala logarítmica: ajustamos μ_log = 2,97 e σ_log = 0,85 para sem bot "
                "(mediana de 19,5h vs. 18,9h real) e μ_log = 2,64 e σ_log = 0,98 para com bot (mediana de 14,0h vs. 13,6h real). "
                "Para as simulações de Erro Tipo I sob H₀ (Q1 e Q3), agrupamos todos os 60 PRs reais em um baseline pooled com "
                "μ_log = 2,80 e σ_log = 0,92, garantindo que ambos os grupos venham da mesma população idêntica com semente 42."
            ),
            fala_variante_30_segundos=(
                "A distribuição Normal geraria valores de tempo negativos com probabilidade substancial diante de desvios padrões "
                "tão altos (23h de DP para média de 27h), o que é fisicamente impossível no mundo real. Além disso, a curva Normal "
                "é perfeitamente simétrica e não reproduz os atrasos pontuais e outliers severos que observamos nos Pull Requests do GitHub."
            ),
            pontos_chave_argicao=(
                "Escolha teórica: Distribuição Log-normal LN(μ_log, σ_log), padrão na literatura para tempos de processo (lead time).",
                "Calibração empírica sem_bot: μ_log = 2,9704, σ_log = 0,8500 (mediana simulada 19,50h; real 18,90h).",
                "Calibração empírica com_bot: μ_log = 2,6391, σ_log = 0,9800 (mediana simulada 14,00h; real 13,60h).",
                "População pooled sob H₀: μ_log = 2,8000, σ_log = 0,9200 (mediana 16,45h, média 25,35h), idêntica para os dois grupos.",
                "Reprodutibilidade estrita: 10.000 repetições de Monte Carlo por condição geradas com semente pseudoaleatória 42.",
            ),
        ),
        PerguntaApresentacaoOral(
            numero=5,
            titulo_curto="Comparação Efetiva dos Dois Testes: Médias vs. Postos",
            pergunta_oficial=(
                "O que cada um dos dois testes compara de fato (médias, postos, proporções...)?"
            ),
            pergunta_variante=(
                "Se o teste t compara médias e o Mann-Whitney compara postos, é possível que eles cheguem a decisões divergentes?"
            ),
            secao_dashboard="Seção 3 (Como os testes funcionam — Gráfico G2 e Tabela Comparativa) e Seção 6",
            onde_apontar_no_dashboard=(
                "Apontar para os dois painéis do Gráfico G2 (Welch à esquerda medindo desvios em unidades de t, e Mann-Whitney à "
                "direita operando sobre a estatística Z da soma de postos U) e para as colunas da Tabela Comparativa na Seção 3 e Seção 6."
            ),
            fala_30_segundos=(
                "O teste t de Welch compara médias aritméticas ponderadas: ele avalia se a diferença entre as médias amostrais "
                "dos dois grupos é significativamente diferente de zero, corrigindo os graus de liberdade para acomodar variâncias desiguais. "
                "Já o teste U de Mann-Whitney é um teste não-paramétrico baseado em postos (ranks): ele junta todas as 60 observações, "
                "ordena em ordem crescente de 1 a 60 e compara a soma dos postos atribuídos a cada grupo, testando a dominância estocástica, "
                "ou seja, se a probabilidade de um PR com bot ser mergeado antes de um sem bot é igual a 50%."
            ),
            fala_variante_30_segundos=(
                "Sim, com certeza. Por operar sobre as grandezas lineares elevadas ao quadrado na variância, o teste t de Welch é "
                "extremamente vulnerável a um único outlier extremo: se um PR levar 500 horas, a média dispara e a variância infla, "
                "destruindo o teste. Já o Mann-Whitney converte 500 horas no posto 60, preservando a ordenação relativa dos outros "
                "29 PRs sem distorcer o resultado."
            ),
            pontos_chave_argicao=(
                "Teste t de Welch: Paramétrico; compara médias populacionais (H₀: μ_sem = μ_com); estatística t com gl de Satterthwaite.",
                "Teste U de Mann-Whitney: Não-paramétrico; compara postos conjuntos (H₀: P(X_com > Y_sem) = 0,50 / dominância estocástica).",
                "Sensibilidade a escalas: Welch depende de valores métricos e escala linear; Mann-Whitney depende exclusivamente de ordenação ordinal.",
                "Impacto de assimetria e outliers: Welch perde poder porque s² infla quadraticamente; Mann-Whitney é invariante a transformações monótonas.",
            ),
        ),
    ]


# ----------------------------------------------------------------------------
# Perguntas 6 a 10 (Issue #60)
# ----------------------------------------------------------------------------
def obter_perguntas_6_a_10() -> List[PerguntaApresentacaoOral]:
    """Retorna a lista estruturada das Perguntas 6 a 10 para a apresentação oral (Issue #60)."""
    return [
        PerguntaApresentacaoOral(
            numero=6,
            titulo_curto="Distribuição sob H₀ e Região de Rejeição (G2)",
            pergunta_oficial=(
                "No G2: o que é a distribuição da estatística sob H₀, e por que a região de rejeição fica onde fica?"
            ),
            pergunta_variante=(
                "Por que a região de rejeição é dividida em duas caudas e o que define a fronteira crítica?"
            ),
            secao_dashboard="Seção 3 (Como os testes funcionam — Gráfico G2)",
            onde_apontar_no_dashboard=(
                "Apontar para o Gráfico G2 (curva cinza da distribuição teórica sob H₀), "
                "para as regiões vermelhas sombreadas nas duas extremidades (caudas de 2,5% à esquerda e à direita) "
                "e para as linhas verticais tracejadas de corte crítico (t = ±2,01 no painel esquerdo e z = ±1,96 no painel direito)."
            ),
            fala_30_segundos=(
                "A distribuição da estatística sob H₀ representa todos os valores que a estatística de teste "
                "assumiria por puro acaso se a hipótese nula fosse verdadeira, isto é, se os bots não alterassem o tempo de merge. "
                "No painel esquerdo temos a distribuição t de Student com 50,6 graus de liberdade e no direito a Normal padrão Z. "
                "A região de rejeição fica nas duas caudas mais extremas porque nosso teste é bicaudal com α = 5%, "
                "alocando 2,5% da probabilidade em cada lado: observar uma estatística tão distante do centro sob H₀ "
                "é tão improvável (menos de 5% de chance) que nos leva a rejeitar a hipótese de igualdade."
            ),
            fala_variante_30_segundos=(
                "Como a nossa pergunta investiga se os bots aumentam OU diminuem o tempo de merge (teste bicaudal), "
                "o risco de falso positivo de 5% é repartido igualmente: 2,5% na cauda esquerda (efeito de aceleração) "
                "e 2,5% na cauda direita (efeito de atraso). Os limites críticos (t = ±2,01 e z = ±1,96) delimitam "
                "exatamente o ponto a partir do qual a probabilidade acumulada sob H₀ torna-se inferior a 5%."
            ),
            pontos_chave_argicao=(
                "Conceito de distribuição nula: Modelo probabilístico da estatística sob H₀ (sem efeito de tratamento).",
                "Painel esquerdo (Welch): t de Student com gl ≈ 50,61 (Welch-Satterthwaite); limites críticos t = ±2,0085.",
                "Painel direito (Mann-Whitney): Distribuição Normal padrão Z (μ = 0, σ = 1); limites críticos z = ±1,95996.",
                "Posição da região de rejeição: Fica nos extremos (2,5% em cada cauda) porque discrepâncias extremas em qualquer sentido contradizem H₀.",
            ),
        ),
        PerguntaApresentacaoOral(
            numero=7,
            titulo_curto="Significado e Equívocos Conceituais do p-valor no Exemplo (G2)",
            pergunta_oficial=(
                "O que significa o p-valor do exemplo mostrado no G2? E o que ele não significa?"
            ),
            pergunta_variante=(
                "Se o p-valor do teste for maior que 0,05, isso prova que H₀ é verdadeira?"
            ),
            secao_dashboard="Seção 3 (Como os testes funcionam — Gráfico G2 e Tabela S01)",
            onde_apontar_no_dashboard=(
                "Apontar para a linha vertical pontilhada (azul/laranja) indicando a estatística observada na amostra "
                "no Gráfico G2 e para a área sombreada nas caudas correspondente ao p-valor (p = 0,5626 para Welch "
                "e p = 0,1315 para Mann-Whitney)."
            ),
            fala_30_segundos=(
                "O p-valor do exemplo é a probabilidade de sortear uma amostra com estatística tão ou mais extrema "
                "que a observada, assumindo que a hipótese nula H₀ seja verdadeira. No G2, ele é a área sob a curva "
                "além da linha da amostra: 56,26% em Welch e 13,15% em Mann-Whitney. "
                "O que ele NÃO significa: NÃO é a probabilidade de H₀ ser verdadeira, NÃO é a chance de estarmos errados "
                "e NÃO mede o tamanho do efeito ou sua importância prática. "
                "Além disso, obter p maior que 0,05 jamais 'prova' que H₀ é verdadeira: apenas indica que os dados não "
                "forneceram evidência suficiente para rejeitá-la com o tamanho da amostra."
            ),
            fala_variante_30_segundos=(
                "Definitivamente não. Na inferência estatística, ausência de evidência não é evidência de ausência. "
                "Um p-valor maior que 0,05 apenas indica que os dados são estatisticamente compatíveis com H₀ diante "
                "da alta dispersão, o que frequentemente ocorre quando a amostra é moderada (n = 30) e o teste não tem "
                "poder estatístico suficiente para detectar a diferença existente (um Erro Tipo II)."
            ),
            pontos_chave_argicao=(
                "Definição correta do p-valor: P(estatística tão ou mais extrema que a observada | H₀ verdadeira).",
                "Valores observados no exemplo (semente 42): Welch t = -0,5828 (p = 0,5626); Mann-Whitney U = 347,5 (z = -1,5154, p = 0,1315).",
                "Três erros conceituais comuns: (1) Tratar p como P(H₀); (2) Confundir p alto com prova de H₀; (3) Confundir significância com magnitude de efeito.",
                "Posição em relação à região crítica: Ambos os p-valores são maiores que 0,05 (caem fora da região vermelha), resultando em não rejeição de H₀.",
            ),
        ),
        PerguntaApresentacaoOral(
            numero=8,
            titulo_curto="Erro Tipo I vs. Erro Tipo II e Gravidade no Cenário",
            pergunta_oficial=(
                "No cenário de vocês, o que seria um erro tipo I e um erro tipo II? Qual dos dois seria mais grave?"
            ),
            pergunta_variante=(
                "Qual é o custo prático de cada erro para uma equipe de Engenharia de Software?"
            ),
            secao_dashboard="Seção 1 (Cenário), Seção 4 (G3 — Erro tipo I) e Seção 5 (G4 — Poder)",
            onde_apontar_no_dashboard=(
                "Apontar para a pergunta de pesquisa na Seção 1, para o teto de 5% de falsos positivos no G3 "
                "(Erro Tipo I) e para o complemento do poder no G4 (onde 100% menos Poder é a taxa de Erro Tipo II β)."
            ),
            fala_30_segundos=(
                "No nosso cenário, o Erro Tipo I seria concluir falsamente que os bots alteram o tempo de merge "
                "quando na verdade não há efeito, fazendo a equipe desperdiçar tempo e dinheiro mantendo automações inúteis. "
                "O Erro Tipo II seria concluir que os bots não fazem diferença quando na verdade eles reduzem o tempo de integração, "
                "descartando uma automação que aceleraria o fluxo. "
                "Consideramos o Erro Tipo II mais grave no contexto de software: o custo de manter bots de CI hoje é irrisório "
                "(GitHub Actions e linters são baratos), enquanto perder a chance de reduzir o lead time dos desenvolvedores em "
                "20% a 30% impõe um custo de oportunidade contínuo e cumulativo muito mais pesado para a empresa."
            ),
            fala_variante_30_segundos=(
                "Em termos operacionais: errar pelo Tipo I custa poucas horas de configuração de scripts e alguns dólares de computação em nuvem; "
                "já errar pelo Tipo II custa centenas de horas de engenheiros bloqueados aguardando revisões manuais por semanas a fio. "
                "Por isso, para a organização, falhar em adotar uma melhoria real de produtividade acarreta prejuízo financeiro e atraso crônico de entregas."
            ),
            pontos_chave_argicao=(
                "Erro Tipo I (α = 5%): Falso positivo. Rejeitar H₀ quando H₀ é verdadeira (adotar bot sem benefício real).",
                "Erro Tipo II (β = 1 - Poder): Falso negativo. Não rejeitar H₀ quando H₁ é verdadeira (descartar bot que acelerava o processo).",
                "Justificativa de gravidade: O custo de oportunidade e desperdício de tempo humano (Erro Tipo II) supera amplamente o custo de infraestrutura de CI/CD (Erro Tipo I).",
                "Balanço: Fixa-se α em 5% no G3 e busca-se maximizar o poder estatístico (minimizar β) no G4.",
            ),
        ),
        PerguntaApresentacaoOral(
            numero=9,
            titulo_curto="Comportamento de Erro Tipo I em G3: Liberal vs. Conservador",
            pergunta_oficial=(
                "No G3, algum teste se afastou de 5%? Ele ficou liberal ou conservador, e por quê?"
            ),
            pergunta_variante=(
                "Por que os outliers tornaram o teste de Welch conservador em vez de torná-lo liberal?"
            ),
            secao_dashboard="Seção 4 (Erro tipo I — Gráfico G3 e Tabela Consolidada)",
            onde_apontar_no_dashboard=(
                "Apontar para o Gráfico G3, mostrando que todas as barras azuis do teste t de Welch "
                "estão abaixo da linha vermelha de 5% (3,93% na base, 3,28% com outliers e 2,90% com amostra pequena), "
                "enquanto as barras laranjas de Mann-Whitney permanecem rigorosamente na faixa sombreada de Bradley (4,58%, 4,52% e 4,33%)."
            ),
            fala_30_segundos=(
                "Sim, o teste t de Welch afastou-se consideravelmente dos 5%, apresentando comportamento estritamente "
                "conservador em todos os cenários simulados: registrou 3,93% na base, 3,28% com outliers e 2,90% com "
                "amostra pequena de n = 10, rejeitando H₀ consideravelmente menos do que o nível nominal esperado. "
                "O teste de Mann-Whitney, em contraste, foi exemplar, mantendo-se entre 4,33% e 4,58%, dentro da margem "
                "estrita de Bradley. "
                "O teste de Welch ficou conservador porque a assimetria lognormal e os outliers entram elevados ao quadrado "
                "na variância amostral de ambos os grupos sob H₀, inflando o erro padrão no denominador de t e comprimindo "
                "a estatística, o que eleva os p-valores e freia falsos positivos às custas de perda de sensibilidade."
            ),
            fala_variante_30_segundos=(
                "Quando a contaminação por outliers ocorre sob H₀ em ambos os grupos comparados, a diferença entre as médias "
                "amostrais no numerador permanece próxima de zero, mas a variância combinada no denominador é drasticamente inflada. "
                "Como o denominador cresce quadraticamente com os valores extremos, a razão t diminui em módulo, tornando muito "
                "raro atingir a região crítica de ±2,01 — gerando o padrão conservador (taxa bem abaixo de 5%)."
            ),
            pontos_chave_argicao=(
                "Mann-Whitney: Taxa empírica rigorosamente calibrada (4,58% base, 4,52% outliers, 4,33% n=10); dentro do critério de robustez de Bradley [4,5%, 5,5%].",
                "Welch: Sistematicamente conservador (3,93% base, 3,28% outliers, 2,90% n=10); maior desvio ocorre com n=10 (-2,10 p.p. de defasagem).",
                "Nenhum teste foi liberal: Nenhum dos dois testes inflou a taxa de falsos positivos acima de 5%.",
                "Mecanismo teórico: Variância s² no denominador de t cresce quadraticamente com a cauda lognormal, comprimindo a estatística |t|.",
            ),
        ),
        PerguntaApresentacaoOral(
            numero=10,
            titulo_curto="Poder Estatístico em G4 e Evolução da Vantagem com o Efeito",
            pergunta_oficial=(
                "No G4, qual teste tem mais poder? A diferença entre eles muda conforme o tamanho do efeito?"
            ),
            pergunta_variante=(
                "Existe algum cenário em que o teste t de Welch supere o teste de Mann-Whitney em poder?"
            ),
            secao_dashboard="Seção 5 (Poder — Gráfico G4, Painel Esquerdo e Painel Direito)",
            onde_apontar_no_dashboard=(
                "Apontar para o painel esquerdo do G4 (mostrando a curva contínua laranja de Mann-Whitney "
                "consistentemente acima da azul de Welch), destacar o ponto de δ = 50% (79,08% vs. 64,20%) "
                "e apontar para o painel direito mostrando o gráfico de diferença de poder abrindo até +14,88 p.p. "
                "no cenário base e atingindo quase +40 p.p. sob outliers."
            ),
            fala_30_segundos=(
                "No gráfico G4, o teste U de Mann-Whitney tem expressivamente mais poder em todas as condições "
                "realistas de Engenharia de Software. A diferença a seu favor cresce à medida que o tamanho do efeito aumenta: "
                "em efeito zero ambos partem próximos de 4% a 5%, mas em 30% de redução a vantagem de Mann-Whitney é de "
                "+7,10 pontos percentuais (29,59% vs. 22,49%), atingindo o ápice em 50% de redução com +14,88 pontos "
                "percentuais de vantagem (79,08% contra 64,20%). "
                "Sob violação por outliers severos, a vantagem de Mann-Whitney dispara para quase 40 pontos percentuais "
                "(62,30% vs. 22,62%), pois postos ordenados não são arruinados pela cauda longa. "
                "A vantagem só muda de lado quando os dados são perfeitamente normais e simétricos sem outliers, "
                "onde Welch lidera por 2,68 p.p. devido à sua eficiência paramétrica ideal."
            ),
            fala_variante_30_segundos=(
                "Sim, o teste t de Welch supera Mann-Whitney apenas na condição de Controle Teórico Gaussiano "
                "(Normal simétrica sem outliers), visível na curva azul tracejada no painel direito do G4. "
                "Nesse caso específico, em δ = 30%, Welch atinge 75,80% contra 73,12% de Mann-Whitney (vantagem de 2,68 p.p.), "
                "o que corresponde exatamente à Eficiência Assintótica Relativa (ARE = 3/π ≈ 95,5%) dos postos sob normalidade perfeita."
            ),
            pontos_chave_argicao=(
                "Líder nas condições do cenário: Teste U de Mann-Whitney é superior em todas as distribuições lognormais com lead time de PRs.",
                "Evolução da vantagem na base: 0% (+0,65 p.p.), 10% (+1,99 p.p.), 20% (+4,16 p.p.), 30% (+7,10 p.p.), 40% (+14,20 p.p.), 50% (+14,88 p.p.).",
                "Sob Outliers (Q3 em δ=50%): Welch sofre colapso para 22,62%, enquanto Mann-Whitney sustenta 62,30% (+39,68 p.p. de vantagem).",
                "Quando muda de lado: Exclusivamente sob distribuição Normal simétrica sem outliers (Welch atinge 75,80% vs. 73,12% de Mann-Whitney em δ=30%).",
            ),
        ),
    ]


# ----------------------------------------------------------------------------
# Perguntas 11 a 15 (Issue #62)
# ----------------------------------------------------------------------------
def obter_perguntas_11_a_15() -> List[PerguntaApresentacaoOral]:
    """Retorna a lista estruturada das Perguntas 11 a 15 para a apresentação oral (Issue #62)."""
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
                "(0,2641 vs. 0,1715) e a redução nas medianas (18,90h vs. 13,60h)."
            ),
            fala_30_segundos=(
                "Sim, nos dados reais minerados do FastAPI (n = 30 por grupo) ambos os testes "
                "chegaram à mesma decisão formal: não rejeitaram H₀ ao nível α = 0,05 (Welch t = -1,128, "
                "p = 0,2641; Mann-Whitney U = 357,0, p = 0,1715). O teste de Mann-Whitney foi sensivelmente "
                "mais sensível, com p-valor menor (0,1715 vs. 0,2641), pois os postos neutralizam o peso "
                "dos outliers de 88h e 105,5h que inflam o desvio de Welch. "
                "E sim, o efeito tem relevância prática: a mediana caiu 28,0% (de 18,90h para 13,60h, "
                "economizando 5,3 horas por PR). O não-rejeite decorre do tamanho amostral moderado (n = 30), "
                "cujo poder é de apenas 28% a 48% conforme as curvas do G4."
            ),
            fala_variante_30_segundos=None,
            pontos_chave_argicao=(
                "Convergência formal: Ambos não rejeitam H₀ a α = 0,05 (p_Welch = 0,2641; p_MW = 0,1715).",
                "Sensibilidade relativa: Mann-Whitney obteve p-valor menor por limitar os outliers aos postos extremos.",
                "Importância prática: Redução de 5,30h na mediana (-28,0%) e 6,47h na média (-23,6%), agilizando o ciclo de entrega.",
                "Limitação de poder com n=30: G4 comprova que o poder era inferior a 50%, gerando não rejeição por subdimensionamento amostral.",
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
                "Normal Simétrico) na zona inferior do painel direito do Gráfico G4."
            ),
            fala_30_segundos=(
                "Recomendamos o teste U de Mann-Whitney para avaliar o tempo de merge de Pull "
                "Requests e métricas de engenharia de software assimétricas, pois ele mantém o "
                "Erro Tipo I calibrado perto de 5% (4,58%) e entrega até +39,68 pontos percentuais "
                "a mais de poder que Welch quando há outliers. "
                "Mudaríamos a recomendação para o teste t de Welch se a métrica seguisse uma "
                "distribuição Normal simétrica sem outliers — situação mostrada na curva azul do "
                "painel direito do G4, onde Welch supera Mann-Whitney (75,80% vs. 73,12% em δ = 30% "
                "pela eficiência assintótica de 95,5% dos postos) — ou se a decisão exigisse "
                "estritamente a média em grande amostra. "
                "A principal limitação do estudo é ser observacional em um único repositório "
                "(FastAPI, n=30), sujeito a fatores confundidores como tamanho do PR e complexidade do código."
            ),
            fala_variante_30_segundos=None,
            pontos_chave_argicao=(
                "Recomendação principal: Teste U de Mann-Whitney (robusto no Erro Tipo I em G3 e dominante em poder nas curvas log-normais de G4).",
                "Quando mudar para t de Welch: (1) Distribuição aproximadamente simétrica/Normal e livre de outliers (onde Welch tem vantagem de ~2,7 p.p. em δ=30% devido à ARE = 3/π ≈ 95,5%), ou (2) análise sobre dados log-transformados validados sem caudas extremas.",
                "Principal limitação do estudo: Coleta real observacional (não-randomizada) restrita a um único projeto (tiangolo/fastapi) com n=30 por grupo, sem controle multivariado para linhas alteradas (LOC), número de revisores humanos ou fuso horário.",
            ),
        ),
    ]


def obter_todas_perguntas() -> List[PerguntaApresentacaoOral]:
    """Retorna todas as 15 perguntas da apresentação oral (1 a 15) em ordem numérica."""
    return obter_perguntas_1_a_5() + obter_perguntas_6_a_10() + obter_perguntas_11_a_15()


# ----------------------------------------------------------------------------
# Resumos tabulares e geradores de Markdown
# ----------------------------------------------------------------------------
def construir_tabela_resumo_perguntas_1_a_5() -> pd.DataFrame:
    """Retorna um DataFrame resumindo as Perguntas 1 a 5, onde apontar e a resposta-síntese."""
    perguntas = obter_perguntas_1_a_5()
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


def construir_tabela_resumo_perguntas_6_a_10() -> pd.DataFrame:
    """Retorna um DataFrame resumindo as Perguntas 6 a 10, onde apontar e a resposta-síntese."""
    perguntas = obter_perguntas_6_a_10()
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


def gerar_roteiro_markdown_perguntas_1_a_5() -> str:
    """Gera o relatório completo em Markdown das Perguntas 1 a 5 com fundamentação técnica."""
    perguntas = obter_perguntas_1_a_5()

    linhas: List[str] = [
        "# Roteiro Individual de Preparação da Apresentação Oral — Perguntas 1 a 5 (Issue #58)",
        "",
        "**Responsável:** Tiago Boaventura Amaral  ",
        "**Tempo estimado por resposta:** ~30 segundos (curta, direta e apoiada visualmente no Dashboard).  ",
        "**Objetivo:** Demonstrar domínio sobre o cenário de pesquisa, direcionalidade do teste, processo de amostragem no GitHub, calibração log-normal na simulação e a distinção conceitual entre testes de médias e testes de postos.",
        "",
    ]
    for p in perguntas:
        linhas.append(f"## Pergunta {p.numero} — {p.titulo_curto}")
        linhas.append(f"- **Enunciado Oficial:** *\"{p.pergunta_oficial}\"*")
        linhas.append(f"- **Seção do Dashboard:** `{p.secao_dashboard}`")
        linhas.append(f"- **Onde apontar na tela:** {p.onde_apontar_no_dashboard}")
        linhas.append(f"- **Fala Direta (30s):**\n  > \"{p.fala_30_segundos}\"")
        if p.pergunta_variante and p.fala_variante_30_segundos:
            linhas.append(f"- **Pergunta Variante da Banca:** *\"{p.pergunta_variante}\"*")
            linhas.append(f"- **Fala Direta para Variante (30s):**\n  > \"{p.fala_variante_30_segundos}\"")
        linhas.append("- **Pontos-Chave e Números para Arguição:**")
        for pt in p.pontos_chave_argicao:
            linhas.append(f"  - {pt}")
        linhas.append("")

    return "\n".join(linhas)


def gerar_roteiro_markdown_perguntas_6_a_10() -> str:
    """Gera o relatório completo em Markdown das Perguntas 6 a 10 com fundamentação técnica."""
    perguntas = obter_perguntas_6_a_10()

    linhas: List[str] = [
        "# Roteiro Individual de Preparação da Apresentação Oral — Perguntas 6 a 10 (Issue #60)",
        "",
        "**Responsável:** Tiago Boaventura Amaral  ",
        "**Tempo estimado por resposta:** ~30 segundos (curta, direta e apoiada visualmente no Dashboard).  ",
        "**Objetivo:** Demonstrar domínio dos conceitos de distribuição nula, região de rejeição, p-valor, erros estatísticos e interpretação comparativa de G3 e G4.",
        "",
    ]
    for p in perguntas:
        linhas.append(f"## Pergunta {p.numero} — {p.titulo_curto}")
        linhas.append(f"- **Enunciado Oficial:** *\"{p.pergunta_oficial}\"*")
        linhas.append(f"- **Seção do Dashboard:** `{p.secao_dashboard}`")
        linhas.append(f"- **Onde apontar na tela:** {p.onde_apontar_no_dashboard}")
        linhas.append(f"- **Fala Direta (30s):**\n  > \"{p.fala_30_segundos}\"")
        if p.pergunta_variante and p.fala_variante_30_segundos:
            linhas.append(f"- **Pergunta Variante da Banca:** *\"{p.pergunta_variante}\"*")
            linhas.append(f"- **Fala Direta para Variante (30s):**\n  > \"{p.fala_variante_30_segundos}\"")
        linhas.append("- **Pontos-Chave e Números para Arguição:**")
        for pt in p.pontos_chave_argicao:
            linhas.append(f"  - {pt}")
        linhas.append("")

    return "\n".join(linhas)


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


def gerar_roteiro_markdown_completo() -> str:
    """Gera o consolidado de todas as 15 perguntas disponíveis (1 a 15)."""
    return (
        gerar_roteiro_markdown_perguntas_1_a_5()
        + "\n\n"
        + "=" * 80
        + "\n\n"
        + gerar_roteiro_markdown_perguntas_6_a_10()
        + "\n\n"
        + "=" * 80
        + "\n\n"
        + gerar_roteiro_markdown_perguntas_11_a_15()
    )


# ----------------------------------------------------------------------------
# Execução direta como script
# ----------------------------------------------------------------------------
if __name__ == "__main__":  # pragma: no cover
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print(gerar_roteiro_markdown_completo())
