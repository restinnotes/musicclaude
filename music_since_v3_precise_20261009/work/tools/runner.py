"""批量调用命令行模型客户端，把提示词/产物/meta 落盘。只用标准库。"""
from __future__ import annotations

import argparse
import contextlib
import concurrent.futures
import json
import os
import shutil
import time
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path

from execution_integrity import (ArtifactConflict, check_policy, checked_resume,
    digest, job_identity, run_process, safe_metadata, safe_text, sha_file, sha_text,
    write_json, write_text, safe_records, source_fingerprint, PROTECT_RE)

MODEL_NAMES = {
    "luna": "gpt-6-luna",
    "luna_noweb": "gpt-6-luna",  # codex exec, tools off (was missing: KeyError on every call)
    "gpro": "gemini-3.1-pro-high",
    "gflash": "gemini-3.8-flash-high",
    "gflash37": "gemini-3.7-flash-high",
    "gflash36": "gemini-3.6-flash-high",
    "gpro_web": "gemini-3.1-pro-high",
    "gflash_web": "gemini-3.8-flash-high",
    "gflash37_web": "gemini-3.7-flash-high",
    "muse": "opencode2api/muse-spark-1.3-contributor-free#xhigh",
    "muse_web": "opencode2api/muse-spark-1.3-contributor-free#xhigh",
    "muse_exec": "muse-spark-1.3-contributor-free",
    # user, 2026-09-25: Luna max through opencode's codex proxy for tool-free tasks (variant is validated by the proxy)
    "luna_oc": "codex-proxy-azure/gpt-6-luna#max",
    # user, 2026-09-27: candidates on the latest chain versions
    "sol": "gpt-6-sol", "sol_noweb": "gpt-6-sol",
    "opus": "claude-opus-5-5", "opus_web": "claude-opus-5-5",
    "sonnet": "claude-sonnet-5-5", "sonnet_web": "claude-sonnet-5-5",
    # judging round only (user, 2026-09-29): same model, but high effort instead of the xhigh that
    # material generation uses, so the generation run39 samples stay comparable with nothing else.
    "sonnet_hi": "claude-sonnet-5-5", "opus_hi": "claude-opus-5-5",
    "grok": "grok-4.7", "grok_web": "grok-4.7",
    # user, 2026-09-30: Grok through our account pool (the launcher t3code uses), not the personal Grok Build balance
    "grokp": "pool-grok-4-7", "grokp_web": "pool-grok-4-7",
    # user, 2026-10-04: the other models served by the same Grok pool, to be tried everywhere
    # grokp45: every call rejected with 401 after auth recovery (2026-10-04) - the pool accounts lack this model
    "grokp_composer": "pool-grok-composer-2-5-fast", "grokp45": "pool-grok-4-5", "grokp43": "pool-grok-4-3",
    "grokp420r": "pool-grok-4-20-reasoning", "grokp420n": "pool-grok-4-20-non-reasoning",
    # grokp420m: the grok CLI always sends client-side tools, which multi-agent models refuse without beta access
    # ("Client-side tools for multi-agent models require beta access", even with --tools "") - not usable for now
    "grokp420m": "pool-grok-4-20-multi-agent", "grokp_fast": "pool-grok-chat-fast",
    # user, 2026-09-27: codex exec lost gpt-6-sol ("not supported when using Codex with a ChatGPT account");
    # use opencode's openai provider instead (variants are validated by the provider)
    "sol_oc": "openai/gpt-6-sol#high", "sol_oc_web": "openai/gpt-6-sol#high",
    "luna_oc2": "openai/gpt-6-luna#max", "luna_oc2_web": "openai/gpt-6-luna#max",
    # user, 2026-09-29: Sol from now on = GPT-6.1 Sol medium (the old gpt-6-sol keys are kept only for past runs)
    "sol61": "openai/gpt-6.1-sol#medium", "sol61_web": "openai/gpt-6.1-sol#medium",
    # same model through codex exec (ChatGPT login) - backup when the opencode OpenAI quota is exhausted
    "sol61_cx": "gpt-6.1-sol", "sol61_cx_web": "gpt-6.1-sol",
    # user, 2026-10-03: harder tasks may use codex GPT-6.1 Sol at high effort
    "sol61_cxh": "gpt-6.1-sol",
    # user, 2026-10-04: GPT-5.6 Sol Extra High on the ChatGPT web page through the user's own MimicGate CLI
    # (mg ask --file; temporary + unpersonalized chat; up to 8 concurrent since 10-04 (`mg parallel`), up to 900 s per answer)
    # R1 (2026-10-08): gpt56w/gpt6w 默认经 tools/gpt2_adapter.py 走用户 gpt2 CLI；
    # MUSIC_WEB_ROUTE=mg 回退到旧 mg 路由（仅应急）。切换见 GPT2_ROUTE_OK。
    "gpt56w": "gpt-5.6-thinking (web, gpt2)",
    "gpt6w": "gpt-6-thinking (web, gpt2)",
    # user, 2026-09-30: GPT-6 Astra medium via opencode codex-proxy-azure (NOT the openai provider)
    "astra": "codex-proxy-azure/gpt-6-astra#medium",
    # user, 2026-09-30: Sol through codex-proxy (not the openai provider); sol61 / sol61_web above stay for past runs
    # sol61_cxp: listed by the server but fails with no-route (6.1 Sol is not actually served there, user 2026-09-30)
    "sol61_cxp": "codex-proxy-azure/gpt-6.1-sol#medium", "sol6_cxp": "codex-proxy-azure/gpt-6-sol#medium",
}
NODE_EXE = r"C:\Program Files\nodejs\node.exe"
MUSE_CMD = r"C:\Users\zuoyi\AppData\Local\Programs\muse\muse.cmd"
MUSE_SHIM_PY = r"C:\Users\zuoyi\AppData\Local\Temp\muse-test\muse_shim.py"
MUSE_SHIM_PORT = 8788
MUSE_SHIM_UPSTREAM = "http://127.0.0.1:18080/v1"
MUSE_SHIM_API_KEY = "public"
MUSE_SHIM_MODEL = "muse-spark-1.3-contributor-free"
# agy (stream-json stdin) keys; _web suffix = allowed online, no forbid_tools
AGY_KEYS = ("gpro", "gflash", "gflash37", "gflash36",
            "gpro_web", "gflash_web", "gflash37_web")
