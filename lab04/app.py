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

from lab04.src.analise_dados_reais import (
    executar_analise_completa_dados_reais,
    gerar_tabela_comparativa_secao6,
)
from lab04.src.apresentacao_oral import (
    avaliar_impacto_alpha_001,
    obter_perguntas_6_a_10,
    obter_perguntas_11_a_15,
)
from lab04.src.cenario import CENARIO
from lab04.src.conclusao_dashboard import (
    obter_expectativa_vs_resultados,
    obter_limitacoes_estudo,
    obter_recomendacao_final,
    obter_resumo_conclusao_markdown,
    obter_tabela_expectativa_vs_resultados,
)
from lab04.src.grafico_g1 import (
    carregar_reais,
    carregar_simulados,
    gerar_g1,
    obter_tabela_comparativa_g1,
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
from lab04.src.simulacao import ParametrosSimulacao
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

col_cen_1, col_cen_2, col_cen_3 = st.columns(3)
with col_cen_1:
    st.subheader("Pergunta de Pesquisa")
    st.info(f"**Pergunta única e objetiva:**\n\n*{CENARIO.pergunta_pesquisa}*")
    st.markdown(
        f"- **Par selecionado:** `{CENARIO.par_id}` ({CENARIO.nome_par})\n"
        f"- **Tipo de teste:** {CENARIO.tipo_teste} (bicaudal / two-sided)\n"
        f"- **Nível de significância:** α = {CENARIO.alpha:.2f} (confiança de {CENARIO.nivel_confianca * 100:.0f}%)"
    )

with col_cen_2:
    st.subheader("Hipóteses Investigadas")
    st.markdown(f"**H₀ (Nula):** {CENARIO.h0_conceitual}")
    st.markdown(f"**H₁ (Alternativa):** {CENARIO.h1_conceitual}")
    st.markdown(
        f"- **t de Welch (médias):** `{CENARIO.h0_welch}` vs. `{CENARIO.h1_welch}`\n"
        f"- **Mann-Whitney (postos):** `{CENARIO.h0_mann_whitney}` vs. `{CENARIO.h1_mann_whitney}`"
    )

with col_cen_3:
    st.subheader("Origem dos Dados Reais")
    st.markdown(
        f"- **Repositório:** `{CENARIO.origem_dados_reais}`\n"
        f"- **Total coletado:** **{CENARIO.n_observacoes_reais_total} Pull Requests** "
        f"({CENARIO.n_observacoes_reais_por_grupo} `com_bot` vs. {CENARIO.n_observacoes_reais_por_grupo} `sem_bot`)\n"
        f"- **Variável resposta:** `{CENARIO.variavel_dependente}`\n"
        f"- **Critério de amostragem:** {CENARIO.criterio_selecao_prs}"
    )

st.subheader("Previsão Inicial do Grupo (Registrada Antes de Simular)")
st.warning(
    f"**Teste com melhor desempenho esperado:** **{CENARIO.teste_esperado_melhor_desempenho}**\n\n"
    f"**Justificativa pré-experimental:** {CENARIO.justificativa_previsao}"
)

# ---------------------------------------------------------------- 2. Os dados
st.header("2. Os dados")
reais = carregar_reais()
simulados = carregar_simulados(semente=42)
st.pyplot(gerar_g1(reais, simulados))
st.markdown(texto_interpretativo(reais, simulados))

st.subheader("Características Descritivas dos Dados Reais e Simulados (Assimetria, Dispersão e Outliers)")
df_tab_g1 = obter_tabela_comparativa_g1(reais, simulados)
st.dataframe(df_tab_g1, use_container_width=True)

with st.expander("Justificativa das Distribuições e Calibração dos Parâmetros da Simulação"):
    st.markdown(
        "### Por que a Distribuição Log-normal?\n"
        "Em Engenharia de Software, tempos de ciclo (como o tempo até o merge de Pull Requests) são grandezas "
        "estritamente positivas ($Y > 0$), contínuas e governadas por fatores multiplicativos, exibindo forte "
        "assimetria à direita (*right-skewness*) e caudas pesadas com presença recorrente de outliers severos "
        "(PRs bloqueados por disputas ou dependências externas). A distribuição normal simétrica falha "
        "em representar esse comportamento, tornando a distribuição Log-normal a escolha teórica mais adequada."
    )
    p_sim = ParametrosSimulacao()
    st.markdown(
        f"### Calibração Rigorosa com Base nos Dados Reais:\n"
        f"- **Grupo Sem Bot (`sem_bot`):** Mediana real de 18,9h → ajustada para $\\mu_{{\\log}} = {p_sim.mu_log_sem_bot:.4f}$ "
        f"e $\\sigma_{{\\log}} = {p_sim.sigma_log_sem_bot:.4f}$ (mediana teórica de 19,5h, média de 28,5h);\n"
        f"- **Grupo Com Bot (`com_bot`):** Mediana real de 13,6h → ajustada para $\\mu_{{\\log}} = {p_sim.mu_log_com_bot:.4f}$ "
        f"e $\\sigma_{{\\log}} = {p_sim.sigma_log_com_bot:.4f}$ (mediana teórica de 14,0h, média de 22,3h);\n"
        f"- **Cenário Baseline Comum sob $H_0$:** Agrupamento *pooled* dos 60 PRs reais → $\\mu_{{\\log}} = {p_sim.mu_log_h0:.4f}$ "
        f"e $\\sigma_{{\\log}} = {p_sim.sigma_log_h0:.4f}$ (mediana teórica comum de 16,5h e média de 25,4h), garantindo que "
        f"ambos os grupos pertençam à mesma população idêntica nas simulações de Erro Tipo I (Q1 e Q3);\n"
        f"- **Reprodutibilidade Estrita:** Todos os dados simulados utilizam semente pseudoaleatória fixa `42` "
        f"(`numpy.random.default_rng(42)`)."
    )

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
rel_reais = executar_analise_completa_dados_reais()
df_tab_secao6 = gerar_tabela_comparativa_secao6(rel_reais)

st.subheader("Resultados Consolidados dos Dois Testes Estatísticos na Amostra Real")
col_card_w, col_card_mw = st.columns(2)
with col_card_w:
    st.markdown(f"### {rel_reais.welch.nome_teste} (Paramétrico)")
    st.metric(
        label="Estatística t (gl)",
        value=f"t = {rel_reais.welch.estatistica_valor:.4f}",
        delta=f"gl = {rel_reais.welch.parametro_auxiliar_valor:.2f}",
        delta_color="off",
    )
    st.metric(
        label="p-valor (bicaudal)",
        value=f"{rel_reais.welch.p_valor:.4f}",
        delta="p ≥ 0,05 (Não Rejeitar H₀)",
        delta_color="off",
    )
    st.metric(
        label="Tamanho do Efeito (d de Cohen)",
        value=f"d = {rel_reais.welch.tamanho_efeito.valor:.4f}",
        delta=f"Magnitude: {rel_reais.welch.tamanho_efeito.magnitude}",
        delta_color="off",
    )
    st.caption(f"**Decisão Formal (α = 0,05):** {rel_reais.welch.decisao_formal}")

with col_card_mw:
    st.markdown(f"### {rel_reais.mann_whitney.nome_teste} (Não-paramétrico)")
    st.metric(
        label="Estatística U (z padronizado)",
        value=f"U = {rel_reais.mann_whitney.estatistica_valor:.1f}",
        delta=f"z = {rel_reais.mann_whitney.parametro_auxiliar_valor:.4f}",
        delta_color="off",
    )
    st.metric(
        label="p-valor (bicaudal)",
        value=f"{rel_reais.mann_whitney.p_valor:.4f}",
        delta="p ≥ 0,05 (Não Rejeitar H₀)",
        delta_color="off",
    )
    st.metric(
        label="Tamanho do Efeito (Rank-Biserial)",
        value=f"r_rb = {rel_reais.mann_whitney.tamanho_efeito.valor:.4f}",
        delta=f"P(com < sem) = {rel_reais.probabilidade_superioridade * 100:.1f}%",
        delta_color="off",
    )
    st.caption(f"**Decisão Formal (α = 0,05):** {rel_reais.mann_whitney.decisao_formal}")

st.subheader("Tabela Comparativa Exigida — Estatística, p-valor, Tamanho do Efeito e Conclusão")
st.dataframe(df_tab_secao6, use_container_width=True)

st.markdown("### Análise da Amostra Real, Decisões de H₀ e Importância Prática")
col_info_1, col_info_2 = st.columns(2)
with col_info_1:
    st.markdown("**1. Integridade dos Dados e Compatibilidade com os Testes:**")
    st.markdown(
        f"- **Dataset Recuperado:** 60 Pull Requests minerados do repositório `{rel_reais.repositorio}` "
        f"(30 do grupo `com_bot` e 30 de `sem_bot`), com 100% de integridade (sem nulos, sem duplicatas, "
        f"datas consistentes e tempos estritamente positivos).\n"
        f"- **Compatibilidade com Pressupostos:** Ambos os grupos violam severamente a normalidade "
        f"(Shapiro-Wilk: p = {rel_reais.pressupostos.shapiro_p_sem_bot:.4g} sem bot e "
        f"p = {rel_reais.pressupostos.shapiro_p_com_bot:.4g} com bot; p < 0,001), apresentando forte assimetria "
        f"à direita ({rel_reais.pressupostos.assimetria_sem_bot:.2f} e {rel_reais.pressupostos.assimetria_com_bot:.2f}) "
        f"e outliers severos (máximos de 88,0 h e 105,5 h). Enquanto Welch tem sua variância inflada pela cauda, "
        f"Mann-Whitney opera sobre postos, sendo perfeitamente adequado e teoricamente compatível."
    )
    st.markdown("**2. Comparação dos Resultados com α = 0,05 e Decisão de H₀:**")
    st.markdown(
        f"- **Teste t de Welch:** p-valor = {rel_reais.welch.p_valor:.4f} ≥ 0,05 → **NÃO REJEITA H₀**.\n"
        f"- **Teste U de Mann-Whitney:** p-valor = {rel_reais.mann_whitney.p_valor:.4f} ≥ 0,05 → **NÃO REJEITA H₀**.\n"
        f"- **Convergência de Decisão:** {rel_reais.resumo_comparativo}"
    )

with col_info_2:
    st.markdown("**3. Medida do Tamanho do Efeito e Importância Prática:**")
    st.markdown(
        f"- **Medidas Adotadas:** Adotou-se o **d de Cohen de Welch** ({rel_reais.welch.tamanho_efeito.valor:.4f}) "
        f"para a comparação de médias e a **correlação rank-biserial r_rb** ({rel_reais.mann_whitney.tamanho_efeito.valor:.4f}, "
        f"equivalente ao Delta de Cliff) para os postos, complementada pela probabilidade de superioridade "
        f"(P(com < sem) = {rel_reais.probabilidade_superioridade * 100:.1f}%).\n"
        f"- **Magnitude Observada:** Ambas as métricas enquadram-se na faixa de magnitude **pequena** "
        f"(|d| < 0,50 e |r_rb| < 0,33).\n"
        f"- **Importância Prática:** {rel_reais.implicacoes_praticas}"
    )
    st.markdown("**4. Por que os Testes Apresentaram p-valores Diferentes?**")
    st.markdown(rel_reais.discussao_diferencas)

with st.expander("Ver diagnóstico de Poder Amostral com n = 30 (Conexão direta com as curvas do Gráfico G4)"):
    st.markdown(rel_reais.diagnostico_poder_n30)
    comp_reais = aplicar_ambos_testes(
        reais,
        alpha=CENARIO.alpha,
        alternativa=CENARIO.tipo_teste,
        origem_dados=f"Amostra de Dados Reais ({rel_reais.repositorio})",
        semente=None,
    )
    st.markdown("**Detalhamento técnico exaustivo dos parâmetros dos dois testes:**")
    st.dataframe(comparacao_para_dataframe(comp_reais), use_container_width=True)

# ------------------------------------------------------------- 7. Conclusão
st.header("7. Conclusão")

st.markdown(obter_resumo_conclusao_markdown())

st.subheader("Expectativa Pré-Simulação vs. Resultados Obtidos (Q1, Q2, Q3 e Dados Reais)")
st.dataframe(obter_tabela_expectativa_vs_resultados(), use_container_width=True)

rec = obter_recomendacao_final()
st.subheader("Recomendação Oficial e Condições de Transição")
col_rec_a, col_rec_b = st.columns(2)
with col_rec_a:
    st.success(
        f"**Teste Recomendado:** {rec.teste_recomendado} ({rec.tipo_abordagem})\n\n"
        f"**Justificativa:** {rec.justificativa_principal}\n\n"
        f"**Medida de Efeito:** {rec.tamanho_efeito_recomendado}"
    )
with col_rec_b:
    st.warning(
        f"**Quando a Recomendação Mudaria:**\n\n{rec.quando_muda_a_recomendacao}"
    )

st.subheader("Principais Limitações do Estudo")
for lim in obter_limitacoes_estudo():
    with st.expander(f"[{lim.numero}] {lim.titulo}"):
        st.markdown(f"**Descrição:** {lim.descricao}")
        st.markdown(f"**Impacto na Inferência:** {lim.impacto_na_inferencia}")
        st.markdown(f"**Como Mitigar Futuramente:** {lim.como_mitigar_futuramente}")

with st.expander("Roteiro de Apoio para a Apresentação Oral — Perguntas 6 a 10 (#60)"):
    for item_p in obter_perguntas_6_a_10():
        st.markdown(f"#### Pergunta {item_p.numero} — {item_p.titulo_curto}")
        st.markdown(f"**Enunciado:** *{item_p.pergunta_oficial}*")
        st.markdown(f"**Onde apontar no Dashboard:** {item_p.onde_apontar_no_dashboard}")
        st.info(f"**Resposta direta (30s):** {item_p.fala_30_segundos}")
        if item_p.pergunta_variante and item_p.fala_variante_30_segundos:
            st.markdown(f"**Variante de arguição:** *{item_p.pergunta_variante}*")
            st.info(f"**Resposta direta p/ variante (30s):** {item_p.fala_variante_30_segundos}")

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
