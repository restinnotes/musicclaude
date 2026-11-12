# PAR TEST — launch all 5 remaining fills AT ONCE (user-ordered concurrency
# test; prior serial discipline was concurrency 1 per research-fill rule set).
# cont2 had been killed while gpt6w-web f3 was in flight (raw json 0 bytes =
# no response ever received); f3 is relaunched here as lane 1.
$ErrorActionPreference = "Continue"
$D = "D:\musicclaude\_bead_auto_20261016\research_fill"
$st = "$D\status_gpt2.tsv"
function LogLine($s){ Add-Content -Path $st -Value $s -Encoding UTF8 }

LogLine "JOB_START_PAR $(Get-Date -Format s)"
$lanes = @(
 @{M="gpt-6-thinking";   B="A-web"; K="gpt6w";  Pv="A_web_v2"; F=3; R=3},
 @{M="gpt-5-6-thinking"; B="A-int"; K="gpt56w"; Pv="A_int_v1"; F=1; R=2},
 @{M="gpt-5-6-thinking"; B="A-int"; K="gpt56w"; Pv="A_int_v1"; F=2; R=3},
 @{M="gpt-5-6-thinking"; B="A-web"; K="gpt56w"; Pv="A_web_v2"; F=1; R=2},
 @{M="gpt-5-6-thinking"; B="A-web"; K="gpt56w"; Pv="A_web_v2"; F=2; R=3}
)
foreach ($l in $lanes) {
  $name = "$($l.B)__$($l.Pv)__$($l.K)__op60__f$($l.F)"
  Remove-Item -Force "$D\lane.$name.done" -ErrorAction SilentlyContinue
  $a = @("-NoProfile","-ExecutionPolicy","Bypass","-File","$D\fill_lane.ps1",
         "-M",$l.M,"-B",$l.B,"-K",$l.K,"-Pv",$l.Pv,"-F",$l.F,"-R",$l.R)
  Start-Process -FilePath powershell.exe -ArgumentList $a -WindowStyle Hidden | Out-Null
}
LogLine "LANES_LAUNCHED 5"
