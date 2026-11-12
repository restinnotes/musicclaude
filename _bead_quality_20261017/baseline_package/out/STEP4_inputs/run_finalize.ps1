$out = 'D:\musicclaude\_bead_auto_20261016\out'
$inp = "$out\STEP4_inputs"
function Get-Resp($s) { return (Get-Content "$inp\mini_$($s)_out.json" -Raw | ConvertFrom-Json).response }
function CCount($t) { return ([regex]::Matches($t,'[\u4e00-\u9fff]').Count) }
$meta = [ordered]@{
 S02='mm.4-16 第1主題'; S03='mm.17-23 間句'; S04='mm.24-34 第1主題（確保）';
 S05='mm.35-39 間句'; S06='mm.40-50 第2主題前半'; S07='mm.51-61 第2主題前半（確保）';
 S08='mm.62-71 第2主題後半'; S10='mm.78-83 挿入句'; S11='mm.84-92 第1主題（再現）';
 S12='mm.93-102 第2主題後半（再現）'; S14='mm.111-116 終結句'
}
$oksegs = @('S02','S03','S04','S05','S06','S07','S08','S10','S11','S12','S14')
$trunc = @('S02','S03','S05','S06','S14')
$times = @{ S02=40; S03=51; S04=21; S05=51; S06=47; S07=23; S08=47; S10=20; S11=38; S12=48; S14=52 }

# 1) BEADS_PARTIAL.md 追加
$pa = $out + '\BEADS_PARTIAL.md'
$sb = [System.Text.StringBuilder]::new()
[void]$sb.Append("`r`n> S02–S08、S10–S12、S14输入：`STEP4_inputs/STEP4_mini_<S>.txt`（短正文、无附件fresh投；S05/S09式如实写明无PRIMARY或备查说明）。`r`n")
[void]$sb.Append('> S13两次投放均pre_submit秒拒，记FAILED（证据：`STEP4_inputs/mini_S13_err.txt`）。' + "`r`n")
foreach ($s in $oksegs) {
  $r = Get-Resp $s
  $n = CCount $r
  $t = $r.Length
  [void]$sb.Append("`r`n## $s $($meta[$s]) —— 极小化投放成功（原样）`r`n`r`n")
  [void]$sb.Append($r + "`r`n")
  $note = ''
  if ($trunc -contains $s) { $note = '；回包末尾标签截断，正文主体完整，原样保留' }
  [void]$sb.Append("`r`n> 输入：`STEP4_inputs/STEP4_mini_$($s).txt`；输出：`STEP4_inputs/mini_$($s)_out.json`，completed=True，耗时$($times[$s])秒，返回码0，response共$($t)字（汉字$($n)）$($note)。`r`n")
}
[void]$sb.Append("`r`n## S13 mm.103-110 第2主題前半（再現） —— FAILED（空缺）`r`n`r`n> 两次投放（各21秒）均 `headless_native_result_rejected / phase=pre_submit` 秒拒，exit=1，未获回包，不重试，记FAILED。证据：`STEP4_inputs/mini_S13_err.txt`。`r`n")
[System.IO.File]::AppendAllText($pa, $sb.ToString(), [System.Text.Encoding]::UTF8)

