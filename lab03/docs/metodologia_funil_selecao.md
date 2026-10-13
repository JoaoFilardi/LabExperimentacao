# Metodologia - Seleção de Repositórios e Funil de Coleta (LAB03S02)

Este documento apresenta a fundamentação metodológica, o desenho experimental e os critérios operacionais da seleção amostral para o estudo de **Mineração de Métricas DORA** em repositórios de código aberto no GitHub, formatado para incorporação direta na seção de Metodologia do artigo científico da SBC, expandido na Sprint 02 para **pelo menos 300 repositórios válidos** (Issue [#32](https://github.com/JoaoFilardi/LabExperimentacao/issues/32)).

---

## 1. Fonte de Dados e Janela de Observação

Os dados brutos são coletados diretamente da **API REST do GitHub** por meio de um pipeline próprio em Python, sem o uso de bibliotecas de terceiros pré-fabricadas de acesso à API (como PyGithub), em conformidade com as restrições da disciplina.

- **Janela de Observação Fixada:** 12 meses fixos (outubro/2025 a setembro/2026, com suporte à janela histórica 01/03/2024 a 28/02/2025).
- **Branch Analisado:** Exclusivamente o *default branch* (`main` ou `master`), registrado no metadado `default_branch` do repositório.
- **Unidade Temporal dos Commits:** `commit.author.date` (momento em que a alteração de código foi escrita).

---

## 2. Funil de Seleção Amostral (Sprint 02)

Para garantir que as métricas DORA sejam calculadas exclusivamente sobre projetos representativos e com histórico confiável de integração e entrega contínua, foi desenhado um **funil de seleção em quatro etapas sequenciais**:

```
[Etapa 1: Candidatos Populares] (1.500 repositórios | stars > 1000, públicos, não-forks, não-arquivados)
             │
             ▼
[Etapa 2: Adoção de CI/CD] (1.080 repositórios | workflows configurados > 0 em .github/workflows)
             │
             ▼
[Etapa 3: Atividade na Janela] (595 repositórios | >= 5 releases formais válidas)
             │
             ▼
[Etapa 4: Atividade de CI na Janela] (330 repositórios | >= 50 workflow runs válidos no default branch)
             │
             ▼
[Etapa 5: Amostra Qualificada S02] (310 repositórios qualificados consolidados no dataset final)
```

### 2.1. Critérios Formais de Inclusão e Exclusão

1. **Etapa 1 - Candidatos Populares:**
   - **Critério:** Repositórios com mais de 1.000 estrelas (`stars:>1000`), públicos, não-forks (`fork:false`) e não-arquivados (`archived:false`).
   - **Justificativa:** Garantir maturidade do projeto e evitar projetos-brinquedo (*toy projects*) ou forks inativos.
   - **Estratégia Técnica:** Para contornar o teto rígido de 1.000 resultados por consulta na Search API do GitHub, as consultas são particionadas em faixas de estrelas decrescentes (`stars:>50000`, `stars:20000..50000`, `stars:10000..20000`, `stars:5000..10000`, etc.).

2. **Etapa 2 - Adoção de CI/CD via GitHub Actions:**
   - **Critério:** Endpoint `GET /repos/{owner}/{repo}/actions/workflows` com `total_count > 0`.
   - **Justificativa:** Repositórios que não utilizam GitHub Actions como motor de CI/CD não possuem dados públicos de execuções automatizadas acessíveis pela API, impossibilitando a medição do *Change Failure Rate* e do *Failed Deployment Recovery Time*. Descartá-los nesta etapa economiza chamadas de API desnecessárias.

3. **Etapa 3 - Mínimo de Atividade na Janela de 12 Meses:**
   - **Critério 3.1 (Releases):** Pelo menos **5 releases publicadas** dentro da janela temporal. Apenas releases formais (`draft=false` e `prerelease=false`) são computadas na definição operacional principal.
   - **Critério 3.2 (Workflow Runs):** Pelo menos **50 workflow runs válidos** na branch padrão disparados por eventos de `push` dentro da janela.
   - **Filtragem de Conclusões:** Consideram-se apenas execuções finalizadas com conclusão interpretável:
     - *Sucesso:* `success`
     - *Falha:* `failure`, `timed_out`, `startup_failure`
     - *Descarte:* `cancelled`, `skipped`, `neutral`, `action_required`, `stale` ou em andamento.

4. **Etapa 4/5 - Amostra Final Selecionada (S02):**
   - Repositórios aprovados em todos os filtros anteriores, totalizando **310 repositórios qualificados** (superando a meta de $\ge 300$ repositórios da S02), com coleta completa de metadados para as questões de pesquisa (RQ 01 a RQ 08).

---

## 3. Tabela do Funil de Seleção

### Versão Markdown (para Documentação e Relatórios)

| Etapa | Descrição do Filtro | Repositórios Restantes | Descartados na Etapa | Retenção da Etapa (%) | Retenção Acumulada (%) |
|:---|:---|:---:|:---:|:---:|:---:|
| 1 | Candidatos Iniciais (`stars > 1000`) | 1.500 | 0 | 100,0% | 100,0% |
| 2 | Adoção de CI/CD (GitHub Actions `total_count > 0`) | 1.080 | 420 | 72,0% | 72,0% |
| 3 | Mínimo de Releases na Janela ($\ge 5$ releases) | 595 | 485 | 55,09% | 39,67% |
| 4 | Mínimo de Workflow Runs na Janela ($\ge 50$ runs em `push`) | 330 | 265 | 55,46% | 22,0% |
| 5 | **Amostra Qualificada Final (Lab03S02)** | **310** | **20** | **93,94%** | **20,67%** |

### Versão LaTeX (Template SBC para o Artigo)

```latex
\begin{table}[ht]
\centering
\caption{Funil de Seleção Amostral de Repositórios (Lab03S02)}
\label{tab:funil_selecao_s02}
\begin{tabular}{|c|p{6.0cm}|r|r|r|}
\hline
\textbf{Etapa} & \textbf{Critério de Filtragem} & \textbf{Restantes} & \textbf{Descarte} & \textbf{Retenção (\%)} \\
\hline
1 & Candidatos Iniciais (\textit{stars} $> 1.000$) & 1.500 & 0 & 100,0\% \\
2 & Adoção de CI/CD (GitHub Actions) & 1.080 & 420 & 72,0\% \\
3 & Releases na Janela ($\ge 5$ releases publicadas) & 595 & 485 & 55,1\% \\
4 & Atividade de CI ($\ge 50$ runs em \textit{push}) & 330 & 265 & 55,5\% \\
\hline
\textbf{Final} & \textbf{Amostra Qualificada (Lab03S02)} & \textbf{310} & \textbf{20} & \textbf{20,7\%} \\
\hline
\end{tabular}
\end{table}
```

---

## 4. Metadados Extraídos para a RQ 06

Para viabilizar a análise comparativa entre fatores e métricas DORA (RQ 06: *Quais características dos repositórios estão associadas a um melhor desempenho DORA?*), foram extraídos os seguintes atributos:

1. **Linguagem Principal (`primary_language`):** Categoria de linguagem de programação predominante registrada no GitHub.
2. **Popularidade (`stars`):** Número de estrelas, permitindo segmentação em quartis (Q1 a Q4).
3. **Número de Contribuidores (`contributors_count`):** Coletado de forma otimizada utilizando `GET /contributors?per_page=1&anon=true` e inspecionando o número da última página no cabeçalho HTTP `Link: rel="last"`.
4. **Idade do Repositório (`age_years`):** Tempo decorrido desde a criação até o término da janela de observação.
5. **Histórico de Releases (`releases_window_count`) e Runs (`runs_window_count`):** Quantificadores da cadência de entrega e integração na janela.
