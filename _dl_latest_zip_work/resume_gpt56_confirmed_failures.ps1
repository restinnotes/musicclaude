$ErrorActionPreference = 'Stop'
$root = 'D:\musicclaude\_dl_latest_zip_work'
Set-Location -LiteralPath $root
$ids = @(
'D_k18_r05_gengpt6w_judgegpt56w_BA',
'D_k20_r01_gengpt6w_judgegpt56w_AB',
'D_k20_r01_gengpt6w_judgegpt56w_BA',
'D_k20_r05_gengpt6w_judgegpt56w_AB',
'D_k20_r05_gengpt6w_judgegpt56w_BA',
'D_k23_r01_gengpt6w_judgegpt56w_BA',
'G_k18_r01_judgegpt56w_AB',
'G_k18_r05_judgegpt56w_AB',
'G_k18_r05_judgegpt56w_BA',
'G_k20_r01_judgegpt56w_AB',
'G_k20_r01_judgegpt56w_BA'
)
$manifest = Get-Content -LiteralPath (Join-Path $root 'jobs\reviews\review_manifest.json') -Raw | ConvertFrom-Json
$log = Join-Path $root 'resume_gpt56_failures_progress.log'
$runner = Join-Path $root 'resume_gpt56_failures_runner.log'
"START $(Get-Date -Format o) count=$($ids.Count)" | Out-File -LiteralPath $log -Encoding utf8
foreach ($id in $ids) {
  $job = @($manifest.jobs | Where-Object job_id -eq $id)[0]
  if ($null -eq $job) { "STOP missing manifest job $id" | Out-File -Append $log; exit 2 }
  $metaPath = Join-Path $root (Join-Path 'results\reviews\gpt56w' ($id + '.meta.json'))
  $txtPath = Join-Path $root (Join-Path 'results\reviews\gpt56w' ($id + '.txt'))
  if (!(Test-Path -LiteralPath $metaPath)) { "STOP missing metadata $id" | Out-File -Append $log; exit 2 }
  $before = Get-Content -LiteralPath $metaPath -Raw | ConvertFrom-Json
  if ($before.status -ne 'confirmed_pre_submit_failure' -or $before.phase -ne 'pre_submit') { "STOP state changed for $id status=$($before.status) phase=$($before.phase)" | Out-File -Append $log; exit 2 }
  $idx = [array]::IndexOf(@($manifest.jobs), $job)
  if (($idx % 2) -eq 0) { $env:CODEX_HOME = Join-Path $env:USERPROFILE '.codex' } else { $env:CODEX_HOME = Join-Path $env:USERPROFILE '.codex-web' }
  "RETRY $id index=$idx profile=$env:CODEX_HOME $(Get-Date -Format o)" | Out-File -Append $log -Encoding utf8
  & python scripts\run_repeated_trials.py --phase review --round-start 1 --round-end 1 --execute --only-job $id --retry-confirmed-pre-submit >> $runner 2>&1
  $code = $LASTEXITCODE
  if (!(Test-Path -LiteralPath $metaPath)) { "STOP metadata disappeared $id exit=$code" | Out-File -Append $log; exit 3 }
  $after = Get-Content -LiteralPath $metaPath -Raw | ConvertFrom-Json
  $chars = if (Test-Path -LiteralPath $txtPath) { (Get-Item -LiteralPath $txtPath).Length } else { 0 }
  "RESULT $id exit=$code status=$($after.status) phase=$($after.phase) chars=$chars $(Get-Date -Format o)" | Out-File -Append $log -Encoding utf8
  if ($code -ne 0 -or $after.status -ne 'success' -or $chars -le 0) { "STOP first repeat failure $id; preserve evidence, no further retries" | Out-File -Append $log; exit 1 }
  Start-Sleep -Seconds 4
}
"DONE $(Get-Date -Format o)" | Out-File -Append $log -Encoding utf8
