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

from lab04.src.apresentacao_oral import (
    avaliar_impacto_alpha_001,
    obter_perguntas_11_a_15,
)
from lab04.src.cenario import CENARIO
from lab04.src.grafico_g1 import (
    carregar_reais,
    carregar_simulados,
    gerar_g1,
    texto_interpretativo,
)
from lab04.src.grafico_g2 import gerar_g2, texto_interpretativo_g2
from lab04.src.grafico_g3 import (
    carregar_ou_simular_dados_g3,
    gerar_g3,
    texto_interpretativo_g3,
)
from lab04.src.grafico_g4 import (
    carregar_ou_simular_dados_g4,
    gerar_g4,
    texto_interpretativo_g4,
)
from lab04.src.simulacao_q1 import (
    carregar_ou_executar_q1,
    gerar_texto_interpretativo_q1,
)
from lab04.src.simulacao_q2 import carregar_ou_executar_q2
from lab04.src.simulacao_q3 import carregar_ou_executar_q3
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
df_g3 = carregar_ou_simular_dados_g3(semente=42, n_simulacoes=10_000)
st.pyplot(gerar_g3(df_dados=df_g3))
st.markdown(texto_interpretativo_g3(df_g3))

st.subheader("Taxas de Erro Tipo I Consolidadas nas Situações Simuladas (10.000 repetições)")
col_g3_1, col_g3_2, col_g3_3 = st.columns(3)
with col_g3_1:
    st.markdown("**Cenário Original (Q1)**\n*Log-normal realista (n=30)*")
    st.metric(
        label=f"{CENARIO.teste_parametrico}",
        value="3,93%",
        delta="-1,07% vs. α=5%",
        delta_color="off",
        help="Comportamento conservador devido à cauda log-normal",
    )
    st.metric(
        label=f"{CENARIO.teste_nao_parametrico}",
        value="4,58%",
        delta="-0,42% vs. α=5%",
        delta_color="off",
        help="Comportamento nominal e robusto sob postos",
    )

with col_g3_2:
    st.markdown("**Violação: Outliers (Q3)**\n*10% contaminação (5x + 50h, n=30)*")
    st.metric(
        label=f"{CENARIO.teste_parametrico}",
        value="3,28%",
        delta="-1,72% vs. α=5%",
        delta_color="off",
        help="Conservadorismo ampliado: variância amostral inflada comprime |t|",
    )
    st.metric(
        label=f"{CENARIO.teste_nao_parametrico}",
        value="4,52%",
        delta="-0,48% vs. α=5%",
        delta_color="off",
        help="Imune a outliers severos: preserva calibração estrita",
    )

with col_g3_3:
    st.markdown("**Violação: Amostra Pequena (Q3)**\n*Log-normal com n=10 por grupo*")
    st.metric(
        label=f"{CENARIO.teste_parametrico}",
        value="2,90%",
        delta="-2,10% vs. α=5%",
        delta_color="off",
        help="Maior desvio observado: falha do Teorema Central do Limite para n=10",
    )
    st.metric(
        label=f"{CENARIO.teste_nao_parametrico}",
        value="4,33%",
        delta="-0,67% vs. α=5%",
        delta_color="off",
        help="Discretização discreta de postos para n=10, ainda próximo de 5%",
    )

# Tabela consolidada com formatação percentual
df_g3_tabela = df_g3.copy()
df_g3_tabela["taxa_empirica_fmt"] = df_g3_tabela["taxa_empirica_pct"].map("{:.2f}%".format)
df_g3_tabela["taxa_teorica_fmt"] = df_g3_tabela["taxa_teorica_pct"].map("{:.1f}%".format)
df_g3_tabela["desvio_nominal_fmt"] = df_g3_tabela["desvio_nominal_pct"].map("{:+.2f}%".format)
df_g3_tabela["ic_95_fmt"] = df_g3_tabela.apply(
    lambda r: f"[{r['ic_inf_pct']:.2f}%, {r['ic_sup_pct']:.2f}%]", axis=1
)

st.dataframe(
    df_g3_tabela[
        [
            "condicao",
            "teste",
            "abordagem",
            "n_rejeicoes",
            "taxa_empirica_fmt",
            "taxa_teorica_fmt",
            "desvio_nominal_fmt",
            "ic_95_fmt",
            "comportamento",
        ]
    ].rename(
        columns={
            "condicao": "Condição Experimental",
            "teste": "Teste Estatístico",
            "abordagem": "Abordagem",
            "n_rejeicoes": "Rejeições H₀ (k)",
            "taxa_empirica_fmt": "Taxa Empírica (%)",
            "taxa_teorica_fmt": "Nível Nominal (α)",
            "desvio_nominal_fmt": "Desvio Frente a α",
            "ic_95_fmt": "IC 95% (Wilson)",
            "comportamento": "Classificação",
        }
    ),
    use_container_width=True,
)

