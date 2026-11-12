# Hidden detached launcher for pipeline.py. No window, no credential/account change.
# Writes run/run_handle.json with PID + stdout/stderr/status/events/terminal paths.
$ctrl = "D:\musicclaude\_baseline_parallel_control_20261010"
$run = Join-Path $ctrl "run"
New-Item -ItemType Directory -Force $run | Out-Null
$pyw = $null
try { $pyw = (Get-Command pythonw -ErrorAction Stop).Source } catch {}
if (-not $pyw) {
  $py = (Get-Command python -ErrorAction Stop).Source
  $pyw = $py -replace 'python\.exe$', 'pythonw.exe'
  if (-not (Test-Path $pyw)) { throw "pythonw not found near $py" }
}
$pipe = Join-Path $ctrl "pipeline.py"
$args = @("-u", "-I", $pipe, "--data-root", "D:\musicclaude\_dl_latest_zip_work", "--max-inflight", "8")
$proc = Start-Process -FilePath $pyw -ArgumentList $args -WorkingDirectory $ctrl `
  -WindowStyle Hidden `
  -RedirectStandardOutput (Join-Path $run "stdout.log") `
  -RedirectStandardError (Join-Path $run "stderr.log") -PassThru
$handle = [ordered]@{
  pid            = $proc.Id
  started_utc    = (Get-Date).ToUniversalTime().ToString("o")
  cmd            = "$pyw -u -I $pipe --data-root D:\musicclaude\_dl_latest_zip_work --max-inflight 8"
  cwd            = $ctrl
  stdout         = (Join-Path $run "stdout.log")
  stderr         = (Join-Path $run "stderr.log")
  status         = (Join-Path $run "status.json")
  events         = (Join-Path $run "events.jsonl")
  selftest       = (Join-Path $run "selftest.log")
  terminal       = (Join-Path $run "pipeline_terminal.json")
  pending        = (Join-Path $run "pending_decisions.json")
  phase2_summary = (Join-Path $run "phase2_summary.json")
}
$handle | ConvertTo-Json | Out-File (Join-Path $run "run_handle.json") -Encoding utf8
Write-Output $proc.Id
