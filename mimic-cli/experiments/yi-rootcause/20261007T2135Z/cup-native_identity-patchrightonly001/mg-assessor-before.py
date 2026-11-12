"""Independent CLI -> existing yi MimicGate -> browser -> ChatGPT.

Python standard library only. API auth is read into memory from the existing
container, never persisted, exposed on argv, or printed.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[1]
API = "http://127.0.0.1:8652"
CONTAINER = "yi-mimicgate-20261002"
MODEL = "gpt-5.6-sol"
EFFORT = "xhigh"
PROFILE = "yi"


def configure_profile(profile):
    global PROFILE, API, CONTAINER
    if profile not in {"yi", "yi-camoufox", "shiyan", "shiyan-camoufox"}:
        raise ValueError("Unknown browser profile")
    PROFILE = profile
    API, CONTAINER = ({"yi": ("http://127.0.0.1:8652", "yi-mimicgate-20261002"),
        "shiyan": ("http://127.0.0.1:8651", "shiyan-mimicgate-20261002"),
        "shiyan-camoufox": ("http://127.0.0.1:8653", "shiyan-camoufox-20261006"),
        "yi-camoufox": ("http://127.0.0.1:8654", "yi-camoufox-20261006")}[profile])


def session_frozen():
    return PROFILE == "yi" and ROOT.joinpath('config', 'session-investigation.freeze').exists()


def verified_effort(model):
    return (model.get('requested_effort') == EFFORT and
        ((model.get('selected_effort') == EFFORT and model.get('fallback_reason') is None) or
         (PROFILE in {'shiyan', 'shiyan-camoufox'} and model.get('selected_effort') == 'high' and
          model.get('fallback_reason') == 'extra_high_unavailable_high_authorized')))


class CLIError(Exception):
    def __init__(self, kind, message, status=None, diagnostics=None):
        super().__init__(message)
        self.kind, self.status, self.diagnostics = kind, status, diagnostics


def safe_text(value, token=""):
    text = str(value)
    if token:
        text = text.replace(token, "[REDACTED]")
    text = re.sub(r"(?i)(Bearer\s+)[A-Za-z0-9._~+/-]{12,}", r"\1[REDACTED]", text)
    text = re.sub(r"(?im)^((?:set-cookie|cookie|authorization)\s*:)\s*.*$", r"\1 [REDACTED]", text)
    return text


def safe_object(value, token=""):
    if isinstance(value, dict):
        return {key: safe_object(item, token) for key, item in value.items()
                if (key in {'session_cookie_count', 'site_cookie_count', 'root_cookie_count', 'cookie_count', 'cookie_count_before', 'temporary_cookie_count', 'cookie_header_bytes_estimate'}
                    and type(item) is int and 0 <= item <= 1000000)
                or (key == 'device_cookie_present' and type(item) is bool)
                or (key == 'device_cookie_sha256' and (item is None or isinstance(item, str) and re.fullmatch('[0-9a-f]{64}', item)))
                or not re.search(r"(?i)(api[_-]?key|bearer|cookie|authorization|secret|access[_-]?token)", key)}
    if isinstance(value, list):
        return [safe_object(item, token) for item in value]
    return safe_text(value, token) if isinstance(value, str) else value


def assess_cup_answer(answer):
    # Inspect explicit answer statements, never count an incidental digit 8.
    # A cited answer/equality is not the author's conclusion. This deliberately
    # covers complete quotation spans, not arbitrary surrounding prose.
    quoted = [(m.start(), m.end()) for m in re.finditer(
        r'“[^”\n]*”|‘[^’\n]*’|「[^」\n]*」|『[^』\n]*』|"[^"\n]*"', answer)]
    patterns = [
        r"\\boxed\s*\{\s*(?:x\s*=\s*)?(\d+)\s*(?:\\text\s*\{[^}]*\})?\s*\}",
        r"(?<![A-Za-z])x\s*(?:=|＝)\s*(\d+)",
        r"(?:答案|最优值|最小值|最少交换次数)\s*(?:是|为|为：|是：|[:：=＝])\s*[*$\s]*(\d+)",
        r"(?:最坏情况|最坏情形|最坏情况下)[^。\n]{0,60}?(?:最少|最优|至少|只需|需要|保证)[^。\n]{0,15}?(\d+)\s*次",
        r"(?:最少|最优)[^。\n]{0,30}?(\d+)\s*次(?:相邻)?交换",
    ]
    boxed_spans = [(m.start(), m.end()) for m in re.finditer(patterns[0], answer)]
    for pattern in patterns:
        matches = list(re.finditer(pattern, answer))
        matches = [m for m in matches if not any(
            start <= m.start() and m.end() <= end for start, end in quoted)]
        if pattern.startswith(r'(?<![A-Za-z])x'):
            # A rejected hypothetical/disputed box must not be reconsidered as
            # an unqualified bare equality by the lower-priority fallback.
            matches = [m for m in matches if not any(
                start <= m.start() and m.end() <= end for start, end in boxed_spans)]
        if pattern.startswith(r'\\boxed'):
            # A displayed number inside a stated hypothetical is not the
            # asserted optimum. Strip only the opening display delimiter to
            # inspect its immediately preceding prose paragraph. Preserve
            # genuine conflicting boxed conclusions as ambiguous.
            asserted_boxes = []
            for match in matches:
                before = answer[:match.start()]
                context = re.sub(r'(?:\\\[|\s)+$', '', before).split('\n\n')[-1]
                following = answer[match.end():match.end() + 90].split('\n')[0]
                if not re.search(r'如果|假设|假定|假如|若(?:能|要|有|存在|声称)|反证假设|'
                                 r'不能(?:直接)?推出|无法证明|要证明|需要证明|还需(?:要)?证明|'
                                 r'尚需证明|尚未证明|不严谨|不充分', context) and not re.search(
                                     r'不严谨|不成立|不充分|还需(?:要)?证明|尚需证明|尚未证明', following):
                    asserted_boxes.append(match)
            matches = asserted_boxes
        if not pattern.startswith(r'\\boxed'):
            matches = [match for match in matches if not re.search(
                r'不能(?:直接)?推出|不能诚实|无法|要证明|需要证明|是否|能否|尚无法确定|还必须|不能由|若声称',
                answer[max(0, match.start() - 90):match.start()].split('\n')[-1])]
        if not pattern.startswith((r'\\boxed', r'(?<![A-Za-z])x')):
            matches = [match for match in matches if not re.search(
                r'不能(?:直接)?推出|不能由|不完整|不严谨|不充分|还需证明|尚需证明|是否|能否|反转排列|倒序排列|逆序数|下界|至少',
                match.group(0) + answer[match.end():match.end() + 90].split('\n')[0])]
        if pattern.startswith(r'(?<![A-Za-z])x'):
            # A quoted/disputed equality is not an asserted answer. Preserve
            # ambiguity for multiple proposed values, but never turn an
            # abstention such as "cannot prove x=6" into the answer 6.
            proposed = sorted({int(match.group(1)) for match in matches})
            if len(proposed) > 1:
                return {"expected_answer": 8, "observed_answer": None, "normal": False,
                    "status": "ambiguous", "evidence": [m.group(0) for m in matches],
                    "method": "explicit_conclusion_text", "proof_independently_verified": False}
            asserted = []
            for match in matches:
                before = answer[max(0, match.start() - 90):match.start()].split('\n')[-1]
                after = answer[match.end():match.end() + 90].split('\n')[0]
                if not re.search(r'不能|无法|不诚实|不能推出|要证明|需要证明|证明存在|是否|能否|如果|假设|假定|假如|若声称|不成立|不严谨|不充分|尚未证明|尚需证明|还需证明|尚无法确定|还必须|还需要|不能诚实|那需要证明|若要', before + after):
                    asserted.append(match)
            matches = asserted
        if matches:
            values = sorted({int(match.group(1)) for match in matches})
            observed = values[0] if len(values) == 1 else None
            return {"expected_answer": 8, "observed_answer": observed,
                    "normal": observed == 8, "status": "matched" if observed == 8 else
                        ("mismatch" if observed is not None else "ambiguous"),
                    "evidence": [match.group(0) for match in matches],
                    "method": "explicit_conclusion_text", "proof_independently_verified": False}
    return {"expected_answer": 8, "observed_answer": None, "normal": False,
            "status": "unrecognized", "evidence": [], "method": "explicit_conclusion_text",
            "proof_independently_verified": False}


def read_auth():
    # Captured stdout is kept solely in this process's memory. Only the fixed
    # Docker command is on argv; the token itself is never an argument.
    code = "from src.config import Config; import sys; sys.stdout.write(Config.API_TOKEN)"
    try:
        result = subprocess.run(["docker", "exec", "-w", "/app", CONTAINER,
                                 "/opt/venv/bin/python", "-c", code],
                                capture_output=True, text=True, timeout=20,
                                creationflags=subprocess.CREATE_NO_WINDOW)
    except (OSError, subprocess.TimeoutExpired):
        raise CLIError("auth_config", "Could not read existing MimicGate authentication into memory") from None
    if result.returncode != 0:
        raise CLIError("auth_config", "Existing MimicGate container or Config is unavailable")
    return result.stdout.strip()


def check_recorded_session():
    """Fail early only on a fresh definitive missing-session observation."""
    code = ("from pathlib import Path; import sys; "
            "p=Path('/app/state/yi-session-status.json'); "
            "sys.stdout.write(p.read_text() if p.exists() else '{}')")
    try:
        result = subprocess.run(['docker', 'exec', CONTAINER, '/opt/venv/bin/python', '-c', code],
                    capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW)
        status = json.loads(result.stdout) if result.returncode == 0 else {}
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return  # The backend independently verifies its live browser cookies.
    if not isinstance(status, dict) or not isinstance(status.get('observed_epoch', 0), (float, int)):
        return
    age = time.time() - status.get('observed_epoch', 0)
    if 0 <= age <= 15 and status.get('session_cookie_count') == 0:
        raise CLIError('authentication_missing',
            'ChatGPT session cookie is missing; no completion request was sent')


def http_json(path, token="", payload=None, timeout=30, standard=False, capture_probe=False):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    if standard:
        headers["X-MimicGate-Mode"] = "temporary-unpersonalized"
    if capture_probe:
        headers['X-MimicGate-Capture-Probe'] = 'cup'
    request = urllib.request.Request(API + path, headers=headers,
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None)
    # Loopback traffic should not pass through a configured external HTTP proxy.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(request, timeout=timeout) as response:
            status = response.status
            body = json.loads(response.read().decode("utf-8"))
            return status, body
    except urllib.error.HTTPError as error:
        try:
            body = safe_object(json.loads(error.read().decode("utf-8")), token)
        except (ValueError, UnicodeError):
            body = {}
        detail = body.get("error") or {}
        raise CLIError(detail.get("type", "http"), detail.get("message", "MimicGate HTTP request failed"),
                       error.code, body.get("mimicgate_diagnostics")) from None
    except (socket.timeout, TimeoutError):
        raise CLIError("timeout", "MimicGate HTTP response timed out; automatic resend is disabled") from None
    except urllib.error.URLError:
        raise CLIError("http_connection", "MimicGate API at 127.0.0.1:8652 is unreachable") from None
    except (ValueError, UnicodeError):
        raise CLIError("http_invalid_response", "MimicGate returned invalid JSON") from None


def standard_call(prompt, record):
    if session_frozen():
        raise CLIError('session_investigation',
            'Browser calls are temporarily frozen while the imported-session loss is investigated; no HTTP request was sent')
    check_recorded_session()
    token = ""
    try:
        status, health = http_json("/healthz", timeout=5)
        if health.get("status") != "ok":
            raise CLIError("health", "MimicGate health check failed", status)
        token = read_auth()
        record["prompt"] = safe_text(prompt, token)
        _, catalog = http_json("/v1/models", token, timeout=300)
        model_ids = [model["id"] for model in catalog.get("data", [])]
        record["preflight"] = {"health": "ok", "target_model_present": MODEL in model_ids,
                               "model_ids": model_ids}
        if MODEL not in model_ids:
            raise CLIError("model_state", "gpt-5.6-sol is absent from the live MimicGate model catalog")
        status, response = http_json("/v1/chat/completions", token,
            {"model": MODEL, "reasoning_effort": EFFORT,
             "messages": [{"role": "user", "content": prompt}], "stream": False},
            timeout=1900, standard=True, capture_probe=record.get('probe') == 'cup')
        record["http_status"] = status
        diagnostics = safe_object(response.get("mimicgate_diagnostics", {}), token)
        record["diagnostics"] = diagnostics
        record["completion_id"] = response.get("id")
        try:
            choice = response["choices"][0]
            answer = choice["message"]["content"]
        except (KeyError, IndexError, TypeError):
            raise CLIError("incomplete_response", "MimicGate response has no final answer", status, diagnostics)
        model = diagnostics.get("model", {})
        required = (diagnostics.get("temporary_chat", {}).get("verified") is True
                    and diagnostics.get("non_personalized", {}).get("verified") is True
                    and diagnostics.get("verification_stage") == "immediately_before_submission"
                    and diagnostics.get("prompt_content_verified") is True
                    and diagnostics.get("prompt_submitted") is True
                    and diagnostics.get("response_complete") is True
                    and model.get("model") == MODEL and verified_effort(model)
                    and response.get("model") == MODEL and choice.get("finish_reason") == "stop"
                    and isinstance(answer, str) and bool(answer.strip()))
        record["response"] = safe_text(answer, token) if isinstance(answer, str) else ""
        record["actual_model"] = model.get("model")
        record["actual_reasoning_effort"] = model.get("selected_effort")
        if not required:
            raise CLIError("state_evidence", "Response lacks the required verified standard-state evidence", status, diagnostics)
        return safe_text(answer, token)
    except CLIError as error:
        error.args = (safe_text(str(error), token),)
        error.diagnostics = safe_object(error.diagnostics, token)
        raise


def save_probe_screenshots(record, run):
    shot = record.get('diagnostics', {}).get('screenshot_evidence') or {}
    if not isinstance(shot, dict):
        return {'complete': False, 'reason': 'invalid_evidence_metadata'}
    request_id = shot.get('request_id')
    if (not isinstance(request_id, str) or not re.fullmatch('[0-9a-f]{32}', request_id)
            or shot.get('directory') != '/app/state/probe-artifacts/' + request_id):
        return {'complete': False, 'reason': 'missing_or_invalid_evidence_directory'}
    items = shot.get('files') or []
    if (not isinstance(items, list) or len(items) != 2 or not all(isinstance(item, dict) and item.get('filename') in
            {'response-viewport.jpg', 'response-full.jpg', 'failure-viewport.jpg', 'failure-full.jpg'}
            and re.fullmatch('[0-9a-f]{64}', str(item.get('sha256', ''))) for item in items)):
        return {'complete': False, 'reason': 'missing_or_invalid_screenshot_files'}
    if len({item['filename'] for item in items}) != 2:
        return {'complete': False, 'reason': 'duplicate_screenshot_file'}
    destination = run / 'screenshots'
    destination.mkdir(exist_ok=True)
    try:
        result = subprocess.run(['docker', 'cp', CONTAINER + ':' + shot['directory'] + '/.', str(destination)],
            capture_output=True, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW)
        if result.returncode or any(hashlib.sha256((destination / item['filename']).read_bytes()).hexdigest()
            != item['sha256'] for item in items):
            return {'complete': False, 'reason': 'copy_or_hash_verification_failed'}
        return {'complete': bool(shot.get('success')), 'directory': str(destination),
                'files': items, 'thinking_time_ui_labels': shot.get('thinking_time_ui_labels', [])}
    except (OSError, subprocess.TimeoutExpired):
        return {'complete': False, 'reason': 'screenshot_copy_failed'}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Temporary + Unpersonalized + GPT-5.6 Sol Extra High, one shot")
    parser.add_argument('--profile', choices=['yi', 'yi-camoufox', 'shiyan', 'shiyan-camoufox'], default='yi',
                        help='Use the named MimicGate profile; authorized shiyan profiles permit verified High fallback')
    commands = parser.add_subparsers(dest="command", required=True)
    ask = commands.add_parser("ask", help="Send one prompt and print the complete answer")
    ask.add_argument("prompt", nargs="?")
    ask.add_argument("--file", type=Path)
    commands.add_parser("check", help="Health, live model catalog, and standard-mode TEST_OK")
    parallel = commands.add_parser('parallel', help='Inspect or set browser concurrency from 1 to 8 when idle')
    parallel.add_argument('limit', type=int, nargs='?', choices=range(1, 9))
    probe = commands.add_parser("probe", help="Run a fixed diagnostic prompt via the same standard call")
    probe.add_argument("name", choices=["cup"])
    args = parser.parse_args(argv)
    configure_profile(args.profile)
    if args.command == 'parallel':
        try:
            if args.limit is not None and session_frozen():
                raise CLIError('session_investigation', 'Concurrency changes are frozen during session investigation')
            _, state = http_json('/v1/mimic-cli/concurrency', read_auth(),
                {'max_concurrency': args.limit} if args.limit is not None else None)
            print(json.dumps(state, ensure_ascii=False, indent=2))
            if args.limit is not None:
                ROOT.joinpath('config').mkdir(exist_ok=True)
                config_name = {'yi': 'concurrency.json', 'shiyan': 'concurrency-shiyan.json',
                               'shiyan-camoufox': 'concurrency-shiyan-camoufox.json',
                               'yi-camoufox': 'concurrency-yi-camoufox.json'}[PROFILE]
                ROOT.joinpath('config', config_name).write_text(
                    json.dumps({'max_concurrency': args.limit}), encoding='utf-8')
            return 0
        except CLIError as error:
            print('ERROR ' + error.kind + ': ' + str(error), file=sys.stderr)
            return 1
    if args.command == "ask":
        if bool(args.prompt is not None) == bool(args.file):
            parser.error("ask requires exactly one of PROMPT or --file PATH")
        try:
            prompt = args.file.read_text(encoding="utf-8-sig") if args.file else args.prompt
        except (OSError, UnicodeError):
            parser.error("Cannot read the prompt file as UTF-8")
    elif args.command == "check":
        prompt = "Reply with exactly TEST_OK. No other text."
    else:
        try:
            prompt = ROOT.joinpath("prompts", "cup.txt").read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError):
            parser.error("Project-owned prompts/cup.txt is missing or is not UTF-8")
    if not prompt.strip():
        parser.error("Prompt must not be empty")
    now = datetime.now(timezone.utc)
    run_id = now.strftime("%Y%m%dT%H%M%S.%fZ") + "-" + uuid.uuid4().hex[:8]
    run = ROOT / "runs" / run_id
    run.mkdir(parents=True)
    record = {"run_id": run_id, "timestamp": now.isoformat(), "command": args.command, "profile": PROFILE,
              "probe": getattr(args, "name", None), "prompt": safe_text(prompt),
              "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
              "requested_model": MODEL, "requested_reasoning_effort": EFFORT,
              "success": False, "response": "", "http_status": None,
              "actual_model": None, "actual_reasoning_effort": None,
              "diagnostics": {}, "error": None}
    started = time.monotonic()
    answer = ""
    try:
        answer = standard_call(prompt, record)
        record["transport_success"] = True
        if args.command == "check" and answer.strip() != "TEST_OK":
            raise CLIError("check_answer", "Live standard request did not return exactly TEST_OK", record["http_status"])
        if args.command == "probe":
            assessment = assess_cup_answer(answer)
            record["probe_assessment"] = assessment
            if not assessment["normal"]:
                raise CLIError("probe_answer_" + assessment["status"],
                    "Cup probe expected answer 8; observed " + str(assessment["observed_answer"]),
                    record["http_status"])
        record["success"] = True
    except CLIError as error:
        record["http_status"] = error.status or record["http_status"]
        record["error"] = {"type": error.kind, "message": str(error)}
        if error.diagnostics:
            record["diagnostics"] = error.diagnostics
            model = error.diagnostics.get("model", {})
            record["actual_model"] = model.get("model")
            record["actual_reasoning_effort"] = model.get("selected_effort")
    except KeyboardInterrupt:
        record["error"] = {"type": "interrupted", "message": "CLI interrupted; server may finish its current request"}
    except Exception as error:
        record["error"] = {"type": "cli_internal", "exception_class": type(error).__name__,
                           "message": "CLI failed; no automatic resend"}
    finally:
        if args.command == 'probe' and record.get('diagnostics', {}).get('request_id'):
            record['local_screenshot_evidence'] = save_probe_screenshots(record, run)
            if not record['local_screenshot_evidence']['complete'] and PROFILE == 'yi' and record['success']:
                record['success'] = False
                record['error'] = {'type': 'probe_evidence_missing', 'message': 'Cup answer returned but screenshot evidence is incomplete; no automatic resend'}
        record["elapsed_seconds"] = round(time.monotonic() - started, 3)
        run.joinpath("prompt.txt").write_text(record["prompt"], encoding="utf-8")
        run.joinpath("response.txt").write_text(record["response"], encoding="utf-8")
        run.joinpath("diagnostics.json").write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Run: " + str(run), file=sys.stderr)
    if answer:
        print(answer)
    if record["success"]:
        return 0
    print("ERROR " + record["error"]["type"] + ": " + record["error"]["message"], file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