with st.expander("Ver detalhes metodológicos das simulações de Erro Tipo I (Q1 e Q3)"):
    st.markdown(
        f"- **Metodologia de Monte Carlo:** 10.000 iterações independentes por condição "
        f"(`semente = 42`), gerando 60.000 amostras simuladas e aplicando ambos os testes sob H₀ verdadeira."
    )
    st.markdown(
        f"- **Linha de Referência Teórica:** Fixada em α = 0,05 (5,0%). A faixa sombreada no G3 delimita "
        f"o intervalo de robustez estrita de Bradley (1978) [4,5% a 5,5%]."
    )
    st.markdown(
        f"- **Comportamento Liberal vs. Conservador:** Nenhum teste se comportou de forma liberal "
        f"(nenhum inflou falsos positivos acima de 5%). O teste de Mann-Whitney foi consistente e robusto "
        f"em todas as situações, enquanto o teste t de Welch revelou-se sistematicamente conservador."
    )

# ------------------------------------------------------------- 5. Poder (G4)
st.header("5. Poder")
df_poder_g4, df_gauss_g4 = carregar_ou_simular_dados_g4(semente=42, n_simulacoes=10_000)
st.pyplot(gerar_g4(df_poder_largo=df_poder_g4, df_gaussiano=df_gauss_g4))
st.markdown(texto_interpretativo_g4(df_poder_largo=df_poder_g4, df_gaussiano=df_gauss_g4))

res_q3 = carregar_ou_executar_q3(semente=42, n_simulacoes=10_000)
res_q2 = carregar_ou_executar_q2(semente=42, n_simulacoes=10_000)

st.subheader("Poder Estatístico por Tamanho de Efeito: Cenário Original vs. Violações (Q2 e Q3)")
st.dataframe(res_q3.df_poder_largo, use_container_width=True)

with st.expander("Ver diagnóstico de impacto de Q3 e controle Gaussiano (quando a vantagem muda de lado)"):
    st.markdown("**Diagnóstico de impacto das violações de pressupostos (Q3):**")
    st.dataframe(res_q3.df_comparativo_impacto, use_container_width=True)
    st.markdown("**Controle Teórico: Distribuição Normal Simétrica sem Outliers (n = 30):**")
    st.dataframe(res_q2.df_controle_gaussiano, use_container_width=True)

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
    "As simulações de Monte Carlo das Sprints 1 e 2 (Q1, Q2 e Q3, 10.000 repetições por condição, semente = 42) "
    "confirmam integralmente a expectativa teórica registrada pelo grupo antes de simular: sob a assimetria "
    "log-normal e a presença de outliers típicas de tempos de merge de Pull Requests, o **teste U de Mann-Whitney** "
    "é a recomendação oficial, pois mantém a taxa de Erro Tipo I calibrada próxima de 5% (4,58% na base, 4,52% "
    "com outliers e 4,33% com n=10) e alcança poder estatístico amplamente superior ao teste t de Welch "
    "(79,08% vs. 64,20% em δ=50% na base, e 62,30% vs. 22,62% sob outliers severos). "
    "A recomendação só mudaria em favor do teste t de Welch caso os tempos de processo fossem simétricos/normais "
    "e isentos de outliers (ou após transformação logarítmica validada sem contaminação de cauda)."
)

with st.expander("Roteiro de Apoio para a Apresentação Oral — Perguntas 11 a 15 (#62)"):
    for item_p in obter_perguntas_11_a_15():
        st.markdown(f"#### Pergunta {item_p.numero} — {item_p.titulo_curto}")
        st.markdown(f"**Enunciado:** *{item_p.pergunta_oficial}*")
        st.markdown(f"**Onde apontar no Dashboard:** {item_p.onde_apontar_no_dashboard}")
        st.info(f"**Resposta direta (30s):** {item_p.fala_30_segundos}")
        if item_p.pergunta_variante and item_p.fala_variante_30_segundos:
            st.markdown(f"**Variante de arguição (Tamanho amostral):** *{item_p.pergunta_variante}*")
            st.info(f"**Resposta direta p/ variante (30s):** {item_p.fala_variante_30_segundos}")
    st.markdown("**Tabela auxiliar para a Pergunta 12 (comparativo empírico α = 0,05 vs. α = 0,01):**")
    st.dataframe(avaliar_impacto_alpha_001(semente=42, n_simulacoes=10_000), use_container_width=True)
