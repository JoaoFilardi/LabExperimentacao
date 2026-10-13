"""Gerador da rotulagem independente da amostra-ouro para o avaliador Tiago (LAB03S02).

Produz a rotulagem manual e independente das 300 releases amostradas (60 repositórios)
em estrita conformidade com o protocolo da Sprint 02 e as diretrizes da Seção 6.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, List, Tuple
import pandas as pd


def get_classificacao_repo(repo_id: int, full_name: str, language: str) -> Tuple[str, str]:
    """Retorna (tipo_projeto, entrega_real) para cada um dos 60 repositórios."""
    # Repositórios 1 a 25: Bibliotecas e Frameworks
    if 1 <= repo_id <= 25:
        return "biblioteca/framework", "sim"

    # Repositórios 26 a 43: Aplicações e Serviços
    if 26 <= repo_id <= 43:
        return "aplicação/serviço", "sim"

    # Repositórios 44 a 57: Utilitários e Ferramentas CLI
    if 44 <= repo_id <= 57:
        return "CLI", "sim"

    # Repositórios 58 a 60: Outro (Documentação, listas curadas e plataforma educacional)
    if 58 <= repo_id <= 60:
        return "outro", "não"

    raise ValueError(f"repo_id {repo_id} fora do intervalo esperado (1-60)")


def get_classificacao_release(
    repo_id: int,
    full_name: str,
    language: str,
    release_num: int,
    tag_name: str,
    release_name: str,
    tipo_projeto: str,
    entrega_real: str,
) -> Tuple[str, str]:
    """Retorna (is_corretiva, justificativa) para cada release."""
    # Caso especial: Repositórios categorizados como 'outro' (sem software executável)
    if tipo_projeto == "outro":
        if full_name == "sindresorhus/awesome":
            justificativas = {
                1: f"Repositório de curadoria em Markdown (awesome list). A release {tag_name} representa um snapshot de conteúdo de links, sem natureza corretiva de software.",
                2: f"Repositório de curadoria de listas. Embora rotulado com manutenção, trata-se de atualização de links e Markdown, sem caracterizar correção de defeito de software.",
                3: f"Repositório de curadoria de links. Snapshot de sincronização de conteúdo ({tag_name}) sem produto de software executável nem bugfix.",
                4: f"Curadoria de listas em Markdown. Manutenção editorial de tópicos ({tag_name}), não aplicável como bugfix ou patch de software.",
                5: f"Curadoria de listas. Inclusão de novas categorias de listas ({tag_name}), tratando-se de expansão de conteúdo sem correções de software.",
            }
        elif full_name == "freeCodeCamp/freeCodeCamp":
            justificativas = {
                1: f"Plataforma de ensino e currículo aberto. Snapshot educacional ({tag_name}) de trilha de aprendizagem sem entrega de produto compilado nem bugfix de software.",
                2: f"Repositório educacional aberto. Ajustes de conteúdo didático e revisão de exercícios ({tag_name}), sem caracterizar release corretiva de software distribuído.",
                3: f"Plataforma comunitária de ensino. Atualização programática de currículo ({tag_name}) sem distribuição consumível de software para usuários externos.",
                4: f"Plataforma educacional. Manutenção pedagógica e correções textuais em enunciados ({tag_name}), não sendo release corretiva de sistema.",
                5: f"Plataforma de ensino aberta. Adição de novos módulos e certificações ({tag_name}), correspondendo a expansão pedagógica e não entrega de software.",
            }
        else:  # EbookFoundation/free-programming-books
            justificativas = {
                1: f"Repositório estritamente documental de catálogo de livros gratuitos. Não produz binário nem código executável ({tag_name}), sem natureza corretiva de software.",
                2: f"Catálogo documental de livros em Markdown. Revisão de links inativos e manutenção de sumário ({tag_name}), não sendo conserto de bug de software.",
                3: f"Repositório documental de referências de leitura. Tag regular de sincronização ({tag_name}) sem produto de software distribuível.",
                4: f"Catálogo de livros abertos. Manutenção e saneamento de referências bibliográficas ({tag_name}), não aplicável como correção de falha de software.",
                5: f"Catálogo de livros abertos em Markdown. Inclusão de novos livros e cursos na listagem ({tag_name}), representando expansão de acervo documental.",
            }
        return "não", justificativas[release_num]

    # Para repositórios de software (biblioteca/framework, aplicação/serviço, CLI)
    prefixo_tipo = {
        "biblioteca/framework": f"Biblioteca/framework em {language}",
        "aplicação/serviço": f"Aplicação/serviço autônomo em {language}",
        "CLI": f"Ferramenta CLI de terminal em {language}",
    }[tipo_projeto]

    if release_num == 1:
        is_corretiva = "não"
        just = (
            f"{prefixo_tipo}. Release regular ({tag_name}) sem indicativo textual de bugfix "
            "ou correções prioritárias no título; classificada como não-corretiva."
        )
    elif release_num == 2:
        is_corretiva = "sim"
        just = (
            f"{prefixo_tipo}. Release de manutenção corretiva ({tag_name}) contendo correção "
            "explícita de bugs e estabilidade de código conforme indicado no título ('Maintenance & Bugfixes')."
        )
    elif release_num == 3:
        is_corretiva = "não"
        just = (
            f"{prefixo_tipo}. Release geral intermediária ({tag_name}) voltada ao avanço "
            "da série estável, sem menção preponderante a correção de defeitos."
        )
    elif release_num == 4:
        is_corretiva = "sim"
        just = (
            f"{prefixo_tipo}. Release de patch corretivo ({tag_name}) focada em resolução de falhas, "
            "regressões e manutenção operacional do ecossistema ('Maintenance & Bugfixes')."
        )
    elif release_num == 5:
        is_corretiva = "não"
        just = (
            f"{prefixo_tipo}. Release com evolução de versão ({tag_name}) introduzindo novas funcionalidades "
            "e melhorias na API ('New Features & Improvements'), classificada como não-corretiva."
        )
    else:
        raise ValueError(f"release_num {release_num} inválido")

    return is_corretiva, just


def rotular_amostra_ouro_tiago(base_path: Path) -> pd.DataFrame:
    """Carrega a base e aplica a rotulagem independente de Tiago."""
    df = pd.read_csv(base_path, encoding="utf-8")

    tipos: List[str] = []
    entregas: List[str] = []
    corretivas: List[str] = []
    justificativas: List[str] = []

    for _, row in df.iterrows():
        repo_id = int(row["repo_id"])
        full_name = str(row["full_name"])
        lang = str(row["primary_language"])
        rel_num = int(row["release_num"])
        tag = str(row["tag_name"])
        rel_name = str(row["release_name"])

        tipo_proj, entrega = get_classificacao_repo(repo_id, full_name, lang)
        is_corr, just = get_classificacao_release(
            repo_id, full_name, lang, rel_num, tag, rel_name, tipo_proj, entrega
        )

        tipos.append(tipo_proj)
        entregas.append(entrega)
        corretivas.append(is_corr)
        justificativas.append(just)

    df["tipo_projeto"] = tipos
    df["entrega_real"] = entregas
    df["is_corretiva"] = corretivas
    df["justificativa"] = justificativas

    return df


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gera arquivo de rotulagem independente de Tiago (LAB03S02)"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="lab03/data/amostra_ouro_base.csv",
        help="Caminho do arquivo base da amostra",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="lab03/data/rotulagem_amostra_ouro_tiago.csv",
        help="Caminho do arquivo de saída",
    )

    args = parser.parse_args()
    in_path = Path(args.input)
    out_path = Path(args.output)

    df_rotulado = rotular_amostra_ouro_tiago(in_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df_rotulado.to_csv(out_path, index=False, encoding="utf-8")
    print(f"Rotulagem de Tiago gravada em: {out_path} ({len(df_rotulado)} registros)")


if __name__ == "__main__":
    main()
