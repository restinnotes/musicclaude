#Requires -RunAsAdministrator
# User-authorized: fixed 32 GiB on D:, preserving the existing 4 GiB C: pagefile.
# No reboot, service shutdown, or paging-file deletion is performed.
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Out = Join-Path $Root 'experiments\yi-rootcause\20261006T1625Z\memory'
$Stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')
function Read-Policy {
    $memory = Get-CimInstance Win32_PerfFormattedData_PerfOS_Memory
    [ordered]@{
        utc=[DateTime]::UtcNow.ToString('o')
        automatic_managed_pagefile=(Get-CimInstance Win32_ComputerSystem).AutomaticManagedPagefile
        configured=@(Get-CimInstance Win32_PageFileSetting | Select-Object Name,InitialSize,MaximumSize)
        active=@(Get-CimInstance Win32_PageFileUsage | Select-Object Name,AllocatedBaseSize,CurrentUsage,PeakUsage)
        paging_files_registry=@((Get-ItemProperty -LiteralPath 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management' -Name PagingFiles).PagingFiles)
        commit_limit_gib=[math]::Round($memory.CommitLimit / 1GB,3)
        committed_gib=[math]::Round($memory.CommittedBytes / 1GB,3)
    }
}
$before = Read-Policy
$backup = Join-Path $Out ('d32-pagefile-before-' + $Stamp + '.json')
$before | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $backup -Encoding UTF8
try {
    $disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='D:'"
    if (-not $disk -or $disk.FreeSpace -lt 40GB) { throw 'D: does not have the required 40 GiB free headroom.' }
    Set-CimInstance -InputObject (Get-CimInstance Win32_ComputerSystem) -Property @{AutomaticManagedPagefile=$false} | Out-Null
    foreach ($spec in @(@{Name='C:\pagefile.sys';InitialSize=[uint32]4096;MaximumSize=[uint32]4096},@{Name='D:\pagefile.sys';InitialSize=[uint32]32768;MaximumSize=[uint32]32768})) {
        $existing = Get-CimInstance Win32_PageFileSetting | Where-Object {$_.Name -ieq $spec.Name}
        if ($existing) {
            Set-CimInstance -InputObject $existing -Property @{InitialSize=$spec.InitialSize;MaximumSize=$spec.MaximumSize} | Out-Null
        } else {
            New-CimInstance -ClassName Win32_PageFileSetting -Property $spec | Out-Null
        }
    }
    $after = Read-Policy
    $d = @($after.configured | Where-Object {$_.Name -ieq 'D:\pagefile.sys'})
    $c = @($after.configured | Where-Object {$_.Name -ieq 'C:\pagefile.sys'})
    if ($after.automatic_managed_pagefile -or $d.Count -ne 1 -or $d[0].InitialSize -ne 32768 -or $d[0].MaximumSize -ne 32768 -or $c.Count -ne 1 -or $c[0].InitialSize -ne 4096 -or $c[0].MaximumSize -ne 4096) {
        throw 'Pagefile configuration read-back did not match the requested sizes.'
    }
    $record = [ordered]@{success=$true;backup_path=$backup;after=$after;reboot_initiated=$false;note='Configuration verified. Active capacity must be checked after the next planned restart.'}
} catch {
    $record = [ordered]@{success=$false;backup_path=$backup;error=$_.Exception.Message;after=(Read-Policy);reboot_initiated=$false}
}
$record | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $Out ('d32-pagefile-result-' + $Stamp + '.json')) -Encoding UTF8
if (-not $record.success) { exit 1 }