MUSE_KEYS = ("muse", "muse_web")
MUSE_EXEC_KEYS = ("muse_exec",)
LUNA_OC_KEYS = ("luna_oc", "sol_oc", "luna_oc2", "sol61", "astra", "sol61_cxp", "sol6_cxp")
OPENAI_OC_WEB_KEYS = ("sol_oc_web", "luna_oc2_web", "sol61_web")
# user, 2026-09-30: the codex-proxy server (127.0.0.1:8081, ssh tunnel) serves gpt-6-sol / gpt-6.1-sol, but the global
# opencode config does not declare them; declare them here (per-call config only; the global config stays untouched)
_CX_EFFORTS = {e: {"reasoningEffort": e} for e in ("low", "medium", "high", "xhigh")}
_CX_MODEL = lambda name: {"name": name, "reasoning": True, "modalities": {"input": ["text", "image"], "output": ["text"]},
                          "limit": {"context": 272000, "output": 128000},
                          "options": {"reasoningEffort": "medium"}, "variants": _CX_EFFORTS}
LUNA_OC_CFG = {"permission": "deny", "provider": {"codex-proxy-azure": {"options": {"timeout": False}, "models": {
    "gpt-6-sol": _CX_MODEL("GPT-6 Sol via Codex Proxy"), "gpt-6.1-sol": _CX_MODEL("GPT-6.1 Sol via Codex Proxy")}}}}
# OPENCODE_CONFIG_CONTENT 在 --standalone 私有 server 下是唯一实测有效的断网手段
# （2026-09-25 探测：诱发提示词下 standalone+该变量零 completed、40 次 refused；
# 同变量 shared 模式、项目级 opencode.json/jsonc、--agent plan、自定义 agent 全部无效）。
# muse（断网）= standalone + permission deny；muse_web = shared + 不设变量。
MUSE_OFFLINE_ENV = {"OPENCODE_CONFIG_CONTENT": '{"permission":"deny"}'}
_PRINT_LOCK = threading.Lock()
_INIT_LOCK = threading.Lock()
_STATE = {"init": False, "env": None, "agy": None, "opencode": None}


CLAUDE_KEYS = ("opus", "opus_web", "sonnet", "sonnet_web", "sonnet_hi", "opus_hi")  # claude CLI route
GROKP_EXTRA = ("grokp_composer", "grokp45", "grokp43", "grokp420r", "grokp420n", "grokp420m", "grokp_fast")
GROK_KEYS = ("grok", "grok_web", "grokp", "grokp_web") + GROKP_EXTRA  # Grok Build CLI (user, 2026-09-28): grok-4.7, xhigh
# 未通过真实健康复测前，未显式选路由的网页请求 fail closed，不默默走旧 mg。
WEB_ROUTE = os.environ.get("MUSIC_WEB_ROUTE", "blocked")
MG_KEYS = ("gpt56w",) if WEB_ROUTE == "mg" else ()
GPT2_KEYS = ("gpt56w", "gpt6w") if WEB_ROUTE == "gpt2" else ()
MG_PY = r"D:\musicclaude\mimic-cli\cli\mg.py"
CODEX_KEYS = ("luna", "luna_noweb", "sol", "sol_noweb", "sol61_cx_web", "sol61_cx", "sol61_cxh")  # codex exec route
CODEX_EFFORT = {"luna": "max", "luna_noweb": "max", "sol61_cx": "medium", "sol61_cx_web": "medium"}  # default high

def fill(template_text, **kv):
    """把模板里的 {{KEY}} 替换成值；有残留 {{ 则抛异常。"""
    out = template_text
    for k, v in kv.items():
        out = out.replace("{{" + str(k) + "}}", str(v))
    if "{{" in out:
        raise ValueError("unfilled placeholder remains in template")
    return out


def _reg_path_value(root, subkey):
    try:
        import winreg
    except ImportError:
        return None
    try:
        with winreg.OpenKey(root, subkey) as k:
            val, _ = winreg.QueryValueEx(k, "Path")
            return val
    except OSError:
        return None


def _ensure_init():
    if _STATE["init"]:
        return
    with _INIT_LOCK:
        if _STATE["init"]:
            return
        env = dict(os.environ)
        reg_vals = []
        try:
            import winreg
            v = _reg_path_value(winreg.HKEY_CURRENT_USER, r"Environment")
            if v:
                reg_vals.append(os.path.expandvars(v))
            v = _reg_path_value(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
            )
            if v:
                reg_vals.append(os.path.expandvars(v))
        except Exception:
            pass
        pkey = "Path" if "Path" in env else ("PATH" if "PATH" in env else "Path")
        old = env.get(pkey, "")
        parts = [p for p in reg_vals if p] + ([old] if old else [])
        env[pkey] = ";".join(parts)
        _STATE["env"] = env
        _STATE["pkey"] = pkey
        _STATE["agy"] = shutil.which("agy", path=env.get(pkey))
        _STATE["opencode"] = shutil.which("opencode", path=env.get(pkey))
        _STATE["init"] = True


