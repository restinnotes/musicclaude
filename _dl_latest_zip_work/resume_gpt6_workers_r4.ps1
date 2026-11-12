param([Parameter(Mandatory=$true)][ValidateSet('A','B')][string]$Group)
$ErrorActionPreference='Stop';$root='D:\musicclaude\_dl_latest_zip_work';Set-Location -LiteralPath $root
if($Group -eq 'A'){$env:CODEX_HOME=Join-Path $env:USERPROFILE '.codex'}else{$env:CODEX_HOME=Join-Path $env:USERPROFILE '.codex-web'}
$manifest=Get-Content -LiteralPath (Join-Path $root 'jobs\reviews\review_manifest.json') -Raw|ConvertFrom-Json
$all=@($manifest.jobs|Where-Object judge_model -eq 'gpt6w');$offset=if($Group -eq 'A'){0}else{1};$selected=@();for($i=$offset;$i-lt $all.Count;$i+=2){$selected += $all[$i]}
$log=Join-Path $root ("resume_gpt6_group{0}_r4_progress.log" -f $Group);$runner=Join-Path $root ("resume_gpt6_group{0}_r4.log" -f $Group)
"START $(Get-Date -Format o) account=$env:CODEX_HOME model=gpt6w manifest_subset=$($selected.Count)"|Out-File -LiteralPath $log -Encoding utf8
$done=0
for($i=0;$i-lt $selected.Count;$i++){
 $job=$selected[$i];$base=Join-Path $root (Join-Path 'results\reviews\gpt6w' $job.job_id);$metaPath=$base+'.meta.json';$txtPath=$base+'.txt'
 if(Test-Path -LiteralPath $txtPath){"[$($i+1)/$($selected.Count)] PRESERVE output $($job.job_id)"|Out-File -Append $log -Encoding utf8;continue}
 if(Test-Path -LiteralPath $metaPath){$meta=Get-Content -LiteralPath $metaPath -Raw|ConvertFrom-Json;if($meta.status -eq 'success'){"[$($i+1)/$($selected.Count)] HOLD success metadata missing output $($job.job_id)"|Out-File -Append $log -Encoding utf8;continue}elseif($meta.status -eq 'confirmed_pre_submit_failure'){"[$($i+1)/$($selected.Count)] DEFER confirmed pre-submit failure $($job.job_id)"|Out-File -Append $log -Encoding utf8;continue}elseif($meta.status -eq 'failure_or_ambiguous'){"[$($i+1)/$($selected.Count)] HOLD ambiguous $($job.job_id)"|Out-File -Append $log -Encoding utf8;continue}else{"[$($i+1)/$($selected.Count)] PRESERVE status=$($meta.status) $($job.job_id)"|Out-File -Append $log -Encoding utf8;continue}}
 "[$($i+1)/$($selected.Count)] START $($job.job_id) $(Get-Date -Format o)"|Out-File -Append $log -Encoding utf8
 & python scripts\run_repeated_trials.py --phase review --round-start 1 --round-end 1 --execute --only-job $job.job_id >> $runner 2>&1
 $code=$LASTEXITCODE;$meta=if(Test-Path -LiteralPath $metaPath){Get-Content -LiteralPath $metaPath -Raw|ConvertFrom-Json}else{$null};$chars=if(Test-Path -LiteralPath $txtPath){(Get-Item -LiteralPath $txtPath).Length}else{0}
 "[$($i+1)/$($selected.Count)] END exit=$code status=$($meta.status) chars=$chars $($job.job_id) $(Get-Date -Format o)"|Out-File -Append $log -Encoding utf8
 if($code -ne 0 -or $null -eq $meta -or $meta.status -ne 'success' -or $chars -le 0){"STOP at $($job.job_id); preserve evidence; no auto retry"|Out-File -Append $log -Encoding utf8;exit 1}
 $done++;Start-Sleep -Seconds 4
}
"DONE success_count=$done $(Get-Date -Format o)"|Out-File -Append $log -Encoding utf8


