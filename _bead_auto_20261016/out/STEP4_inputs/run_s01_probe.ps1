$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
$inp = 'D:\musicclaude\_bead_auto_20261016\out\STEP4_inputs'
$dir = Join-Path $inp "retry_$ts"
New-Item -ItemType Directory -Force $dir | Out-Null
$gpt2 = 'D:\musicclaude\gpt2agent-safechain\bin\gpt2.cmd'
$t0 = Get-Date
& $gpt2 ask --file (Join-Path $inp 'STEP4_short_S01.txt') --attach (Join-Path $inp 'ATTACH_S01_Apool.txt') --model gpt-6-thinking --json > (Join-Path $dir 'S01_out.json') 2> (Join-Path $dir 'S01_err.txt')
$code = $LASTEXITCODE
$dt = [int]((Get-Date) - $t0).TotalSeconds
"exit=$code elapsed=${dt}s dir=$dir" | Out-File (Join-Path $dir 'timing.txt') -Encoding utf8
Get-Date -Format 'yyyy-MM-dd HH:mm:ss' | Out-File (Join-Path $dir 'done.txt') -Encoding utf8
