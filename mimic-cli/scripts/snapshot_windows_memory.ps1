$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$OutputDir = Join-Path $Root 'experiments\yi-rootcause\20261006T1625Z\memory'
$timestamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
$memory = Get-CimInstance Win32_PerfFormattedData_PerfOS_Memory
$computer = Get-CimInstance Win32_ComputerSystem
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
$processes = @(Get-Process | ForEach-Object {
    [pscustomobject][ordered]@{ name = $_.ProcessName; pid = $_.Id; working_set_gib = [math]::Round($_.WorkingSet64 / 1GB, 3); private_commit_gib = [math]::Round($_.PrivateMemorySize64 / 1GB, 3) }
})
$record = [ordered]@{
    utc = [DateTime]::UtcNow.ToString('o')
    available_physical_gib = [math]::Round($memory.AvailableBytes / 1GB, 3)
    total_commit_gib = [math]::Round($memory.CommitLimit / 1GB, 3)
    used_commit_gib = [math]::Round($memory.CommittedBytes / 1GB, 3)
    available_commit_gib = [math]::Round(($memory.CommitLimit - $memory.CommittedBytes) / 1GB, 3)
    automatic_managed_pagefile = $computer.AutomaticManagedPagefile
    is_administrator = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    pagefile_settings = @(Get-CimInstance Win32_PageFileSetting | Select-Object Name,InitialSize,MaximumSize)
    active_pagefiles = @(Get-CimInstance Win32_PageFileUsage | Select-Object Name,AllocatedBaseSize,CurrentUsage,PeakUsage)
    fixed_disks = @(Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | Select-Object DeviceID,Size,FreeSpace)
    processes = $processes
    exhaustion_events_24h = @(Get-WinEvent -FilterHashtable @{LogName='System';ProviderName='Microsoft-Windows-Resource-Exhaustion-Detector';StartTime=(Get-Date).AddDays(-1)} -ErrorAction SilentlyContinue | Select-Object TimeCreated,Id,Message)
}
$path = Join-Path $OutputDir ('windows-commit-audit-' + $timestamp + '.json')
$record | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $path -Encoding UTF8
[ordered]@{ path=$path; available_physical_gib=$record.available_physical_gib; used_commit_gib=$record.used_commit_gib; total_commit_gib=$record.total_commit_gib; available_commit_gib=$record.available_commit_gib; exhaustion_events=$record.exhaustion_events_24h.Count; is_administrator=$record.is_administrator; top_private_commit=@($processes | Sort-Object private_commit_gib -Descending | Select-Object -First 10) } | ConvertTo-Json -Depth 4
