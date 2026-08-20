# Relatório Parcial - Laboratório 01 (Sprint 2)

Este relatório apresenta a metodologia de coleta de dados, a formulação de hipóteses informais e os resultados de validação de consistência dos dados referentes à **RQ01** (Idade do Repositório) e **RQ02** (Total de PRs Merged).

---

## 1. Hipóteses Informais

Antes da análise quantitativa detalhada, formulamos as seguintes hipóteses:

*   **Hipótese para RQ01 (Idade do Repositório):**
    *   *Enunciado:* Sistemas populares tendem a ser maduros e antigos (idade elevada).
    *   *Justificativa:* Projetos de software levam tempo para ganhar relevância, adoção da comunidade e acumular um volume significativo de estrelas no GitHub. Espera-se que a maioria dos 1.000 repositórios mais populares tenha mais de 3 a 5 anos de criação.
*   **Hipótese para RQ02 (Contribuição Externa):**
    *   *Enunciado:* Sistemas populares possuem um volume muito alto de contribuição externa (total de PRs aceitos/merged elevado).
    *   *Justificativa:* Por serem populares e atraírem grande atenção de desenvolvedores, esses projetos costumam receber uma quantidade massiva de melhorias, correções de bugs e adições de recursos de contribuidores voluntários através de Pull Requests.

---

## 2. Metodologia de Coleta de Dados

A coleta de dados foi realizada utilizando um script Python que consome a API GraphQL do GitHub através da biblioteca padrão do Python (`urllib.request`), em conformidade com as regras da disciplina de evitar dependências externas de terceiros (como `requests` ou `python-dotenv`).

Para mitigar o erro de gateway **502 Bad Gateway** (comum ao consultar campos complexos e agregados de repositórios massivos de uma só vez), implementamos um controle de paginação que realiza a busca em lotes de **10 em 10 repositórios** utilizando os cursores `endCursor` e `hasNextPage`, totalizando 100 requisições para obter a amostra de 1.000 repositórios ordenados por número de estrelas em ordem decrescente.

Os dados foram salvos localmente no arquivo `repositorios_1000.csv` contendo as colunas de identificação e todas as métricas necessárias para o laboratório.

---

## 3. Resultados da Validação de Consistência (RQ01 e RQ02)

O script `valida_dados.py` foi executado para ler o arquivo `repositorios_1000.csv` e extrair as estatísticas descritivas básicas e identificar outliers pelo método do Intervalo Interquartil (IQR).

### 3.1. Estatísticas Descritivas

| Métrica | RQ01 (Idade em Dias) | RQ02 (PRs Merged) |
| :--- | :---: | :---: |
| **Total de Registros** | 1000 | 1000 |
| **Valores Nulos/Ausentes** | 0 | 0 |
| **Mínimo** | 5 dias | 0 |
| **Máximo** | 6.703 dias (~18.3 anos) | 103.316 |
| **Média** | 2.798,97 dias (~7.67 anos) | 4.234,17 |
| **Primeiro Quartil (Q1 - 25%)**| 1.282,00 dias (~3.51 anos) | 175 |
| **Mediana / Q2 (50%)** | 2.829,00 dias (~7.75 anos) | 768 |
| **Terceiro Quartil (Q3 - 75%)**| 4.148,50 dias (~11.37 anos) | 3.425 |
| **IQR (Q3 - Q1)** | 2.866,50 dias | 3.250 |
| **Limites de Outliers** | \[-3017.75, 8448.25\] | \[-4700.00, 8300.00\] |
| **Quantidade de Outliers** | 0 (0.00%) | 124 (12.40%) |

---

## 4. Discussão sobre Consistência e Outliers

*   **Consistência e Nulos:** Não foram detectados valores nulos ou ausentes nas métricas de idade e PRs merged, o que confirma a consistência da extração via GraphQL.
*   **Distribuição da RQ01 (Idade):** A mediana (2.829 dias / 7.75 anos) e a média (2.798 dias / 7.67 anos) estão extremamente próximas, indicando uma distribuição de idades equilibrada e sem distorções severas. A ausência de outliers corrobora que a idade dos projetos populares varia dentro do intervalo esperado de funcionamento do GitHub (criado em 2008, há cerca de 18 anos).
*   **Distribuição da RQ02 (PRs Merged - Skewness):** Há uma assimetria acentuada à direita (cauda longa). Enquanto a mediana é de apenas 768 PRs merged, a média sobe para 4.234 e o valor máximo alcança impressionantes 103.316 PRs. O método IQR detectou **124 outliers (12.40%)**, representando projetos gigantes e hiperativos (ex: grandes frameworks e projetos corporativos) que destoam da maior parte dos repositórios open-source da amostra.
