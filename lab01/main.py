import sys
from datetime import datetime, timezone
from graphql_client import execute_query

# Query para os repositorios mais populares 
QUERY = """
query($quantidade: Int!, $depois: String) {
  search(query: "stars:>1 sort:stars-desc", type: REPOSITORY, first: $quantidade, after: $depois) {
    edges {
      node {
        ... on Repository {
          nameWithOwner
          stargazerCount
          createdAt
          pullRequests(states: MERGED) {
            totalCount
          }
          releases {
            totalCount
          }
          pushedAt
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
"""


def main():
    try:
        repos = []
        limite = 100
        tamanho_lote = 10
        depois = None

        print("Buscando dados no GitHub API...")

        # Busca os repositorios em lotes de 10
        while len(repos) < limite:
            print(f"Buscando lote (ja temos {len(repos)}/100)...")

            variables = {
                "quantidade": tamanho_lote,
                "depois": depois
            }

            dados = execute_query(QUERY, variables)

            search_data = dados["data"]["search"]
            edges = search_data["edges"]

            for edge in edges:
                if edge and edge.get("node") and len(repos) < limite:
                    repos.append(edge["node"])

            page_info = search_data["pageInfo"]

            if not page_info["hasNextPage"]:
                break

            depois = page_info["endCursor"]

        print(f"Sucesso! Encontrados {len(repos)} repositorios.")
        print("\n--- Amostra dos 10 primeiros repositorios ---")

        agora = datetime.now(timezone.utc)

        for i, repo in enumerate(repos[:10], start=1):
            nome = repo["nameWithOwner"]
            estrelas = repo["stargazerCount"]
            criado_em = repo["createdAt"]
            prs_merged = repo["pullRequests"]["totalCount"]

            total_releases = repo["releases"]["totalCount"]
            ultimo_push = repo["pushedAt"]

            # Calcula a idade do repositorio
            data_criacao = datetime.fromisoformat(
                criado_em.replace("Z", "+00:00")
            )
            diferenca = agora - data_criacao

            anos = diferenca.days // 365
            dias_restantes = diferenca.days % 365

            # Calcula o tempo desde o ultimo push
            data_ultimo_push = datetime.fromisoformat(
                ultimo_push.replace("Z", "+00:00")
            )
            diferenca_push = agora - data_ultimo_push
            dias_ultimo_push = diferenca_push.days

            print(f"\n{i}. {nome}")
            print(f"   Estrelas: {estrelas}")
            print(f"   Criado em: {criado_em}")
            print(
                f"   Idade: {anos} anos e {dias_restantes} dias "
                f"({diferenca.days} dias no total)"
            )
            print(f"   PRs Merged: {prs_merged}")
            print(f"   Releases: {total_releases}")
            print(
                f"   Dias desde o ultimo push: "
                f"{dias_ultimo_push} dias"
            )

    except Exception as e:
        print(f"Erro ao executar o script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()