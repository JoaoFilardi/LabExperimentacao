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
            
            # Calcula a idade
            data_criacao = datetime.fromisoformat(criado_em.replace("Z", "+00:00"))
            diferenca = agora - data_criacao
            
            anos = diferenca.days // 365
            dias_restantes = diferenca.days % 365
            
            print(f"\n{i}. {nome}")
            print(f"   Estrelas: {estrelas}")
            print(f"   Criado em: {criado_em}")
            print(f"   Idade: {anos} anos e {dias_restantes} dias ({diferenca.days} dias no total)")
            print(f"   PRs Merged: {prs_merged}")
            
    except Exception as e:
        print(f"Erro ao executar o script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
