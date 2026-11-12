# B组：CODEX_HOME=.codex-web（web账号），单并发，发车间隔>=5s
# 用法: powershell -File run_review_groupB.ps1
$env:CODEX_HOME = "$env:USERPROFILE\.codex-web"
Set-Location "D:\musicclaude\_dl_latest_zip_work"
$jobs = Get-Content review_groupB.txt | Where-Object { $_.Trim() -ne "" }
$n = $jobs.Count; $i = 0
foreach ($j in $jobs) {
  $i++
  $meta1 = "results\reviews\gpt6w\$j.meta.json"
  $meta2 = "results\reviews\gpt56w\$j.meta.json"
  $txt1 = "results\reviews\gpt6w\$j.txt"
  $txt2 = "results\reviews\gpt56w\$j.txt"
  if ((Test-Path $meta1) -or (Test-Path $txt1) -or (Test-Path $meta2) -or (Test-Path $txt2)) {
    "[$i/$n] SKIP exists: $j" | Out-File -Append review_groupB_progress.log -Encoding utf8
    continue
  }
  "[$i/$n] START $j $(Get-Date -Format o)" | Out-File -Append review_groupB_progress.log -Encoding utf8
  python scripts/run_repeated_trials.py --phase review --round-start 1 --round-end 1 --execute --only-job $j >> review_groupB.log 2>&1
  $code = $LASTEXITCODE
  "[$i/$n] END $j exit=$code $(Get-Date -Format o)" | Out-File -Append review_groupB_progress.log -Encoding utf8
  if ($code -ne 0) {
    # STOP on first failure per runner rule; do NOT auto continue
    "[$i/$n] STOP at $j" | Out-File -Append review_groupB_progress.log -Encoding utf8
    break
  }
  Start-Sleep -Seconds 5
}
"GROUP B DONE $(Get-Date -Format o)" | Out-File -Append review_groupB_progress.log -Encoding utf8