# 2) BEAD_SOURCE_LEDGER.md 追加
$lg = $out + '\BEAD_SOURCE_LEDGER.md'
$lb = [System.Text.StringBuilder]::new()
[void]$lb.Append("`r`n## STEP4极小化mini轮（仅GPT-6w，短正文无附件fresh投）`r`n`r`n")
[void]$lb.Append('S09/S01沿用既有成功（见BEADS_PARTIAL.md头）。本轮12段：11段成功，S13记FAILED（2次均秒拒，未超上限）。mini输入 `STEP4_inputs/STEP4_mini_<S>.txt` 约500字内：指令＋本段Pool压缩（A07/A08逐字原文，其余UID备查说明；S05如实写明连接段性质）。无附件。`r`n`r`n")
[void]$lb.Append('| 段 | 范围标签 | 结果 | 证据 | response字数 |' + "`r`n")
[void]$lb.Append('|---|---|---|---|---|' + "`r`n")
foreach ($s in $oksegs) {
  $r = Get-Resp $s
  $n = CCount $r
  $t = $r.Length
  $tg = ''
  if ($trunc -contains $s) { $tg = '（标签尾截断）' }
  [void]$lb.Append("| $s | $($meta[$s]) | 成功 | mini_$($s)_out.json | response共$($t)字（汉字$($n)）$($tg) |`r`n")
}
[void]$lb.Append('| S13 | mm.103-110第2主題前半（再現） | FAILED×2 | mini_S13_err.txt | 无回包 |' + "`r`n")
[void]$lb.Append("`r`n- 舍弃账本：UNCERTAIN/LONG_RANGE/UNRESOLVED未进读者正文；int通道PRIMARY未逐字展开处仅作备查说明，未虚构具体内容。缺口4件（A02/A09/A10/A11）无条目，未参与生成。`r`n")
[System.IO.File]::AppendAllText($lg, $lb.ToString(), [System.Text.Encoding]::UTF8)

# 3) BEADS_FOR_USER.md 重写
$r01 = Get-Resp 'S01'
$r09 = Get-Resp 'S09'
$n01 = CCount $r01; $t01 = $r01.Length
$n09 = CCount $r09; $t09 = $r09.Length
$ub = [System.Text.StringBuilder]::new()
[void]$ub.Append('# BEADS_FOR_USER（肖邦《船歌》Op.60 · STEP4 GPT-6w极小化 · 读者珠子全文逐段）' + "`r`n`r`n")
[void]$ub.Append('> 本轮状态：**14段中13段成功，S13 FAILED空缺。** 各段珠子为GPT-6w fresh投放回包response原样，未编造A不支持的内容。' + "`r`n")
[void]$ub.Append('> 冻结段：C2＝朝山奈津子／PTNA（2008）十四段 S01–S14（1–116连续无重叠）。' + "`r`n")
[void]$ub.Append('> 生成链路：仅GPT-6w（`D:\musicclaude\gpt2agent-safechain\bin\gpt2.cmd --model gpt-6-thinking --json`），短正文无附件。' + "`r`n")
$total = $t01 + $t09
$all = [ordered]@{ S01='mm.1-3 序奏' }
foreach ($s in $oksegs) { $all[$s] = $meta[$s] }
$order = @('S01','S02','S03','S04','S05','S06','S07','S08','S09','S10','S11','S12','S13','S14')
$respmap = @{ S01=$r01; S09=$r09 }
foreach ($s in $oksegs) { $respmap[$s] = Get-Resp $s; $total += ($respmap[$s]).Length }
foreach ($s in $order) {
  if ($s -eq 'S13') {
    [void]$ub.Append("`r`n## S13 mm.103-110 第2主題前半（再現） —— FAILED（空缺）`r`n`r`n> 两次投放均pre_submit秒拒，未获回包，如实空缺。`r`n")
    continue
  }
  $lab = $all[$s]
  if ($s -eq 'S09') { $lab = 'mm.72-77 間句' }
  $r = $respmap[$s]
  $n = CCount $r; $t = $r.Length
  $tg = ''
  if ($trunc -contains $s) { $tg = '（回包末尾标签截断，正文主体完整，原样保留）' }
  [void]$ub.Append("`r`n## $s $lab（$($t)字）$($tg)`r`n`r`n")
  [void]$ub.Append($r + "`r`n")
}
[void]$ub.Append("`r`n- 珠子总字数：$total（13段成功回包字符数之和，含标点标签；S13空缺）。`r`n")
[void]$ub.Append('- UNRESOLVED/LONG_RANGE未进读者正文。缺口4件（A02 gpt56w/web半成品、A09 opus_web、A10 sol61_cx_web、A11 V2A基线）无条目，未参与生成。' + "`r`n")
[System.IO.File]::WriteAllText($out + '\BEADS_FOR_USER.md', $ub.ToString(), [System.Text.Encoding]::UTF8)

# 4) RUN_CALLS_AND_FILES.md 追加
$rc = $out + '\RUN_CALLS_AND_FILES.md'
$rb = [System.Text.StringBuilder]::new()
[void]$rb.Append("`r`n## STEP4极小化mini轮调用（仅GPT-6w，短正文无附件fresh投）`r`n`r`n")
[void]$rb.Append('| # | 时间（UTC+8） | 命令 | 结果 |' + "`r`n")
[void]$rb.Append('|---|---|---|---|' + "`r`n")
foreach ($s in $oksegs) {
  [void]$rb.Append("| M4-$s | 2026-10-16 03:29–03:37 | ask --file STEP4_inputs/STEP4_mini_$($s).txt --model gpt-6-thinking --json | exit=0，$($times[$s])秒，completed=true |`r`n")
}
[void]$rb.Append('| M4-S13 | 2026-10-16 03:37 | ask --file STEP4_inputs/STEP4_mini_S13.txt --model gpt-6-thinking --json ×2 | exit=1×2，各21秒，pre_submit秒拒，记FAILED |' + "`r`n")
[void]$rb.Append("`r`n- S09/S01既有成功沿用（53秒/50秒）。本轮12段串行：11段一次成功，S13两次秒拒后记FAILED（未超每段2次上限）。未做：git、读谱、T/H/Thread/WHY/E7、盲评。`r`n")
[void]$rb.Append('- 新增文件：STEP4_inputs/STEP4_mini_S02..S14.txt（12段mini输入）、mini_<S>_out.json/.err（回包与证据）、mini12_timing.txt、run_mini12.ps1、mini_responses_extract.txt（归档中间文件）。' + "`r`n")
[System.IO.File]::AppendAllText($rc, $rb.ToString(), [System.Text.Encoding]::UTF8)

# 5) 打zip覆盖 + sha256
$zip = 'C:\Users\zuoyi\Downloads\music_bead_auto_20261016.zip'
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path "$out\*" -DestinationPath $zip -Force
$sha = (Get-FileHash $zip -Algorithm SHA256).Hash
$bytes = (Get-Item $zip).Length
"ZIP=$zip BYTES=$bytes SHA256=$sha" | Out-File "$inp\mini12_zip.txt" -Encoding utf8
"ZIP=$zip"
"BYTES=$bytes"
"SHA256=$sha"
"TOTAL_CHARS=$total"
