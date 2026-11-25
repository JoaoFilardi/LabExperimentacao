# LAB05 --- Contextualização do experimento

## Comparação de desempenho entre PostgreSQL 17 e PostgreSQL 18

> **Finalidade deste arquivo:** fornecer contexto permanente à IA
> utilizada pela equipe. A cada tarefa, a equipe deve enviar este
> arquivo junto com a issue específica que está trabalhando. A IA deve
> executar somente o escopo daquela issue, respeitando a divisão em
> sprints e sem antecipar as próximas etapas.

------------------------------------------------------------------------

## 1. Contexto acadêmico

Este projeto faz parte do **LAB05 --- Experimento em software real:
medindo o que importa em produção**, da disciplina Laboratório de
Experimentação de Software, do curso de Engenharia de Software.

O objetivo do laboratório é planejar, executar e analisar um estudo
sobre um software real, em operação e de alto impacto. O trabalho deve
aplicar conceitos de Medição e Experimentação, apresentar evidências,
analisar resultados e explicar o que as descobertas significam para quem
utiliza o software.

O foco deve ser o **software em funcionamento**, e não a mineração de um
repositório público do GitHub. Portanto, não devemos usar commits,
issues, pull requests ou análise estática do código-fonte do PostgreSQL
como objeto do estudo. O objeto de pesquisa será o comportamento do
PostgreSQL executando operações reais de banco de dados em um ambiente
controlado.

O trabalho está dividido em três sprints, com issues específicas. A IA
deve ajudar a equipe a concluir cada issue individualmente, sem realizar
automaticamente o trabalho das três sprints.

## 2. Software escolhido

**PostgreSQL**, um sistema gerenciador de banco de dados relacional
(SGBD) de código aberto, utilizado para armazenar, consultar e gerenciar
dados em aplicações e sistemas de empresas.

-   Site oficial: https://www.postgresql.org/
-   Documentação oficial: https://www.postgresql.org/docs/
-   Documentação do pgbench:
    https://www.postgresql.org/docs/current/pgbench.html
-   Imagens oficiais para Docker: https://hub.docker.com/\_/postgres

### Por que escolhemos o PostgreSQL?

1.  É um software real, mantido e utilizado em ambientes de produção.
2.  Possui versões oficiais e documentação pública.
3.  Pode ser executado localmente, permitindo controlar as condições do
    experimento.
4.  Oferece ferramentas de benchmark, como o `pgbench`.
5.  Permite coletar métricas quantitativas de desempenho e consumo de
    recursos.
6.  É possível repetir os testes e comparar os resultados
    estatisticamente.
7.  Os resultados podem ser relacionados ao impacto que desempenho e
    eficiência de banco de dados têm para aplicações e empresas.

A equipe deverá documentar evidências atuais dos critérios **real**,
**em operação** e **alto impacto**, com fontes e data de acesso. Não
basta afirmar que o PostgreSQL é popular: é necessário apresentar dados
verificáveis, por exemplo, pesquisas de uso, informações oficiais e
indicadores públicos.

## 3. Tema e pergunta de pesquisa

### Tema

**Análise comparativa de desempenho e consumo de recursos entre
PostgreSQL 17 e PostgreSQL 18 em operações de banco de dados.**

### Pergunta principal de pesquisa (RQ)

**A versão 18 do PostgreSQL apresenta diferenças de desempenho e
eficiência no uso de recursos computacionais em comparação com a versão
17, sob uma carga de trabalho controlada?**

A pergunta é intencionalmente neutra: não devemos pressupor que a versão
mais recente será necessariamente melhor. O experimento deve permitir
identificar melhorias, pioras ou ausência de diferenças relevantes.

### Objetivo geral

Comparar o comportamento do PostgreSQL 17 e do PostgreSQL 18 ao executar
uma carga de trabalho equivalente, observando desempenho e consumo de
recursos computacionais.

### Objetivos específicos

-   Preparar ambientes equivalentes para as duas versões.
-   Definir uma carga de trabalho reproduzível.
-   Executar operações equivalentes nas duas versões.
-   Coletar medidas de latência, vazão e consumo de recursos.
-   Repetir as execuções para reduzir a influência de variações
    ocasionais.
-   Analisar os dados com estatística adequada.
-   Discutir o significado prático dos resultados e as limitações do
    estudo.

## 4. O que queremos demonstrar

Queremos produzir evidências que respondam:

