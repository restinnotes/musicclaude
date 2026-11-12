$ErrorActionPreference = 'Stop'
$firstTraceProcess = Get-Process -Id 35348 -ErrorAction SilentlyContinue
if ($null -ne $firstTraceProcess) { Wait-Process -InputObject $firstTraceProcess -ErrorAction SilentlyContinue }
$firstAnalysis = 'D:\musicclaude\_thread_evo_20261019\evaluations\d13_20261025\modeltrace_20261025T235216Z\analysis.json'
if (Test-Path -LiteralPath $firstAnalysis) {
    $analysis = Get-Content -LiteralPath $firstAnalysis -Raw -Encoding UTF8 | ConvertFrom-Json
    $lastProbe = $analysis.probes | Select-Object -Last 1
    if ($lastProbe.error_code -match 'UNUSUAL_ACTIVITY|RATE_LIMIT|QUOTA|LIMIT_EXCEEDED') {
        Write-Output 'GPT6 comparison not submitted because the preceding test reported an explicit account restriction.'
        exit 2
    }
}
Set-Location -LiteralPath 'D:\musicclaude\_thread_evo_20261019'
$env:PYTHONIOENCODING = 'utf-8'
& 'C:\Users\zuoyi\AppData\Local\Programs\Python\Python312\python.exe' -u '.\d13_modeltrace_20261025.py' --model 'gpt-6-thinking'
exit $LASTEXITCODE
