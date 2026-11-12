$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$LogFile = Join-Path $Root 'logs\cup-scheduler.jsonl'
$Container = 'yi-mimicgate-20261002'
$Profile = 'yi'
$DockerExe = Join-Path $env:LOCALAPPDATA 'Programs\DockerDesktop\resources\bin\docker.exe'
$PythonExe = Join-Path $env:LOCALAPPDATA 'Programs\Python\Python312\python.exe'
$CliPath = Join-Path $Root 'cli\mg.py'

function Write-ProbeLog {
    param([hashtable]$Record)
    $Record.timestamp_utc = [DateTime]::UtcNow.ToString('o')
    $Record.container = $Container
    $Record.profile = $Profile
    Add-Content -LiteralPath $LogFile -Value ($Record | ConvertTo-Json -Compress) -Encoding UTF8
}

function Send-ProbeAlert {
    param([string]$Message)
    try {
        Add-Type -AssemblyName System.Windows.Forms
        Add-Type -AssemblyName System.Drawing
        $icon = New-Object System.Windows.Forms.NotifyIcon
        $icon.Icon = [System.Drawing.SystemIcons]::Warning
        $icon.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Warning
        $icon.BalloonTipTitle = 'MimicGate 水杯题报警'
        $icon.BalloonTipText = $Message
        $icon.Visible = $true
        $icon.ShowBalloonTip(10000)
        Start-Sleep -Seconds 12
        $icon.Visible = $false
        $icon.Dispose()
    } catch {
        Write-ProbeLog @{ status = 'alert_delivery_failed'; error_type = $_.Exception.GetType().Name }
    }
}