-   Qual versão apresentou menor latência nas condições testadas?
-   Qual versão conseguiu executar mais transações por segundo?
-   Houve diferença no consumo de CPU?
-   Houve diferença no consumo de memória?
-   As diferenças observadas são consistentes entre as repetições?
-   As diferenças são estatisticamente significativas e, principalmente,
    têm tamanho de efeito relevante?
-   O que esses resultados podem significar para uma empresa que utiliza
    PostgreSQL?

**Não é objetivo provar antecipadamente que o PostgreSQL 18 é
superior.** Uma conclusão válida pode indicar que uma versão teve melhor
resultado em determinada métrica, que outra teve melhor resultado em
outra, que não houve diferença detectável ou que o experimento não teve
evidência suficiente para concluir.

Também não devemos generalizar os resultados para todos os cenários de
produção. A conclusão deve ser limitada ao hardware, às configurações,
aos dados e à carga de trabalho utilizados.

## 5. Desenho geral do experimento

A proposta inicial é comparar duas condições:

-   **Tratamento A:** PostgreSQL 17.
-   **Tratamento B:** PostgreSQL 18.

As duas versões deverão executar a mesma carga de trabalho, com
estrutura de banco, volume de dados, parâmetros relevantes e condições
de execução equivalentes.

### Unidade experimental

Uma execução de benchmark em uma versão do PostgreSQL, sob uma
configuração e carga de trabalho definidas.

### Variável independente

A versão do PostgreSQL (17 ou 18).

### Variáveis dependentes

-   Latência das operações.
-   Transações por segundo (TPS).
-   Consumo de CPU.
-   Consumo de memória RAM.

### Variáveis de controle

Sempre que tecnicamente possível, manter constantes:

-   Máquina física utilizada.
-   Sistema operacional e versão do Docker.
-   Recursos disponibilizados aos containers.
-   Configurações equivalentes do PostgreSQL.
-   Estrutura e volume do banco de dados.
-   Carga de trabalho e parâmetros do benchmark.
-   Número de clientes/conexões simultâneas.
-   Duração de cada execução.
-   Procedimento de aquecimento (warm-up).
-   Procedimento de coleta das métricas.

A equipe deverá registrar diferenças inevitáveis entre as versões e não
alterar parâmetros de uma versão sem justificar e documentar a decisão.

## 6. Uso do Docker

### Por que usar Docker?

A equipe pretende utilizar o Docker para executar as duas versões do
PostgreSQL sem precisar instalar cada versão diretamente no Windows ou
ficar desinstalando e reinstalando o banco.

O Docker permite manter ambientes separados e reproduzíveis:

-   Um container com PostgreSQL 17.
-   Um container com PostgreSQL 18.
-   Volumes separados para os dados.
-   Portas diferentes no computador hospedeiro.
-   Configurações e limites de recursos documentados.

As imagens oficiais do PostgreSQL podem ser obtidas pelo Docker Hub. A
equipe deve conferir as tags disponíveis e utilizar tags explícitas,
evitando `latest`, para que o ambiente possa ser reproduzido.

### Arquitetura planejada

``` text
                    Computador da equipe
                 Windows + Docker Desktop
                            |
             +--------------+--------------+
             |                             |
      Container PostgreSQL 17       Container PostgreSQL 18
             |                             |
       Banco de teste A               Banco de teste B
             |                             |
             +--------------+--------------+
                            |
                  Script de benchmark
                    (pgbench / Python)
                            |
                   Coleta de resultados
                            |
                 CSV + logs + metadados
                            |
                Análise estatística e gráficos
```

### Cuidados importantes com Docker

1.  Os dois containers devem usar imagens oficiais e tags de versão
    explícitas.
2.  Cada container deve ter seu próprio volume de dados.
3.  As portas externas devem ser diferentes, por exemplo, `5432` e
    `5433`.
4.  As credenciais de teste devem ser fictícias e não reutilizar senhas
    pessoais.
5.  Os limites de CPU e memória devem ser equivalentes, quando
    aplicável.
6.  Os bancos devem possuir dados e estruturas equivalentes.
7.  A equipe deve registrar os comandos, arquivos de configuração e
    versões utilizados.
8.  O benchmark não deve competir com outros processos pesados do
    computador.
9.  Os testes devem ser executados de forma controlada,
    preferencialmente alternando a ordem das versões ou justificando a
    ordem adotada.
10. Não executar testes de carga em servidores de terceiros. Todo o
    benchmark será realizado nos ambientes locais controlados pela
    equipe.

