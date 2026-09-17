"""Kata 04: planejamento de reposicao de estoque."""


def planejar_reposicao(produtos, estoque_minimo):
    """Retorna produtos abaixo do minimo."""

    if estoque_minimo < 0:
        raise ValueError("estoque minimo nao pode ser negativo")

    reposicao = []

    for produto in produtos:
        nome = produto["nome"]
        estoque = produto["estoque"]

        if estoque < 0:
            raise ValueError("estoque nao pode ser negativo")

        if estoque < estoque_minimo:
            quantidade = estoque_minimo - estoque

            reposicao.append({
                "nome": nome,
                "repor": quantidade
            })

    reposicao.sort(key=lambda produto: (-produto["repor"], produto["nome"]))

    return reposicao