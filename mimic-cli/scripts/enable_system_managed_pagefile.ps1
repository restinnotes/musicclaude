#Requires -RunAsAdministrator
# This is a prepared remedy. Running it changes Windows paging policy.
# It backs up the old policy, does not stop applications, and does not reboot.
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$OutputDir = Join-Path $Root 'experiments\yi-rootcause\20261006T1625Z\memory'
$computer = Get-CimInstance Win32_ComputerSystem
$before = [ordered]@{
    utc = [DateTime]::UtcNow.ToString('o')
    automatic_managed_pagefile = $computer.AutomaticManagedPagefile
    pagefile_settings = @(Get-CimInstance Win32_PageFileSetting | Select-Object Name,InitialSize,MaximumSize)
    active_pagefiles = @(Get-CimInstance Win32_PageFileUsage | Select-Object Name,AllocatedBaseSize,CurrentUsage,PeakUsage)
}
$backupPath = Join-Path $OutputDir ('pagefile-before-change-' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ') + '.json')
$before | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $backupPath -Encoding UTF8
Set-CimInstance -InputObject $computer -Property @{AutomaticManagedPagefile=$true} | Out-Null
$after = Get-CimInstance Win32_ComputerSystem
if (-not $after.AutomaticManagedPagefile) { throw 'Windows did not accept the system-managed pagefile policy.' }
$result = [ordered]@{
    automatic_managed_pagefile = $after.AutomaticManagedPagefile
    backup_path = $backupPath
    restart_requested = $false
    note = 'Policy changed. A restart may be needed; verify the active pagefiles and commit limit after your next planned restart. No restart was initiated.'
}
$resultPath = Join-Path $OutputDir ('pagefile-after-change-' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ') + '.json')
$result | ConvertTo-Json | Set-Content -LiteralPath $resultPath -Encoding UTF8
$result | ConvertTo-Json
