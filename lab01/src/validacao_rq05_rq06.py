import csv
import os
from collections import Counter


def calcular_mediana(valores):
    """Calcula a mediana de uma lista de numeros."""
    ordenados = sorted(valores)
    n = len(ordenados)
    if n == 0:
        return 0
    if n % 2 == 1:
        return ordenados[n // 2]
    else:
        return (ordenados[n // 2 - 1] + ordenados[n // 2]) / 2


def calcular_quartis(valores):
    """Calcula Q1, Q2 (Mediana) e Q3 de uma lista de numeros."""
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
        metade_superior = ordenados[meio + 1:]

    q1 = calcular_mediana(metade_inferior)
    q3 = calcular_mediana(metade_superior)

    return q1, q2, q3


def analisar_rq05_linguagem(linguagens):
    """Valida a coluna categorica 'linguagem_primaria' (RQ05)."""
    total = len(linguagens)
    vazios = sum(1 for l in linguagens if l is None or l.strip() == "")
    sem_linguagem = sum(1 for l in linguagens if l == "N/A")

    contagem = Counter(linguagens)
    distintas = len(contagem)
    top10 = contagem.most_common(10)

    print("\n=== ANALISE DE CONSISTENCIA: RQ05 (Linguagem Primaria) ===")
    print(f"Total de registros: {total}")
    print(f"Valores vazios/ausentes (string vazia): {vazios}")
    print(f"Repositorios sem linguagem primaria definida (N/A): {sem_linguagem} ({sem_linguagem/total*100:.2f}%)")
    print(f"Quantidade de linguagens distintas (excluindo N/A): {distintas - (1 if sem_linguagem else 0)}")
    print("Top 10 linguagens mais frequentes:")
    for lang, qtd in top10:
        print(f"  - {lang}: {qtd} ({qtd/total*100:.2f}%)")

    return {
        "total": total,
        "vazios": vazios,
        "na_count": sem_linguagem,
        "distintas": distintas,
        "top10": top10,
    }


def analisar_rq06_razao_issues(razoes, issues_total):
    """Valida a coluna numerica 'razao_issues_fechadas' (RQ06), em percentual (0-100)."""
    total = len(razoes)
    nulos = sum(1 for v in razoes if v is None)

    validos = [v for v in razoes if v is not None]
    validos_count = len(validos)

    fora_do_intervalo = [v for v in validos if v < 0 or v > 100]

    media = sum(validos) / validos_count
    minimo = min(validos)
    maximo = max(validos)

    q1, q2, q3 = calcular_quartis(validos)
    iqr = q3 - q1
    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr
    outliers = [v for v in validos if v < limite_inferior or v > limite_superior]

    zero_issues_total = sum(1 for t in issues_total if t == 0)
    razao_100 = sum(1 for v in validos if v == 100.0)
    razao_0 = sum(1 for v in validos if v == 0.0)

    print("\n=== ANALISE DE CONSISTENCIA: RQ06 (Razao de Issues Fechadas, %) ===")
    print(f"Total de registros: {total}")
    print(f"Valores nulos/ausentes: {nulos}")
    print(f"Valores fora do intervalo [0, 100]: {len(fora_do_intervalo)}")
    print(f"Minimo: {minimo:.2f}")
    print(f"Maximo: {maximo:.2f}")
    print(f"Media: {media:.2f}")
    print(f"Q1 (25%): {q1:.2f}")
    print(f"Mediana / Q2 (50%): {q2:.2f}")
    print(f"Q3 (75%): {q3:.2f}")
    print(f"IQR: {iqr:.2f}")
    print(f"Limites de outlier: [{limite_inferior:.2f}, {limite_superior:.2f}]")
    print(f"Quantidade de Outliers: {len(outliers)} ({len(outliers)/validos_count*100:.2f}%)")
    print(f"Repositorios com issues_total = 0 (razao definida como 0%): {zero_issues_total} ({zero_issues_total/total*100:.2f}%)")
    print(f"Repositorios com 100% das issues fechadas: {razao_100} ({razao_100/total*100:.2f}%)")
    print(f"Repositorios com 0% das issues fechadas: {razao_0} ({razao_0/total*100:.2f}%)")

    return {
        "nulos": nulos,
        "fora_do_intervalo": len(fora_do_intervalo),
        "min": minimo,
        "max": maximo,
        "media": media,
        "mediana": q2,
        "q1": q1,
        "q3": q3,
        "outliers_count": len(outliers),
        "zero_issues_total": zero_issues_total,
    }


def main():
    csv_path = "lab01/repositorios_1000.csv"
    if not os.path.exists(csv_path):
        csv_path = "repositorios_1000.csv"
    if not os.path.exists(csv_path):
        print(f"Erro: Arquivo de dados nao encontrado. Rode a mineracao primeiro.")
        return

    linguagens = []
    razoes = []
    issues_total = []

    try:
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)

            for i, linha in enumerate(reader, start=1):
                # Coluna 9: linguagem_primaria
                # Coluna 10: issues_total
                # Coluna 12: razao_issues_fechadas
                try:
                    val_lingua = linha[9]
                    val_issues_total = linha[10]
                    val_razao = linha[12]

                    linguagens.append(val_lingua if val_lingua != "" else None)
                    issues_total.append(int(val_issues_total) if val_issues_total != "" else None)
                    razao = float(val_razao) if val_razao != "" else None
                    razoes.append(razao)
                except (IndexError, ValueError) as e:
                    print(f"Erro ao converter linha {i}: {e}")

        analisar_rq05_linguagem([l for l in linguagens if l is not None])
        analisar_rq06_razao_issues(razoes, issues_total)

    except Exception as e:
        print(f"Erro ao ler e processar o CSV: {e}")


if __name__ == "__main__":
    main()
