"""Kata 03: deteccao de janelas de temperatura validas."""


def contar_janelas_validas(temperaturas, tamanho, limite):
    if tamanho <= 0:
        raise ValueError("Tamanho invalido")

    if not temperaturas or tamanho > len(temperaturas):
        return 0

    janelas_validas = 0
    total_elementos = len(temperaturas)

    for i in range(total_elementos - tamanho + 1):
        janela = temperaturas[i : i + tamanho]
        media = sum(janela) / tamanho

        if media <= limite or limite in janela:
            janelas_validas += 1

    return janelas_validas