**Importante:** Docker ajuda a isolar e reproduzir os ambientes, mas não
garante sozinho que eles sejam perfeitamente equivalentes. A equipe
precisa verificar e documentar as condições experimentais.

## 7. Ferramentas previstas

  -----------------------------------------------------------------------
  Ferramenta                          Finalidade
  ----------------------------------- -----------------------------------
  Docker Desktop                      Executar e isolar as versões do
                                      PostgreSQL

  Imagens oficiais do PostgreSQL      Disponibilizar as versões 17 e 18

  pgbench                             Gerar carga de trabalho e medir
                                      desempenho

  Python                              Automatizar execuções, organizar
                                      dados e realizar análises

  SQL                                 Criar estruturas, dados e consultas

  CSV                                 Armazenar resultados brutos e
                                      organizados

  Bibliotecas de análise e gráficos   Calcular estatísticas e gerar
                                      visualizações

  Git/GitHub                          Versionar scripts, configurações e
                                      documentação do grupo
  -----------------------------------------------------------------------

A equipe pode escolher bibliotecas Python adequadas, como pandas, SciPy
e Matplotlib, justificando seu uso. Não é necessário construir uma
aplicação web.

## 8. Métricas e interpretação

### 8.1 Latência

Tempo necessário para concluir uma operação ou transação, normalmente
expresso em milissegundos.

-   Menor latência tende a representar resposta mais rápida.
-   Registrar média e medidas de dispersão; considerar também mediana e
    percentis, se a ferramenta permitir.

### 8.2 Transações por segundo (TPS)

Quantidade de transações concluídas por segundo.

-   Maior TPS indica maior vazão para a carga de trabalho testada.
-   Deve ser interpretado junto com a latência e as condições do teste.

### 8.3 Consumo de CPU

Percentual ou quantidade de CPU utilizada durante a execução.

-   Ajuda a avaliar o custo computacional para realizar o trabalho.
-   É importante usar o mesmo método de coleta nas duas condições.

### 8.4 Consumo de memória

Memória utilizada pelo container ou processo durante o teste.

-   Registrar unidade, ferramenta e intervalo de coleta.
-   Não confundir memória alocada, limite do container e memória
    efetivamente utilizada.

### Métricas complementares

Se houver tempo e instrumentação adequada, a equipe poderá avaliar taxa
de falhas, leituras/escritas ou comportamento sob diferentes níveis de
concorrência. Essas métricas complementares não devem desviar o foco da
pergunta principal.

## 9. Plano de coleta e qualidade dos dados

A coleta deve ser planejada antes da execução definitiva.

-   Realizar uma coleta piloto para verificar se os scripts funcionam e
    se as métricas fazem sentido.
-   Definir previamente parâmetros e duração dos testes.
-   Fazer múltiplas repetições por versão.
-   Registrar resultados brutos, inclusive execuções com problemas.
-   Não apagar resultados desfavoráveis.
-   Registrar falhas, interrupções e motivos de exclusão.
-   Identificar cada execução com versão, data/hora, configuração e
    número da repetição.
-   Salvar os dados em CSV e manter logs suficientes para auditoria.
-   Separar dados brutos de dados tratados.
-   Validar se não há valores ausentes, duplicados ou unidades
    inconsistentes.

A quantidade final de repetições, a duração, o número de clientes e o
tamanho do conjunto de dados devem ser definidos e justificados pela
equipe. Não inventar um número de repetições sem considerar o tempo
disponível, a variabilidade e a viabilidade do ambiente.

## 10. Plano de análise estatística

A análise deve ser compatível com o tipo de dado, a distribuição e o
desenho do experimento.

### Estatística descritiva

Apresentar, no mínimo, medidas adequadas para cada métrica, como:

-   Média.
-   Mediana.
-   Desvio padrão.
-   Mínimo e máximo.
-   Intervalo interquartil, quando útil.

Usar tabelas e gráficos comparativos. Para distribuições assimétricas,
não depender apenas da média.

### Teste de hipótese

A formulação inicial para cada métrica poderá ser:

-   **H0:** não há diferença entre as versões na métrica avaliada.
-   **H1:** há diferença entre as versões na métrica avaliada.

A equipe deve decidir se o teste será unilateral ou bilateral com base
na pergunta e no planejamento, não depois de observar os resultados.

A escolha do teste estatístico deve considerar: - Se as observações são
independentes ou pareadas. - Distribuição dos dados e pressupostos do
teste. - Quantidade de observações. - Escala de medida da métrica.

