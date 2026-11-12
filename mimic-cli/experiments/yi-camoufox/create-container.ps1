$ErrorActionPreference = 'Stop'
docker create --name yi-camoufox-20261006 --init --restart no --memory 2560m --memory-swap 3584m --shm-size 512m `
    -p 127.0.0.1:8654:8000 -p 127.0.0.1:5804:6080 `
    --mount type=volume,src=yi-camoufox-browser,dst=/app/browser_data `
    --mount type=volume,src=yi-camoufox-state,dst=/app/state `
    --mount type=volume,src=yi-camoufox-logs,dst=/app/logs `
    --mount type=volume,src=yi-mimicgate-20261002-state,dst=/imports,readonly `
    yi-mimicgate-camoufox:comparison-20261006
if ($LASTEXITCODE -ne 0) { throw 'Yi comparison container creation failed' }
