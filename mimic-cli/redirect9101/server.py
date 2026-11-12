from __future__ import annotations

import argparse
import json
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

UPSTREAM_HOST = "127.0.0.1"
UPSTREAM_PORT = 5802
UPSTREAM_URL = f"http://{UPSTREAM_HOST}:{UPSTREAM_PORT}/"


def upstream_available() -> bool:
    try:
        with socket.create_connection((UPSTREAM_HOST, UPSTREAM_PORT), timeout=1.0):
            return True
    except OSError:
        return False


class Handler(BaseHTTPRequestHandler):
    server_version = "MimicGateLocalRedirect/1.0"
    sys_version = ""

    def log_message(self, fmt: str, *args: object) -> None:
        # Keep the hidden local redirect quiet and avoid storing browser paths.
        return

    def do_GET(self) -> None:
        self._dispatch(send_body=True)

    def do_HEAD(self) -> None:
        self._dispatch(send_body=False)

    def _dispatch(self, *, send_body: bool) -> None:
        path = urlsplit(self.path).path
        if path == "/health":
            available = upstream_available()
            payload = json.dumps(
                {"status": "ok" if available else "unavailable", "service": "mimicgate-9101-redirect", "target": UPSTREAM_URL},
                ensure_ascii=False,
            ).encode("utf-8")
            self.send_response(200 if available else 503)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            if send_body:
                self.wfile.write(payload)
            return

        if not upstream_available():
            payload = f"MimicGate GUI is not reachable at {UPSTREAM_URL}".encode("utf-8")
            self.send_response(503)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            if send_body:
                self.wfile.write(payload)
            return

        self.send_response(302)
        self.send_header("Location", UPSTREAM_URL)
        self.send_header("Content-Length", "0")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()


def main() -> None:
    parser = argparse.ArgumentParser(description="Redirect local port 9101 to the active MimicGate GUI.")
    parser.add_argument("--port", type=int, default=9101)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    server.serve_forever(poll_interval=0.5)


if __name__ == "__main__":
    main()