def _build_task(model_key):
    """返回 (argv, stdin_mode, model_name)。argv 里是绝对路径。"""
    if model_key in ("gpt56w", "gpt6w") and model_key not in MG_KEYS:
        raise RuntimeError("网页路由未获健康验收或未显式选择；不回退。MUSIC_WEB_ROUTE=" + WEB_ROUTE)
    _ensure_init()
    if model_key in CODEX_KEYS:
        codex_js = os.path.join(os.environ.get("APPDATA", ""), r"npm\node_modules\@openai\codex\bin\codex.js")
        offline = model_key.endswith("_noweb") or model_key in ("sol61_cx", "sol61_cxh")
        search = "disabled" if offline else "live"
        effort = CODEX_EFFORT.get(model_key, "high")
        argv = [NODE_EXE, codex_js, "exec", "--skip-git-repo-check", "--json",
                "-m", MODEL_NAMES[model_key], "-c", f'model_reasoning_effort="{effort}"',
                "-c", f'web_search="{search}"']
        if offline:
            # web_search=disabled alone falls back to shell/MCP; switch every tool surface off
            for feat in ("shell_tool", "unified_exec", "apps", "plugins", "browser_use", "computer_use",
                         "in_app_browser", "multi_agent", "image_generation"):
                argv += ["--disable", feat]
            argv += ["-c", "mcp_servers.node_repl.enabled=false"]
        argv.append("-")
        return argv, "raw", MODEL_NAMES[model_key]
    if model_key in MG_KEYS:
        # the prompt file path is appended at call time (mg ask --file <prompt>); stdout is the full answer
        return [sys.executable, MG_PY, "ask", "--file"], "mg_file", MODEL_NAMES[model_key]
    if model_key in GROK_KEYS:
        # Grok Build single-turn mode from an empty cwd, neutral system prompt, prompt via --prompt-file.
        # User, 2026-09-28: do not restrict grok's tools. The earlier web tool allowlist
        # (web_search,web_fetch,open_page,open_page_with_find) left the model with read-only research
        # tools and no way to keep working, so 22 of 24 web jobs returned only their opening
        # "let me look this up" sentence (86-150 chars) and the runner still saw status=ok.
        # Only the offline key keeps --disable-web-search so the no-web branches stay offline.
        grok = shutil.which("grok", path=_STATE["env"].get(_STATE["pkey"])) or str(Path.home() / ".grok/bin/grok.exe")
        if model_key.startswith("grokp"):
            grok = str(Path.home() / ".grok/bin/grok-pool-v3.exe")
        # grok-4-5 / grok-4-3 accept at most "high" (measured 2026-10-04); the rest run at xhigh
        effort = "high" if model_key in ("grokp45", "grokp43") else "xhigh"
        argv = [grok, "-m", MODEL_NAMES[model_key], "--reasoning-effort", effort, "--output-format", "json",
                "--system-prompt-override", "You are a helpful assistant."]
        if model_key in ("grok_web", "grokp_web"):
            # Web turns research across many tool calls, so they need auto-approval and a turn budget.
            # Without them grok's turn ends with stopReason="cancelled" after 2-3 turns and returns only
            # its opening sentence (45-150 chars), which the runner used to record as a complete sample:
            # 22 of 24 web jobs in the first pass were truncated this way. Measured 2026-09-28 with
            # bypassPermissions + --max-turns 60: stopReason=end_turn, 4460 chars, $0.48.
            argv += ["--permission-mode", "bypassPermissions", "--max-turns", "60"]
        else:
            # Offline branches have nothing to research, so the model writes the answer itself.
            argv += ["--no-subagents", "--disable-web-search"]
        return argv, "prompt_file", MODEL_NAMES[model_key]
    if model_key in CLAUDE_KEYS:
        # Claude Code print mode, run from an empty cwd; no settings files, no MCP, neutral system prompt
        # (the default one is a coding agent). Offline: no tools at all; web: only WebSearch/WebFetch.
        claude = shutil.which("claude", path=_STATE["env"].get(_STATE["pkey"]))
        if not claude:
            raise FileNotFoundError("claude CLI not found in PATH")
        tools = "WebSearch,WebFetch" if model_key.endswith("_web") else ""
        # Material generation keeps Sonnet at xhigh (user, 2026-09-27); the judging round uses the
        # separate sonnet_hi key at high (user, 2026-09-29). Opus is high everywhere.
        effort = "high" if model_key.endswith("_hi") else ("xhigh" if model_key.startswith("sonnet") else "high")
        argv = [claude, "-p", "--model", MODEL_NAMES[model_key], "--effort", effort, "--output-format", "json",
                "--setting-sources", "", "--strict-mcp-config", "--system-prompt", "You are a helpful assistant.",
                "--tools", tools]
        if tools:
            argv += ["--allowedTools", tools]
        return argv, "raw", MODEL_NAMES[model_key]
    if model_key in AGY_KEYS:
        # User, 2026-09-25: stop using agy; Gemini now goes through opencode's antigravity-tools provider.
        # Offline keys mirror Muse offline (--standalone + deny config); *_web keys run in shared mode, tools allowed.
        opc = _STATE["opencode"]
        if not opc:
            raise FileNotFoundError("opencode not found in PATH (registry+env)")
        model = MODEL_NAMES[model_key]
        # always --standalone: only a private server reads OPENCODE_CONFIG_CONTENT (the shared service knows only
        # the globally declared models and rejects e.g. gemini-3.8-flash-high with provider.no-route)
        argv = [opc, "run", "--standalone", "--format", "json", "--model", "antigravity-tools/" + model]
        return argv, "raw", model
    if model_key in LUNA_OC_KEYS:
        # offline like muse: --standalone private server + deny config via OPENCODE_CONFIG_CONTENT
        opc = _STATE["opencode"]
        if not opc:
            raise FileNotFoundError("opencode not found in PATH (registry+env)")
        return [opc, "run", "--standalone", "--format", "json", "--model", MODEL_NAMES[model_key]], "raw", MODEL_NAMES[model_key]
    if model_key in OPENAI_OC_WEB_KEYS:
        # online like muse_web: shared server, no deny config, web tools allowed
        return [_STATE["opencode"], "run", "--format", "json", "--model", MODEL_NAMES[model_key]], "raw", MODEL_NAMES[model_key]
    if model_key in MUSE_KEYS:
        opc = _STATE["opencode"]
        if not opc:
            raise FileNotFoundError("opencode not found in PATH (registry+env)")
        # muse 断网（2026-09-25 实测有效）：--standalone 私有 server + 环境变量
        # OPENCODE_CONFIG_CONTENT='{"permission":"deny"}'。诱发提示词（明确要求上网+
        # 执行命令+读文件）下 standalone+该变量两次跑均为零 completed（一次 40 次
        # refused，一次 5 次 refused，文本照常输出）；同变量 shared 模式、项目级
        # opencode.json/jsonc（新旧 schema、deny 全量、agent 覆盖）、--agent plan
        # 全部挡不住（每次都有 completed）。muse_web 用 shared 模式且不设该变量。
        if model_key == "muse":
            argv = ["ignored", "run", "--standalone", "--format", "json", "--model", MODEL_NAMES[model_key]]
        else:
            argv = ["ignored", "run", "--format", "json", "--model", MODEL_NAMES[model_key]]
        argv[0] = opc
        return argv, "raw", MODEL_NAMES[model_key]
    if model_key in MUSE_EXEC_KEYS:
        # offline hard gate: CLI flags only (no config file mechanism exists).
        # 2026-09-25 probe: --disable-web-tools --disable-shell --disable-write
        # + no --workspace + untrusted cwd. web_search/powershell then fail
        # (HTTP 404 / policy denied / sandbox unavailable), but read_file on an
        # absolute path STILL completes (workspace root does not confine reads)
        # and 'search' (local file listing) still runs. So reads/listings are
        # NOT blocked: the forbid_tools void-and-retry below is the real gate
        # for read-like tools, same as for `muse`.
        argv = [MUSE_CMD, "exec", "--provider", "meta",
                "--base-url", "http://127.0.0.1:8788",
                "--model", MUSE_SHIM_MODEL,
                "--reasoning-effort", "xhigh", "--json",
                "--disable-web-tools", "--disable-shell", "--disable-write",
                "--no-session-log", "--approval-mode", "never"]
        return argv, "muse_exec", MODEL_NAMES[model_key]
    raise ValueError(f"unknown model_key: {model_key}")


