"""Kata 02: resumo de transacoes de uma conta."""

from decimal import Decimal


def resumir_transacoes(transacoes):
    """Calcula saldo e quantidade de operacoes por conta."""
    if not transacoes:
        return {}

    resumo = {}

    for transacao in transacoes:
        conta = transacao.get("conta")
        tipo = transacao.get("tipo")
        valor = transacao.get("valor")

        if not conta or not conta.strip():
            raise ValueError("conta obrigatoria")

        if tipo not in {"credito", "debito"}:
            raise ValueError("tipo de transacao invalido")

        valor_decimal = Decimal(str(valor))
        if valor_decimal < 0:
            raise ValueError("valor nao pode ser negativo")

        if conta not in resumo:
            resumo[conta] = {"saldo": Decimal("0"), "quantidade": 0}

        if tipo == "credito":
            resumo[conta]["saldo"] += valor_decimal
        else:
            resumo[conta]["saldo"] -= valor_decimal

        resumo[conta]["quantidade"] += 1

    return {conta: resumo[conta] for conta in sorted(resumo)}
