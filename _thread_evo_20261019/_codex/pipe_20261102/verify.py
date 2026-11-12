"""Offline integration checks: real modules, stubbed model boundary, guarded writes."""
import contextlib
import copy
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import threading
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
TEMP = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))
RESULTS = {"mock_prompts": [], "saved_files": [], "real_prompts": [], "checks": []}
BLOCKED = []


def inside_temp(path):
    return Path(os.fsdecode(path)).resolve().is_relative_to(TEMP)


def audit(event, args):
    # No transport, model CLI, shell, or process creation is allowed in this process.
    if event.startswith("socket.") or event in {"subprocess.Popen", "os.system", "os.startfile", "os.posix_spawn"}:
        BLOCKED.append(event)
        raise AssertionError(f"offline validation forbids {event}")
    if event == "open" and not isinstance(args[0], int):
        path, mode, flags = args
        writing = (mode is not None and any(c in mode for c in "wax+")) or (
            flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
        if writing and not inside_temp(path):
            BLOCKED.append(f"write: {path}")
            raise AssertionError(f"write outside validation directory: {path}")
    if event == "os.mkdir" and not inside_temp(args[0]) and not Path(args[0]).is_dir():
        BLOCKED.append(f"mkdir: {args[0]}")
        raise AssertionError(f"new directory outside validation directory: {args[0]}")
    if event in {"os.remove", "os.rmdir", "os.rename", "os.link", "os.symlink"}:
        paths = args[:2] if event in {"os.rename", "os.link", "os.symlink"} else args[:1]
        if any(not inside_temp(p) for p in paths):
            BLOCKED.append(event)
            raise AssertionError(f"mutation outside validation directory: {event}")


sys.addaudithook(audit)
import evo


def forbidden(*args, **kwargs):
    raise AssertionError("unstubbed model call reached")


# Patch before importing any consumer. Each test installs its explicit fake later.
evo.call = forbidden
evo.done = lambda rid: False
import covjudge
import v6fix as V
V.parse = forbidden
import schemes as legacy
import pipe

ORIGINAL_OUT = V.OUT
legacy.REF = "m6w"
SPECS = {name: pipe.load_spec(ROOT / "schemes" / f"{name}.json") for name in ("P", "Q")}
CONTEXTS = {w: pipe.work_context(w, "m6w") for w in ("op60", "op61")}
CAPTURE = {}
LOCK = threading.Lock()


def fake_json(w, sid):
    graph = CONTEXTS[w][1]
    segments = []
    previous = None
    for segment in graph["segments"]:
        sec = segment["sec"]
        # Exercise previous/same/future/invalid references, follows and extra fields.
        cites = ([previous] if previous else []) + [f"{sec}-1", "S99-1", 17, None]
        segments.append({"sec": sec, "relation": "还说不清", "items": [
            {"text": f"{w}/{sid}/{sec}：中文、引号\"与换行\n第二行。", "cite": cites, "after": False},
            {"text": f"{sec} 的第二条。", "cite": [previous] if previous else [], "after": "yes"},
        ]})
        previous = f"{sec}-1"
    return {"来源": f"{w}/{sid}", "混合": [True, None, 3, "中文"], "segments": segments}


def parse_id(rid):
    parts = rid.split("_")
    return parts[1], parts[2]


def fake_parse(rid):
    return fake_json(*parse_id(rid))


def fake_call(rid, message, **kwargs):
    with LOCK:
        assert rid not in CAPTURE, f"duplicate call: {rid}"
        CAPTURE[rid] = {"message": message, "kwargs": copy.deepcopy(kwargs)}
    return "unused; output comes from V.parse stub"


def prepare_out(label):
    out = TEMP / label
    out.mkdir(exist_ok=True)
    for w in CONTEXTS:
        (out / f"{w}_m6w.json").write_bytes((ORIGINAL_OUT / f"{w}_m6w.json").read_bytes())
    V.OUT = out
    return out


def check(label, details):
    RESULTS["checks"].append({"name": label, "passed": True, "details": details})


def digest(data):
    return hashlib.sha256(data).hexdigest()


def assert_raises(fn, error=ValueError):
    try:
        fn()
    except error:
        return
    raise AssertionError(f"expected {error.__name__}")


def write_spec(name, data):
    path = TEMP / f"fixture_{name}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def raw_spec(name):
    return json.loads((ROOT / "schemes" / f"{name}.json").read_text(encoding="utf-8"))


def validate_all():
    global CAPTURE
    transcript = io.StringIO()
    with contextlib.redirect_stdout(transcript), patch.object(V, "parse", fake_parse), patch.object(evo, "call", fake_call):
        for name, tag in [("P", "pa"), ("Q", "qa")]:
            legacy.SCHEME, legacy.TAG = name, tag
            CAPTURE = {}
            old_out = prepare_out(f"legacy_{name}")
            for w in CONTEXTS:
                getattr(legacy, f"run_{name}")(w)
            expected = copy.deepcopy(CAPTURE)
            CAPTURE = {}
            new_out = prepare_out(f"pipe_{name}")
            pipe.run(SPECS[name], tag)
            actual = copy.deepcopy(CAPTURE)
            assert actual.keys() == expected.keys()
            for rid in sorted(expected):
                a, b = expected[rid], actual[rid]
                assert a["message"] == b["message"], f"prompt mismatch: {rid}"
                assert a["kwargs"] == b["kwargs"], f"call arguments mismatch: {rid}"
                folder = TEMP / "rendered"
                folder.mkdir(exist_ok=True)
                for suffix, record in [("legacy", a), ("pipe", b)]:
                    (folder / f"{rid}_{suffix}.txt").write_text(record["message"], encoding="utf-8", newline="\n")
                RESULTS["mock_prompts"].append({"scheme": name, "run_id": rid, "equal": True,
                    "characters": len(a["message"]), "utf8_sha256": digest(a["message"].encode("utf-8")),
                    "call_kwargs_equal": True, "model": a["kwargs"]["model"]})

            for w in CONTEXTS:
                for ext in ("json", "md"):
                    filename = f"{w}_{tag}.{ext}"
                    before, after = (old_out / filename).read_bytes(), (new_out / filename).read_bytes()
                    assert before == after, f"saved bytes mismatch: {filename}"
                    RESULTS["saved_files"].append({"scheme": name, "file": filename,
                                                  "bytes_equal": True, "sha256": digest(after)})

            # Compare all existing pa/qa prompts for this pipeline. These currently
            # contain only the initial step; if descendants appear, use real outputs.
            for w, (builtins, _) in CONTEXTS.items():
                for sid in SPECS[name]["_steps"]:
                    rid = f"sc{tag}_{w}_{sid}"
                    path = ROOT / "runs" / rid / "prompt.txt"
                    if not path.exists():
                        continue
                    real_outputs = {}
                    unavailable = []
                    for dep in SPECS[name]["_deps"][sid]:
                        output = ROOT / "runs" / f"sc{tag}_{w}_{dep}" / "output.txt"
                        if not output.exists():
                            unavailable.append(dep)
                        else:
                            parsed = evo.parse_json(output.read_text(encoding="utf-8-sig"))
                            real_outputs[dep] = parsed
                    if unavailable:
                        RESULTS["real_prompts"].append({"run_id": rid, "skipped": "missing real dependencies",
                                                        "dependencies": unavailable})
                        continue
                    rendered = pipe.render_step(SPECS[name], sid, builtins, real_outputs)
                    saved = path.read_text(encoding="utf-8")
                    # This is the exact existing evo/gpt3_call/mg_call NO_WEB rule.
                    effective = rendered
                    if evo.NO_WEB.strip() not in effective[-60:]:
                        effective += evo.NO_WEB
                    direct_equal = rendered == saved
                    assert effective == saved, f"transport-adjusted real prompt mismatch: {rid}"
                    RESULTS["real_prompts"].append({"run_id": rid, "direct_body_equal": direct_equal,
                        "effective_text_equal": True, "only_difference": None if direct_equal else "evo.NO_WEB suffix",
                        "characters": len(saved), "utf8_sha256": digest(saved.encode("utf-8")),
                        "windows_written_bytes_equal": effective.replace("\n", "\r\n").encode("utf-8") == path.read_bytes()})
                    assert RESULTS["real_prompts"][-1]["windows_written_bytes_equal"]

        # Cache hits must skip submission but still parse and save, including SAMPLE.
        spec = SPECS["P"]
        cached, seen_ids = [], []
        def cached_done(rid):
            cached.append(rid)
            return True
        def cached_parse(rid):
            seen_ids.append(rid)
            return fake_parse(rid)
        sample_out = prepare_out("sample_cache")
        with patch.object(evo, "done", cached_done), patch.object(evo, "call", forbidden), patch.object(V, "parse", cached_parse):
            pipe.run(spec, "pa", sample="2")
        assert set(cached) == set(seen_ids) == {
            f"scpa_{w}_{sid}_s2" for w in CONTEXTS for sid in spec["_steps"]}
        assert all((sample_out / f"{w}_pas2.json").exists() for w in CONTEXTS)
        check("SAMPLE and cache", "6 cache hits; scpa_<work>_<step>_s2; outputs <work>_pas2.json/.md; no submit")

        # Dependency/concurrency checks use barriers rather than timing assumptions.
        for name in ("P", "Q"):
            b = threading.Barrier(2)
            work_names = []
            def work_parallel_call(rid, msg, **kwargs):
                w, sid = parse_id(rid)
                if sid == ("A0" if name == "P" else "A1"):
                    work_names.append(w)
                    b.wait(timeout=8)
                return "stub"
            prepare_out(f"parallel_works_{name}")
            with patch.object(evo, "call", work_parallel_call):
                pipe.run(SPECS[name], "parallel")
            assert set(work_names) == {"op60", "op61"}
        check("both works parallel", "P and Q initial steps for op60/op61 met at a two-party barrier")

        branch_barrier = threading.Barrier(2)
        finished_branches = set()
        started = set()
        def branch_call(rid, msg, **kwargs):
            _, sid = parse_id(rid)
            with LOCK:
                if sid in {"A2", "A3"}:
                    assert "A1" in started
                if sid == "A4":
                    assert finished_branches == {"A2", "A3"}
                started.add(sid)
            if sid in {"A2", "A3"}:
                branch_barrier.wait(timeout=8)
                with LOCK:
                    finished_branches.add(sid)
            return "stub"
        prepare_out("parallel_Q_branches")
        with patch.object(evo, "call", branch_call):
            pipe.run_work(SPECS["Q"], "op60", "branches")
        check("Q branch dependencies", "A2/A3 ran concurrently after A1; A4 began only after both finished")

        # Truly independent steps, inferred edit dependencies and g56 mapping.
        custom = {"name": "independent", "steps": [
            {"id": sid, "prompt_file": "Q_A2.txt", "replace": {}, "model": "g56"}
            for sid in ("left", "right")], "final": "right"}
        independent = pipe.load_spec(write_spec("independent", custom))
        independent_barrier = threading.Barrier(2)
        requested_models = []
        def independent_call(rid, msg, **kwargs):
            requested_models.append(kwargs["model"])
            independent_barrier.wait(timeout=8)
            return "stub"
        prepare_out("independent")
        with patch.object(evo, "call", independent_call):
            pipe.run_work(independent, "op60", "independent")
        assert requested_models == [V.JUDGES["g56"], V.JUDGES["g56"]]
        check("independent steps and g56", "two steps without dependencies ran concurrently; both used V.JUDGES['g56']")

        edit_spec = raw_spec("Q")
        edit_spec["edits"] = [{"prompt_file": "Q_A3.txt", "old": "只输出结构化结果。",
                               "new": ["step:A2", {"text": "CENTER"}]}]
        loaded = pipe.load_spec(write_spec("edit_dependency", edit_spec))
        assert "A2" in loaded["_deps"]["A3"]
        assert pipe.resolve({"text": "CENTER"}, {}, {}) == "CENTER"
        check("source forms", "nested list concatenation, explicit literal and edit step references validated")

        # A failed parsed step must never release descendants or save a final graph.
        failures = []
        def failed_parse(rid):
            failures.append(rid)
            return None
        with patch.object(V, "parse", failed_parse), patch.object(evo, "call", lambda *a, **k: None), patch.object(pipe, "save", forbidden):
            assert_raises(lambda: pipe.run_work(SPECS["P"], "op60", "fail"), RuntimeError)
            failures.clear()
            assert_raises(lambda: pipe.run(SPECS["P"], "fail"), RuntimeError)
        assert set(failures) == {"scfail_op60_A0", "scfail_op61_A0"}
        check("failure propagation", "unusable JSON stopped P descendants and save; two-work runner raised a failure")

        mutations = []
        def invalid(label, mutate):
            data = raw_spec("P")
            mutate(data)
            assert_raises(lambda: pipe.load_spec(write_spec(label, data)))
            mutations.append(label)
        invalid("cycle", lambda s: s["steps"][0].update(after=["A2"]))
        invalid("unknown_dep", lambda s: s["steps"][0].update(after=["missing"]))
        invalid("duplicate", lambda s: s["steps"].append(copy.deepcopy(s["steps"][0])))
        invalid("model", lambda s: s["steps"][0].update(model="invalid"))
        invalid("path_escape", lambda s: s["steps"][0].update(prompt_file="../schemes.py"))
        missing_prompt = raw_spec("P")
        missing_prompt["steps"][0]["prompt_file"] = "nonexistent.txt"
        assert_raises(lambda: pipe.load_spec(write_spec("missing_prompt", missing_prompt)), FileNotFoundError)
        mutations.append("missing_prompt")
        invalid("edit_stale", lambda s: s["edits"][0].update(old="not present anywhere"))
        invalid("final", lambda s: s.update(final="unknown"))
        invalid("source", lambda s: s["steps"][0]["replace"].update({"{X}": 42}))
        invalid("empty_placeholder", lambda s: s["steps"][0]["replace"].update({"": "x"}))
        for sample in ["", "-1", "1/2", "x"]:
            assert_raises(lambda sample=sample: pipe.run(SPECS["P"], "pa", sample=sample))
        assert_raises(lambda: pipe.run(SPECS["P"], "../escape"))
        check("preflight validation", ", ".join(mutations) + "; invalid SAMPLE/TAG; all rejected without model submission")

        # Run the actual CLI entry point with stubbed transport and fresh output paths.
        cli_out = prepare_out("cli")
        CAPTURE = {}
        with patch.dict(os.environ, {"SAMPLE": "3", "REF": "m6w"}):
            pipe.main(["run", str(ROOT / "schemes/P.json"), "cli"])
        assert set(CAPTURE) == {f"sccli_{w}_{sid}_s3" for w in CONTEXTS for sid in SPECS["P"]["_steps"]}
        assert all((cli_out / f"{w}_clis3.json").exists() for w in CONTEXTS)
        check("CLI", "main(['run', absolute_spec, 'cli']) honored SAMPLE=3 and REF=m6w for both works")

        cli_errors = io.StringIO()
        with contextlib.redirect_stderr(cli_errors), patch.object(evo, "call", forbidden):
            try:
                pipe.main(["run", str(TEMP / "fixture_cycle.json"), "invalid"])
            except SystemExit as exc:
                assert exc.code == 1
            else:
                raise AssertionError("invalid CLI spec should exit with code 1")
        assert "dependency cycle" in cli_errors.getvalue()
        check("CLI failure status", "invalid dependency graph returned SystemExit(1) before any submission")

    (TEMP / "verification_stdout.txt").write_text(transcript.getvalue(), encoding="utf-8")
    before = json.loads((TEMP / "protected_before.json").read_text(encoding="utf-8"))
    changes = [name for name, sha in before.items() if digest((ROOT / name).read_bytes()) != sha]
    assert not changes, f"protected files changed: {changes}"
    check("protected files", f"{len(before)} existing files retain identical SHA-256")
    assert not BLOCKED, BLOCKED
    check("offline/write guard", "no network/process events; no attempted writes outside validation directory; -B prevents pycache")
    RESULTS["success"] = True
    RESULTS["counts"] = {"mock_prompts": len(RESULTS["mock_prompts"]),
                         "saved_files": len(RESULTS["saved_files"]), "real_prompts": len(RESULTS["real_prompts"]),
                         "checks": len(RESULTS["checks"]), "protected_files": len(before)}


try:
    validate_all()
except Exception as exc:
    RESULTS["success"] = False
    RESULTS["error"] = repr(exc)
    raise
finally:
    V.OUT = ORIGINAL_OUT
    (TEMP / "results.json").write_text(json.dumps(RESULTS, ensure_ascii=False, indent=2), encoding="utf-8")
    with (TEMP / "log.md").open("a", encoding="utf-8") as handle:
        handle.write("\n## 离线验证执行\n\n")
        handle.write(f"- success: {RESULTS.get('success')}\n")
        if "error" in RESULTS:
            handle.write(f"- error: {RESULTS['error']}\n")
        for row in RESULTS["mock_prompts"]:
            handle.write(f"- 假 JSON：{row['run_id']}，正文及调用参数逐字一致，{row['characters']} 字符，SHA-256 {row['utf8_sha256']}。\n")
        for row in RESULTS["real_prompts"]:
            handle.write(f"- 真实 prompt：{json.dumps(row, ensure_ascii=False)}\n")
        for row in RESULTS["checks"]:
            handle.write(f"- {row['name']}: PASS — {row['details']}\n")
        handle.write(f"- 成品 JSON/Markdown 字节比较：{len(RESULTS['saved_files'])} 份通过；具体 SHA-256 见 results.json。\n")
        handle.write(f"- 审计阻止事件：{BLOCKED}。\n")
print(json.dumps({"success": RESULTS["success"], "counts": RESULTS.get("counts")}, ensure_ascii=False))
