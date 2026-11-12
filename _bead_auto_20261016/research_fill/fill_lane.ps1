# fill_lane.ps1 — ONE gpt2 fill job per lane (long-call discipline identical to
# the serial runs: frozen prompt, effort max, raw evidence, no auto-retry).
# Lanes touch only their own files; serializing on the local channel is the
# experiment itself (user-ordered parallel test).
param([string]$M,[string]$B,[string]$K,[string]$Pv,[int]$F,[int]$R)
$ErrorActionPreference = "Continue"
$D   = "D:\musicclaude\_bead_auto_20261016\research_fill"
$G   = "D:\musicclaude\gpt2agent-safechain\bin\gpt2.cmd"
$RUN = "research_fill_20261016"
$name = "$($B)__$($Pv)__$($K)__op60__f$F"
$pf   = "$D\prompts\$($B)__$($Pv)_original.txt"
$st   = "$D\status_gpt2.tsv"
$lane = "$D\status_lane.$name.tsv"
$done = "$D\lane.$name.done"
function LogLine($f,[string]$s){ Add-Content -Path $f -Value $s -Encoding UTF8 }

LogLine $lane "JOBStart`t$name`t$M"
if (-not (Test-Path $pf)) { LogLine $lane "MISSING`t$name`t$pf"; Set-Content -Path $done -Value "missing" -Encoding UTF8; return }

$h = [System.Security.Cryptography.SHA256]::Create()
$sha = ([BitConverter]::ToString($h.ComputeHash([System.IO.File]::ReadAllBytes($pf)))).Replace("-","").ToLower()

$started = Get-Date
$sStr = $started.ToString("s")
cmd /c "$G ask --file $pf --model $M --json > $D\raw\$name.json 2> $D\raw\$name.err"
$ec = $LASTEXITCODE
$ended = Get-Date
$sec = [int]($ended - $started).TotalSeconds
$eStr = $ended.ToString("s")

if ($ec -eq 0 -and (Test-Path "$D\raw\$name.json")) {
  try {
    $jj = Get-Content "$D\raw\$name.json" -Raw -Encoding UTF8 | ConvertFrom-Json
    $resp = $jj.response
    if (-not $resp -or $resp.Length -lt 1500) { throw "response too short: $($resp.Length)" }
    Set-Content -Path "$D\outputs\$name.md" -Value $resp -Encoding UTF8
    $meta = [ordered]@{
      job_id = $name; run = $RUN; branch = $B; model_key = $K; model_cli = $M
      prompt_version = $Pv; prompt_file = $pf; prompt_sha256 = $sha
      work_key = "op60"; sample = "f$F"; round_label = "fill-round$R"
      started = $sStr; ended = $eStr; seconds = $sec; status = "ok"
      exit_code = $ec; output_file = "outputs/$name.md"; output_chars = $resp.Length
      cli_metadata = $jj.metadata
    }
    Set-Content -Path "$D\meta\$name.json" -Value ($meta | ConvertTo-Json -Depth 6) -Encoding UTF8
    LogLine $lane "OK`t$B`t$K`t$name`t$sec s`t$($resp.Length) ch"
  } catch {
    LogLine $lane "PARSE_FAIL`t$B`t$K`t$name`t$sec s`tec=$ec`t$($_.Exception.Message)"
  }
} else {
  $tail = ""; try { $tail = ((Get-Content "$D\raw\$name.err" -Tail 3 -ErrorAction SilentlyContinue) -join " / ") } catch {}
  LogLine $lane "FAIL`t$B`t$K`t$name`t$sec s`tec=$ec`t$tail"
}
try { Add-Content -Path $st -Value "LANE`t$B`t$K`t$name`tec=$ec`t$sec s" -Encoding UTF8 } catch {}
Set-Content -Path $done -Value $ec -Encoding UTF8
