param([string]$OutputDirectory = 'C:\Users\zuoyi\Documents\Codex\2026-10-03\new-chat\outputs')
$ErrorActionPreference = 'Stop'
$os = Get-CimInstance Win32_OperatingSystem
$memory = Get-CimInstance Win32_PerfFormattedData_PerfOS_Memory
$groups = Get-CimInstance Win32_PerfFormattedData_PerfProc_Process |
    Where-Object { $_.Name -notin @('_Total','Idle') } |
    Group-Object { $_.Name -replace '#\d+$','' } |
    ForEach-Object {
        [pscustomobject]@{
            process = $_.Name
            count = $_.Count
            private_resident_bytes = ($_.Group | Measure-Object WorkingSetPrivate -Sum).Sum
            working_set_bytes = ($_.Group | Measure-Object WorkingSet -Sum).Sum
            committed_private_bytes = ($_.Group | Measure-Object PrivateBytes -Sum).Sum
        }
    } | Sort-Object private_resident_bytes -Descending
$container = docker stats yi-mimicgate-20261002 --no-stream --format '{{json .}}' | ConvertFrom-Json
$report = [pscustomobject]@{
    timestamp = (Get-Date).ToUniversalTime().ToString('o')
    physical_total_bytes = [long]$os.TotalVisibleMemorySize * 1024
    physical_available_bytes = $memory.AvailableBytes
    committed_bytes = $memory.CommittedBytes
    commit_limit_bytes = $memory.CommitLimit
    nonpaged_pool_bytes = $memory.PoolNonpagedBytes
    resident_paged_pool_bytes = $memory.PoolPagedResidentBytes
    processes = $groups
    mimicgate = [pscustomobject]@{memory=$container.MemUsage;cpu=$container.CPUPerc;pids=$container.PIDs}
    notes = @('private_resident_bytes is physical private working set; shared pages are excluded.', 'Docker container memory is included in WSL accounting; do not add both figures.', 'committed_bytes includes pagefile-backed allocations and is not resident RAM.', 'System, kernel, cache, compression, and shared pages explain the difference from process totals.', 'Memory was sampled while the staged parallel test was running.')
}
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$path = Join-Path $OutputDirectory '内存占用采样.json'
$report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $path -Encoding utf8
Write-Output $path
