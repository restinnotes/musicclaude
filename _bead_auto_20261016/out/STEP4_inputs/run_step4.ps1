$segs = @("S01","S02","S03","S04","S05","S06","S07","S08","S09","S10","S11","S12","S13","S14")
$gpt2 = "D:\musicclaude\gpt2agent-safechain\bin\gpt2.cmd"
$inp = "D:\musicclaude\_bead_auto_20261016\out\STEP4_inputs"
"START $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File "$inp\STEP4_timing.txt" -Encoding utf8
foreach ($s in $segs) {
  $t0 = Get-Date
  & $gpt2 ask --file "$inp\STEP4_prompt_$s.txt" --model gpt-6-thinking --json > "$inp\STEP4_stdout_$s.json" 2> "$inp\STEP4_stderr_$s.txt"
  $code = $LASTEXITCODE
  $dt = [int]((Get-Date) - $t0).TotalSeconds
  "$s exit=$code elapsed=${dt}s" | Out-File "$inp\STEP4_timing.txt" -Append -Encoding utf8
}
"DONE $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File "$inp\STEP4_timing.txt" -Append -Encoding utf8
