import sys
import csv
import os
from datetime import datetime, timezone
from graphql_client import execute_query

# Query para os repositorios mais populares 
QUERY = """
query($quantidade: Int!, $depois: String) {
  search(query: "stars:>1 sort:stars-desc", type: REPOSITORY, first: $quantidade, after: $depois) {
    pageInfo {
      hasNextPage
      endCursor
    }
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
          primaryLanguage {
            name
          }
          issues {
            totalCount
          }
          closedIssues: issues(states: CLOSED) {
            totalCount
          }
        }
      }
    }
  }
}
"""

def exibir_amostra(repos_amostra):
    """Exibe no console uma amostra formatada de repositorios."""
    print("\n--- Amostra dos 10 primeiros repositorios ---")
    for i, repo in enumerate(repos_amostra, start=1):
        # Verifica se o formato e o retornado pela API (dicionario) ou pelo CSV (lista de strings)
        if isinstance(repo, dict):
            nome = repo["nameWithOwner"]
            estrelas = repo["stargazerCount"]
            criado_em = repo["createdAt"]
            prs_merged = repo["pullRequests"]["totalCount"] if repo.get("pullRequests") else 0
            total_releases = repo["releases"]["totalCount"] if repo.get("releases") else 0
            ultimo_push = repo["pushedAt"]
            
            lang_node = repo["primaryLanguage"]
            linguagem = lang_node["name"] if lang_node else "N/A"
            
            total_issues = repo["issues"]["totalCount"] if repo.get("issues") else 0
            issues_fechadas = repo["closedIssues"]["totalCount"] if repo.get("closedIssues") else 0
            
            # Calculos
            data_criacao = datetime.fromisoformat(criado_em.replace("Z", "+00:00"))
            diferenca_idade = datetime.now(timezone.utc) - data_criacao
            anos_idade = diferenca_idade.days // 365
            dias_restantes = diferenca_idade.days % 365
            
            data_ultimo_push = datetime.fromisoformat(ultimo_push.replace("Z", "+00:00"))
            dias_ultimo_push = (datetime.now(timezone.utc) - data_ultimo_push).days
            
            if total_issues > 0:
                razao_issues = f"{(issues_fechadas / total_issues) * 100:.2f}%"
            else:
                razao_issues = "0.00%"
        else:
            # Formato vindo do CSV (lista de strings)
            # Ordem gravada: nome, estrelas, criado_em, anos, dias, total_dias, prs, releases, dias_push, lang, total_iss, fechadas_iss, razao
            nome, estrelas, criado_em, anos_idade, dias_restantes, _, prs_merged, total_releases, dias_ultimo_push, linguagem, total_issues, issues_fechadas, razao_issues = repo
            # Adiciona o '%' caso nao tenha vindo formatado
            if not razao_issues.endswith("%"):
                razao_issues = f"{razao_issues}%"
                
        print(f"\n{i}. {nome} ({linguagem})")
        print(f"   Estrelas: {estrelas}")
        print(f"   Criado em: {criado_em} (Idade: {anos_idade} anos e {dias_restantes} dias)")
        print(f"   PRs Merged: {prs_merged} | Releases: {total_releases} | Ultimo Push: {dias_ultimo_push} dias atras")
        print(f"   Issues: {issues_fechadas}/{total_issues} ({razao_issues})")

def carregar_dados_locais():
    """Carrega a amostra direto do CSV local sem fazer novas requisicoes à API."""
    csv_path = "lab01/repositorios_1000.csv"
    if not os.path.exists(csv_path):
        print(f"\n[Aviso] O arquivo '{csv_path}' nao existe. Selecione a opcao de minerar primeiro.")
        return
        
    try:
        repos_amostra = []
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader) # Pula cabecalho
            for _ in range(10):
                try:
                    linha = next(reader)
                    repos_amostra.append(linha)
                except StopIteration:
                    break
                    
        if repos_amostra:
            exibir_amostra(repos_amostra)
        else:
            print("\nO arquivo CSV esta vazio.")
    except Exception as e:
        print(f"Erro ao ler os dados do arquivo local: {e}")

def minerar_dados():
    """Realiza a consulta GraphQL completa de 1000 itens e exporta para o CSV."""
    try:
        repos = []
        limite = 1000
        tamanho_lote = 10
        depois = None
        
        print("\nIniciando a mineracao GraphQL do GitHub em lotes para evitar timeouts (502)...")
        
        while len(repos) < limite:
            print(f"Buscando lote (ja temos {len(repos)}/{limite})...")
            variables = {"quantidade": tamanho_lote, "depois": depois}
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
            
        print(f"Sucesso! Foram minerados {len(repos)} repositorios.")
        
        # Escrita no arquivo CSV
        csv_path = "lab01/repositorios_1000.csv"
        print(f"Salvando dados em {csv_path}...")
        
        agora = datetime.now(timezone.utc)
        
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            # Cabecalho do CSV
            writer.writerow([
                "nome", "estrelas", "data_criacao", "idade_anos", "idade_dias", 
                "idade_total_dias", "prs_merged", "total_releases", "dias_ultimo_push", 
                "linguagem_primaria", "issues_total", "issues_fechadas", "razao_issues_fechadas"
            ])
            
            for repo in repos:
                nome = repo["nameWithOwner"]
                estrelas = repo["stargazerCount"]
                criado_em = repo["createdAt"]
                prs_merged = repo["pullRequests"]["totalCount"] if repo.get("pullRequests") else 0
                total_releases = repo["releases"]["totalCount"] if repo.get("releases") else 0
                ultimo_push = repo["pushedAt"]
                
                lang_node = repo["primaryLanguage"]
                linguagem = lang_node["name"] if lang_node else "N/A"
                
                total_issues = repo["issues"]["totalCount"] if repo.get("issues") else 0
                issues_fechadas = repo["closedIssues"]["totalCount"] if repo.get("closedIssues") else 0
                
                # Calculos necessarios para exportacao
                data_criacao = datetime.fromisoformat(criado_em.replace("Z", "+00:00"))
                diferenca_idade = agora - data_criacao
                anos_idade = diferenca_idade.days // 365
                dias_restantes = diferenca_idade.days % 365
                
                data_ultimo_push = datetime.fromisoformat(ultimo_push.replace("Z", "+00:00"))
                diferenca_push = agora - data_ultimo_push
                dias_ultimo_push = diferenca_push.days
                
                if total_issues > 0:
                    razao_issues = (issues_fechadas / total_issues) * 100
                else:
                    razao_issues = 0.0
                    
                writer.writerow([
                    nome, estrelas, criado_em, anos_idade, dias_restantes, 
                    diferenca_idade.days, prs_merged, total_releases, dias_ultimo_push, 
                    linguagem, total_issues, issues_fechadas, f"{razao_issues:.2f}"
                ])
                
        print("Exportacao concluida com sucesso!")
        
        # Mostra a amostra dos 10 primeiros
        exibir_amostra(repos[:10])
            
    except Exception as e:
        print(f"Erro durante a mineracao de dados: {e}")

def main():
    while True:
        print("\n================ MENU ================")
        print("1. Exibir amostra dos dados locais (CSV)")
        print("2. Minerar dados do GitHub de novo (gera CSV)")
        print("3. Sair")
        print("======================================")
        opcao = input("Escolha uma opcao (1-3): ").strip()
        
        if opcao == "1":
            carregar_dados_locais()
        elif opcao == "2":
            minerar_dados()
        elif opcao == "3":
            print("Saindo do programa. Ate mais!")
            break
        else:
            print("Opcao invalida. Digite 1, 2 ou 3.")

if __name__ == "__main__":
    main()
