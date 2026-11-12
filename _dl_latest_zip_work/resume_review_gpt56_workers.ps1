param([Parameter(Mandatory=$true)][ValidateSet('A','B')][string]$Group)
$ErrorActionPreference = 'Stop'
$root = 'D:\musicclaude\_dl_latest_zip_work'
Set-Location -LiteralPath $root
if ($Group -eq 'A') { $env:CODEX_HOME = Join-Path $env:USERPROFILE '.codex' } else { $env:CODEX_HOME = Join-Path $env:USERPROFILE '.codex-web' }
$log = Join-Path $root ("resume_gpt56_group{0}_progress.log" -f $Group)
$runnerLog = Join-Path $root ("resume_gpt56_group{0}.log" -f $Group)
$manifest = Get-Content -LiteralPath (Join-Path $root 'jobs\reviews\review_manifest.json') -Raw | ConvertFrom-Json
$all = @($manifest.jobs | Where-Object {$_.judge_model -eq 'gpt56w'})
$selected = @()
$offset = if ($Group -eq 'A') { 0 } else { 1 }
for ($i=$offset; $i -lt $all.Count; $i+=2) { $selected += $all[$i] }
"GROUP $Group START $(Get-Date -Format o) account=$env:CODEX_HOME model=gpt56w jobs=$($selected.Count)" | Out-File -LiteralPath $log -Encoding utf8
for ($i=0; $i -lt $selected.Count; $i++) {
  $job = $selected[$i]
  $prefix = Join-Path $root (Join-Path 'results\reviews' (Join-Path $job.judge_model $job.job_id))
  $metaPath = "$prefix.meta.json"
  $txtPath = "$prefix.txt"
  $retry = $false
  if (Test-Path -LiteralPath $txtPath) {
    "[$($i+1)/$($selected.Count)] PRESERVE output: $($job.job_id)" | Out-File -Append -LiteralPath $log -Encoding utf8
    continue
  }
  if (Test-Path -LiteralPath $metaPath) {
    $meta = Get-Content -LiteralPath $metaPath -Raw | ConvertFrom-Json
    if ($meta.status -eq 'success') {
      "[$($i+1)/$($selected.Count)] HOLD success metadata missing text: $($job.job_id)" | Out-File -Append -LiteralPath $log -Encoding utf8
      continue
    } elseif ($meta.status -eq 'confirmed_pre_submit_failure' -and $meta.phase -eq 'pre_submit') {
      "[$($i+1)/$($selected.Count)] DEFER confirmed pre-submit failure for later single-point retry: $($job.job_id)" | Out-File -Append -LiteralPath $log -Encoding utf8
      continue
    } elseif ($meta.status -eq 'failure_or_ambiguous') {
      "[$($i+1)/$($selected.Count)] HOLD ambiguous; no retry: $($job.job_id)" | Out-File -Append -LiteralPath $log -Encoding utf8
      continue
    } else {
      "[$($i+1)/$($selected.Count)] PRESERVE existing status=$($meta.status): $($job.job_id)" | Out-File -Append -LiteralPath $log -Encoding utf8
      continue
    }
  }
  "[$($i+1)/$($selected.Count)] START retry=$retry $($job.job_id) $(Get-Date -Format o)" | Out-File -Append -LiteralPath $log -Encoding utf8
  $args = @('scripts\run_repeated_trials.py','--phase','review','--round-start','1','--round-end','1','--execute','--only-job',$job.job_id)
  if ($retry) { $args += '--retry-confirmed-pre-submit' }
  & python @args >> $runnerLog 2>&1
  $code = $LASTEXITCODE
  "[$($i+1)/$($selected.Count)] END exit=$code $($job.job_id) $(Get-Date -Format o)" | Out-File -Append -LiteralPath $log -Encoding utf8
  if ($code -ne 0) {
    "STOP group $Group at $($job.job_id); inspect evidence before proceeding" | Out-File -Append -LiteralPath $log -Encoding utf8
    break
  }
  Start-Sleep -Seconds 5
}
"GROUP $Group DONE $(Get-Date -Format o)" | Out-File -Append -LiteralPath $log -Encoding utf8
