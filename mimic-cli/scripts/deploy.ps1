param([switch]$NoRestart)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
if (Test-Path -LiteralPath (Join-Path $projectRoot 'config/session-investigation.freeze')) {
    throw 'Deployment is frozen during imported-session investigation. No container or browser operation was performed.'
}
$containerName = 'yi-mimicgate-20261002'
$inspection = docker inspect $containerName | ConvertFrom-Json
if ($LASTEXITCODE -ne 0 -or !$inspection[0].State.Running) { throw 'Existing MimicGate container is not running.' }
$tabState = Invoke-RestMethod 'http://127.0.0.1:8652/v1/tabs' -TimeoutSec 10
if ($tabState.concurrency.in_flight -ne 0 -or $tabState.concurrency.waiting -ne 0) {
    throw 'MimicGate has active or queued requests. No source or configuration was changed.'
}
if (!(Test-Path -LiteralPath (Join-Path $projectRoot 'src\chatgpt\standard_mode.py'))) { throw 'Standalone source missing.' }
if (!$NoRestart) {
    $memoryQuery = 'import sys,json; sys.path.insert(0,sys.argv[1]); from runtime_memory_guard import snapshot,headroom_error; row=snapshot(); print(json.dumps(row)); sys.exit(1 if headroom_error(row,2,5) else 0)'
    python -c $memoryQuery (Join-Path $projectRoot 'work')
    if ($LASTEXITCODE -ne 0) { throw 'Insufficient memory for a browser restart. No source or configuration was changed.' }
}
$backupPath = Join-Path $projectRoot ('backups\deploy-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Force -Path $backupPath | Out-Null
docker cp "${containerName}:/app/src/." $backupPath
if ($LASTEXITCODE -ne 0) { throw 'Source backup failed; deployment aborted.' }
$files = @('config.py','session_observer.py','request_observer.py','cookie_capacity.py','mg_native_hint_settings.py','api/probe_evidence.py','api/submission_pacing.py','chatgpt/client.py','chatgpt/standard_mode.py','chatgpt/effort_policy.py','chatgpt/detector.py','browser/human.py','browser/manager.py','browser/stealth.py','browser/identity_policy.py','browser/environment_evidence.py','api/browser_gate.py','api/openai_routes.py','api/standard_completion.py')
# The owned .env contains one public native-browser flag. Refuse to overwrite
# any other file contents, which may contain user settings or credentials.
# Only a finite status is printed; environment contents never leave Docker.
$envState = docker exec -w /app $containerName /opt/venv/bin/python -c 'from pathlib import Path; p=Path("/app/.env"); print("absent" if not p.exists() else "owned" if not p.is_symlink() and p.is_file() and p.stat().st_size < 128 and p.read_text().strip() == "MIMICGATE_NATIVE_BROWSER_IDENTITY=1" else "other")'
if ($LASTEXITCODE -ne 0 -or $envState.Trim() -notin @('absent','owned')) {
    throw 'Existing environment settings require a preserving merge. No deployment was performed.'
}
$nativePolicyFiles = @{
    'config/native-browser.env' = '/app/.env'
    'config/native-browser-policy.json' = '/app/state/.mg-patchright-only.json'
    'config/native-hints.json' = '/app/state/.mg-native-hints.json'
}
$policyBackupManifest = @{}
foreach ($policyFile in $nativePolicyFiles.Keys) {
    $destination = $nativePolicyFiles[$policyFile]
    $policyState = docker exec $containerName /opt/venv/bin/python -c 'from pathlib import Path; import sys; p=Path(sys.argv[1]); print("other" if p.is_symlink() else "absent" if not p.exists() else "file" if p.is_file() else "other")' $destination
    if ($LASTEXITCODE -ne 0 -or $policyState.Trim() -notin @('absent','file')) {
        throw 'Native policy target is not a regular file. No source or policy was changed.'
    }
    $policyBackupManifest[$destination] = $policyState.Trim()
    if ($policyState.Trim() -eq 'file') {
        docker cp "${containerName}:$destination" (Join-Path $backupPath ([System.IO.Path]::GetFileName($destination)))
        if ($LASTEXITCODE -ne 0) { throw 'Native policy backup failed. No source or policy was changed.' }
    }
}
$policyBackupManifest | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $backupPath 'native-policy-before.json') -Encoding utf8
# All native policy backups must finish before the first source mutation.
foreach ($file in $files) {
    docker cp (Join-Path $projectRoot "src/$file") "${containerName}:/app/src/$file"
    if ($LASTEXITCODE -ne 0) { throw "Deploy failed: $file; source backup at $backupPath" }
}
foreach ($policyFile in $nativePolicyFiles.Keys) {
    $destination = $nativePolicyFiles[$policyFile]
    docker cp (Join-Path $projectRoot $policyFile) "${containerName}:$destination"
    if ($LASTEXITCODE -ne 0) { throw 'Native browser policy deployment failed.' }
}
$parallelConfig = Join-Path $projectRoot 'config/concurrency.json'
docker cp $parallelConfig "${containerName}:/app/state/mimic-cli-concurrency.json"
if ($LASTEXITCODE -ne 0) { throw 'Concurrency configuration deployment failed.' }
docker exec $containerName chown 1000:1000 /app/state/mimic-cli-concurrency.json
if ($LASTEXITCODE -ne 0) { throw 'Concurrency configuration ownership failed.' }
docker exec -w /app $containerName /opt/venv/bin/python -m compileall -q /app/src
if ($LASTEXITCODE -ne 0) { throw "Source compilation failed; backup at $backupPath" }
if (!$NoRestart) {
    # Restart the SAME container gracefully. Never remove/recreate it or its volumes.
    docker restart --timeout 60 $containerName
    if ($LASTEXITCODE -ne 0) { throw 'Container restart failed.' }
    $ready = $false
    for ($index=0; $index -lt 60; $index++) {
        try {
            $result = Invoke-RestMethod 'http://127.0.0.1:8652/healthz' -TimeoutSec 2
            if ($result.status -eq 'ok') { $ready=$true; break }
        } catch {}
        Start-Sleep -Seconds 2
    }
    if (!$ready) { throw 'MimicGate did not become ready within 120 seconds.' }
    docker exec -w /app $containerName /opt/venv/bin/python -c 'from src.config import Config; import os; from src.browser.identity_policy import patchright_only_mode; assert os.environ.get("MIMICGATE_NATIVE_BROWSER_IDENTITY") == "1" and patchright_only_mode(); print("Native browser policy verified")'
    if ($LASTEXITCODE -ne 0) { throw 'Native browser policy did not activate after restart.' }
}
Write-Output "Deployed standalone patches. Backup: $backupPath"
