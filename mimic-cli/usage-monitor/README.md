# 9101 MimicGate request monitor

This keeps the original 9101 usage-monitor interface and reads request counts from the active `yi-mimicgate-20261002` Docker API at `127.0.0.1:8652/v1/gateway/activity`.

The current Docker activity endpoint keeps an in-memory cumulative count for its running process and returns only the 30 most recent request records. On first connection, the monitor seeds its counter from that live summary and Docker start time; afterwards it stores count/time/status/model metadata locally so daily, weekly, rolling-7-day, and cumulative counts continue across monitor and Docker restarts. The small local state file never stores prompts, request payloads, response previews, client IPs, cookies, or API tokens.

The API token is read into memory from the active Docker container's `Config`; it is not copied from the old `D:\ai-stack` key file or stored on disk. The monitor binds only to `127.0.0.1:9101` and polls the Docker activity endpoint once per second. MimicGate excludes `/v1/gateway/*` activity reads from request telemetry, so the monitor does not count its own polling.