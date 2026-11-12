# Luna A-int fill round 1: codex exec luna_noweb (tool-free offline), frozen A_int_v1 prompt via stdin.
$ErrorActionPreference = "Continue"
$D = "D:\musicclaude\_bead_auto_20261016\research_fill"
$pf = "$D\prompts\A-int__A_int_v1_luna_noweb_original.txt"
$codex = "$env:APPDATA\npm\node_modules\@openai\codex\bin\codex.js"
$st = "$D\status_luna.tsv"
function Log($s){ Add-Content -Path $st -Value $s -Encoding UTF8 }
$name = "A-int__A_int_v1__luna__op60__f1"
$h = [System.Security.Cryptography.SHA256]::Create()
$psha = ([BitConverter]::ToString($h.ComputeHash([System.IO.File]::ReadAllBytes($pf)))).Replace("-","").ToLower()
$started = Get-Date; $sStr = $started.ToString("s")
cmd /c "node `"$codex`" exec --skip-git-repo-check --json -m gpt-6-luna -c model_reasoning_effort=max --disable shell_tool --disable unified_exec --disable apps --disable plugins --disable browser_use --disable computer_use --disable in_app_browser --disable multi_agent --disable image_generation -c mcp_servers.node_repl.enabled=false - < `"$pf`" > `"$D\raw\$name.jsonl`" 2> `"$D\raw\$name.err`""
$ec = $LASTEXITCODE
$ended = Get-Date; $sec = [int]($ended - $started).TotalSeconds
$eStr = $ended.ToString("s")
if ($ec -eq 0) {
  $last = $null
  foreach ($line in [IO.File]::ReadLines("$D\raw\$name.jsonl")) {
    if ($line -match '"agent_message"') {
      try { $o = $line | ConvertFrom-Json; if ($o.item.text) { $last = $o.item.text } elseif ($o.msg.message) { $last = $o.msg.message } } catch {}
    }
  }
  if ($last -and $last.Length -ge 1000) {
    Set-Content -Path "$D\outputs\$name.md" -Value $last -Encoding UTF8
    $meta = [ordered]@{ job_id=$name; run="research_fill_20261016"; branch="A-int"; model_key="luna"
      harness="codex exec luna_noweb (tool-free)"; prompt_version="A_int_v1"; prompt_file=$pf; prompt_sha256=$psha
      work_key="op60"; sample="f1"; round_label="fill-round3(luna-int adopted: run08 s1,s2 + this)"
      started=$sStr; ended=$eStr; seconds=$sec; status="ok"; exit_code=$ec
      output_file="outputs/$name.md"; output_chars=$last.Length }
    Set-Content -Path "$D\meta\$name.json" -Value ($meta | ConvertTo-Json -Depth 4) -Encoding UTF8
    Log "OK`t$name`t$sec s`t$($last.Length) ch"
  } else {
    Log "NO_MSG`t$name`t$sec s`tec=$ec`t(last agent_message too short or absent)"
  }
} else {
  $tail = ((Get-Content "$D\raw\$name.err" -Tail 3 -ErrorAction SilentlyContinue) -join " / ")
  Log "FAIL`t$name`t$sec s`tec=$ec`t$tail"
}
