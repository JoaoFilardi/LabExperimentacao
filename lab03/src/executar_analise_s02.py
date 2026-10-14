"""Executa a análise da issue #34: concordância, consenso e avaliação da heurística.

Uso (na raiz do repositório, SÓ depois de concluídas as três rotulagens):
    python -m lab03.src.executar_analise_s02 \
        --kayque lab03/data/rotulagem_amostra_ouro_kayque.csv \
        --joao   lab03/data/rotulagem_amostra_ouro_joao.csv \
        --tiago  lab03/data/rotulagem_amostra_ouro_tiago.csv \
        [--desempates lab03/data/desempates_consenso.csv]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .concordancia import calcular_concordancia, carregar, divergencias, verificar_amostra
from .consenso import carregar_desempates, construir_consenso
from .heuristica_corretiva import avaliar_versoes


def main() -> int:
    p = argparse.ArgumentParser(description="Análise de concordância, consenso e heurística (LAB03S02)")
    p.add_argument("--kayque", required=True)
    p.add_argument("--joao", required=True)
    p.add_argument("--tiago", required=True)
    p.add_argument("--desempates", default=None)
    p.add_argument("--saida", default="lab03/data")
    a = p.parse_args()

    dfs = carregar({"kayque": a.kayque, "joao": a.joao, "tiago": a.tiago})
    erros = verificar_amostra(dfs)
    if erros:
        print("Arquivos inconsistentes, análise interrompida:")
        for e in erros:
            print(f" - {e}")
        return 1

    out = Path(a.saida)
    out.mkdir(parents=True, exist_ok=True)

    conc = calcular_concordancia(dfs)
    conc.to_csv(out / "concordancia_fleiss.csv", index=False, encoding="utf-8")
    print(conc.to_string(index=False))

    div = divergencias(dfs)
    div.to_csv(out / "divergencias.csv", index=False, encoding="utf-8")
    print(f"\nDivergências: {len(div)} (em {out / 'divergencias.csv'})")

    final, pend = construir_consenso(dfs, carregar_desempates(a.desempates))
    final.to_csv(out / "amostra_ouro_final.csv", index=False, encoding="utf-8")
    pend.to_csv(out / "pendencias_consenso.csv", index=False, encoding="utf-8")
    if len(pend):
        print(f"ATENÇÃO: {len(pend)} caso(s) sem maioria; decidir em grupo e registrar em --desempates.")

    res = avaliar_versoes(final)
    res.to_csv(out / "heuristica_avaliacao.csv", index=False, encoding="utf-8")
    print("\nAvaliação da heurística (versões avaliadas):")
    print(res.to_string(index=False))
    if not res.iloc[-1]["atingiu_limiar"]:
        print("F1 < 0,70 em todas as versões: refinar a heurística (adicionar versão em HEURISTICAS).")
    return 0


if __name__ == "__main__":
    sys.exit(main())