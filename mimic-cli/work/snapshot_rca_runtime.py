"""Read-only diagnostic snapshot, without printing credentials or response content."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'work'))
from clone_yi_no_stealth import docker

def main():
    container = sys.argv[1]
    directory = Path(sys.argv[2])
    directory.mkdir(parents=True, exist_ok=True)
    docker('cp', container + ':/app/state/yi-session-observer.jsonl', str(directory / 'docker-session-observer.jsonl'))
    rows = []
    for line in (directory / 'docker-session-observer.jsonl').read_text(encoding='utf-8').splitlines():
        try:
            rows.append(json.loads(line))
        except ValueError:
            pass
    cutoff = '2026-10-06T16:25:00'
    interesting = [r for r in rows if r.get('utc', '') >= cutoff and r.get('event') in ('generation_wire_request', 'generation_wire_cookie_metadata', 'generation_stream_metadata', 'generation_stream_finished', 'auth_cookie_loss_observed', 'cookie_capacity_pruned')]
    keys = ('utc', 'event', 'wire_epoch', 'sent_cookie_count', 'sent_auth_cookie_count',
        'sent_device_cookie_sha256', 'cookie_header_bytes', 'bytes_observed', 'sse_done', 'failed',
        'network_canceled_after_sse_done', 'status', 'metadata_records', 'sent_context_cookie_names')
    compact = [{**{k: r[k] for k in keys if k in r},
        'model': r.get('metadata', {}).get('model'),
        'thinking_effort': r.get('metadata', {}).get('thinking_effort'),
        'timezone': r.get('metadata', {}).get('timezone')} for r in interesting[-4:]]
    heartbeats = [r for r in rows if r.get('event') == 'heartbeat']
    print(json.dumps({'utc': datetime.now(timezone.utc).isoformat(),
        'recent_generation_and_auth_metadata': compact, 'latest_auth_heartbeat': heartbeats[-1] if heartbeats else None}, ensure_ascii=False))

if __name__ == '__main__':
    main()
