"""Dashboard do LAB04 - Testes de hipótese por dentro.

Como abrir (na pasta que contém a pasta lab04):
    python -m streamlit run lab04/app.py

Seções na ordem exigida pelo enunciado:
    1. Cenário  2. Os dados (G1)  3. Como os testes funcionam (G2)
    4. Erro tipo I (G3)  5. Poder (G4)  6. Dados reais  7. Conclusão
"""
import sys
from pathlib import Path

# garante que o pacote lab04 seja encontrado ao rodar com streamlit
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from lab04.src.cenario import CENARIO
from lab04.src.grafico_g1 import (
    carregar_reais,
    carregar_simulados,
    gerar_g1,
    texto_interpretativo,
)
from lab04.src.grafico_g2 import gerar_g2, texto_interpretativo_g2
from lab04.src.simulacao_q1 import (
    carregar_ou_executar_q1,
    gerar_texto_interpretativo_q1,
)
from lab04.src.testes_estatisticos import (
    aplicar_ambos_testes,
    comparacao_para_dataframe,
)

LINK_REPOSITORIO = "https://github.com/JoaoFilardi/LabExperimentacao"
LINK_PROJECTS = "https://github.com/JoaoFilardi/LabExperimentacao/projects"

st.set_page_config(page_title="LAB04 - Testes de Hipótese", layout="wide")

st.title("LAB04 - Testes de Hipótese por Dentro: Cenário, Simulação e Visualização")
st.markdown(
    f"**Repositório:** [{LINK_REPOSITORIO}]({LINK_REPOSITORIO}) | "
    f"**GitHub Projects:** [{LINK_PROJECTS}]({LINK_PROJECTS}) | "
    f"**Par selecionado:** {CENARIO.par_id} ({CENARIO.nome_par})"
)

# ---------------------------------------------------------------- 1. Cenário
st.header("1. Cenário")
st.markdown(CENARIO.texto_dashboard_cenario)
with st.expander("Ver detalhes formais das hipóteses e previsão pré-simulação"):
    st.markdown(f"- **Pergunta de pesquisa:** {CENARIO.pergunta_pesquisa}")
    st.markdown(f"- **H₀ (conceitual):** {CENARIO.h0_conceitual}")
    st.markdown(f"- **H₁ (conceitual):** {CENARIO.h1_conceitual}")
    st.markdown(f"- **H₀ / H₁ (t de Welch):** `{CENARIO.h0_welch}` vs. `{CENARIO.h1_welch}`")
    st.markdown(
        f"- **H₀ / H₁ (U de Mann-Whitney):** `{CENARIO.h0_mann_whitney}` vs. `{CENARIO.h1_mann_whitney}`"
    )
    st.markdown(
        f"- **Direção e significância:** Teste {CENARIO.tipo_teste} com α = {CENARIO.alpha:.2f} "
        f"(confiança de {CENARIO.nivel_confianca * 100:.0f}%)."
    )
    st.markdown(f"- **Previsão inicial (antes de simular):** {CENARIO.justificativa_previsao}")

# ---------------------------------------------------------------- 2. Os dados
st.header("2. Os dados")
reais = carregar_reais()
simulados = carregar_simulados(semente=42)
st.pyplot(gerar_g1(reais, simulados))
st.markdown(texto_interpretativo(reais, simulados))

# ------------------------------------------- 3. Como os testes funcionam (G2)
st.header("3. Como os testes funcionam")
st.pyplot(gerar_g2(simulados=simulados, semente=42, alpha=CENARIO.alpha))
st.markdown(texto_interpretativo_g2(simulados=simulados, semente=42, alpha=CENARIO.alpha))

comp_simulados = aplicar_ambos_testes(
    simulados,
    alpha=CENARIO.alpha,
    alternativa=CENARIO.tipo_teste,
    origem_dados="Dados Simulados S01 (semente = 42)",
    semente=42,
)
st.subheader("Resultados e interpretação nos dados simulados (S01 — semente = 42)")
st.dataframe(comparacao_para_dataframe(comp_simulados), use_container_width=True)
st.markdown(f"**Decisão e resumo:** {comp_simulados.resumo_comparativo}")
st.markdown(f"**Diferenças observadas e razões estatísticas:** {comp_simulados.explicacao_diferencas}")

# ------------------------------------------------------- 4. Erro tipo I (G3)
st.header("4. Erro tipo I")
res_q1 = carregar_ou_executar_q1(semente=42, n_simulacoes=10_000)

col_q1_a, col_q1_b, col_q1_c = st.columns(3)
with col_q1_a:
    st.metric(
        label="Nível Teórico Nominal (α)",
        value="5,00%",
        help="Taxa teórica esperada sob H₀ verdadeira",
    )