Não escolher automaticamente um teste t sem verificar se ele é adequado.
Quando necessário, considerar alternativas não paramétricas ou métodos
de reamostragem.

### Significância e tamanho do efeito

Relatar o nível de significância adotado, o valor-p, o intervalo de
confiança quando aplicável e uma medida de tamanho do efeito.

Uma diferença estatisticamente significativa não é necessariamente
importante na prática. A interpretação deve considerar a magnitude da
diferença e o impacto possível para quem utiliza o banco de dados.

Se forem realizados testes para várias métricas, discutir o risco de
múltiplas comparações e avaliar se é necessário algum ajuste.

## 11. Relação com os conteúdos da disciplina

O estudo deve aplicar os conceitos que fizerem sentido, sem apenas
citá-los.

-   **GQM (Goal-Question-Metric):** transformar o objetivo em perguntas
    e métricas observáveis.
-   **Medição e escalas:** definir o que cada métrica representa, sua
    unidade e escala.
-   **Entidades e atributos:** identificar o PostgreSQL como
    produto/software e os atributos avaliados.
-   **Planejamento experimental:** tratamentos, variáveis, unidade
    experimental, controles, instrumentação e operação.
-   **Hipóteses:** formular H0 e H1 antes de analisar os resultados.
-   **Estatística:** descrever os dados, selecionar testes adequados e
    interpretar tamanho do efeito.
-   **Ameaças à validade:** discutir validade de conclusão, interna, de
    construto e externa.
-   **Lei de Goodhart e armadilhas de medição:** discutir por que
    otimizar uma métrica isolada pode produzir uma visão incompleta do
    desempenho.

A equipe também deve classificar o estudo nas sete categorias de
pesquisa trabalhadas na Aula 8, justificando cada classificação conforme
o método realmente executado. Não classificar o estudo de forma
automática ou sem justificativa.

## 12. Ameaças à validade que devem ser consideradas

### Validade de conclusão

-   Número insuficiente de repetições.
-   Alta variabilidade entre execuções.
-   Teste estatístico inadequado.
-   Baixo poder estatístico.
-   Múltiplas comparações.

### Validade interna

-   Outros processos consumindo recursos durante o teste.
-   Diferenças de configuração entre containers.
-   Aquecimento e cache favorecendo uma execução.
-   Ordem fixa dos testes.
-   Diferenças de dados ou de carga entre versões.

### Validade de construto

-   TPS e latência podem não representar todos os aspectos de
    desempenho.
-   Consumo de memória do container pode não refletir isoladamente a
    eficiência do banco.
-   O benchmark pode não representar adequadamente uma aplicação real.

### Validade externa

-   Resultados obtidos em uma única máquina não representam todos os
    servidores.
-   Uma carga sintética não representa todos os padrões de uso.
-   Os resultados não permitem afirmar que uma versão será melhor em
    qualquer ambiente de produção.

A equipe deve registrar medidas de mitigação para cada ameaça relevante.

## 13. Impacto para empresas e usuários

O trabalho não deve terminar apenas com a afirmação de que uma versão
teve determinado TPS ou latência.

A equipe deve traduzir os resultados para uma interpretação prática, por
exemplo:

-   Se uma versão concluiu a mesma carga em menos tempo, o que isso
    poderia representar para uma aplicação?
-   Se uma versão utilizou menos CPU para entregar vazão semelhante,
    qual seria o possível benefício operacional?
-   Se houve aumento de TPS, em quais condições esse ganho poderia ser
    relevante?
-   Qual é a limitação de extrapolar o resultado de uma máquina de
    testes para uma empresa?

Quando possível, relacionar a discussão a números públicos e fontes
confiáveis sobre adoção e uso do PostgreSQL. Qualquer extrapolação deve
ser identificada como estimativa, apresentar suas premissas e deixar
claro o que o experimento não permite afirmar.

## 14. Organização em três sprints

As issues do GitHub Projects são a unidade de trabalho. A IA deve usar
este contexto para interpretar cada issue, mas **não deve executar todas
as etapas do projeto de uma só vez**.

### Sprint 1 --- Proposta, planejamento e preparação

Objetivo: definir o estudo e deixar o plano de coleta pronto, incluindo
uma coleta piloto quando prevista na issue.

Exemplos de atividades: - Definir pergunta, objetivo e hipóteses. -
Justificar a escolha do PostgreSQL e comprovar os critérios de
seleção. - Definir as sete categorias de pesquisa. - Elaborar GQM,
variáveis, métricas e desenho experimental. - Planejar o uso de
Docker. - Preparar ambiente e scripts conforme o escopo das issues. -
Fazer piloto e registrar ajustes necessários.

