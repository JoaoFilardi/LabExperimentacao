"""Kata 02: resumo de transacoes de uma conta."""

from decimal import Decimal


def resumir_transacoes(transacoes):
    """Calcula saldo e quantidade de operacoes por conta."""
    resumo = {}

    for transacao in transacoes:
        conta = transacao.get("conta")
        tipo = transacao.get("tipo")
        valor = Decimal(str(transacao.get("valor")))

        if not conta:
            raise ValueError("conta obrigatoria")
        if tipo not in {"credito", "debito"}:
            raise ValueError("tipo de transacao invalido")
        if valor < 0:
            raise ValueError("valor negativo")

        if conta not in resumo:
            resumo[conta] = {"saldo": Decimal("0"), "quantidade": 0}

        resumo[conta]["saldo"] += valor if tipo == "credito" else -valor
        resumo[conta]["quantidade"] += 1

    return dict(sorted(resumo.items()))