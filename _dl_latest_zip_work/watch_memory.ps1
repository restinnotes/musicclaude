# Memory watchdog for review phase (2026-10-10).
# Runner refuses to start when min(available_physical, available_commit) < 5 GiB
# (initializer-pss-limit-mib 1536 tier). Cause: r5apex_dx12 holding ~7.6 GiB.
# Prints MEMORY_OK once headroom is back, then exits. Silent otherwise.
$ErrorActionPreference = "SilentlyContinue"
while ($true) {
  $os = Get-CimInstance Win32_OperatingSystem
  if ($os) {
    $phys = $os.FreePhysicalMemory / 1048576.0
    $commit = $os.FreeVirtualMemorySize / 1048576.0
    $min = [Math]::Min($phys, $commit)
    if ($min -ge 5.3) {
      Write-Output ("MEMORY_OK phys={0:N2}GiB commit={1:N2}GiB" -f $phys, $commit)
      exit 0
    }
  }
  Start-Sleep -Seconds 60
}