with col_q1_b:
    st.metric(
        label=f"Taxa Empírica — {res_q1.metricas_welch.nome_teste}",
        value=f"{res_q1.metricas_welch.taxa_erro_tipo_1 * 100:.2f}%",
        delta=f"{res_q1.metricas_welch.diferenca_nominal * 100:+.2f}%",
        delta_color="off",
        help="393 rejeições em 10.000 simulações (comportamento conservador)",
    )
with col_q1_c:
    st.metric(
        label=f"Taxa Empírica — {res_q1.metricas_mann_whitney.nome_teste}",
        value=f"{res_q1.metricas_mann_whitney.taxa_erro_tipo_1 * 100:.2f}%",
        delta=f"{res_q1.metricas_mann_whitney.diferenca_nominal * 100:+.2f}%",
        delta_color="off",
        help="458 rejeições em 10.000 simulações (comportamento nominal)",
    )

st.dataframe(
    res_q1.tabela_resumo[
        [
            "teste",
            "tipo_abordagem",
            "n_simulacoes",
            "n_rejeicoes_h0",
            "taxa_erro_tipo_1_pct",
            "alpha_nominal_pct",
            "diferenca_nominal_pct",
            "ic_95_formatado",
            "comportamento",
            "bradley_estrito",
        ]
    ],
    use_container_width=True,
)
st.markdown(gerar_texto_interpretativo_q1(res_q1))

with st.expander("Ver detalhes metodológicos das 10.000 simulações sob H₀ (Questão Q1)"):
    st.markdown(
        f"- **Configuração sob H₀:** Ambos os grupos gerados sob distribuição Log-normal "
        f"idêntica baseada no agrupamento pooled dos dados reais "
        f"(μ_log = 2,8053, σ_log = 0,9254, n = 30 por grupo), garantindo efeito nulo real."
    )
    st.markdown(
        f"- **Reprodutibilidade:** Semente fixa = {res_q1.semente} via `numpy.random.default_rng({res_q1.semente})`."
    )
    st.markdown(
        f"- **Aderência à distribuição Uniforme U(0, 1) dos p-valores:**\n"
        f"  - Teste t de Welch: p-valor KS = `{res_q1.metricas_welch.ks_pvalor_uniforme:.2e}` "
        f"(rejeita a uniformidade devido à distorção causada pela cauda longa).\n"
        f"  - Teste U de Mann-Whitney: p-valor KS = `{res_q1.metricas_mann_whitney.ks_pvalor_uniforme:.4f}` "
        f"(aderente à uniformidade teórica sob H₀)."
    )
    st.markdown(
        f"- **Critério de Robustez de Bradley (1978):** Mann-Whitney atende ao critério estrito "
        f"[4,5% a 5,5%]; Welch atende ao critério liberal [2,5% a 7,5%], situando-se abaixo de 4,5%."
    )

st.info(
    "O Gráfico G3 consolidará visualmente estas taxas empíricas de Erro Tipo I lado a lado com as "
    "situações de violação de pressupostos (Q3)."
)

# ------------------------------------------------------------- 5. Poder (G4)
st.header("5. Poder")
st.info(
    "Gráfico G4 (curvas de poder estatístico × tamanho do efeito para ambos os testes — Q2 e Q3) "
    "será integrado na Sprint 2 (LAB04S02)."
)

# ------------------------------------------------------------ 6. Dados reais
st.header("6. Dados reais")
comp_reais = aplicar_ambos_testes(
    reais,
    alpha=CENARIO.alpha,
    alternativa=CENARIO.tipo_teste,
    origem_dados="Amostra de Dados Reais (tiangolo/fastapi)",
    semente=None,
)
st.dataframe(comparacao_para_dataframe(comp_reais), use_container_width=True)
st.markdown(f"**Conclusão nos dados reais:** {comp_reais.resumo_comparativo}")
st.markdown(f"**Comparação entre os testes na amostra real:** {comp_reais.explicacao_diferencas}")

# ------------------------------------------------------------- 7. Conclusão
st.header("7. Conclusão")
st.markdown(
    "Na Sprint 1 (S01), a aplicação preliminar sobre uma única amostra simulada (n = 30 por grupo, semente = 42) "
    "já evidencia a previsão teórica do grupo: o teste U de Mann-Whitney obteve um p-valor mais de quatro vezes "
    "menor que o teste t de Welch (p = 0,1315 vs. p = 0,5626), pois o t de Welch teve sua média e seu desvio "
    "padrão distorcidos pelo outlier de cauda longa (110,1 h). A recomendação definitiva sobre qual teste adotar "
    "e em que condições a vantagem muda de lado será consolidada na Sprint 2 após as 10.000 repetições de Q1, Q2 e Q3."
)
