"""Kata 03: deteccao de janelas de temperatura validas."""


def contar_janelas_validas(temperaturas, tamanho, limite):
    """Conta janelas consecutivas cuja temperatura media nao excede o limite."""
    if tamanho <= 0:
        raise ValueError("tamanho deve ser positivo")

    if tamanho > len(temperaturas):
        return 0

    janela = temperaturas[:tamanho]
    soma = sum(janela)
    validas = int(soma / tamanho <= limite or limite in janela)

    for indice in range(tamanho, len(temperaturas)):
        soma += temperaturas[indice] - temperaturas[indice - tamanho]
        janela = temperaturas[indice - tamanho + 1 : indice + 1]
        validas += int(soma / tamanho <= limite or limite in janela)

    return validas