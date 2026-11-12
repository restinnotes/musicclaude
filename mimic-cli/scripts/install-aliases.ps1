$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$binPath = Join-Path $projectRoot 'bin'
$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if (($userPath -split ';') -notcontains $binPath) {
    [Environment]::SetEnvironmentVariable('Path', ($userPath.TrimEnd(';') + ';' + $binPath), 'User')
}
if (($env:Path -split ';') -notcontains $binPath) { $env:Path += ';' + $binPath }
Write-Output 'Installed mg, mg-ask and mg-cup on the user PATH. New terminals inherit the change.'
