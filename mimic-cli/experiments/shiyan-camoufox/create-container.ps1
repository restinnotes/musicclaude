$ErrorActionPreference = 'Stop'
$candidateName = 'shiyan-camoufox-20261006'
docker create --name $candidateName --init --restart no --memory 2560m --memory-swap 3584m --shm-size 512m `
    -p 127.0.0.1:8653:8000 -p 127.0.0.1:5803:6080 `
    --mount type=volume,src=shiyan-camoufox-browser,dst=/app/browser_data `
    --mount type=volume,src=shiyan-camoufox-state,dst=/app/state `
    --mount type=volume,src=shiyan-camoufox-logs,dst=/app/logs `
    --mount type=volume,src=shiyan-mimicgate-20261002-state,dst=/imports,readonly `
    shiyan-mimicgate-camoufox:comparison-20261006
if ($LASTEXITCODE -ne 0) { throw 'Comparison container creation failed.' }
Write-Output 'Created isolated comparison container; not started.'
