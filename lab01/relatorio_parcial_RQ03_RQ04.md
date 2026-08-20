## 1. Hipóteses Informais

Antes da análise quantitativa detalhada, formulamos as seguintes hipóteses:

- **Hipótese para RQ03 (Total de Releases):**
  - _Enunciado:_ Sistemas populares tendem a lançar releases com frequência (total de GitHub Releases elevado).
  - _Justificativa:_ Projetos muito populares costumam versionar o que entregam para uma base grande de usuários. Espera-se mediana de releases maior que zero e um grupo com dezenas ou centenas de releases (bibliotecas e frameworks). Parte da amostra pode ter zero releases (listas _awesome_, livros e projetos que usam só tag/commit), sem invalidar a tendência do conjunto.
- **Hipótese para RQ04 (Tempo até a última atualização):**
  - _Enunciado:_ Sistemas populares são atualizados com frequência (poucos dias desde o último push).
  - _Justificativa:_ Mantenedores e a comunidade tendem a manter o repositório ativo. Espera-se mediana baixa (dias ou poucas semanas, não anos) e a maior parte da amostra atualizada há menos de 30 dias. Alguns projetos famosos podem estar parados; isso não quebra a hipótese se a maioria continuar ativa.

---

## 2. Metodologia de Coleta de Dados

A coleta de dados foi realizada utilizando um script Python que consome a API GraphQL do GitHub através da biblioteca padrão do Python (`urllib.request`), em conformidade com as regras da disciplina de evitar dependências externas de terceiros (como `requests` ou `python-dotenv`).

Para mitigar o erro de gateway **502 Bad Gateway** (comum ao consultar campos complexos e agregados de repositórios massivos de uma só vez), o grupo implementou um controle de paginação que realiza a busca em lotes de **10 em 10 repositórios** utilizando os cursores `endCursor` e `hasNextPage`, totalizando 100 requisições para obter a amostra de 1.000 repositórios ordenados por número de estrelas em ordem decrescente.

Os dados foram salvos localmente no arquivo `repositorios_1000.csv`. Para esta parte do laboratório foram usadas as colunas `total_releases` (RQ03) e `dias_ultimo_push` (RQ04).

---

## 3. Resultados da Validação de Consistência (RQ03 e RQ04)

O script `validacao_rq03_rq04.py` foi executado para ler o arquivo `repositorios_1000.csv` e extrair as estatísticas descritivas básicas e identificar outliers pelo método do Intervalo Interquartil (IQR).

### 3.1. Estatísticas Descritivas

| Métrica                         | RQ03 (Total de Releases) | RQ04 (Dias desde o último push) |
| :------------------------------ | :----------------------: | :-----------------------------: |
| **Total de Registros**          |           1000           |              1000               |
| **Valores Nulos/Ausentes**      |            0             |                0                |
| **Mínimo**                      |            0             |                0                |
| **Máximo**                      |          1.000           |              2.450              |
| **Média**                       |          126,16          |             113,45              |
| **Primeiro Quartil (Q1 - 25%)** |            0             |                0                |
| **Mediana / Q2 (50%)**          |            39            |                1                |
| **Terceiro Quartil (Q3 - 75%)** |          146,50          |              49,50              |
| **IQR (Q3 - Q1)**               |          146,50          |              49,50              |
| **Limites de Outliers**         |   \[-219.75, 366.25\]    |       \[-74.25, 123.75\]        |
| **Quantidade de Outliers**      |        92 (9,20%)        |          193 (19,30%)           |

---

## 4. Discussão sobre Consistência e Outliers

- **Consistência e Nulos:** Não foram detectados valores nulos ou ausentes nas métricas de total de releases e dias desde o último push, o que confirma a consistência da extração via GraphQL. Zero não é dado faltando: em RQ03 significa ausência de GitHub Releases; em RQ04 significa push no mesmo dia da coleta.
- **Distribuição da RQ03 (Releases - Skewness):** Há assimetria à direita. A mediana é 39 releases, enquanto a média sobe para 126,16. **286 repositórios (28,6%)** têm zero releases (listas e projetos que não usam GitHub Releases). O método IQR detectou **92 outliers (9,20%)**, em geral com mais de ~366 releases. **21 repositórios têm exatamente 1000 releases** (ex.: `vercel/next.js`, `home-assistant/core`), o que pode indicar um teto da API; isso quase não altera a mediana, mas subestima o máximo.
- **Distribuição da RQ04 (Dias desde o último push - Skewness):** Também há cauda longa. A mediana é de apenas 1 dia, mas a média sobe para 113,45 por causa de repositórios parados. Cerca de 72,5% da amostra teve push nos últimos 30 dias. O método IQR detectou **193 outliers (19,30%)**, em geral sem push há mais de ~124 dias (ex.: `exacity/deeplearningbook-chinese` com 2450 dias, `atom/atom` com 1323). São casos plausíveis (projeto parado ou descontinuado), não erro no CSV.
