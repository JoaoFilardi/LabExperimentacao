"""Kata 04: planejamento de reposicao de estoque.

Trial: Kayque Allan - K4 com IA (Tratamento B)
Issue: #18
"""


def planejar_reposicao(produtos, estoque_minimo):
    """Retorna produtos abaixo do minimo, ordenados por urgencia e nome."""
    if estoque_minimo < 0:
        raise ValueError("estoque_minimo deve ser nao negativo")

    reposicoes = []
    for produto in produtos:
        nome = produto["nome"]
        estoque = produto["estoque"]

        if estoque < 0:
            raise ValueError(f"estoque negativo para o produto {nome!r}")

        if estoque < estoque_minimo:
            reposicoes.append({"nome": nome, "repor": estoque_minimo - estoque})

    reposicoes.sort(key=lambda item: (-item["repor"], item["nome"]))
    return reposicoes