def _parse_luna(stdout_text):
    counts: dict = {}
    last_text = ""
    for line in stdout_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        if obj.get("type") != "item.completed":
            continue
        item = obj.get("item") or {}
        itype = item.get("type", "")
        if itype == "agent_message":
            t = item.get("text", "")
            if isinstance(t, str) and t:
                last_text = t
        elif itype:
            counts[itype] = counts.get(itype, 0) + 1
    return last_text, counts, None


def _parse_agy(stdout_text):
    counts: dict = {}
    final = ""
    found_result = False
    ok = False
    err = None
    for line in stdout_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        ev = obj.get("event")
        if ev == "step_update":
            su = obj.get("step_update") or {}
            st = su.get("step_type", obj.get("step_type"))
            state = su.get("state", obj.get("state"))
            if state == "DONE" and st:
                counts[st] = counts.get(st, 0) + 1
                tn = su.get("tool_name")
                if st == "tool" and tn:
                    counts["tool:" + tn] = counts.get("tool:" + tn, 0) + 1
        elif ev == "result":
            found_result = True
            res = obj.get("result") or {}
            status = res.get("status")
            if status == "SUCCESS":
                ok = True
                resp = res.get("response")
                if isinstance(resp, str):
                    final = resp
                elif resp is None:
                    final = ""
                elif isinstance(resp, (dict, list)):
                    final = json.dumps(resp, ensure_ascii=False)
                else:
                    final = str(resp)
            else:
                ok = False
                e = res.get("error", res)
                err = e if isinstance(e, str) else json.dumps(e, ensure_ascii=False) if e is not None else f"status={status}"
    if not found_result:
        return "", counts, False, "no result event in stdout"
    if not ok:
        return "", counts, False, err or "result status != SUCCESS"
    return final, counts, True, None


def _parse_muse(stdout_text):
    """opencode --format json: text parts joined in order; tool parts counted by name."""
    texts, counts = [], {}
    for line in stdout_text.splitlines():
        try:
            obj = json.loads(line)
        except Exception:
            continue
        part = obj.get("part") or {}
        if part.get("type") == "text" and isinstance(part.get("text"), str):
            texts.append(part["text"])
        elif part.get("type") == "tool" and part.get("tool"):
            # only calls that actually ran count as tool use; refused attempts are kept for the record
            ran = (part.get("state") or {}).get("status") == "completed"
            key = ("tool:" if ran else "tried:") + str(part["tool"])
            counts[key] = counts.get(key, 0) + 1
    return "\n\n".join(t.strip() for t in texts if t.strip()), counts


def _parse_muse_exec(stdout_text):
    """muse exec --json JSONL: final text from run_output_delta/run_terminal;
    tool use from task_lifecycle proposed + completed/failed/rejected/output.

    completed + 真实结果 = `tool:`；rejected，或 failed 且附带 denied/
    unavailable/unknown-tool/os error/HTTP 404/sandbox failure 等文本 =
    `tried:`（被拒，未执行）。failed 但无失败文本 = 视为真正执行过（`tool:`）。
    reminder.* 等非 tool.* 的 task_kind 不计入（内部提醒子任务，非工具调用）。
    output 事件只承载结果文本，不单独计数（由配对的 completed/failed 计一次）。
    """
    texts, counts = [], {}
    proposed = {}
    terms, deltas = [], []
    for line in stdout_text.splitlines():
        try:
            obj = json.loads(line)
        except Exception:
            continue
        pl = obj.get("payload") or {}
        kind = pl.get("kind")
        if kind == "run_terminal":
            terms.append(pl)
            continue
        if kind == "run_output_delta" and isinstance(pl.get("text"), str):
            deltas.append(pl["text"])
            continue
        if kind == "task_lifecycle":
            ev = pl.get("event") or {}
            ek = ev.get("kind")
            if ek == "proposed":
                tk = ev.get("task_kind", "")
                if tk.startswith("tool."):
                    proposed[ev.get("task_id")] = tk[5:]
            elif ek in ("completed", "failed", "rejected", "output") and ev.get("task_id") in proposed:
                if ek == "output":
                    continue  # outcome recorded by the paired completed/failed/rejected
                name = proposed.pop(ev["task_id"])
                chunk = ev.get("chunk") or ""
                reason = ev.get("reason") or ""
                fail_text = (chunk + " " + reason).lower()
                denied = ("denied" in fail_text or "unavailable" in fail_text
                          or "unknown tool" in fail_text or "not found" in fail_text
                          or "os error" in fail_text or "failed" in fail_text
                          or "http 404" in fail_text or "environment failure" in fail_text)
                key = ("tried:" if (ek == "rejected" or (ek == "failed" and denied)) else "tool:") + name
                counts[key] = counts.get(key, 0) + 1
    if terms:
        last = terms[-1]
        if isinstance(last.get("text"), str) and last["text"].strip():
            texts = [last["text"]]
        else:
            texts = deltas
    else:
        texts = deltas
    return "".join(texts).strip(), counts


# every opencode child runs in a folder whose local config switches all tools off.
# NOTE: 2026-09-25 探测结论：项目级 opencode.json/jsonc 对 opencode 2.0.16 的 run
# 无约束力（新旧 schema、deny 全量、agent 覆盖、--agent plan 全部挡不住，每次都有
# completed；--standalone 同样无效）。唯一有效的是环境变量
# OPENCODE_CONFIG_CONTENT='{"permission":"deny"}' + --standalone（诱发提示词下
# 3 次跑均为零 completed：40/5/14 次 refused，真实音乐提示词下零 completed、
# 11 次 refused 且正文质量正常）。muse 的隔离靠该变量（见 MUSE_OFFLINE_ENV）+
# forbid_tools 事后作废重跑；这两个文件仅作占位/双保险。
# opencode aborts a provider request on its default request timeout; long xhigh Muse turns (>~5 min) came back empty.
# Verified 2026-09-25: with the timeout off, the same failing prompt finished in 351 s and 274 s (2/2).
RATE_LIMIT_WAIT = 120  # seconds to wait after an upstream 429 before the next attempt
OPENCODE_NO_TIMEOUT = {"provider": {"opencode2api": {"options": {"timeout": False}}}}
# Gemini through opencode: declare the antigravity-tools models the user's global config lacks, and switch off
# opencode's provider request timeout (same failure mode as Muse on long turns).
GEMINI_PROVIDER_CFG = {"provider": {"antigravity-tools": {"options": {"timeout": False}, "models": {
    m: {} for m in ("gemini-3.8-flash-high", "gemini-3.1-pro-high", "gemini-3.7-flash-high", "gemini-3.6-flash-high")}}}}
