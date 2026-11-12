# review_lane.ps1 — one gpt2 STEP3-v3 review call per lane (split A/B).
# Same evidence discipline: raw json + err kept, no auto-retry.
param([string]$Pf,[string]$OutBase)
$ErrorActionPreference = "Continue"
$D = "D:\musicclaude\_bead_auto_20261016\out\STEP3_inputs"
$G = "D:\musicclaude\gpt2agent-safechain\bin\gpt2.cmd"
$done = "$D\review.$OutBase.done"
if (Test-Path $done) { Remove-Item $done -Force }
$started = Get-Date
$sStr = $started.ToString("s")
cmd /c "$G ask --file $Pf --model gpt-6-thinking --json > $D\$OutBase.json 2> $D\$OutBase.err"
$ec = $LASTEXITCODE
$sec = [int]((Get-Date) - $started).TotalSeconds
$ln = ""
try { $ln = ((Get-Item "$D\$OutBase.json").Length) } catch { $ln = "?" }
Add-Content -Path "$D\review_runs.tsv" -Value "REVIEW`t$OutBase`t$($sStr)`tec=$ec`t$sec s`traw=$ln B" -Encoding UTF8
Set-Content -Path $done -Value $ec -Encoding UTF8
