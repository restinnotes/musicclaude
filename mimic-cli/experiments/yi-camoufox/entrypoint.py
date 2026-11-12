import os
from pathlib import Path
import secrets
import signal
import subprocess
import time


def stop_children(processes):
    # Keep Xvfb alive until the API/browser has closed its persistent profile.
    for process in reversed(processes):
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def main():
    os.umask(0o077)
    state = Path('/app/state')
    state.mkdir(exist_ok=True)
    token_path = state / 'api-token'
    if not token_path.exists():
        token_path.write_text(secrets.token_urlsafe(32), encoding='utf-8')
    token_path.chmod(0o600)
    dotenv = Path('/app/.env')
    dotenv.write_text('API_TOKEN=' + token_path.read_text() + '\n', encoding='utf-8')
    dotenv.chmod(0o600)
    (state / 'mimic-cli-policy.json').write_text('{"allow_high_fallback":false}', encoding='utf-8')
    (state / 'mimic-cli-concurrency.json').write_text('{"max_concurrency":1}', encoding='utf-8')
    (state / 'capture-probes.enabled').touch()
    processes = []

    def stop(*args):
        stop_children(processes)
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    processes.append(subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1366x768x24', '-nolisten', 'tcp']))
    for _ in range(100):
        if subprocess.run(['xdpyinfo'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
            break
        time.sleep(.1)
    else:
        stop()
    for command in [
        ['fluxbox'],
        ['x11vnc', '-display', ':99', '-localhost', '-forever', '-shared', '-rfbport', '5900', '-nopw', '-quiet'],
        ['websockify', '--web=/usr/share/novnc', '0.0.0.0:6080', '127.0.0.1:5900'],
        ['/opt/venv/bin/python', '-m', 'src.api.server'],
    ]:
        processes.append(subprocess.Popen(command))
    while True:
        if any(process.poll() is not None for process in processes):
            print('A comparison service stopped; shutting down isolated container.', flush=True)
            stop()
        time.sleep(1)


if __name__ == '__main__':
    main()
