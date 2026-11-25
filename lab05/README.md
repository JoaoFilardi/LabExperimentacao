LAB05 — Laboratório 05 · 20 pontos

Curso

Engenharia de Software

Disciplina

Laboratório de Experimentação de Software

Turno

Noite

Período / Sala

6º

Professor(a)

Danilo Maia

# Experimento em software real: medindo o que importa em produção

## 1. Objetivo

Planejar, executar e analisar um **experimento sobre um software real**, que esteja **em operação** e tenha **alto impacto** em empresas ou em um grande conjunto de usuários.

Este é o laboratório mais aberto do semestre. **O grupo escolhe o software, a pergunta, o tipo de estudo, as métricas, o formato do documento e o formato da apresentação.** O que se avalia é a qualidade das escolhas e a forma como o grupo aplica o que aprendeu:

- na disciplina teórica de **Medição e Experimentação** (seção 3);
- nos **laboratórios anteriores** desta disciplina (seção 4).

No fim, o grupo responde a duas perguntas: **"o que o estudo mostrou?"** e **"o que isso significa para quem usa esse software?"**

## 2. O software: real, em operação e de alto impacto

**a) Critérios sugeridos.** O ideal é que o software atenda aos três critérios abaixo, com evidências (números e fontes):

| Critério         | O que significa                                                          | Evidência esperada                                                         |
| :--------------- | :----------------------------------------------------------------------- | :------------------------------------------------------------------------- |
| **Real**         | Software que existe e é usado de fato, não um protótipo feito pelo grupo | Site oficial, repositório, documentação                                    |
| **Em operação**  | Usado hoje em produção, em uma versão mantida                            | Versão atual, data do último release, empresas ou órgãos que o usam        |
| **Alto impacto** | Afeta muitas empresas ou muitos usuários                                 | Nº de usuários, downloads, empresas, instalações ou transações (com fonte) |

**Atenção:** não são aceitos **repositórios públicos do GitHub** como objeto de pesquisa (por exemplo, minerar commits, issues ou pull requests, ou analisar o código-fonte de projetos open source, como nos Labs 01 e 03). O foco deste laboratório é o **software em operação**, não o seu repositório.

**b) Inspirações.** Os caminhos abaixo são **ideias, não uma lista fechada**. O grupo pode seguir um deles, **combinar vários** ou propor algo totalmente diferente:

| Caminho                                   | Ideia                                                                              | Exemplos                                                                                                                                         |
| :---------------------------------------- | :--------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------- |
| **Rodar o software no ambiente do grupo** | Usar a mesma versão que roda em produção e variar versões, configurações ou cargas | PostgreSQL 15 × 17; Redis × Valkey; Nginx com gzip × brotli; Python 3.11 × 3.13; Node.js 20 × 22                                                 |
| **Medir o serviço de fora**               | Observar o software em produção como um usuário comum                              | Desempenho e acessibilidade de sites gov.br; tempo de resposta de APIs públicas ao longo do dia; peso das páginas de grandes e-commerces         |
| **Estudar com pessoas**                   | Participantes usam o software real e o grupo mede tempo, erros e satisfação        | App × site de um serviço público; dois apps de banco digital; IDE com e sem assistente de IA                                                     |
| **Analisar dados de operação**            | Usar dados publicados sobre o funcionamento do software em produção                | Disponibilidade e incidentes em páginas de status; postmortems públicos; dados abertos de atendimento de serviços digitais do governo            |
| **Ouvir quem usa ou mantém**              | Survey ou entrevistas com usuários ou desenvolvedores do software                  | Percepção de qualidade de um app público; práticas de teste de mantenedores de uma biblioteca popular                                            |
| **Avaliar a qualidade do produto**        | Avaliar características da ISO/IEC 25010 no software em uso                        | Acessibilidade (WCAG) de serviços públicos com axe ou Lighthouse; segurança de cabeçalhos HTTP; compatibilidade entre navegadores e dispositivos |
| **Outro caminho**                         | Qualquer proposta que atenda aos critérios da seção 2a                             | A combinar com o professor na S01                                                                                                                |

Estudos que **combinam caminhos** (por exemplo, analisar dados de operação e depois confirmar com um experimento controlado, ou medir e depois entrevistar) tendem a gerar evidência mais forte e são valorizados.

