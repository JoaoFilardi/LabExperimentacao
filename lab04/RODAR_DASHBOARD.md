# Como Rodar o Dashboard do LAB04 e Requisitos do Projeto

Guia rápido e completo para configuração do ambiente e execução do dashboard interativo do **LAB04 — Testes de Hipótese por Dentro: Cenário, Simulação e Visualização**.

---

## 1. O que é preciso (Pré-requisitos)

Para executar o dashboard e reproduzir as análises e simulações, você precisará de:

- **Python 3.10 ou superior** instalado no sistema.
- Gerenciador de pacotes `pip` atualizado.
- Terminal / Shell (PowerShell, Bash, Command Prompt ou terminal integrado do VS Code).
- Navegador web (Google Chrome, Firefox, Edge, etc.) para visualizar a interface interativa.

### Bibliotecas Utilizadas:
- `streamlit`: Servidor web e interface interativa do dashboard.
- `pandas`: Estruturação, agregação e exibição das tabelas de dados.
- `numpy`: Vetorização de Monte Carlo e manipulação matricial de alta performance.
- `matplotlib`: Renderização dos gráficos comparativos (G1 a G4).
- `scipy`: Cálculos das estatísticas de teste ($t$ de Welch, Mann-Whitney $U$, graus de liberdade de Satterthwaite e p-valores).
- `pytest`: Validação da suíte de 90 testes automatizados de unidade e regressão.

---

## 2. Instalação das Dependências

Abra o terminal na pasta raiz do projeto (`LabExperimentacao`) e instale as dependências usando o arquivo de requisitos localizado na pasta do laboratório:

```bash
python -m pip install -r lab04/requirements.txt
```

*(Ou instale manualmente caso prefira sem o arquivo):*
```bash
python -m pip install streamlit pandas numpy matplotlib scipy pytest
```

---

## 3. Como Rodar o Dashboard (Comando Único)

A partir da raiz do repositório (`LabExperimentacao`), execute o comando único:

```bash
python -m streamlit run lab04/app.py
```

O Streamlit iniciará o servidor local e abrirá a página automaticamente no seu navegador padrão:
👉 **URL Local:** `http://localhost:8501`

*(Se estiver executando o comando diretamente de dentro da pasta `lab04`, use: `streamlit run app.py`).*

---

## 4. O que você encontrará no Dashboard

O dashboard foi projetado para ser autossuficiente e está organizado nas 7 seções oficiais exigidas pela disciplina:

1. **1. Cenário:** Pergunta de pesquisa, hipóteses $H_0$ e $H_1$, metadados da coleta de dados reais no GitHub (`tiangolo/fastapi`) e previsão inicial do grupo antes de simular.
2. **2. Os dados (G1):** Gráfico G1 comparativo (reais vs. simulados), tabela de estatísticas descritivas (assimetria, outliers, dispersão) e expander com a justificativa técnica da distribuição Log-normal.
3. **3. Como os testes funcionam (G2):** Gráfico G2 apresentando a distribuição da estatística sob $H_0$, as regiões críticas de corte ($\alpha = 0{,}05$) e a interpretação do p-valor com uma amostra da S01.
4. **4. Erro tipo I (G3):** Gráfico G3 com os resultados de 10.000 simulações de Monte Carlo com $H_0$ verdadeira, comparando as taxas de falsos positivos frente à linha de 5%.
5. **5. Poder (G4):** Gráfico G4 com as curvas de poder estatístico sob $H_1$ para diferentes tamanhos de efeito ($\delta$ de 0% a 50%) e análise de robustez sob violações.
6. **6. Dados reais:** Tabela comparativa e síntese da aplicação de Welch e Mann-Whitney sobre os 60 Pull Requests minerados do FastAPI.
7. **7. Conclusão:** 
   - Tabela *Expectativa Inicial vs. Resultados Empíricos*;
   - Recomendação oficial fundamentada (**Teste U de Mann-Whitney**) e condições em que ela mudaria;
   - Limitações do estudo observacional;
   - **Roteiro estruturado de apoio para a Apresentação Oral** cobrindo as 15 perguntas oficiais organizadas em expanders (Perguntas 1 a 5, 6 a 10 e 11 a 15).

---

## 5. Como Rodar a Suíte de Testes Automatizados

Para certificar-se de que todas as rotinas estatísticas e componentes do laboratório estão funcionando sem regressões:

```bash
python -m pytest lab04/tests
```

*Todos os testes utilizam semente pseudoaleatória fixa (`semente = 42`), garantindo reprodutibilidade exata.*

---

## 6. Execução Individual de Módulos (CLI)

Se desejar gerar artefatos individuais em disco (arquivos PNG e CSV na pasta `lab04/data/`):

| Ação | Comando CLI |
|:---|:---|
| **Gerar Gráfico G1** | `python -m lab04.src.grafico_g1` |
| **Gerar Gráfico G2** | `python -m lab04.src.grafico_g2` |
| **Executar Simulações Q1 (Erro Tipo I)** | `python -m lab04.src.simulacao_q1` |
| **Executar Simulações Q2 (Poder)** | `python -m lab04.src.simulacao_q2` |
| **Executar Simulações Q3 (Violações)** | `python -m lab04.src.simulacao_q3` |
| **Gerar Gráfico G3** | `python -m lab04.src.grafico_g3` |
| **Gerar Gráfico G4** | `python -m lab04.src.grafico_g4` |
| **Gerar Análise dos Dados Reais** | `python -m lab04.src.analise_dados_reais` |
| **Exibir Conclusão e Recomendações** | `python -m lab04.src.conclusao_dashboard` |
| **Exibir Roteiro Oral (15 Perguntas)** | `python -m lab04.src.apresentacao_oral` |
