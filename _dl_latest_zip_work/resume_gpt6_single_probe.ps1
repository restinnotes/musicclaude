$ErrorActionPreference='Stop'
$root='D:\musicclaude\_dl_latest_zip_work';$id='D_k11_r01_gengpt56w_judgegpt6w_AB';Set-Location -LiteralPath $root
$env:CODEX_HOME=Join-Path $env:USERPROFILE '.codex-web'
$base=Join-Path $root (Join-Path 'results\reviews\gpt6w' $id)
if((Test-Path -LiteralPath ($base+'.meta.json')) -or (Test-Path -LiteralPath ($base+'.txt'))){throw 'Probe target already has evidence; refusing overwrite.'}
$log=Join-Path $root 'resume_gpt6_single_probe.log'
"START $id profile=$env:CODEX_HOME $(Get-Date -Format o)"|Out-File -LiteralPath $log -Encoding utf8
& python scripts\run_repeated_trials.py --phase review --round-start 1 --round-end 1 --execute --only-job $id *> (Join-Path $root 'resume_gpt6_single_probe_runner.log')
$code=$LASTEXITCODE;$meta=Get-Content -LiteralPath ($base+'.meta.json') -Raw|ConvertFrom-Json;$chars=if(Test-Path -LiteralPath ($base+'.txt')){(Get-Item -LiteralPath ($base+'.txt')).Length}else{0}
"RESULT exit=$code status=$($meta.status) phase=$($meta.phase) chars=$chars $(Get-Date -Format o)"|Out-File -Append -LiteralPath $log -Encoding utf8