**Cuidados de ética:** não faça teste de carga ou de estresse em sistema de terceiros. Ao medir serviços de fora, respeite os termos de uso e o robots.txt e use no máximo 1 requisição por segundo. Não colete dados pessoais. Com participantes, obtenha consentimento e não use contas ou dados reais deles.

## 3. O que vem da disciplina teórica (Medição e Experimentação)

O grupo escolhe **quais conceitos fazem sentido** para o seu estudo. Sugestões de pontos de referência:

| Tema                                        | Como pode aparecer no estudo                                                                                    |
| :------------------------------------------ | :-------------------------------------------------------------------------------------------------------------- |
| **Medição e armadilhas**                    | Lei de Goodhart, Campbell, Falácia de McNamara: a métrica escolhida pode ser "jogada"?                          |
| **GQM**                                     | Objetivo no template de Basili, perguntas e métricas                                                            |
| **Entidades e atributos**                   | Produto, processo ou recurso; atributo interno ou externo; medida direta ou derivada                            |
| **Escalas**                                 | Escala de cada métrica e as estatísticas permitidas para ela                                                    |
| **Métricas de produto, processo e recurso** | LOC, CK, Halstead, complexidade, ISO/IEC 25010, MTBF/MTTR, DORA, SLI/SLO                                        |
| **Categorias de pesquisa**                  | Natureza, objetivos, abordagem, procedimentos, tempo, controle e nível de evidência, cada uma com justificativa |
| **Planejamento de experimentos**            | Hipóteses, variáveis, sujeitos ou objetos, design, instrumentação, operação                                     |
| **Ameaças à validade**                      | Conclusão, interna, construto e externa, com mitigação                                                          |
| **Análise**                                 | Estatística descritiva, teste de hipótese adequado, tamanho do efeito                                           |

**Sugestão:** classificar o estudo nas **7 categorias de pesquisa** da Aula 8, com justificativa, e discutir as **ameaças à validade** costuma enriquecer qualquer caminho.

## 4. O que vem dos laboratórios anteriores

O grupo pode reaproveitar o que já construiu e praticou. Sugestões:

| Laboratório | O que pode ser reaproveitado                                                                                               |
| :---------- | :------------------------------------------------------------------------------------------------------------------------- |
| **Lab01**   | Coleta automatizada de dados via API e Kanban no GitHub Projects                                                           |
| **Lab02**   | Desenho de experimento com tratamentos e participantes (LLM × codificação manual)                                          |
| **Lab03**   | Conceitos das métricas DORA (lead time, frequência, falhas, recuperação), aplicados agora à operação do software escolhido |
| **Lab04**   | Escolha do teste de hipótese, simulação de erro tipo I e poder, dashboard                                                  |

Uma sugestão para a apresentação é mostrar **o que foi reaproveitado e o que foi feito de novo**.

## 5. Impacto: o que o resultado significa para quem usa

Traduza o resultado do estudo para **o mundo real** do software escolhido. Exemplos:

- *"A versão 17 respondeu 18% mais rápido. Com X milhões de consultas por dia nas empresas que usam o PostgreSQL, isso equivale a Y horas de CPU economizadas por dia."*
- *"Os sites gov.br levam em média 9 s para carregar no celular. Com Z milhões de acessos por mês, os cidadãos passam W horas por mês esperando."*

O grupo decide como medir e mostrar o impacto. Sugere-se usar **números públicos e com fonte** e deixar claro **o que não é possível afirmar** (os limites de generalizar o resultado, ligados à validade externa).

## 6. Responsabilidades do trio

A divisão abaixo é uma **sugestão**. O grupo pode adaptá-la como preferir.

| Integrante | Papel sugerido            | Responsável por                                                                                                   |
| :--------- | :------------------------ | :---------------------------------------------------------------------------------------------------------------- |
| **A**      | Planejamento e Método     | Escolha do software e comprovação dos três critérios, categorias da pesquisa, GQM, hipóteses e ameaças à validade |
| **B**      | Instrumentação e Operação | Ambiente ou roteiro de coleta, scripts, execução do estudo, regras de ética e validação dos dados                 |
| **C**      | Análise e Impacto         | Estatística descritiva, testes de hipótese, tamanho do efeito, visualizações e estimativa de impacto              |