### Sprint 2 --- Execução e validação

Objetivo: realizar a coleta planejada e validar os dados.

Exemplos de atividades: - Executar os benchmarks definitivos. - Coletar
métricas e logs. - Repetir execuções conforme o protocolo. - Validar
consistência, completude e rastreabilidade dos dados. - Registrar
desvios do planejamento. - Revisar metodologia e ameaças à validade.

### Sprint 3 --- Análise, impacto e entrega

Objetivo: interpretar os resultados e preparar os materiais finais.

Exemplos de atividades: - Fazer análise descritiva e inferencial
adequada. - Calcular e interpretar tamanho do efeito. - Criar gráficos e
tabelas. - Relacionar resultados ao impacto para empresas e usuários. -
Consolidar as sete categorias e as ameaças à validade. - Elaborar
conclusões, limitações, documento e apresentação.

**A distribuição acima é um guia de organização. A descrição e os
critérios de aceite da issue específica prevalecem.** Não antecipar uma
atividade de sprint futura apenas porque ela aparece neste arquivo.

## 15. Como a IA deve trabalhar em cada issue

Sempre que receber este arquivo e uma issue, a IA deve seguir estas
regras:

1.  Ler este documento inteiro para compreender o tema, os objetivos, a
    metodologia e as decisões do grupo.
2.  Identificar o título, a descrição, a sprint e os critérios de aceite
    da issue enviada.
3.  Traduzir a issue genérica em tarefas concretas relacionadas ao
    experimento PostgreSQL 17 × PostgreSQL 18.
4.  Trabalhar **somente no escopo da issue atual**.
5.  Não executar automaticamente outras issues, mesmo que estejam
    descritas ou sejam previsíveis.
6.  Não antecipar a coleta definitiva, análise estatística ou
    apresentação se a issue atual não pedir isso.
7.  Antes de alterar arquivos ou executar comandos potencialmente
    destrutivos, explicar o que será feito e preservar dados existentes.
8.  Reutilizar a estrutura, os scripts e as decisões já existentes no
    projeto. Inspecionar o projeto antes de criar arquivos duplicados.
9.  Não inventar resultados, fontes, números de impacto ou evidências.
    Quando algo depender de pesquisa ou execução, obter a evidência e
    registrar sua origem.
10. Se faltar uma decisão importante, apontar a lacuna e propor uma
    opção justificada. Não fingir que a equipe já aprovou uma decisão.
11. Registrar decisões metodológicas, parâmetros, comandos e resultados
    de forma reproduzível.
12. Ao concluir, informar o que foi feito, quais arquivos foram criados
    ou alterados, como validar o resultado e o que ficou pendente.
13. Se a issue não puder ser concluída por falta de ferramenta,
    permissão ou informação, explicar precisamente o bloqueio em vez de
    simular a execução.
14. Não modificar o escopo do experimento sem sinalizar a mudança e sua
    justificativa.

### Prompt curto para acompanhar cada issue

A equipe pode enviar a seguinte instrução junto com a issue:

> Leia o arquivo de contextualização do LAB05 e use-o como referência
> para compreender nosso experimento sobre PostgreSQL 17 e PostgreSQL
> 18. Agora execute somente o que é solicitado na issue que estou
> enviando. Transforme os itens genéricos da issue em atividades
> concretas relacionadas ao nosso tema. Respeite o escopo e a sprint
> atual, não antecipe outras issues e não faça etapas futuras por conta
> própria. Inspecione os arquivos existentes antes de criar ou alterar
> qualquer coisa. Ao final, apresente o que foi realizado, os arquivos
> modificados, como validar e as pendências.

## 16. Critério de qualidade do projeto

O trabalho estará bem encaminhado se outra pessoa conseguir:

1.  Entender por que o PostgreSQL foi escolhido.
2.  Identificar exatamente o que está sendo comparado.
3.  Recriar os ambientes Docker.
4.  Reexecutar a mesma carga de trabalho.
5.  Encontrar os dados brutos e os scripts utilizados.
6.  Reproduzir as análises e os gráficos.
7.  Entender como as conclusões foram obtidas.
8.  Reconhecer as limitações e ameaças à validade.

**Resultado esperado:** um experimento acadêmico reproduzível, com
evidências quantitativas e análise crítica, capaz de responder à
pergunta de pesquisa e explicar o significado dos resultados sem
extrapolar o que os dados permitem concluir.
