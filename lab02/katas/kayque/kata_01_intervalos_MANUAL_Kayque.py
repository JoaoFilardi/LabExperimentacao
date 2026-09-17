"""Kata 01: consolidacao de intervalos de atendimento."""


def mesclar_intervalos(intervalos):
    """Retorna intervalos ordenados, sem sobreposicao e sem lacunas de um minuto."""
    if not intervalos:
        return []

    ordenados = sorted(intervalos, key=lambda item: (item[0], item[1]))
    mesclados = []

    for inicio, fim in ordenados:
        if inicio > fim:
            raise ValueError("inicio nao pode ser maior que o fim")

        if not mesclados or inicio > mesclados[-1][1] + 1:
            mesclados.append([inicio, fim])
        else:
            mesclados[-1][1] = max(mesclados[-1][1], fim)

    return [(inicio, fim) for inicio, fim in mesclados]
