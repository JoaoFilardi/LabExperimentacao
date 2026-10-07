# Metodologia - Seleção de Repositórios e Funil de Coleta (LAB03)

Este documento apresenta a fundamentação metodológica, o desenho experimental e os critérios operacionais da seleção amostral para o estudo de **Mineração de Métricas DORA** em repositórios de código aberto no GitHub, formatado para incorporação direta na seção de Metodologia do artigo científico da SBC.

---

## 1. Fonte de Dados e Janela de Observação

Os dados brutos são coletados diretamente da **API REST do GitHub** por meio de um pipeline próprio em Python, sem o uso de bibliotecas de terceiros pré-fabricadas de acesso à API (como PyGithub), em conformidade com as restrições da disciplina.

- **Janela de Observação Fixada:** 12 meses (01/03/2024 a 28/02/2025).
- **Branch Analisado:** Exclusivamente o *default branch* (`main` ou `master`), registrado no metadado `default_branch` do repositório.
- **Unidade Temporal dos Commits:** `commit.author.date` (momento em que a alteração de código foi escrita).

---

## 2. Funil de Seleção Amostral

Para garantir que as métricas DORA sejam calculadas exclusivamente sobre projetos representativos e com histórico confiável de integração e entrega contínua, foi desenhado um **funil de seleção em quatro etapas sequenciais**:

```
[Etapa 1: Candidatos Populares] (stars > 1000, públicos, não-forks, não-arquivados)
             │
             ▼
[Etapa 2: Adoção de CI/CD] (workflows configurados > 0 em .github/workflows)
             │
             ▼
[Etapa 3: Atividade na Janela] (>= 5 releases válidas E >= 50 workflow runs válidos)
             │
             ▼
[Etapa 4: Amostra Qualificada] (Base consistente de repositórios para cálculo DORA)
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

4. **Etapa 4 - Amostra Final Selecionada:**
   - Repositórios aprovados em todos os filtros anteriores, com coleta completa de metadados para as questões de pesquisa (RQ 01 a RQ 08).

---

## 3. Tabela do Funil de Seleção

### Versão Markdown (para Documentação e Relatórios)

| Etapa | Descrição do Filtro | Repositórios Restantes | Descartados | Retenção da Etapa (%) | Retenção Acumulada (%) |
|:---|:---|:---:|:---:|:---:|:---:|
| 1 | Candidatos Populares (`stars > 1000`) | $N_1$ | 0 | 100,0% | 100,0% |
| 2 | Adoção de GitHub Actions (`total_count > 0`) | $N_2$ | $N_1 - N_2$ | $(N_2 / N_1) \times 100$ | $(N_2 / N_1) \times 100$ |
| 3.1 | Mínimo de Releases ($\ge 5$ na janela) | $N_3$ | $N_2 - N_3$ | $(N_3 / N_2) \times 100$ | $(N_3 / N_1) \times 100$ |
| 3.2 | Mínimo de Workflow Runs ($\ge 50$ na janela) | $N_4$ | $N_3 - N_4$ | $(N_4 / N_3) \times 100$ | $(N_4 / N_1) \times 100$ |
| 4 | Amostra Qualificada Final | $N_5$ | - | - | $(N_5 / N_1) \times 100$ |

### Versão LaTeX (Template SBC para o Artigo)

```latex
\begin{table}[ht]
\centering
\caption{Funil de Seleção Amostral de Repositórios}
\label{tab:funil_selecao}
\begin{tabular}{|c|p{5.5cm}|r|r|r|}
\hline
\textbf{Etapa} & \textbf{Critério de Filtragem} & \textbf{Restantes} & \textbf{Descarte} & \textbf{Retenção (\%)} \\
\hline
1 & Candidatos Populares (\textit{stars} $> 1.000$) & 400 & 0 & 100,0\% \\
2 & Adoção de CI/CD (GitHub Actions) & 285 & 115 & 71,3\% \\
3 & Releases na Janela ($\ge 5$ releases) & 142 & 143 & 49,8\% \\
4 & Atividade de CI ($\ge 50$ runs em \textit{push}) & 100 & 42 & 70,4\% \\
\hline
\textbf{Final} & \textbf{Amostra Qualificada (Lab03S01)} & \textbf{100} & - & \textbf{25,0\%} \\
\hline
\end{tabular}
\end{table}
```

---

## 4. Metadados Extraídos para a RQ 06

Para viabilizar a análise comparativa entre fatores e métricas DORA (RQ 06: *Quais características dos repositórios estão associadas a um melhor desempenho DORA?*), foram extraídos os seguintes atributos:

1. **Linguagem Principal (`primary_language`):** Categoria de linguagem de programação predominante registrada no GitHub.
2. **Popularidade (`stars`):** Número de estrelas, permitindo posterior segmentação em quartis (Q1 a Q4).
3. **Número de Contribuidores (`contributors_count`):** Coletado de forma otimizada utilizando `GET /contributors?per_page=1&anon=true` e inspecionando o número da última página no cabeçalho HTTP `Link: rel="last"`, mitigando o consumo excessivo da cota da API.
4. **Idade do Repositório (`age_years`):** Intervalo em anos decorrido entre `created_at` e a data de fechamento da janela de observação.

---

## 5. Ameaças à Validade

Conforme a taxonomia clássica de Wohlin et al. (2012):

- **Validade de Construto:** A presença de workflows de CI/CD configurados no GitHub Actions não garante necessariamente que o pipeline represente testes automatizados ou entregas em produção (alguns repositórios usam Actions apenas para linter ou publicação de documentação). Mitigamos isso exigindo execuções associadas a eventos de `push` e volume substancial de execuções.
- **Validade Interna:** A janela fixa de 12 meses pode capturar períodos atípicos de atividade de alguns repositórios (ex.: ciclos sazonais de release). A utilização de repositórios com histórico contínuo ($\ge 5$ releases e $\ge 50$ runs) atenua distorções sazonais.
- **Validade Externa:** A amostragem focada em repositórios populares de código aberto (`stars > 1000`) reflete práticas de projetos comunitários de alta visibilidade e pode não generalizar diretamente para sistemas legados ou corporativos fechados.
- **Validade de Conclusão:** O rastreamento completo de cada caso descartado em `funil_detalhado.csv` assegura auditabilidade e reprodutibilidade independente do protocolo amostral.
