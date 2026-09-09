import csv
import os

def calcular_mediana(valores):
    """Calcula a mediana de uma lista de números."""
    ordenados = sorted(valores)
    n = len(ordenados)
    if n == 0:
        return 0
    if n % 2 == 1:
        return ordenados[n // 2]
    else:
        return (ordenados[n // 2 - 1] + ordenados[n // 2]) / 2

def calcular_quartis(valores):
    """Calcula Q1, Q2 (Mediana) e Q3 de uma lista de números."""
    ordenados = sorted(valores)
    n = len(ordenados)
    if n == 0:
        return 0, 0, 0
    
    q2 = calcular_mediana(ordenados)
    
    meio = n // 2
    if n % 2 == 0:
        metade_inferior = ordenados[:meio]
        metade_superior = ordenados[meio:]
    else:
        metade_inferior = ordenados[:meio]
        metade_superior = ordenados[meio+1:]
        
    q1 = calcular_mediana(metade_inferior)
    q3 = calcular_mediana(metade_superior)
    
    return q1, q2, q3

def analisar_coluna(valores, nome_metrica):
    """Gera estatisticas basicas e identifica outliers usando IQR."""
    total = len(valores)
    nulos = sum(1 for v in valores if v is None)
    
    # Remove None para os calculos
    valores_validos = [v for v in valores if v is not None]
    validos_count = len(valores_validos)
    
    if validos_count == 0:
        print(f"\nSem dados validos para {nome_metrica}.")
        return {}
        
    media = sum(valores_validos) / validos_count
    minimo = min(valores_validos)
    maximo = max(valores_validos)
    
    q1, q2, q3 = calcular_quartis(valores_validos)
    iqr = q3 - q1
    
    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr
    
    outliers = [v for v in valores_validos if v < limite_inferior or v > limite_superior]
    
    print(f"\n=== ANALISE DE CONSISTENCIA: {nome_metrica} ===")
    print(f"Total de registros: {total}")
    print(f"Valores nulos/ausentes: {nulos}")
    print(f"Valores validos analisados: {validos_count}")
    print(f"Minimo: {minimo}")
    print(f"Maximo: {maximo}")
    print(f"Media: {media:.2f}")
    print(f"Q1 (25%): {q1}")
    print(f"Mediana / Q2 (50%): {q2}")
    print(f"Q3 (75%): {q3}")
    print(f"IQR: {iqr:.2f}")
    print(f"Limites de outlier: [{limite_inferior:.2f}, {limite_superior:.2f}]")
    print(f"Quantidade de Outliers: {len(outliers)} ({len(outliers)/validos_count*100:.2f}%)")
    
    return {
        "nulos": nulos,
        "min": minimo,
        "max": maximo,
        "media": media,
        "mediana": q2,
        "q1": q1,
        "q3": q3,
        "outliers_count": len(outliers)
    }

def main():
    csv_path = "lab01/repositorios_1000.csv"
    if not os.path.exists(csv_path):
        print(f"Erro: Arquivo '{csv_path}' nao encontrado. Rode a mineracao primeiro.")
        return

    idades_dias = []
    prs_merged = []
    
    try:
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            
            for i, linha in enumerate(reader, start=1):
                # Coluna 5: idade_total_dias
                # Coluna 6: prs_merged
                try:
                    val_idade = linha[5]
                    val_prs = linha[6]
                    
                    # Checagem de nulos
                    id_dia = int(val_idade) if val_idade != "" else None
                    pr_merged = int(val_prs) if val_prs != "" else None
                    
                    idades_dias.append(id_dia)
                    prs_merged.append(pr_merged)
                except (IndexError, ValueError) as e:
                    print(f"Erro ao converter linha {i}: {e}")
                    
        analiser_rq01 = analisar_coluna(idades_dias, "RQ01 (Idade do Repositorio em dias)")
        analiser_rq02 = analisar_coluna(prs_merged, "RQ02 (Total de PRs Merged)")
        
    except Exception as e:
        print(f"Erro ao ler e processar o CSV: {e}")

if __name__ == "__main__":
    main()
