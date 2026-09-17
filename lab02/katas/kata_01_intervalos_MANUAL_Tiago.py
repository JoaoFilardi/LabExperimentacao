def mesclar_intervalos(intervalos):
    if not intervalos:
        return []

    for inicio, fim in intervalos:
        if inicio > fim:
            raise ValueError("inicio nao pode ser maior que o fim")

    intervalos = sorted(intervalos)

    resultado = [intervalos[0]]

    for inicio, fim in intervalos[1:]:
        ultimo_inicio, ultimo_fim = resultado[-1]

        if inicio <= ultimo_fim + 1:
            resultado[-1] = (ultimo_inicio, max(ultimo_fim, fim))
        else:
            resultado.append((inicio, fim))

    return resultado