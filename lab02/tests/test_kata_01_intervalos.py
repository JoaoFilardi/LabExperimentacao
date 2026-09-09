import pytest

from katas.kata_01_intervalos import mesclar_intervalos


def test_ordena_e_mescla_intervalos_sobrepostos():
    intervalos = [(9, 12), (1, 4), (3, 7), (15, 18)]

    assert mesclar_intervalos(intervalos) == [(1, 7), (9, 12), (15, 18)]


def test_mescla_intervalos_que_encostam():
    assert mesclar_intervalos([(1, 3), (4, 6), (8, 9)]) == [(1, 6), (8, 9)]


def test_preserva_intervalos_separados():
    assert mesclar_intervalos([(2, 2), (5, 8)]) == [(2, 2), (5, 8)]


def test_lista_vazia_retorna_lista_vazia():
    assert mesclar_intervalos([]) == []


def test_rejeita_inicio_maior_que_fim():
    with pytest.raises(ValueError):
        mesclar_intervalos([(5, 2)])


def test_nao_modifica_a_lista_recebida():
    intervalos = [(4, 6), (1, 2)]

    mesclar_intervalos(intervalos)

    assert intervalos == [(4, 6), (1, 2)]