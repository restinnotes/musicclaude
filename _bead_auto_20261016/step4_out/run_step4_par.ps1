# run_step4_par.ps1 — launch all 14 GPT-6w STEP4-v3 bead lanes AT ONCE
# (parallel batch authorized by user 2026-10-17; per-lane evidence, no auto-retry).
$ErrorActionPreference = "Continue"
$R = "D:\musicclaude\_bead_auto_20261016"
$D = "$R\step4_out"
$st = "$D\status_step4.tsv"
function Log($s){ Add-Content -Path $st -Value $s -Encoding UTF8 }
New-Item -ItemType Directory -Force "$D\raw" | Out-Null
New-Item -ItemType Directory -Force "$D\beads" | Out-Null
New-Item -ItemType Directory -Force "$D\meta" | Out-Null
Log "JOB_START_PAR $(Get-Date -Format s)"
$segs = @("S01","S02","S03","S04","S05","S06","S07","S08","S09","S10","S11","S12","S13","S14")
foreach ($s in $segs) {
  Remove-Item -Force "$D\lane.STEP4_$s.done" -ErrorAction SilentlyContinue
  $a = @("-NoProfile","-ExecutionPolicy","Bypass","-File","$D\step4_bead_lane.ps1","-Seg",$s)
  Start-Process -FilePath powershell.exe -ArgumentList $a -WindowStyle Hidden | Out-Null
}
Log "LANES_LAUNCHED 14"