## 7. Sprints

**O conteúdo de cada sprint é uma sugestão:** o grupo pode reorganizar as atividades conforme o caminho escolhido (por exemplo, um estudo longitudinal se beneficia de começar a coletar cedo; um survey pode precisar de mais tempo de divulgação).

| Sprint                             | Pontos | Sugestão de conteúdo                                                                                                                                                                    |
| :--------------------------------- | :----- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Lab05S01**                       | 5      | Proposta: software com evidências dos três critérios + pergunta de pesquisa + caminho(s) escolhido(s) + primeira versão das 7 categorias + plano de coleta e de análise + coleta piloto |
| **Lab05S02**                       | 5      | Coleta completa + dados validados e versionados + análise (descritiva, testes e tamanho do efeito, quando couber) + ameaças à validade                                                  |
| **Lab05S03**                       | 5      | Impacto para empresas ou usuários + 7 categorias revisadas e justificadas + conclusões e limitações + rascunho do documento e da apresentação                                           |
| **Documento Final e Apresentação** | 5      | Documento e apresentação de **10 minutos**, ambos em **formato livre** (seção 8)                                                                                                        |

Link do repositório/GitHub Projects: `<preencher>`

## 8. Documento e apresentação: formato livre

**O formato é escolha do grupo**, tanto do documento quanto da apresentação. Alguns exemplos:

- **Documento:** relatório, artigo no formato de conferência (SBC ou IEEE), dashboard interativo, notebook comentado, site, post técnico, README completo.
- **Apresentação:** slides, demonstração ao vivo, vídeo, pôster, reunião simulada com um CTO ou com o gestor do serviço público, defesa no formato de banca.

**A criatividade conta.** Sugestões do que abordar, em qualquer formato:

1. O software, e por que ele é real, está em operação e tem alto impacto (com números).
2. A pergunta de pesquisa e o caminho escolhido para respondê-la.
3. As **7 categorias da pesquisa**, com a justificativa de cada uma.
4. Os conceitos da disciplina teórica aplicados corretamente (seção 3).
5. O que foi reaproveitado dos laboratórios anteriores (seção 4).
6. Os resultados, com a análise adequada ao tipo de dado e à escala das métricas.
7. As ameaças à validade (dos 4 tipos).
8. O impacto para empresas ou usuários e o que **não é possível** afirmar.

O professor pode pedir a qualquer integrante que explique qualquer parte, inclusive as que não apresentou.

## 9. Pontuação e prazo

**Prazo final:** conforme cronograma da disciplina. **Valor total:** 20 pontos.

## 10. Dúvidas frequentes

**Precisamos seguir um dos caminhos da seção 2?** Não. Eles são inspirações. O grupo pode combinar caminhos ou propor outro.

**Precisa ser um experimento controlado?** Não. Um estudo quase-experimental, observacional, um survey ou uma análise de dados de operação também valem. O importante é classificar corretamente o que foi feito e discutir o que isso significa para a força da evidência.

**Podemos testar o desempenho de um site ou de uma API de outra empresa?** Só medindo de fora, como um usuário comum, com no máximo 1 requisição por segundo. Teste de carga em sistema de terceiros não deve ser feito, porque pode derrubar o serviço e violar os termos de uso. Para testar sob carga, rode o software no ambiente de vocês.

**Um software de código aberto rodando na nossa máquina conta como "em operação"?** Sim, especialmente se for a mesma versão (ou a versão mantida) que empresas usam em produção.

**Podemos estudar um repositório público do GitHub?** Não. Repositórios públicos do GitHub não são aceitos como pesquisa (mineração de commits, issues, pull requests ou análise do código-fonte), porque já foram explorados nos Labs 01 e 03. Rodar no ambiente do grupo um software open source usado em produção (ex.: PostgreSQL) continua valendo: nesse caso o objeto de pesquisa é o software em funcionamento, não o repositório.

**Dois grupos podem estudar o mesmo software?** Não. Cada grupo estuda um software diferente.

**Onde encontro os números de impacto?** Relatórios oficiais (ex.: painéis do gov.br), páginas de clientes do fornecedor, downloads no PyPI, npm ou Docker Hub, pesquisas como o Stack Overflow Developer Survey e o DB-Engines. Sugere-se informar o link e a data de acesso.