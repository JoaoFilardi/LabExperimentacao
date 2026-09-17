"""Kata 01: consolidacao de intervalos de atendimento."""


def mesclar_intervalos(intervalos):
    """Retorna intervalos ordenados, sem sobreposicao e sem lacunas de um minuto."""
    if not intervalos:
        return []

    for inicio, fim in intervalos:
        if inicio > fim:
            raise ValueError("inicio nao pode ser maior que o fim")

    ordenados = sorted(intervalos, key=lambda x: (x[0], x[1]))
    mesclados = []

    atual_inicio, atual_fim = ordenados[0]

    for proximo_inicio, proximo_fim in ordenados[1:]:
        # Mescla se houver sobreposicao ou se forem contiguos (sem lacuna de 1 min)
        if proximo_inicio <= atual_fim + 1:
            atual_fim = max(atual_fim, proximo_fim)
        else:
            mesclados.append((atual_inicio, atual_fim))
            atual_inicio, atual_fim = proximo_inicio, proximo_fim

    mesclados.append((atual_inicio, atual_fim))
    return mesclados