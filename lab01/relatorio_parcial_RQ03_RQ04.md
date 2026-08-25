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
| **Terceiro Quartil (Q3 - 75%)** |          146,2           |              49,2               |
| **IQR (Q3 - Q1)**               |          146,2           |              49,2               |
| **Limites de Outliers**         |   \[-219.38, 365.62\]    |       \[-73.88, 123.12\]        |
| **Quantidade de Outliers**      |        92 (9,20%)        |          193 (19,30%)           |

---

## 4. Discussão sobre Consistência e Outliers

- **Consistência e Nulos:** Não foram detectados valores nulos ou ausentes nas métricas de total de releases e dias desde o último push, o que confirma a consistência da extração via GraphQL. Zero não é dado faltando: em RQ03 significa ausência de GitHub Releases; em RQ04 significa push no mesmo dia da coleta.
- **Distribuição da RQ03 (Releases - Skewness):** Há assimetria à direita. A mediana é 39 releases, enquanto a média sobe para 126,16. **286 repositórios (28,6%)** têm zero releases (listas e projetos que não usam GitHub Releases). O método IQR detectou **92 outliers (9,20%)**, em geral com mais de ~366 releases. **21 repositórios têm exatamente 1000 releases** (ex.: `vercel/next.js`, `home-assistant/core`), o que pode indicar um teto da API; isso quase não altera a mediana, mas subestima o máximo.
- **Distribuição da RQ04 (Dias desde o último push - Skewness):** Também há cauda longa. A mediana é de apenas 1 dia, mas a média sobe para 113,45 por causa de repositórios parados. Cerca de 72,5% da amostra teve push nos últimos 30 dias. O método IQR detectou **193 outliers (19,30%)**, em geral sem push há mais de ~124 dias (ex.: `exacity/deeplearningbook-chinese` com 2450 dias, `atom/atom` com 1323). São casos plausíveis (projeto parado ou descontinuado), não erro no CSV.

## 5. Análise estatística e gráficos — Sprint 3

A análise foi executada sem nova consulta à API, usando exclusivamente `lab01/repositorios_1000.csv`. O script utilizado foi:

```
python lab01/analise_rq03_rq04.py
```

O script reutiliza o mesmo cálculo de percentil linear da validação da S02. Os gráficos gerados ficam em `lab01/graficos_rq03_rq04/`:

- `histograma_rq03.png` e `histograma_rq04.png`: distribuição das duas métricas;
- `boxplots_rq03_rq04.png`: mediana, quartis e valores extremos;
- `faixas_rq04.png`: contagem por faixa de dias desde o último push.

### 5.1. RQ03 — total de releases

| Métrica                       |          Resultado |
| ----------------------------- | -----------------: |
| Registros válidos             |               1000 |
| Mínimo / máximo               |           0 / 1000 |
| Média                         |             126,16 |
| Q1 / mediana / Q3             | 0,0 / 39,0 / 146,2 |
| IQR                           |              146,2 |
| Outliers pelo IQR             |          92 (9,2%) |
| Repositórios com zero release |        286 (28,6%) |

O histograma mostra concentração forte nos valores baixos e cauda à direita; o boxplot evidencia os valores extremos. A média é mais de três vezes a mediana, portanto a mediana representa melhor o repositório típico. A hipótese é parcialmente confirmada: a mediana é maior que zero e há projetos com dezenas ou centenas de releases, mas 28,6% não possui GitHub Release. Os 21 valores iguais a 1000 foram mantidos e tratados como possível teto da API, não como dados corrigidos.

### 5.2. RQ04 — dias desde o último push

| Métrica                     |        Resultado |
| --------------------------- | ---------------: |
| Registros válidos           |             1000 |
| Mínimo / máximo             |         0 / 2450 |
| Média                       |           113,45 |
| Q1 / mediana / Q3           | 0,0 / 1,0 / 49,2 |
| IQR                         |             49,2 |
| Outliers pelo IQR           |      193 (19,3%) |
| Push no mesmo dia da coleta |      430 (43,0%) |

O histograma e o boxplot mostram uma distribuição assimétrica, com muitos valores próximos de zero e uma cauda de repositórios sem atualização há meses ou anos. O gráfico de faixas registra 430 no mesmo dia, 190 entre 1 e 7 dias, 105 entre 8 e 30 dias, 65 entre 31 e 90 dias, 96 entre 91 e 365 dias, 47 entre 1 e 2 anos e 67 há mais de 2 anos. Portanto, 725 (72,5%) tiveram push nos últimos 30 dias. A hipótese é confirmada para a maioria da amostra: a mediana é de 1 dia, embora a média seja elevada pelos projetos parados.
