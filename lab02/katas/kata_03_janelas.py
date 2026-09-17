"""Kata 03: deteccao de janelas de temperatura validas."""


def contar_janelas_validas(temperaturas, tamanho, limite):
    """Conta janelas consecutivas cuja temperatura media nao excede o limite."""
    if tamanho <= 0:
        raise ValueError("tamanho deve ser um inteiro positivo")

    total = len(temperaturas)
    if total < tamanho:
        return 0

    validas = 0
    for inicio in range(total - tamanho + 1):
        janela = temperaturas[inicio:inicio + tamanho]
        media = sum(janela) / tamanho
        if media <= limite:
            validas += 1

    return validas