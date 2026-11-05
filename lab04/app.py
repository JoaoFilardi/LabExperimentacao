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
st.info(
    "Gráfico G3 (taxa empírica de Erro Tipo I em 10.000 simulações sob H₀ nas condições base e "
    "com violação de pressupostos — Q1 e Q3) será integrado na Sprint 2 (LAB04S02)."
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
