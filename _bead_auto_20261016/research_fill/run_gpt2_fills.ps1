# Serial GPT-web research fills (gpt6w x6, gpt56w x4) via safechain CLI, concurrency 1.
# Each call: same frozen prompt text as historical A rounds; raw JSON kept as evidence.
$ErrorActionPreference = "Continue"
$D = "D:\musicclaude\_bead_auto_20261016\research_fill"
$G = "D:\musicclaude\gpt2agent-safechain\bin\gpt2.cmd"
$RUN = "research_fill_20261016"
$st = "$D\status_gpt2.tsv"
function Log($s){ Add-Content -Path $st -Value $s -Encoding UTF8 }

# 1) lightweight checks first (no model call)
cmd /c $G check > "$D\raw\gpt2_check.txt" 2>&1
if ($LASTEXITCODE -ne 0) { Log "CHECK_FAILED ec=$LASTEXITCODE"; exit 1 }
cmd /c $G health > "$D\raw\gpt2_health.txt" 2>&1
Log "HEALTH_FIRSTLINE`t$((Get-Content "$D\raw\gpt2_health.txt" -TotalCount 2 | Out-String).Trim())"
Log "JOB_START $(Get-Date -Format s)"

$promptInt  = "$D\prompts\A-int__A_int_v1_original.txt"
$promptWeb  = "$D\prompts\A-web__A_web_v2_original.txt"
$pvInt  = "A_int_v1"
$pvWeb  = "A_web_v2"

# round_no = adopted-round index within this branch+model group (run106 s1 = round1 for gpt56w groups)
$jobs = @(
 @{m="gpt-6-thinking";      b="A-int"; k="gpt6w";   pv=$pvInt;  f=1; r=1},
 @{m="gpt-6-thinking";      b="A-int"; k="gpt6w";   pv=$pvInt;  f=2; r=2},
 @{m="gpt-6-thinking";      b="A-int"; k="gpt6w";   pv=$pvInt;  f=3; r=3},
 @{m="gpt-6-thinking";      b="A-web"; k="gpt6w";   pv=$pvWeb;  f=1; r=1},
 @{m="gpt-6-thinking";      b="A-web"; k="gpt6w";   pv=$pvWeb;  f=2; r=2},
 @{m="gpt-6-thinking";      b="A-web"; k="gpt6w";   pv=$pvWeb;  f=3; r=3},
 @{m="gpt-5-6-thinking";    b="A-int"; k="gpt56w";  pv=$pvInt;  f=1; r=2},
 @{m="gpt-5-6-thinking";    b="A-int"; k="gpt56w";  pv=$pvInt;  f=2; r=3},
 @{m="gpt-5-6-thinking";    b="A-web"; k="gpt56w";  pv=$pvWeb;  f=1; r=2},
 @{m="gpt-5-6-thinking";    b="A-web"; k="gpt56w";  pv=$pvWeb;  f=2; r=3}
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
