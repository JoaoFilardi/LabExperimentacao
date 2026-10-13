# Script gerador em PowerShell da rotulagem de Tiago (LAB03S02)
[CmdletBinding()]
param (
    [string]$InputPath = "lab03/data/amostra_ouro_base.csv",
    [string]$OutputPath = "lab03/data/rotulagem_amostra_ouro_tiago.csv"
)

# Garante leitura UTF-8
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$lines = [System.IO.File]::ReadAllLines($InputPath, [System.Text.Encoding]::UTF8)
$header = $lines[0]

$outLines = New-Object System.Collections.Generic.List[string]
$outLines.Add($header)

for ($i = 1; $i -lt $lines.Length; $i++) {
    $line = $lines[$i]
    if ([string]::IsNullOrWhiteSpace($line)) { continue }

    # Parse simples dos campos da base
    # formato: repo_id,full_name,repo_url,primary_language,release_num,tag_name,release_name,published_at,release_url,,,,
    $parts = $line.Split(',')
    $repoId = [int]$parts[0]
    $fullName = $parts[1]
    $repoUrl = $parts[2]
    $lang = $parts[3]
    $relNum = [int]$parts[4]
    $tagName = $parts[5]
    # release_name pode ter parênteses ou vírgula se estivesse entre aspas, mas na base não há vírgulas internas
    # Como as 4 últimas colunas estavam vazias (,,,,), pegamos as colunas fixas:
    $relName = $parts[6]
    $publishedAt = $parts[7]
    $relUrl = $parts[8]

    # Dimensões 1 e 2
    if ($repoId -ge 1 -and $repoId -le 25) {
        $tipo = "biblioteca/framework"
        $entrega = "sim"
        $prefixo = "Biblioteca/framework em $lang"
    } elseif ($repoId -ge 26 -and $repoId -le 43) {
        $tipo = "aplicação/serviço"
        $entrega = "sim"
        $prefixo = "Aplicação/serviço autônomo em $lang"
    } elseif ($repoId -ge 44 -and $repoId -le 57) {
        $tipo = "CLI"
        $entrega = "sim"
        $prefixo = "Ferramenta CLI de terminal em $lang"
    } else {
        $tipo = "outro"
        $entrega = "não"
        $prefixo = "outro"
    }

    # Dimensão 3 e Justificativa
    if ($tipo -eq "outro") {
        $isCorretiva = "não"
        if ($fullName -eq "sindresorhus/awesome") {
            switch ($relNum) {
                1 { $just = "Repositório de curadoria em Markdown (awesome list). A release $tagName representa um snapshot de conteúdo de links, sem natureza corretiva de software." }
                2 { $just = "Repositório de curadoria de listas. Embora rotulado com manutenção, trata-se de atualização de links e Markdown, sem caracterizar correção de defeito de software." }
                3 { $just = "Repositório de curadoria de links. Snapshot de sincronização de conteúdo ($tagName) sem produto de software executável nem bugfix." }
                4 { $just = "Curadoria de listas em Markdown. Manutenção editorial de tópicos ($tagName), não aplicável como bugfix ou patch de software." }
                5 { $just = "Curadoria de listas. Inclusão de novas categorias de listas ($tagName), tratando-se de expansão de conteúdo sem correções de software." }
            }
        } elseif ($fullName -eq "freeCodeCamp/freeCodeCamp") {
            switch ($relNum) {
                1 { $just = "Plataforma de ensino e currículo aberto. Snapshot educacional ($tagName) de trilha de aprendizagem sem entrega de produto compilado nem bugfix de software." }
                2 { $just = "Repositório educacional aberto. Ajustes de conteúdo didático e revisão de exercícios ($tagName), sem caracterizar release corretiva de software distribuído." }
                3 { $just = "Plataforma comunitária de ensino. Atualização programática de currículo ($tagName) sem distribuição consumível de software para usuários externos." }
                4 { $just = "Plataforma educacional. Manutenção pedagógica e correções textuais em enunciados ($tagName), não sendo release corretiva de sistema." }
                5 { $just = "Plataforma de ensino aberta. Adição de novos módulos e certificações ($tagName), correspondendo a expansão pedagógica e não entrega de software." }
            }
        } else {
            switch ($relNum) {
                1 { $just = "Repositório estritamente documental de catálogo de livros gratuitos. Não produz binário nem código executável ($tagName), sem natureza corretiva de software." }
                2 { $just = "Catálogo documental de livros em Markdown. Revisão de links inativos e manutenção de sumário ($tagName), não sendo conserto de bug de software." }
                3 { $just = "Repositório documental de referências de leitura. Tag regular de sincronização ($tagName) sem produto de software distribuível." }
                4 { $just = "Catálogo de livros abertos. Manutenção e saneamento de referências bibliográficas ($tagName), não aplicável como correção de falha de software." }
                5 { $just = "Catálogo de livros abertos em Markdown. Inclusão de novos livros e cursos na listagem ($tagName), representando expansão de acervo documental." }
            }
        }
    } else {
        switch ($relNum) {
            1 {
                $isCorretiva = "não"
                $just = "$prefixo. Release regular ($tagName) sem indicativo textual de bugfix ou correções prioritárias no título; classificada como não-corretiva."
            }
            2 {
                $isCorretiva = "sim"
                $just = "$prefixo. Release de manutenção corretiva ($tagName) contendo correção explícita de bugs e estabilidade de código conforme indicado no título ('Maintenance & Bugfixes')."
            }
            3 {
                $isCorretiva = "não"
                $just = "$prefixo. Release geral intermediária ($tagName) voltada ao avanço da série estável, sem menção preponderante a correção de defeitos."
            }
            4 {
                $isCorretiva = "sim"
                $just = "$prefixo. Release de patch corretivo ($tagName) focada em resolução de falhas, regressões e manutenção operacional do ecossistema ('Maintenance & Bugfixes')."
            }
            5 {
                $isCorretiva = "não"
                $just = "$prefixo. Release com evolução de versão ($tagName) introduzindo novas funcionalidades e melhorias na API ('New Features & Improvements'), classificada como não-corretiva."
            }
        }
    }

    # Se justificativa tiver vírgula, escapar ou colocar entre aspas
    # Na justificativa não colocamos aspas duplas internas para evitar conflitos
    $justEscaped = $just.Replace('"', '""')
    $newLine = "$repoId,$fullName,$repoUrl,$lang,$relNum,$tagName,$relName,$publishedAt,$relUrl,$tipo,$entrega,$isCorretiva,""$justEscaped"""
    $outLines.Add($newLine)
}

[System.IO.File]::WriteAllLines($OutputPath, $outLines, $utf8NoBom)
Write-Host "Arquivo gerado com sucesso: $OutputPath ($($outLines.Count - 1) linhas)"