$started = Get-Date
try {
    if (-not (Test-Path -LiteralPath $DockerExe) -or -not (Test-Path -LiteralPath $PythonExe) -or -not (Test-Path -LiteralPath $CliPath)) {
        Write-ProbeLog @{ status = 'setup_error'; error_type = 'required_executable_or_cli_missing' }
        Send-ProbeAlert '定时水杯题探针缺少运行文件；请检查 MimicGate 本机安装。'
        exit 1
    }

    $dockerState = (& $DockerExe inspect --format '{{.State.Running}}' $Container 2>$null | Out-String).Trim()
    $dockerExit = $LASTEXITCODE
    if ($dockerExit -ne 0 -or $dockerState -ne 'true') {
        Write-ProbeLog @{ status = 'skipped_docker_not_running' }
        exit 0
    }

    # Avoid adding a diagnostic generation while the user's gateway is busy.
    $gateway = Invoke-RestMethod -Uri 'http://127.0.0.1:8652/v1/tabs' -TimeoutSec 5
    if ($null -eq $gateway.concurrency.in_flight -or $null -eq $gateway.concurrency.waiting) {
        throw 'Gateway activity could not be verified; diagnostic submission cancelled.'
    }
    if ($gateway.concurrency.in_flight -gt 0 -or $gateway.concurrency.waiting -gt 0) {
        Write-ProbeLog @{ status = 'skipped_gateway_busy'; in_flight = $gateway.concurrency.in_flight; waiting = $gateway.concurrency.waiting }
        exit 0
    }

    # A low commit limit can cause allocation failures even with free RAM.
    # Skip this diagnostic request; never stop an existing generation or container.
    $memory = Get-CimInstance Win32_PerfFormattedData_PerfOS_Memory
    if ($null -eq $memory.AvailableBytes -or $null -eq $memory.CommitLimit -or $null -eq $memory.CommittedBytes) {
        throw 'Windows memory counters were unavailable; diagnostic submission cancelled.'
    }
    $physicalFreeGiB = [math]::Round(([double]$memory.AvailableBytes / 1GB), 3)
    $commitFreeGiB = [math]::Round((([double]$memory.CommitLimit - [double]$memory.CommittedBytes) / 1GB), 3)
    # This task submits one cup question into an existing browser, not a stress run.
    if ($physicalFreeGiB -lt 3 -or $commitFreeGiB -lt 3) {
        Write-ProbeLog @{ status = 'skipped_low_memory'; available_physical_gib = $physicalFreeGiB; available_commit_gib = $commitFreeGiB; minimum_physical_gib = 3; minimum_commit_gib = 3; budget_scope = 'one_request_with_existing_browser' }
        exit 0
    }

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $PythonExe
    $psi.Arguments = '"' + $CliPath + '" --profile ' + $Profile + ' probe cup'
    $psi.WorkingDirectory = $Root
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    [void]$process.Start()
    $stdoutTask = $process.StandardOutput.ReadToEndAsync()
    $stderrTask = $process.StandardError.ReadToEndAsync()
    # Outlast the 30-minute browser budget, CLI preparation and evidence export.
    $finished = $process.WaitForExit(2400000)
    if (-not $finished) {
        try { $process.Kill() } catch {}
        $process.WaitForExit()
    }
    $stdout = $stdoutTask.GetAwaiter().GetResult()
    $stderr = $stderrTask.GetAwaiter().GetResult()
    $exitCode = if ($finished) { $process.ExitCode } else { 124 }
    $runMatch = [Regex]::Match($stderr, '(?m)^Run:\s*(.+)$')
    $runPath = if ($runMatch.Success) { $runMatch.Groups[1].Value.Trim() } else { '' }

    $diagnostic = $null
    $diagnosticPath = if ($runPath) { Join-Path $runPath 'diagnostics.json' } else { '' }
    if ($diagnosticPath -and (Test-Path -LiteralPath $diagnosticPath)) {
        try { $diagnostic = Get-Content -LiteralPath $diagnosticPath -Raw -Encoding UTF8 | ConvertFrom-Json } catch {}
    }
    $actualEffort = if ($diagnostic.actual_reasoning_effort) { [string]$diagnostic.actual_reasoning_effort } else { '' }
    if (-not $actualEffort -and $diagnostic.diagnostics.model.selected_effort) {
        $actualEffort = [string]$diagnostic.diagnostics.model.selected_effort
    }
    $observedAnswer = $diagnostic.probe_assessment.observed_answer
    $probeStatus = if ($diagnostic.probe_assessment.status) { [string]$diagnostic.probe_assessment.status } else { '' }
    $errorType = if ($diagnostic.error.type) { [string]$diagnostic.error.type } elseif (-not $finished) { 'scheduler_timeout' } else { '' }
    $normal = ($finished -and $exitCode -eq 0 -and $diagnostic.success -eq $true -and
        [string]$diagnostic.actual_model -eq 'gpt-5.6-sol' -and $actualEffort -eq 'xhigh' -and
        [string]$observedAnswer -eq '8' -and $diagnostic.probe_assessment.normal -eq $true)

    if ($normal) {
        Write-ProbeLog @{ status = 'normal'; elapsed_seconds = [math]::Round(((Get-Date) - $started).TotalSeconds, 1); requested_effort = 'xhigh'; actual_effort = $actualEffort; expected_answer = 8; observed_answer = 8; run_path = $runPath }
        exit 0
    }

    $reason = if ($observedAnswer -ne $null) { '答案=' + [string]$observedAnswer } elseif ($probeStatus) { '答案=' + $probeStatus } elseif ($errorType) { '错误=' + $errorType } else { '档位、答案或运行状态无法验证' }
    if (-not $actualEffort) { $actualEffort = '未验证' }
    Write-ProbeLog @{ status = 'alert'; elapsed_seconds = [math]::Round(((Get-Date) - $started).TotalSeconds, 1); requested_effort = 'xhigh'; actual_effort = $actualEffort; expected_answer = 8; observed_answer = $observedAnswer; probe_status = $probeStatus; error_type = $errorType; run_path = $runPath }
    $where = if ($runPath) { '；诊断：' + $runPath + '\diagnostics.json' } else { '' }
    $message = '水杯题异常：' + $reason + '；实际档位=' + $actualEffort + $where
    if ($message.Length -gt 240) { $message = $message.Substring(0, 237) + '...' }
    Send-ProbeAlert $message
    exit 1
} catch {
    Write-ProbeLog @{ status = 'worker_error'; error_type = $_.Exception.GetType().Name }
    Send-ProbeAlert '后台水杯题探针运行异常；请检查 logs\cup-scheduler.jsonl。'
    exit 1
}