OPENCODE_NO_TOOLS = {"$schema": "https://opencode.ai/config.json", "tools": {"*": False}, "permission": {"*": "deny"}, **OPENCODE_NO_TIMEOUT}
# user-tested extra layer: permission-array form (websearch+webfetch+execute+shell deny).
OPENCODE_NO_NET = {"$schema": "https://opencode.ai/config.json", "websearch": False,
                   "permissions": [
                       {"action": "websearch", "resource": "*", "effect": "deny"},
                       {"action": "webfetch", "resource": "*", "effect": "deny"},
                       {"action": "execute", "resource": "*", "effect": "deny"},
                       {"action": "shell", "resource": "*", "effect": "deny"}]}


def _muse_shim_alive(port=MUSE_SHIM_PORT):
    import socket
    try:
        s = socket.create_connection(("127.0.0.1", port), timeout=3)
        s.close()
        return True
    except OSError:
        return False


def _ensure_muse_shim():
    """shim 常驻 8788：先检查监听，不在就用独立隐藏进程启动并等就绪。"""
    if _muse_shim_alive():
        return
    import sys
    import time
    log = Path(MUSE_SHIM_PY).parent / "shim_runner.log"
    # detached + hidden: runner 退出后 shim 继续存活
    creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
    startupinfo = None
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE
    with open(str(log), "ab") as lf:
        subprocess.Popen(
            [sys.executable, MUSE_SHIM_PY, "generic", "--port", str(MUSE_SHIM_PORT),
             "--upstream", MUSE_SHIM_UPSTREAM, "--api-key", MUSE_SHIM_API_KEY,
             "--model", MUSE_SHIM_MODEL],
            stdout=lf, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
            cwd=str(Path(MUSE_SHIM_PY).parent),
            creationflags=creationflags, startupinfo=startupinfo,
            close_fds=True)
    for _ in range(60):
        if _muse_shim_alive():
            return
        time.sleep(1)
    raise RuntimeError("muse shim did not listen on 8788 (log=%s)" % log)


def _sanitize_argv(argv):
    out = []
    for a in argv:
        s = a if isinstance(a, str) else str(a)
        out.append(f"<{len(s)} chars>" if len(s) > 300 else s)
    return out


def _write_text(path, text):
    write_text(path, text)


# Machine-wide cap on concurrent model calls, shared by every script and process on this box.
# One opencode --standalone call peaks near 400 MB; 2026-09-25 several scripts each raised their own
# pool, ~158 calls ran at once and exhausted 31.5 GB of RAM. Slots are OS file locks, so a slot held by
# a process that dies is released automatically.
MAX_GLOBAL_CALLS = int(os.environ.get("MUSIC_MAX_CALLS", "40"))
# Per-provider cap on top of the machine cap. 2026-09-25: the antigravity-tools proxy answered 8 concurrent
# Gemini calls in ~49 s each, but with ~38 concurrent long prompts it went silent (0 replies in 2 h, every
# call hit its timeout while holding a machine slot).
MAX_GEMINI_CALLS = int(os.environ.get("MUSIC_MAX_GEMINI_CALLS", "8"))
_SLOT_DIR = Path(__file__).resolve().parents[1] / "runs" / "_call_slots"


class _GlobalSlot:
    def __init__(self, pool="all", cap=None):
        self.pool, self.cap = pool, cap

    def __enter__(self):
        import msvcrt
        cap = self.cap if self.cap is not None else MAX_GLOBAL_CALLS
        slot_dir = _SLOT_DIR if self.pool == "all" else _SLOT_DIR / self.pool
        slot_dir.mkdir(parents=True, exist_ok=True)
        while True:
            for i in range(cap):
                fd = os.open(str(slot_dir / f"slot{i:03d}"), os.O_RDWR | os.O_CREAT)
                try:
                    msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                except OSError:
                    os.close(fd)
                    continue
                self.fd = fd
                return self
            time.sleep(2)

    def __exit__(self, *exc):
        import msvcrt
        try:
            os.lseek(self.fd, 0, os.SEEK_SET)
            msvcrt.locking(self.fd, msvcrt.LK_UNLCK, 1)
        finally:
            os.close(self.fd)
        return False


def request_identity_for(job):
    """当前真实入口与输入/采样身份；用于新记录，绝不补写历史身份证据。"""
    model = job["model_key"]
    if model in GPT2_KEYS:
        import gpt2_adapter
        producer = gpt2_adapter.producer_identity()
        identity = gpt2_adapter.request_identity(model, "max", job["prompt"], producer=producer,
                                                sampling_key=job.get("sampling_key", job["job_id"]))
        identity["request_context"] = job_identity(job, dict(producer, runner_sha256=sha_file(__file__)))
        return identity
    producer = {"runner_sha256": sha_file(__file__),
                "integrity_sha256": sha_file(Path(__file__).with_name("execution_integrity.py"))}
    try:
        argv, stdin_mode, name = _build_task(model)
        files = {str(p): sha_file(p) for p in map(Path, argv) if p.is_file()}
        # 入口 JS 很小，但实际 Codex 执行的是包内 native binary；两者都冻结。
        for arg in argv:
            p = Path(arg)
            if p.name == "codex.js" and p.is_file():
                for native in p.parent.parent.rglob("codex.exe"):
                    files[str(native)] = sha_file(native)
        producer.update(route=stdin_mode, model_name=name, argv=_sanitize_argv(argv), cli_files=files,
                        gemini_config_sha256=digest(GEMINI_PROVIDER_CFG) if model in AGY_KEYS else None)
    except Exception as e:
        producer.update(route="initialization_failed", model_name=MODEL_NAMES.get(model, model),
                        initialization_error=safe_text("%s: %s" % (type(e).__name__, e)))
    return job_identity(job, producer)


