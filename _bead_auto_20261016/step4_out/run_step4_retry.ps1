# Retry failed STEP4 lanes in small waves (<=4 concurrent) to stay under the
# extension initializer queue. Each lane launches exactly once per marker;
# a lane that fails inside a wave is logged with its error tail and NOT
# relaunched by this script (no auto-retry; relaunch is a manual decision).
param([string]$Segs = "", [int]$WaveSize = 4)
$ErrorActionPreference = "Continue"
$D = "D:\musicclaude\_bead_auto_20261016\step4_out"
if (-not $Segs -or $Segs.Trim() -eq "") {
    Write-Output "NO_SEGS_GIVEN"; exit 1
}
$list = ($Segs -split "[,;\s]+") | Where-Object { $_ -match "^S\d{2}$" } | Select-Object -Unique
if (-not $list -or $list.Count -eq 0) { Write-Output "NO_VALID_SEGS: $Segs"; exit 1 }
Add-Content -Path "$D\status_step4.tsv" -Value "JOB_RETRY_PAR`t$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`tsegs=$($list -join ',')`twaveSize=$WaveSize"
    foreach ($s in $batch) {
        Remove-Item -Path "$D\lane.STEP4_$s.done" -Force -ErrorAction SilentlyContinue
        Add-Content -Path "$D\status_step4.tsv" -Value "RETRY_LAU`tseg=$s`t$(Get-Date -Format 'HH:mm:ss')"
        Start-Process -FilePath "powershell.exe" -WindowStyle Hidden -ArgumentList @(
            "-NoProfile", "-ExecutionPolicy", "Bypass",
            "-File", "$D\step4_bead_lane.ps1", "-Seg", $s)
    }
    # wait until every lane in this wave has a terminal done marker (even after the LAST wave,
    # so the final accounting does not fire while lanes are still running)
    $deadline = (Get-Date).AddMinutes(40)
    while ((Get-Date) -lt $deadline) {
        $done = 0
        foreach ($s in $batch) { if (Test-Path "$D\lane.STEP4_$s.done") { $done++ } }
        if ($done -ge $batch.Count) { break }
        Start-Sleep -Seconds 15
    }
    if ($i + $WaveSize -lt $list.Count) {
        # clear queue head room before next launch
        Start-Sleep -Seconds 20
    }
$bad = @(); $okN = 0; $failN = 0
foreach ($s in $list) {
    $p = "$D\lane.STEP4_$s.done"
    if (Test-Path $p) {
        $code = (Get-Content $p -ErrorAction SilentlyContinue | Select-Object -First 1)
        if ("$code".Trim() -eq "0") { $okN++ } else { $failN++; $bad += $s }
    } else { $failN++; $bad += "$s(no-marker)" }
}
Add-Content -Path "$D\status_step4.tsv" -Value "JOB_RETRY_DONE`t$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`tok=$okN fail=$failN bad=$($bad -join ',')"
Write-Output "RETRY_COMPLETE ok=$okN fail=$failN bad=$($bad -join ',')"
