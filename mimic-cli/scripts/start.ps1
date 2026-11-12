$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
if (Test-Path -LiteralPath (Join-Path $projectRoot 'config/session-investigation.freeze')) {
    throw 'Yi startup is frozen during the imported-session investigation. Use the existing shiyan test profile explicitly.'
}
$containerName = 'yi-mimicgate-20261002'
$inspection = docker inspect $containerName | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw 'Existing container missing; automatic recreation is intentionally unsupported.' }
if (!$inspection[0].State.Running) {
    docker start $containerName
    if ($LASTEXITCODE -ne 0) { throw 'Could not start existing MimicGate container.' }
}
Write-Output 'MimicGate API: http://127.0.0.1:8652 ; browser GUI: http://127.0.0.1:5802/'
