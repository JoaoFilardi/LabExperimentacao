"""
Script de snapshot do GitHub Projects (v2) via GraphQL.

Objetivo: ao final de cada sprint (S01, S02, S03...), exporta os itens
(Issues) do Project do grupo e o status atual de cada um (coluna do board)
para um CSV. Como a API do GitHub Projects nao guarda historico de mudanca
de coluna, essa serie de snapshots acumulados sprint a sprint e a base de
dados dos Labs 04 e 05.

Reaproveita o mesmo client GraphQL (graphql_client.py) usado na Parte 1
do laboratorio, seguindo a regra da disciplina de nao usar bibliotecas de
terceiros que consultem a API do GitHub.

Configuracao (variaveis de ambiente ou arquivo .env, igual ao GITHUB_TOKEN
usado em graphql_client.py):
    GITHUB_TOKEN        -> token com escopo de leitura do repo e do Project
    PROJECT_OWNER        -> login do usuario ou organizacao dona do Project
    PROJECT_NUMBER        -> numero do Project (v2), visto na URL do board
    PROJECT_OWNER_TYPE    -> "org" ou "user" (padrao: "org")

Uso:
    python lab01/snapshot_projects.py --sprint S02

Saida:
    lab01/snapshot_s02.csv (ou lab01/snapshot_<sprint em minusculo>.csv)
"""

import argparse
import csv
import os
import sys
from datetime import datetime, timezone

from graphql_client import execute_query

QUERY_ORG = """
query($login: String!, $numero: Int!, $depois: String) {
  organization(login: $login) {
    projectV2(number: $numero) {
      title
      url
      items(first: 50, after: $depois) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          fieldValueByName(name: "Status") {
            ... on ProjectV2ItemFieldSingleSelectValue {
              name
            }
          }
          content {
            ... on Issue {
              number
              title
              url
              state
              assignees(first: 5) {
                nodes {
                  login
                }
              }
              createdAt
              updatedAt
              closedAt
            }
          }
        }
      }
    }
  }
}
"""

QUERY_USER = """
query($login: String!, $numero: Int!, $depois: String) {
  user(login: $login) {
    projectV2(number: $numero) {
      title
      url
      items(first: 50, after: $depois) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          id
          fieldValueByName(name: "Status") {
            ... on ProjectV2ItemFieldSingleSelectValue {
              name
            }
          }
          content {
            ... on Issue {
              number
              title
              url
              state
              assignees(first: 5) {
                nodes {
                  login
                }
              }
              createdAt
              updatedAt
              closedAt
            }
          }
        }
      }
    }
  }
}
"""


def carregar_config():
    owner = os.getenv("PROJECT_OWNER")
    numero = os.getenv("PROJECT_NUMBER")
    tipo = os.getenv("PROJECT_OWNER_TYPE", "org").strip().lower()

    for caminho in [".env", "lab01/.env", "../.env"]:
        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8") as f:
                for linha in f:
                    linha = linha.strip()
                    if linha and not linha.startswith("#") and "=" in linha:
                        chave, valor = linha.split("=", 1)
                        chave = chave.strip()
                        valor = valor.strip()
                        if chave == "PROJECT_OWNER" and not owner:
                            owner = valor
                        elif chave == "PROJECT_NUMBER" and not numero:
                            numero = valor
                        elif chave == "PROJECT_OWNER_TYPE" and tipo == "org":
                            tipo = valor.strip().lower()

    if not owner or not numero:
        raise ValueError(
            "PROJECT_OWNER e PROJECT_NUMBER precisam estar definidos "
            "(variavel de ambiente ou arquivo .env). Ex.: PROJECT_OWNER=nome-do-grupo, "
            "PROJECT_NUMBER=1"
        )

    return owner, int(numero), tipo


def buscar_itens_do_project(owner: str, numero: int, tipo: str):
    """Pagina sobre os itens do Project (v2) e retorna a lista completa de nodes."""
    query = QUERY_ORG if tipo == "org" else QUERY_USER
    itens = []
    cursor = None
    project_title = None
    project_url = None

    while True:
        resultado = execute_query(query, {"login": owner, "numero": numero, "depois": cursor})
        raiz = resultado["data"]["organization" if tipo == "org" else "user"]

        if raiz is None or raiz.get("projectV2") is None:
            raise RuntimeError(
                f"Nao foi possivel encontrar o Project numero {numero} para '{owner}' "
                f"(tipo={tipo}). Confira PROJECT_OWNER, PROJECT_NUMBER e PROJECT_OWNER_TYPE."
            )

        project = raiz["projectV2"]
        project_title = project["title"]
        project_url = project["url"]

        pagina = project["items"]
        itens.extend(pagina["nodes"])

        if pagina["pageInfo"]["hasNextPage"]:
            cursor = pagina["pageInfo"]["endCursor"]
        else:
            break

    return project_title, project_url, itens


def montar_linhas_csv(itens, sprint: str):
    data_snapshot = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    linhas = []

    for item in itens:
        conteudo = item.get("content")
        # Ignora "draft issues" (item sem Issue de verdade associada) - o
        # laboratorio pede que todo cartao seja uma Issue rastreavel.
        if not conteudo:
            continue

        status_field = item.get("fieldValueByName")
        status = status_field["name"] if status_field else "Sem Status"

        assignees = conteudo.get("assignees", {}).get("nodes", [])
        assignees_str = ";".join(a["login"] for a in assignees) if assignees else ""

        linhas.append([
            sprint,
            data_snapshot,
            conteudo["number"],
            conteudo["title"],
            conteudo["url"],
            status,
            conteudo["state"],
            assignees_str,
            conteudo.get("createdAt", ""),
            conteudo.get("updatedAt", ""),
            conteudo.get("closedAt") or "",
        ])

    return linhas


def salvar_csv(linhas, caminho_saida: str):
    cabecalho = [
        "sprint", "data_snapshot", "issue_number", "titulo", "url",
        "status_coluna", "estado_issue", "assignees",
        "criada_em", "atualizada_em", "fechada_em",
    ]
    with open(caminho_saida, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(cabecalho)
        writer.writerows(linhas)


def main():
    parser = argparse.ArgumentParser(description="Exporta snapshot do GitHub Projects (v2) para CSV.")
    parser.add_argument("--sprint", required=True, help="Identificador da sprint, ex.: S02")
    args = parser.parse_args()

    sprint = args.sprint.strip().upper()

    try:
        owner, numero, tipo = carregar_config()
        print(f"Consultando Project #{numero} de '{owner}' (tipo={tipo})...")
        titulo, url, itens = buscar_itens_do_project(owner, numero, tipo)
        print(f"Project: {titulo} ({url})")
        print(f"Itens encontrados: {len(itens)}")

        linhas = montar_linhas_csv(itens, sprint)
        print(f"Itens com Issue valida (draft issues ignoradas): {len(linhas)}")

        nome_saida = f"snapshot_{sprint.lower()}.csv"
        caminho_saida = os.path.join("lab01", nome_saida) if os.path.isdir("lab01") else nome_saida
        salvar_csv(linhas, caminho_saida)
        print(f"Snapshot salvo em: {caminho_saida}")

    except Exception as e:
        print(f"Erro ao gerar snapshot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
