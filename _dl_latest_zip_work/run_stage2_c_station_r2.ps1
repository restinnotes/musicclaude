param([Parameter(Mandatory=$true)][ValidateSet('C02','C11','C23')][string]$Job,[Parameter(Mandatory=$true)][ValidateSet('A','B')][string]$Group)
$ErrorActionPreference='Stop';$root='D:\musicclaude\_dl_latest_zip_work';Set-Location -LiteralPath $root
$env:CODEX_HOME=if($Group -eq 'A'){Join-Path $env:USERPROFILE '.codex'}else{Join-Path $env:USERPROFILE '.codex-web'}
$log=Join-Path $root ("stage2_{0}_r06_r08_r2_progress.log"-f $Job);$runner=Join-Path $root ("stage2_{0}_r06_r08_r2_runner.log"-f $Job)
"START $Job rounds=06-08 group=$Group profile=$env:CODEX_HOME $(Get-Date -Format o)"|Out-File -LiteralPath $log -Encoding utf8
& python scripts\run_repeated_trials.py --phase trial --round-start 6 --round-end 8 --track C --execute --only-job $Job >> $runner 2>&1
$code=$LASTEXITCODE;"END $Job exit=$code $(Get-Date -Format o)"|Out-File -Append -LiteralPath $log -Encoding utf8
if($code-ne 0){"STOP; inspect run evidence before any retry"|Out-File -Append $log;exit $code}