def run_job(run_dir, job, timeout=3600):
    """执行新 job 或 exact identity 只读恢复；旧/冲突 job 必须另取新名。"""
    run_dir = Path(run_dir)
    job_id = job["job_id"]
    branch = job.get("branch", "")
    model_key = job["model_key"]
    check_policy(model_key)
    identity = request_identity_for(job)
    previous = checked_resume(run_dir, job_id, identity)
    if previous is not None:
        return previous
    if any((run_dir / d / (job_id + ext)).exists() for d, ext in (("prompts", ".txt"), ("outputs", ".md"))):
        raise ArtifactConflict("旧/未完成产物只读，请用新 run/job_id：" + job_id)
    if model_key in GPT2_KEYS:
        # R1：网页模型经 gpt2 适配器（缓存键含 prompt 全文；旧缓存隔离）。
        # 串行化：gpt2 链路一次只跑一个浏览器初始化，并发由调用方控制。
        import sys as _sys
        _this_dir = str(Path(__file__).resolve().parent)
        if _this_dir not in _sys.path:
            _sys.path.insert(0, _this_dir)
        import gpt2_adapter
        # 锁在 adapter 内：直接 smoke 调用也与 runner 共用，避免嵌套同槽死锁。
        meta = gpt2_adapter.call_web_gpt(
            model_key, job["prompt"], run_id=Path(run_dir).name,
            job_id=job_id, out_dir=run_dir,
            effort="max", timeout=timeout,
            max_attempts=int(job.get("max_attempts", 1)),
            sampling_key=job.get("sampling_key", job_id),
            use_cache=job.get("use_cache", True), request_context=identity["request_context"])
        meta["branch"] = branch
        meta["prompt_version"] = job.get("prompt_version", "")
        meta["prompt_template"] = job.get("prompt_template")
        meta["work_key"] = job.get("work_key", "")
        meta["work_name"] = job.get("work_name", "")
        meta["sample"] = job.get("sample", 0)
        meta["extra"] = job.get("extra") or {}
        meta["model_name"] = MODEL_NAMES.get(model_key, model_key)
        meta["tool_counts"] = meta.get("tool_counts") or {}
        write_json(run_dir / "meta" / (job_id + ".json"), meta)
        return meta
    prompt = job["prompt"]
    prompt_version = job.get("prompt_version", "")
    prompt_template = job.get("prompt_template")
    work_key = job.get("work_key", "")
    work_name = job.get("work_name", "")
    sample = job.get("sample", 0)
    extra = job.get("extra") or {}

    prompts_dir = run_dir / "prompts"
    outputs_dir = run_dir / "outputs"
    raw_dir = outputs_dir / "raw"
    meta_dir = run_dir / "meta"
    empty_cwd = run_dir / "_empty_cwd"
    web_cwd = run_dir / "_web_cwd"
    mexec_cwd = run_dir / "_muse_exec_cwd"
    for d in (prompts_dir, outputs_dir, raw_dir, meta_dir, empty_cwd, web_cwd, mexec_cwd):
        d.mkdir(parents=True, exist_ok=True)
    if model_key == "muse":
        (empty_cwd / "opencode.json").write_text(json.dumps(OPENCODE_NO_TOOLS), encoding="utf-8")
        (empty_cwd / "opencode.jsonc").write_text(json.dumps(OPENCODE_NO_NET), encoding="utf-8")
        work_dir = empty_cwd
    elif model_key == "muse_web":
        # online Muse: separate cwd, no offline config written
        for stale in ("opencode.json", "opencode.jsonc"):
            try:
                (web_cwd / stale).unlink()
            except OSError:
                pass
        (web_cwd / "opencode.json").write_text(json.dumps({"$schema": "https://opencode.ai/config.json", **OPENCODE_NO_TIMEOUT}), encoding="utf-8")
        work_dir = web_cwd
    elif model_key in MUSE_EXEC_KEYS:
        # 空目录，不传 --workspace（默认 cwd 即 workspace root，保持 untrusted）；
        # 不在该目录放任何项目文件
        for stale in ("opencode.json", "opencode.jsonc", ".opencode"):
            try:
                p = mexec_cwd / stale
                if p.is_dir() and not p.is_symlink():
                    shutil.rmtree(p)
                else:
                    p.unlink()
            except OSError:
                pass
        work_dir = mexec_cwd
    elif (model_key in AGY_KEYS and model_key.endswith("_web")) or model_key in OPENAI_OC_WEB_KEYS:
        work_dir = web_cwd
    else:
        work_dir = empty_cwd

    prompt_rel = f"prompts/{job_id}.txt"
    output_rel = f"outputs/{job_id}.md"
    stdout_rel = f"outputs/raw/{job_id}.stdout.txt"
    stderr_rel = f"outputs/raw/{job_id}.stderr.txt"
    _write_text(run_dir / prompt_rel, prompt)

    started_dt = datetime.now()
    started = started_dt.isoformat(timespec="seconds")

    try:
        if identity["producer"].get("initialization_error"):
            raise RuntimeError(identity["producer"]["initialization_error"])
        argv, stdin_mode, model_name = _build_task(model_key)
        if extra.get("images") and model_key in CODEX_KEYS:
            # codex exec -i <image> ...; images are given as absolute paths in job["extra"]["images"]
            argv = argv[:-1] + [x for img in extra["images"] for x in ("-i", str(img))] + argv[-1:]
    except Exception as e:
        ended_dt = datetime.now()
        meta = {
            "job_id": job_id, "branch": branch, "model_key": model_key,
            "model_name": MODEL_NAMES.get(model_key, model_key),
            "argv": [], "stdin_mode": "raw",
            "prompt_file": prompt_rel, "prompt_version": prompt_version,
            "prompt_template": prompt_template, "work_key": work_key,
            "work_name": work_name, "sample": sample,
            "started": started, "ended": ended_dt.isoformat(timespec="seconds"),
            "seconds": round((ended_dt - started_dt).total_seconds(), 1),
            "exit_code": None, "status": "failed", "error": f"{type(e).__name__}: {e}",
            "attempts": 0, "output_file": output_rel, "stdout_file": stdout_rel,
            "stderr_file": stderr_rel, "output_chars": 0, "replacement_chars": 0,
            "tool_counts": {}, "extra": extra,
        }
        _write_text(run_dir / output_rel, "")
        _write_text(run_dir / stdout_rel, "")
        _write_text(run_dir / stderr_rel, "")
        meta.update(request_identity=identity, producer_identity=identity["producer"],
                    prompt_sha256=sha_text(prompt), response_sha256=None,
                    automatic_retry=False, retry_safe=True, failure_phase="local_initialization",
                    queue_stop=False, raw_redacted=True)
        meta = safe_metadata(meta)
        write_json(meta_dir / (job_id + ".json"), meta)
        return meta

    _ensure_init()
    child_env = dict(_STATE["env"])
    if model_key == "muse":
        # 唯一实测有效的断网手段；muse_web 故意不设以允许联网
        child_env.update(MUSE_OFFLINE_ENV)
    if model_key in AGY_KEYS:
        gem_cfg = dict(GEMINI_PROVIDER_CFG)
        if not model_key.endswith("_web"):
            gem_cfg["permission"] = "deny"
        child_env["OPENCODE_CONFIG_CONTENT"] = json.dumps(gem_cfg)
    if model_key in LUNA_OC_KEYS:
        child_env["OPENCODE_CONFIG_CONTENT"] = json.dumps(LUNA_OC_CFG)
    if model_key in MUSE_EXEC_KEYS:
        child_env["META_API_KEY"] = "local-shim-placeholder"
        _ensure_muse_shim()

    if stdin_mode == "ndjson":
        stdin_bytes = (json.dumps({"event": "user", "message": {"content": prompt}}, ensure_ascii=False) + "\n").encode("utf-8")
    elif stdin_mode in ("muse_exec", "prompt_file", "mg_file"):
        # 完整提示词走 --prompt-file（已落盘的 prompts/<job_id>.txt），不走 stdin
        stdin_bytes = None
    else:
        stdin_bytes = prompt.encode("utf-8")

    attempts = 0
    exit_code = None
    error = None
    final_text = ""
    tool_counts: dict = {}
    out_s = err_s = ""
    queue_stop = False
    provider = ("gemini" if model_key in AGY_KEYS else "codex" if model_key in CODEX_KEYS
                else "mg" if model_key in MG_KEYS else "grokpool" if model_key.startswith("grokp")
                else "model_" + model_key)
    hold_file = _SLOT_DIR / provider / "queue_hold.json"
    prompt_file_abs = str((run_dir / prompt_rel).resolve())
    # 单次提交；解析重采样由实验层另取 attempt ID，不能覆盖本 job 的失败证据。
    for _ in range(min(1, max(0, int(job.get("max_attempts", 1))))):
        try:
            provider_slot = (_GlobalSlot("gemini", MAX_GEMINI_CALLS) if model_key in AGY_KEYS
                             else _GlobalSlot("mg", 8) if model_key in MG_KEYS  # user 10-04: `mg parallel` max_concurrency 8
                             # the Grok pool rejects calls over its concurrency cap; keep all pool models to 2 at once
                             else _GlobalSlot("grokpool", 2) if model_key.startswith("grokp")
                             else contextlib.nullcontext())
            # provider slot first: waiting for Gemini must not hold one of the machine slots
            with provider_slot, _GlobalSlot():
                if hold_file.exists():
                    error = "provider queue held; inspect " + str(hold_file)
                    queue_stop = True
                    break
                attempts += 1
                if stdin_mode == "mg_file":
                    cp = run_process(list(argv) + [prompt_file_abs], input=None, capture_output=True,
                                        cwd=str(work_dir), env=child_env, timeout=timeout,
                                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                elif stdin_mode in ("muse_exec", "prompt_file"):
                    run_argv = list(argv) + ["--prompt-file", prompt_file_abs]
                    cp = run_process(run_argv, input=None, capture_output=True,
                                        cwd=str(work_dir), env=child_env, timeout=timeout,
                                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                else:
                    cp = run_process(argv, input=stdin_bytes, capture_output=True,
                                        cwd=str(work_dir), env=child_env, timeout=timeout,
                                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            exit_code = cp.returncode
            out_s = cp.stdout.decode("utf-8", "replace")
            err_s = cp.stderr.decode("utf-8", "replace")
        except subprocess.TimeoutExpired as e:
            exit_code = None
            out_s = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
            err_s = (e.stderr or b"").decode("utf-8", "replace") if isinstance(e.stderr, bytes) else (e.stderr or "")
            error = f"timeout after {timeout}s"
            queue_stop = True
            write_json(hold_file, {"job_id": job_id, "run_id": run_dir.name,
                                  "reason": "timeout; server turn unknown", "created": datetime.now().isoformat()})
            _write_text(run_dir / stdout_rel, safe_records(out_s))
            _write_text(run_dir / stderr_rel, safe_records(err_s))
            final_text, tool_counts = "", {}
            break  # 本地进程树已回收；服务端状态未知，不自动重复提交。
        except Exception as e:
            exit_code = None
            error = f"{type(e).__name__}: {e}"
            out_s, err_s = "", error
            _write_text(run_dir / stdout_rel, safe_records(out_s))
            _write_text(run_dir / stderr_rel, safe_records(err_s))
            final_text, tool_counts = "", {}
            continue

        _write_text(run_dir / stdout_rel, safe_records(out_s))
        _write_text(run_dir / stderr_rel, safe_records(err_s))

        if exit_code != 0 and PROTECT_RE.search(err_s):  # 10-09: only a failed call's stderr; model text must not lock the queue
            error = "protection signal; provider queue stopped"
            queue_stop = True
            final_text, tool_counts = "", {}
            write_json(hold_file, {"job_id": job_id, "run_id": run_dir.name,
                                  "reason": "protection_signal", "created": datetime.now().isoformat()})
            break
        if exit_code != 0:
            tail = safe_text(err_s.strip()[-500:])
            error = f"exit {exit_code}" + (f": {tail}" if tail else "")
            final_text, tool_counts = "", {}
            if PROTECT_RE.search(err_s):
                break  # 不通过重试规避账号保护/限流。
            continue

        if model_key in GROK_KEYS:
            try:
                res = json.loads(out_s[out_s.find("{"):out_s.rfind("}") + 1])
            except Exception:
                res = {}
            final_text = res.get("text") or ""
            tool_counts = {"num_turns": res.get("num_turns", 0)}
            if res.get("type") == "error" or not final_text.strip():
                error = "grok: " + (str(res.get("message") or res.get("stopReason") or "empty output"))[:300]
                final_text = ""
                continue
            # A web job that only restates its plan and stops (e.g. "let me look this up" and nothing
            # else) is a truncated turn, not an answer. Reject it so the job is retried instead of
            # being stored as a complete sample.
            if model_key in ("grok_web", "grokp_web") and len(final_text.strip()) < 400:
                error = f"grok: truncated web turn ({len(final_text.strip())} chars, no article)"
                final_text = ""
                continue
        elif model_key in MG_KEYS:
            final_text = out_s.strip()
            run_line = next((l for l in err_s.splitlines() if l.startswith("Run:")), "")
            tool_counts = {"mg_run": run_line[4:].strip()}
            if not final_text:
                error = "mg: empty answer " + err_s.strip()[-300:]
                continue
        elif model_key in CLAUDE_KEYS:
            try:
                res = json.loads(out_s.strip().splitlines()[-1])
            except Exception:
                res = {}
            final_text = res.get("result") or ""
            tool_counts = {"num_turns": res.get("num_turns", 0)}
            if res.get("is_error") or not final_text.strip():
                error = "claude: " + (str(res.get("subtype") or res.get("result") or "empty output"))[:300]
                final_text = ""
                continue
        elif model_key in CODEX_KEYS:
            final_text, tool_counts, _ = _parse_luna(out_s)
            if not final_text.strip():
                error = "empty output"
                final_text = ""
                continue
            # 10-09: codex "error" items are config warnings (e.g. ignored config key), not tool use
            used = [k for k in tool_counts if k not in ("reasoning", "todo_list", "error")]
            if job.get("forbid_tools") and used:
                error = "tools used: " + ",".join(used)
                final_text = ""
                continue
        elif model_key in AGY_KEYS and False:  # agy retired 2026-09-25; kept for reference
            final_text, tool_counts, ok, perr = _parse_agy(out_s)
            if not ok:
                error = perr or "agy result != SUCCESS"
                final_text = ""
                continue
            if not final_text.strip():
                error = "empty output"
                final_text = ""
                continue
            # internal-weight branches must not reach the web; discard and retry if they did
            used = [k for k in tool_counts if k.startswith("tool:") and k[5:] in job.get("forbid_tools", ())]
            if used:
                error = "forbidden tools used: " + ",".join(used)
                final_text = ""
                continue
        else:  # muse / muse_exec
            if model_key in MUSE_EXEC_KEYS:
                final_text, tool_counts = _parse_muse_exec(out_s)
            else:
                final_text, tool_counts = _parse_muse(out_s)
            if not final_text.strip():
                error = "empty output"
                continue
            # antigravity-tools answers a tool attempt it cannot route with a canned apology instead of the text
            if model_key in AGY_KEYS and "尝试调取实时信息时遇到了格式异常" in final_text:
                error = "proxy canned tool-error reply"
                final_text = ""
                continue
            # opencode ships web tools; the local config turns them off, and any tool call voids a no-tool job
            used = [k for k in tool_counts if k.startswith("tool:")]
            if used and job.get("forbid_tools"):
                error = "tools used: " + ",".join(used)
                final_text = ""
                continue
        error = None
        break

    if not final_text.strip() and error is None:
        error = "empty output (no successful attempt)"
    status = "ok" if error is None else "failed"
    _write_text(run_dir / output_rel, final_text)
    ended_dt = datetime.now()
    meta = {
        "job_id": job_id, "branch": branch, "model_key": model_key,
        "model_name": model_name, "argv": _sanitize_argv(argv),
        "stdin_mode": stdin_mode, "prompt_file": prompt_rel,
        "prompt_version": prompt_version, "prompt_template": prompt_template,
        "work_key": work_key, "work_name": work_name, "sample": sample,
        "started": started, "ended": ended_dt.isoformat(timespec="seconds"),
        "seconds": round((ended_dt - started_dt).total_seconds(), 1),
        "exit_code": exit_code, "status": status, "error": error,
        "attempts": attempts, "output_file": output_rel,
        "stdout_file": stdout_rel, "stderr_file": stderr_rel,
        "output_chars": len(final_text),
        "replacement_chars": final_text.count("\ufffd"),
        "tool_counts": tool_counts, "extra": extra,
    }
    meta.update(request_identity=identity, producer_identity=identity["producer"],
                response_sha256=sha_text(final_text) if status == "ok" else None,
                prompt_sha256=sha_text(prompt), automatic_retry=False,
                retry_safe=False if error else None, queue_stop=queue_stop,
                raw_redacted=True, consumer_identity=identity["producer"],
                attempts_requested=int(job.get("max_attempts", 1)))
    meta = safe_metadata(meta)
    write_json(meta_dir / (job_id + ".json"), meta)
    return meta


def run_jobs(run_dir, jobs, max_workers=8, timeout=3600):
    """并行执行 jobs；已有 ok 的 meta 则跳过。返回与输入同序的 meta 列表。"""
    run_dir = Path(run_dir)
    results: dict = {}
    pending = []

    def _report(m):
        with _PRINT_LOCK:
            print(f"[{m['status']}] {m['job_id']} {m['seconds']} {m['output_chars']} {m['tool_counts']}", flush=True)

    if len({j["job_id"] for j in jobs}) != len(jobs):
        raise ValueError("duplicate job_id in batch")
    for j in jobs:
        check_policy(j["model_key"])
        data = checked_resume(run_dir, j["job_id"], request_identity_for(j))
        if data is not None:
            results[j["job_id"]] = data
            _report(data)
            continue
        pending.append(j)
    if pending:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
            futs = {ex.submit(run_job, str(run_dir), j, timeout): j["job_id"] for j in pending}
            for fut in concurrent.futures.as_completed(futs):
                m = fut.result()
                results[m["job_id"]] = m
                _report(m)
    return [results[j["job_id"]] for j in jobs]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("jobs_json")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--timeout", type=float, default=3600)
    a = ap.parse_args(argv)
    jobs_path = Path(a.jobs_json)
    jobs = json.loads(jobs_path.read_text(encoding="utf-8"))
    for j in jobs:
        if ("prompt" not in j or j["prompt"] is None) and "prompt_file" in j:
            pf = Path(j["prompt_file"])
            if not pf.is_absolute():
                if not pf.exists() and (jobs_path.parent / pf).exists():
                    pf = jobs_path.parent / pf
            j["prompt"] = pf.read_text(encoding="utf-8")
        if "prompt" not in j or not isinstance(j["prompt"], str):
            raise ValueError(f"job {j.get('job_id')} missing prompt (or prompt_file)")
    run_jobs(a.run_dir, jobs, max_workers=a.workers, timeout=a.timeout)


if __name__ == "__main__":
    main()
