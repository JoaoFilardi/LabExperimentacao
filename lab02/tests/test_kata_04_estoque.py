import pytest

from katas.kata_04_estoque import planejar_reposicao


def test_retorna_produtos_abaixo_do_minimo():
    produtos = [
        {"nome": "arroz", "estoque": 3},
        {"nome": "feijao", "estoque": 10},
        {"nome": "oleo", "estoque": 1},
    ]

    assert planejar_reposicao(produtos, 5) == [
        {"nome": "oleo", "repor": 4},
        {"nome": "arroz", "repor": 2},
    ]


def test_ordena_empates_por_nome():
    produtos = [
        {"nome": "banana", "estoque": 3},
        {"nome": "arroz", "estoque": 3},
    ]

    assert planejar_reposicao(produtos, 5) == [
        {"nome": "arroz", "repor": 2},
        {"nome": "banana", "repor": 2},
    ]


def test_estoque_igual_ao_minimo_nao_precisa_repor():
    assert planejar_reposicao([{"nome": "arroz", "estoque": 5}], 5) == []


def test_lista_vazia_retorna_lista_vazia():
    assert planejar_reposicao([], 5) == []


def test_minimo_negativo_e_rejeitado():
    with pytest.raises(ValueError):
        planejar_reposicao([], -1)


def test_estoque_negativo_e_rejeitado():
    produtos = [{"nome": "arroz", "estoque": -1}]

    with pytest.raises(ValueError):
        planejar_reposicao(produtos, 5)