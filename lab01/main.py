import sys
from datetime import datetime, timezone
from graphql_client import execute_query

# Query para os 100 repositorios mais populares
QUERY = """
query {
  search(query: "stars:>1 sort:stars-desc", type: REPOSITORY, first: 100) {
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
  }
}
"""

def main():
    try:
        print("Buscando dados no GitHub API...")
        dados = execute_query(QUERY)
        
        repos = []
        for edge in dados["data"]["search"]["edges"]:
            if edge and edge.get("node"):
                repos.append(edge["node"])
                
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
            
            # Calcula a idade
            data_criacao = datetime.fromisoformat(criado_em.replace("Z", "+00:00"))
            diferenca = agora - data_criacao
            
            anos = diferenca.days // 365
            dias_restantes = diferenca.days % 365

            # Calcula o tempo desde o ultimo push
            data_ultimo_push = datetime.fromisoformat(ultimo_push.replace("Z", "+00:00"))
            diferenca_push = agora - data_ultimo_push
            dias_ultimo_push = diferenca_push.days
                        
            
            print(f"\n{i}. {nome}")
            print(f"   Estrelas: {estrelas}")
            print(f"   Criado em: {criado_em}")
            print(f"   Idade: {anos} anos e {dias_restantes} dias ({diferenca.days} dias no total)")
            print(f"   PRs Merged: {prs_merged}")
            print(f"   Releases: {total_releases}")
            print(f"   Dias desde o ultimo push: {dias_ultimo_push} dias")
            
    except Exception as e:
        print(f"Erro ao executar o script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
