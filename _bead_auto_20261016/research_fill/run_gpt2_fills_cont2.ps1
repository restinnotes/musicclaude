# Remaining 5 fills after the server-restart kill (cont2). Done so far:
# gpt6w int f1/f2/f3, gpt6w web f1/f2. Killed #6 (gpt6w web f3) at 0 s with
# 0-byte raw json => no response ever returned => safe re-init. Same frozen
# prompts; concurrency 1; no auto-retry on failure.
$ErrorActionPreference = "Continue"
$D = "D:\musicclaude\_bead_auto_20261016\research_fill"
$G = "D:\musicclaude\gpt2agent-safechain\bin\gpt2.cmd"
$RUN = "research_fill_20261016"
$st = "$D\status_gpt2.tsv"
function Log($s){ Add-Content -Path $st -Value $s -Encoding UTF8 }

$promptInt  = "$D\prompts\A-int__A_int_v1_original.txt"
$promptWeb  = "$D\prompts\A-web__A_web_v2_original.txt"
$pvInt  = "A_int_v1"
$pvWeb  = "A_web_v2"

$jobs = @(
 @{m="gpt-6-thinking";   b="A-web"; k="gpt6w";  pv=$pvWeb; f=3; r=3},
 @{m="gpt-5-6-thinking"; b="A-int"; k="gpt56w"; pv=$pvInt;  f=1; r=2},
 @{m="gpt-5-6-thinking"; b="A-int"; k="gpt56w"; pv=$pvInt;  f=2; r=3},
 @{m="gpt-5-6-thinking"; b="A-web"; k="gpt56w"; pv=$pvWeb;  f=1; r=2},
 @{m="gpt-5-6-thinking"; b="A-web"; k="gpt56w"; pv=$pvWeb;  f=2; r=3}
)

$promptSha = @{}
foreach ($pf in @($promptInt,$promptWeb)) {
  $h = [System.Security.Cryptography.SHA256]::Create()
  $hash = ([BitConverter]::ToString($h.ComputeHash([System.IO.File]::ReadAllBytes($pf)))).Replace("-","").ToLower()
  $promptSha[$pf] = $hash
}

foreach ($j in $jobs) {
  $name = "$($j.b)__$($j.pv)__$($j.k)__op60__f$($j.f)"
  $pf = if ($j.b -eq "A-int") { $promptInt } else { $promptWeb }
  $started = Get-Date
  $sStr = $started.ToString("s")
  cmd /c "$G ask --file $pf --model $($j.m) --json > $D\raw\$name.json 2> $D\raw\$name.err"
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
        job_id = $name; run = $RUN; branch = $j.b; model_key = $j.k; model_cli = $j.m
        prompt_version = $j.pv; prompt_file = $pf; prompt_sha256 = $promptSha[$pf]
        work_key = "op60"; sample = "f$($j.f)"; round_label = "fill-round$($j.r)"
        started = $sStr; ended = $eStr; seconds = $sec; status = "ok"
        exit_code = $ec; output_file = "outputs/$name.md"; output_chars = $resp.Length
        cli_metadata = $jj.metadata
      }
      Set-Content -Path "$D\meta\$name.json" -Value ($meta | ConvertTo-Json -Depth 6) -Encoding UTF8
      Log "OK`t$($j.b)`t$($j.k)`t$name`t$sec s`t$($resp.Length) ch"
    } catch {
      Log "PARSE_FAIL`t$($j.b)`t$($j.k)`t$name`t$sec s`tec=$ec`t$($_.Exception.Message)"
    }
  } else {
    $tail = ""; try { $tail = ((Get-Content "$D\raw\$name.err" -Tail 3 -ErrorAction SilentlyContinue) -join " / ") } catch {}
    Log "FAIL`t$($j.b)`t$($j.k)`t$name`t$sec s`tec=$ec`t$tail"
  }
}
Log "ALL_DONE $(Get-Date -Format s)"
