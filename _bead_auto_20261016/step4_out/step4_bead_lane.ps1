# step4_bead_lane.ps1 — one GPT-6w STEP4-v3 bead call per lane (parallel
# batch authorized by user 2026-10-17). Same evidence discipline as fills:
# per-lane raw json / err / meta / done marker, no auto-retry, failures logged.
param([string]$Seg)
$ErrorActionPreference = "Continue"
$R = "D:\musicclaude\_bead_auto_20261016"
$D = "$R\step4_out"
$G = "D:\musicclaude\gpt2agent-safechain\bin\gpt2.cmd"
$st = "$D\status_step4.tsv"
$PROMPTS = "$R\out\STEP4_inputs_v3"
$done = "$D\lane.STEP4_$Seg.done"
function Log($s){ Add-Content -Path $st -Value $s -Encoding UTF8 }
$pf = "$PROMPTS\STEP4_prompt_$Seg.txt"
if (-not (Test-Path $pf)) { Log "MISSING`t$Seg`t$pf"; Set-Content -Path $done -Value 2 -Encoding UTF8; exit }
if (Test-Path $done) { Remove-Item $done -Force }
$started = Get-Date
$sStr = $started.ToString("s")
cmd /c "$G ask --file `"$pf`" --model gpt-6-thinking --json > `"$D\raw\STEP4_$Seg.json`" 2> `"$D\raw\STEP4_$Seg.err`""
$ec = $LASTEXITCODE
$ended = Get-Date
$sec = [int]($ended - $started).TotalSeconds
$eStr = $ended.ToString("s")
if ($ec -eq 0 -and (Test-Path "$D\raw\STEP4_$Seg.json") -and (Get-Item "$D\raw\STEP4_$Seg.json").Length -gt 0) {
  try {
    $jj = Get-Content "$D\raw\STEP4_$Seg.json" -Raw -Encoding UTF8 | ConvertFrom-Json
    $resp = $jj.response
    if (-not $resp -or $resp.Length -lt 1200) { throw "response too short: $($resp.Length)" }
    Set-Content -Path "$D\beads\STEP4_$Seg.md" -Value $resp -Encoding UTF8
    $meta = [ordered]@{
      seg = $Seg; prompt_file = $pf; model = "gpt-6-thinking"; thinking_effort = "max"
      prompt_bytes = (Get-Item $pf).Length
      started = $sStr; ended = $eStr; seconds = $sec; status = "ok"
      exit_code = $ec; response_chars = $resp.Length; cli_metadata = $jj.metadata
    }
    Set-Content -Path "$D\meta\STEP4_$Seg.json" -Value ($meta | ConvertTo-Json -Depth 6) -Encoding UTF8
    Log "OK`t$Seg`t$sec s`t$($resp.Length) ch"
  } catch {
    Log "PARSE_FAIL`t$Seg`t$sec s`tec=$ec`t$($_.Exception.Message)"
  }
} else {
  $tail = ""; try { $tail = ((Get-Content "$D\raw\STEP4_$Seg.err" -Tail 3 -ErrorAction SilentlyContinue) -join " / ") } catch {}
  Log "FAIL`t$Seg`t$sec s`tec=$ec`t$tail"
}
Set-Content -Path $done -Value $ec -Encoding UTF8
