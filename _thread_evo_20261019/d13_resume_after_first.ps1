$ErrorActionPreference = 'Stop'
$projectRoot = 'D:\musicclaude\_thread_evo_20261019'
$pythonExe = 'C:\Users\zuoyi\AppData\Local\Programs\Python\Python312\python.exe'
$firstProcessId = 35696
$firstProcess = Get-Process -Id $firstProcessId -ErrorAction SilentlyContinue
if ($null -ne $firstProcess) {
    Wait-Process -InputObject $firstProcess -ErrorAction SilentlyContinue
}
Set-Location -LiteralPath $projectRoot
$env:PYTHONIOENCODING = 'utf-8'
& $pythonExe -u '.\d13_resume_20261025.py'
$queueExitCode = $LASTEXITCODE
& $pythonExe '.\d13_deliver.py' summary
& $pythonExe '.\d13_deliver.py' provenance
& $pythonExe '.\d13_readable.py'
& $pythonExe '.\d13_report.py'
exit $queueExitCode
