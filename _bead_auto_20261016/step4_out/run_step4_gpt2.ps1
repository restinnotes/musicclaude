# STEP4 v3 — 14 serial GPT-6w bead-generation calls (one per segment).
# Prompts prebuilt at out\STEP4_inputs_v3\STEP4_prompt_SXX.txt by build_step4_v3.py.
# Same discipline as research fills: concurrency 1, effort max, evidence saved raw,
# NO auto-retry on failure (log and continue; retry decision is manual).
$ErrorActionPreference = "Continue"
$R = "D:\musicclaude\_bead_auto_20261016"
$D = "$R\step4_out"
$G = "D:\musicclaude\gpt2agent-safechain\bin\gpt2.cmd"
$st = "$D\status_step4.tsv"
$PROMPTS = "$R\out\STEP4_inputs_v3"
New-Item -ItemType Directory -Force "$D\raw" | Out-Null
New-Item -ItemType Directory -Force "$D\beads" | Out-Null
New-Item -ItemType Directory -Force "$D\meta" | Out-Null
function Log($s){ Add-Content -Path $st -Value $s -Encoding UTF8 }

Log "JOB_START $(Get-Date -Format s)"
$segs = @("S01","S02","S03","S04","S05","S06","S07","S08","S09","S10","S11","S12","S13","S14")
foreach ($s in $segs) {
  $pf  = "$PROMPTS\STEP4_prompt_$s.txt"
  if (-not (Test-Path $pf)) { Log "MISSING`t$s`t$pf"; continue }
  $started = Get-Date
  $sStr = $started.ToString("s")
  cmd /c "$G ask --file `"$pf`" --model gpt-6-thinking --json > `"$D\raw\STEP4_$s.json`" 2> `"$D\raw\STEP4_$s.err`""
  $ec = $LASTEXITCODE
  $ended = Get-Date
  $sec = [int]($ended - $started).TotalSeconds
  $eStr = $ended.ToString("s")
  if ($ec -eq 0 -and (Test-Path "$D\raw\STEP4_$s.json")) {
    try {
      $jj = Get-Content "$D\raw\STEP4_$s.json" -Raw -Encoding UTF8 | ConvertFrom-Json
      $resp = $jj.response
      if (-not $resp -or $resp.Length -lt 1200) { throw "response too short: $($resp.Length)" }
      Set-Content -Path "$D\beads\STEP4_$s.md" -Value $resp -Encoding UTF8
      $meta = [ordered]@{
        seg = $s; prompt_file = $pf; model = "gpt-6-thinking"; thinking_effort = "max"
        started = $sStr; ended = $eStr; seconds = $sec; status = "ok"
        exit_code = $ec; response_chars = $resp.Length; cli_metadata = $jj.metadata
      }
      Set-Content -Path "$D\meta\STEP4_$s.json" -Value ($meta | ConvertTo-Json -Depth 6) -Encoding UTF8
      Log "OK`t$s`t$sec s`t$($resp.Length) ch"
    } catch {
      Log "PARSE_FAIL`t$s`t$sec s`tec=$ec`t$($_.Exception.Message)"
    }
  } else {
    $tail = ""; try { $tail = ((Get-Content "$D\raw\STEP4_$s.err" -Tail 3 -ErrorAction SilentlyContinue) -join " / ") } catch {}
    Log "FAIL`t$s`t$sec s`tec=$ec`t$tail"
  }
}
Log "ALL_DONE $(Get-Date -Format s)"
