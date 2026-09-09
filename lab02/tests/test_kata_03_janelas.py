import pytest

from katas.kata_03_janelas import contar_janelas_validas


def test_conta_janelas_com_media_abaixo_do_limite():
    temperaturas = [20, 22, 24, 30]

    assert contar_janelas_validas(temperaturas, 2, 25) == 2


def test_media_igual_ao_limite_e_valida():
    assert contar_janelas_validas([10, 20, 30], 2, 20) == 2


def test_janela_de_tamanho_um():
    assert contar_janelas_validas([1, 5, 3], 1, 3) == 2


def test_tamanho_maior_que_a_lista_retorna_zero():
    assert contar_janelas_validas([1, 2], 3, 10) == 0


def test_lista_vazia_retorna_zero():
    assert contar_janelas_validas([], 2, 10) == 0


@pytest.mark.parametrize("tamanho", [0, -1])
def test_tamanho_invalido_e_rejeitado(tamanho):
    with pytest.raises(ValueError):
        contar_janelas_validas([1, 2], tamanho, 10)