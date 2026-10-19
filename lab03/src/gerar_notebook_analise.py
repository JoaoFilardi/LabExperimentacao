"""Utilitário para gerar o Jupyter Notebook interativo analise_rq01_rq04.ipynb."""

from pathlib import Path
import nbformat as nbf


def build_notebook(output_path: Path) -> None:
    nb = nbf.v4.new_notebook()

    cells = []

    # 1. Título e Metadados
    cells.append(nbf.v4.new_markdown_cell(
        "# [LAB03S03] Análise Descritiva das Métricas DORA (RQ01 a RQ04) e Classificação de Referência (C1)\n\n"
        "**Disciplina:** Laboratório de Experimentação de Software  \n"
        "**Sprint:** S03 | **Issue:** #39  \n"
        "**Objetivo:** Realizar a análise descritiva das quatro métricas DORA a partir do dataset consolidado da S02, "
        "calculando mediana e IQR em todas as variantes obrigatórias, tratando os casos de censura e gerando a classificação DORA de referência (C1).\n\n"
        "---"
    ))

    # 2. Configuração e Imports
    cells.append(nbf.v4.new_markdown_cell(
        "## 1. Importação de Bibliotecas e Configuração do Ambiente"
    ))
    cells.append(nbf.v4.new_code_cell(
        "import sys\n"
        "from pathlib import Path\n"
        "\n"
        "# Assegura resolução correta dos módulos do projeto\n"
        "repo_root = Path.cwd().resolve()\n"
        "if repo_root.name == 'notebooks':\n"
        "    repo_root = repo_root.parent.parent\n"
        "elif repo_root.name == 'lab03':\n"
        "    repo_root = repo_root.parent\n"
        "if str(repo_root) not in sys.path:\n"
        "    sys.path.insert(0, str(repo_root))\n"
        "\n"
        "import pandas as pd\n"
        "import numpy as np\n"
        "import matplotlib.pyplot as plt\n"
        "import seaborn as sns\n"
        "\n"
        "from lab03.src.analise_rq01_rq04 import (\n"
        "    verificar_integridade_dataset,\n"
        "    classificar_dora_c1_df,\n"
        "    analisar_rq01_df,\n"
        "    analisar_rq02_lt,\n"
        "    analisar_rq03_cfr,\n"
        "    analisar_rq04_rt,\n"
        "    analisar_c1_geral,\n"
        "    gerar_graficos_analise,\n"
        "    exportar_tabelas_estatisticas,\n"
        "    exportar_dataset_c1,\n"
        "    DORA_CATEGORIES,\n"
        "    DORA_PALETTE,\n"
        ")\n"
        "\n"
        "sns.set_theme(style='whitegrid', font='sans-serif')\n"
        "print('Ambiente configurado com sucesso!')"
    ))

    # 3. Carregamento e Integridade
    cells.append(nbf.v4.new_markdown_cell(
        "## 2. Carregamento do Dataset da S02 e Verificação de Integridade\n\n"
        "Carrega o CSV final consolidado da S02 (`lab03/data/metricas_dora.csv`) e verifica a conformidade com o dicionário de dados."
    ))
    cells.append(nbf.v4.new_code_cell(
        "csv_path = repo_root / 'lab03' / 'data' / 'metricas_dora.csv'\n"
        "df_raw = pd.read_csv(csv_path)\n"
        "\n"
        "integridade = verificar_integridade_dataset(df_raw)\n"
        "print(f'Total de repositórios: {integridade[\"n_total\"]}')\n"
        "print(f'Dataset íntegro e válido? {integridade[\"valido\"]}')\n"
        "if integridade['avisos']:\n"
        "    print(f'Avisos: {integridade[\"avisos\"]}')\n"
        "\n"
        "df_raw.head(3)"
    ))

    # 4. Classificação DORA C1
    cells.append(nbf.v4.new_markdown_cell(
        "## 3. Enquadramento DORA e Classificação de Referência (C1)\n\n"
        "Aplica as regras formais da Tabela de Referência (Seção 5 do enunciado) e calcula a pontuação C1 "
        "(Elite=4, High=3, Medium=2, Low=1; mediana dos 4 scores arredondada para baixo)."
    ))
    cells.append(nbf.v4.new_code_cell(
        "df_c1 = classificar_dora_c1_df(df_raw)\n"
        "print('Colunas geradas:', [c for c in df_c1.columns if c.startswith('c1_') or c.endswith('_category')])\n"
        "df_c1[['full_name', 'c1_df_category', 'c1_lt_category', 'c1_cfr_category', 'c1_rt_category', 'c1_overall_score', 'c1_overall_category']].head(5)"
    ))

    # 5. RQ 01
    cells.append(nbf.v4.new_markdown_cell(
        "## 4. RQ 01: Deployment Frequency (Releases por Semana)\n\n"
        "- **Métrica:** $\\text{releases válidas} \\div 52.14$\n"
        "- **Estatísticas Obrigatórias:** Mediana e IQR."
    ))
    cells.append(nbf.v4.new_code_cell(
        "rq01_res = analisar_rq01_df(df_c1)\n"
        "pd.DataFrame([rq01_res['estatisticas']])"
    ))
    cells.append(nbf.v4.new_code_cell(
        "print('Distribuição Categórica RQ01:')\n"
        "for cat in DORA_CATEGORIES:\n"
        "    print(f'  {cat:6s}: {rq01_res[\"distribuicao_contagem\"][cat]} repos ({rq01_res[\"distribuicao_percentual\"][cat]}%)')"
    ))

    # 6. RQ 02
    cells.append(nbf.v4.new_markdown_cell(
        "## 5. RQ 02: Lead Time for Changes (Variantes Obrigatórias a e b)\n\n"
        "- **Variante (a) Por Release:** Mediana entre releases de $(\\text{data release} - \\text{commit mais antigo})$.\n"
        "- **Variante (b) Por Commit:** Mediana de todos os commits de todas as releases $(\\text{data release} - \\text{commit.author.date})$.\n"
        "- **Divergência:** Commits antigos isolados elevam a Variante (a), mantendo a Variante (b) mais robusta."
    ))
    cells.append(nbf.v4.new_code_cell(
        "rq02_res = analisar_rq02_lt(df_c1)\n"
        "pd.DataFrame([rq02_res['variante_a'], rq02_res['variante_b'], rq02_res['diferenca']])"
    ))

    # 7. RQ 03
    cells.append(nbf.v4.new_markdown_cell(
        "## 6. RQ 03: Change Failure Rate (Variantes Obrigatórias a e b)\n\n"
        "- **Variante (a) Proxy de CI:** Falhas no default branch com `event=push` sobre total de runs válidos.\n"
        "- **Variante (b) Proxy de Entrega:** Releases seguidas por release corretiva em até 7 dias.\n"
        "- **Censura:** Releases nos últimos 7 dias da janela ficam fora do denominador."
    ))
    cells.append(nbf.v4.new_code_cell(
        "rq03_res = analisar_rq03_cfr(df_c1)\n"
        "print('Censura da Variante b:', rq03_res['censura_entrega'])\n"
        "pd.DataFrame([rq03_res['variante_a'], rq03_res['variante_b']])"
    ))

    # 8. RQ 04
    cells.append(nbf.v4.new_markdown_cell(
        "## 7. RQ 04: Failed Deployment Recovery Time (Horas e Censura)\n\n"
        "- **Métrica:** Duração dos episódios de falha por workflow até o próximo sucesso.\n"
        "- **Tratamento de Censura:** Episódios não recuperados até o encerramento da janela são censurados (evitando viés de sobrevivência)."
    ))
    cells.append(nbf.v4.new_code_cell(
        "rq04_res = analisar_rq04_rt(df_c1)\n"
        "print('Censura Agregada:', rq04_res['censura_agregada'])\n"
        "pd.DataFrame([rq04_res['tempo_recuperacao'], rq04_res['taxa_censura_repositorio']])"
    ))

    # 9. Classificação DORA Geral C1
    cells.append(nbf.v4.new_markdown_cell(
        "## 8. Classificação DORA de Referência Geral (C1)\n\n"
        "Distribuição geral consolidada e comparativo cruzado entre as 4 métricas."
    ))
    cells.append(nbf.v4.new_code_cell(
        "c1_res = analisar_c1_geral(df_c1)\n"
        "print('Distribuição Geral DORA C1:')\n"
        "for cat in DORA_CATEGORIES:\n"
        "    print(f'  {cat:6s}: {c1_res[\"distribuicao_contagem\"][cat]} repositórios ({c1_res[\"distribuicao_percentual\"][cat]}%)')\n"
        "\n"
        "c1_res['tabela_comparativa']"
    ))

    # 10. Geração e Exportação
    cells.append(nbf.v4.new_markdown_cell(
        "## 9. Exportação de Tabelas, Figuras e Dataset de Referência para RQ07"
    ))
    cells.append(nbf.v4.new_code_cell(
        "data_dir = repo_root / 'lab03' / 'data'\n"
        "fig_dir = data_dir / 'figuras'\n"
        "\n"
        "tabelas = exportar_tabelas_estatisticas(rq01_res, rq02_res, rq03_res, rq04_res, c1_res, data_dir)\n"
        "dataset_c1 = exportar_dataset_c1(df_c1, data_dir / 'classificacao_dora_c1.csv')\n"
        "figs = gerar_graficos_analise(df_c1, fig_dir)\n"
        "\n"
        "print(f'Tabelas exportadas com sucesso: {[p.name for p in tabelas.values()]}')\n"
        "print(f'Dataset C1 salvo em: {dataset_c1.name}')\n"
        "print(f'Total de figuras geradas: {len(figs)}')\n"
        "for f in figs:\n"
        "    print(f' - {f.name}')"
    ))

    nb.cells = cells

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fp:
        nbf.write(nb, fp)
    print(f"Notebook gerado com sucesso em: {output_path}")


if __name__ == "__main__":
    out = Path("lab03/notebooks/analise_rq01_rq04.ipynb")
    build_notebook(out)
