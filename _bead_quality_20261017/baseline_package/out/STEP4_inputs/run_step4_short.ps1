$segs = @("S02","S03","S04","S05","S06","S07","S08","S09","S10","S11","S12","S13","S14")
$gpt2 = "D:\musicclaude\gpt2agent-safechain\bin\gpt2.cmd"
$inp = "D:\musicclaude\_bead_auto_20261016\out\STEP4_inputs"
"START2 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File "$inp\STEP4_timing2.txt" -Encoding utf8
foreach ($s in $segs) {
  $t0 = Get-Date
  & $gpt2 ask --file "$inp\STEP4_short_$s.txt" --attach "$inp\ATTACH_$s`_Apool.txt" --model gpt-6-thinking --json > "$inp\STEP4_short_out_$s.json" 2> "$inp\STEP4_short_err_$s.txt"
  $code = $LASTEXITCODE
  $dt = [int]((Get-Date) - $t0).TotalSeconds
  "$s exit=$code elapsed=${dt}s" | Out-File "$inp\STEP4_timing2.txt" -Append -Encoding utf8
}
"DONE2 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File "$inp\STEP4_timing2.txt" -Append -Encoding utf8
