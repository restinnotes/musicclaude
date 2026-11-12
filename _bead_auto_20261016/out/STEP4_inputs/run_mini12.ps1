$segs = @("S02","S03","S04","S05","S06","S07","S08","S10","S11","S12","S13","S14")
$gpt2 = "D:\musicclaude\gpt2agent-safechain\bin\gpt2.cmd"
$inp = "D:\musicclaude\_bead_auto_20261016\out\STEP4_inputs"
"START_MINI12 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File "$inp\mini12_timing.txt" -Encoding utf8
foreach ($s in $segs) {
  for ($try = 1; $try -le 2; $try++) {
    $t0 = Get-Date
    & $gpt2 ask --file "$inp\STEP4_mini_$s.txt" --model gpt-6-thinking --json > "$inp\mini_$($s)_out.json" 2> "$inp\mini_$($s)_err.txt"
    $code = $LASTEXITCODE
    $dt = [int]((Get-Date) - $t0).TotalSeconds
    $ok = $false
    if (($code -eq 0) -and (Test-Path "$inp\mini_$($s)_out.json")) {
      $c = Get-Content "$inp\mini_$($s)_out.json" -Raw
      if ($c -match '"completed"\s*:\s*true') { $ok = $true }
    }
    "$s try$try exit=$code elapsed=${dt}s ok=$ok" | Out-File "$inp\mini12_timing.txt" -Append -Encoding utf8
    if ($ok) { break }
  }
}
"DONE_MINI12 $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" | Out-File "$inp\mini12_timing.txt" -Append -Encoding utf8
