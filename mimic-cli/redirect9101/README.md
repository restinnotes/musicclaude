# 9101 → current MimicGate GUI

`http://127.0.0.1:9101/` is a local shortcut that issues an HTTP redirect to the active Docker GUI at `http://127.0.0.1:5802/`. The browser ends up on MimicGate's native origin, so its existing cookies and UI requests continue to use port 5802.

The service listens only on `127.0.0.1`. `/health` reports whether the MimicGate GUI port is reachable. The former usage-monitor source and ledgers under `D:\ai-stack\usage-monitor` and `D:\ai-stack\adapters\gpt2agent-adapter` are left untouched and are not loaded by this service.

The `MimicGate9101Redirect` logon task starts this script with the user's windowless Python executable. It does not depend on the `D:\ai-stack` virtual environment or its startup files.