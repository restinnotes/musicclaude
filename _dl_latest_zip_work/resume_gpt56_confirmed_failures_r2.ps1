$ErrorActionPreference = 'Stop'
$root = 'D:\musicclaude\_dl_latest_zip_work'
Set-Location -LiteralPath $root
$manifest = Get-Content -LiteralPath (Join-Path $root 'jobs\reviews\review_manifest.json') -Raw | ConvertFrom-Json
$queue = @($manifest.jobs | Where-Object judge_model -eq 'gpt56w')
$log = Join-Path $root 'resume_gpt56_failures_r2_progress.log'
$runner = Join-Path $root 'resume_gpt56_failures_r2_runner.log'
$pending = @()
for ($i=0; $i -lt $queue.Count; $i++) {
  $job=$queue[$i]; $metaPath=Join-Path $root (Join-Path 'results\reviews\gpt56w' ($job.job_id+'.meta.json'))
  if (Test-Path -LiteralPath $metaPath) { $meta=Get-Content -LiteralPath $metaPath -Raw|ConvertFrom-Json; if ($meta.status -eq 'confirmed_pre_submit_failure' -and $meta.phase -eq 'pre_submit') {$pending += [pscustomobject]@{job=$job;index=$i}} }
}
"START $(Get-Date -Format o) pending=$($pending.Count)" | Out-File -LiteralPath $log -Encoding utf8
foreach ($entry in $pending) {
  $id=$entry.job.job_id; $i=$entry.index
  $metaPath=Join-Path $root (Join-Path 'results\reviews\gpt56w' ($id+'.meta.json'))
  $txtPath=Join-Path $root (Join-Path 'results\reviews\gpt56w' ($id+'.txt'))
  $before=Get-Content -LiteralPath $metaPath -Raw|ConvertFrom-Json
  if ($before.status -ne 'confirmed_pre_submit_failure' -or $before.phase -ne 'pre_submit') {"STOP state changed $id"|Out-File -Append $log; exit 2}
  $env:CODEX_HOME=if(($i%2)-eq 0){Join-Path $env:USERPROFILE '.codex'}else{Join-Path $env:USERPROFILE '.codex-web'}
  "RETRY $id subsetIndex=$i profile=$env:CODEX_HOME $(Get-Date -Format o)"|Out-File -Append -LiteralPath $log -Encoding utf8
  & python scripts\run_repeated_trials.py --phase review --round-start 1 --round-end 1 --execute --only-job $id --retry-confirmed-pre-submit >> $runner 2>&1
  $code=$LASTEXITCODE; $after=Get-Content -LiteralPath $metaPath -Raw|ConvertFrom-Json; $chars=if(Test-Path -LiteralPath $txtPath){(Get-Item -LiteralPath $txtPath).Length}else{0}
  "RESULT $id exit=$code status=$($after.status) chars=$chars $(Get-Date -Format o)"|Out-File -Append -LiteralPath $log -Encoding utf8
  if($code-ne 0 -or $after.status-ne 'success' -or $chars-le 0){"STOP first repeat failure $id; preserve evidence"|Out-File -Append $log; exit 1}
  Start-Sleep -Seconds 4
}
"DONE $(Get-Date -Format o)"|Out-File -Append $log -Encoding utf8
