from decimal import Decimal

import pytest

from katas.kata_02_transacoes import resumir_transacoes


def test_calcula_saldo_e_quantidade_por_conta():
    transacoes = [
        {"conta": "A", "tipo": "credito", "valor": "10.50"},
        {"conta": "A", "tipo": "debito", "valor": "3.25"},
        {"conta": "B", "tipo": "credito", "valor": "4.00"},
    ]

    assert resumir_transacoes(transacoes) == {
        "A": {"saldo": Decimal("7.25"), "quantidade": 2},
        "B": {"saldo": Decimal("4.00"), "quantidade": 1},
    }


def test_contas_sao_ordenadas_no_resultado():
    transacoes = [
        {"conta": "Z", "tipo": "credito", "valor": "1"},
        {"conta": "A", "tipo": "credito", "valor": "2"},
    ]

    assert list(resumir_transacoes(transacoes)) == ["A", "Z"]


def test_lista_vazia_retorna_dicionario_vazio():
    assert resumir_transacoes([]) == {}


def test_valores_negativos_sao_rejeitados():
    transacao = [{"conta": "A", "tipo": "credito", "valor": "-1"}]

    with pytest.raises(ValueError):
        resumir_transacoes(transacao)


def test_tipo_desconhecido_e_rejeitado():
    transacao = [{"conta": "A", "tipo": "transferencia", "valor": "1"}]

    with pytest.raises(ValueError):
        resumir_transacoes(transacao)


def test_conta_obrigatoria_e_rejeitada_quando_vazia():
    transacao = [{"conta": "", "tipo": "credito", "valor": "1"}]

    with pytest.raises(ValueError):
        resumir_transacoes(transacao)