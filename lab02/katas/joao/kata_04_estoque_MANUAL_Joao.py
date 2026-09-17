"""Kata 04: planejamento de reposicao de estoque."""


def planejar_reposicao(produtos, estoque_minimo):
    if estoque_minimo < 0:
        raise ValueError("Estoque minimo invalido")

    plano = []

    for produto in produtos:
        if produto["estoque"] < 0:
            raise ValueError("Estoque do produto invalido")

        if produto["estoque"] < estoque_minimo:
            repor = estoque_minimo - produto["estoque"]
            plano.append({"nome": produto["nome"], "repor": repor})


    def criterio_ordenacao(item):
        return item["nome"]

    plano.sort(key=criterio_ordenacao)
    plano.sort(key=lambda item: item["repor"], reverse=True)

    return plano
