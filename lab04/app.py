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
from lab04.src.grafico_g1 import carregar_reais, carregar_simulados, gerar_g1

LINK_REPOSITORIO = "<preencher>"  # link do repositório / GitHub Projects do grupo
LINK_DASHBOARD = "<preencher>"  # link do dashboard publicado, se houver

st.set_page_config(page_title="LAB04 - Testes de Hipótese", layout="wide")

st.title("LAB04 - Testes de Hipótese por Dentro")
st.caption(f"Repositório / GitHub Projects: {LINK_REPOSITORIO} | Dashboard: {LINK_DASHBOARD}")

# ---------------------------------------------------------------- 1. Cenário
st.header("1. Cenário")
st.markdown(CENARIO.texto_dashboard_cenario)

# ---------------------------------------------------------------- 2. Os dados
st.header("2. Os dados")
reais = carregar_reais()
simulados = carregar_simulados()
st.pyplot(gerar_g1(reais, simulados))
st.markdown(
    "Nos dados reais, a mediana do tempo até o merge é 18,9 h sem bot e 13,6 h com bot, "
    "com assimetria positiva (1,79 e 1,91) e cauda longa à direita, com outliers acima de 100 h. "
    "Os dados simulados (n = 30 por grupo) seguem o mesmo padrão de assimetria à direita, com medianas "
    "de 21,2 h e 16,5 h, embora no grupo sem bot a cauda simulada seja mais curta "
    "(DP de 14,0 h contra 24,2 h nos reais). Os parâmetros log-normais foram ajustados às medianas e à "
    "dispersão logarítmica da amostra real, e as diferenças restantes decorrem da variação amostral com n = 30."
)

# ------------------------------------------- 3. Como os testes funcionam (G2)
st.header("3. Como os testes funcionam")
st.info("G2 ainda não implementado.")

# ------------------------------------------------------- 4. Erro tipo I (G3)
st.header("4. Erro tipo I")
st.info("G3 será implementado na Sprint 2.")

# ------------------------------------------------------------- 5. Poder (G4)
st.header("5. Poder")
st.info("G4 será implementado na Sprint 2.")

# ------------------------------------------------------------ 6. Dados reais
st.header("6. Dados reais")
st.info("Tabela com estatística, p-valor, tamanho do efeito e conclusão de cada teste: a implementar.")

# ------------------------------------------------------------- 7. Conclusão
st.header("7. Conclusão")
st.info("A preencher ao final do laboratório.")