param([switch]$NoRestart)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$containerName = 'shiyan-mimicgate-20261002'
$inspection = docker inspect $containerName | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw 'Existing shiyan container is unavailable.' }
if ($inspection[0].State.Running) {
    $poolText = python (Join-Path $projectRoot 'cli/mg.py') --profile shiyan parallel
    if ($LASTEXITCODE -ne 0) { throw 'Cannot verify shiyan is idle; deployment aborted.' }
    $poolState = $poolText | ConvertFrom-Json
    if ($poolState.in_flight -ne 0 -or $poolState.waiting -ne 0) { throw 'Shiyan requests are active; deployment aborted.' }
}
$backupPath = Join-Path $projectRoot ('backups/shiyan-deploy-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Force -Path $backupPath | Out-Null
docker cp "${containerName}:/app/src/." $backupPath
if ($LASTEXITCODE -ne 0) { throw 'Source backup failed.' }
$files = @('config.py','session_observer.py','request_observer.py','cookie_capacity.py','api/probe_evidence.py','api/submission_pacing.py','chatgpt/client.py','chatgpt/standard_mode.py','chatgpt/effort_policy.py','chatgpt/detector.py','browser/human.py','browser/manager.py','api/browser_gate.py','api/openai_routes.py','api/standard_completion.py')
foreach ($file in $files) {
    docker cp (Join-Path $projectRoot "src/$file") "${containerName}:/app/src/$file"
    if ($LASTEXITCODE -ne 0) { throw "Deploy failed: $file" }
}
foreach ($pair in @(@('concurrency-shiyan.json','mimic-cli-concurrency.json'),@('policy-shiyan.json','mimic-cli-policy.json'))) {
    docker cp (Join-Path $projectRoot "config/$($pair[0])") "${containerName}:/app/state/$($pair[1])"
    if ($LASTEXITCODE -ne 0) { throw 'Shiyan configuration deployment failed.' }
}
if (!$inspection[0].State.Running) {
    python -m compileall -q (Join-Path $projectRoot 'src')
    if ($LASTEXITCODE -ne 0) { throw 'Source compilation failed; shiyan was not started.' }
    docker start $containerName | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Shiyan startup failed.' }
} elseif (!$NoRestart) {
    docker exec -w /app $containerName /opt/venv/bin/python -m compileall -q /app/src
    if ($LASTEXITCODE -ne 0) { throw 'Source compilation failed; shiyan was not restarted.' }
    docker restart --timeout 60 $containerName | Out-Null
    if ($LASTEXITCODE -ne 0) { throw 'Shiyan restart failed.' }
}
docker exec $containerName chown 1000:1000 /app/state/mimic-cli-concurrency.json /app/state/mimic-cli-policy.json
if ($LASTEXITCODE -ne 0) { throw 'Shiyan configuration ownership failed.' }
docker exec -w /app $containerName /opt/venv/bin/python -m compileall -q /app/src
if ($LASTEXITCODE -ne 0) { throw 'Shiyan source compilation failed.' }
Write-Output "Shiyan source deployed; backup: $backupPath"
