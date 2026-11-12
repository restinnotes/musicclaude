"""Offline integration/regression tests. Run: python _codex/test_v6dirs.py.

Model transport and output paths are patched; every test-time write is confined
to a TemporaryDirectory. The real run_parallel, parsers, graph readers and join
renderer are exercised. No subprocess/model transport is invoked.
"""
import ast
import builtins
import copy
from contextlib import ExitStack, redirect_stdout, redirect_stderr
import hashlib
import io
import itertools
import json
from pathlib import Path
import re
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import covjudge
import draft10
import evo
import v6dirs
import v6fix


def segment(s, previous=None, revised=False):
    sec = s["id"]
    links = ([{"from": f"{previous}-1", "to": f"{sec}-1", "rel": "提供理由"}]
             if previous else [])
    # A forward/dangling link must be removed by tidy before delivery.
    links.append({"from": "S99-1", "to": f"{sec}-1", "rel": "说明"})
    return {"sec": sec, "relation": "没在想", "items": [
        {"id": f"{sec}-1", "text": "刚才的犹豫让他再等一会儿。" if revised else "他还想再等一会儿。",
         "key": "等一会儿", "follows": False, "explains": ["B1"]}],
        "because": links, "gaps": [{"bead": "B4", "why": "尚未说清"}]}


def whole_answer(w, revised=False):
    segs = draft10.segs(w)
    # Deliberately reverse model order: assembly must use sec, not list position.
    return {"segments": list(reversed([segment(s, segs[i - 1]["id"] if i else None, revised)
                                       for i, s in enumerate(segs)])),
            "changes": [{"v6": ["R1"], "now": ["S01-1"], "what": "改写",
                         "why": "退改版" if revised else "第一版"}]}


def check_answer(sec, needs_revision=False, radical=False):
    result = {"items": [{"id": f"{sec}-1", "label": "ok", "why": "符合边界"}], "links": [],
              "readable": "是", "readable_why": "读得懂", "lost": [],
              "unexplained": [{"bead": "B4", "why": "已在 gaps 中，应当排除"}], "wordy": []}
    if radical:
        result.update(progress="否" if needs_revision else "是", progress_why="需要接上前段")
    elif needs_revision:
        result["wordy"] = [{"ids": [f"{sec}-1"], "why": "需要精简"}]
    return result


class FakeModel:
    def __init__(self, base):
        self.base = base
        self.calls = []
        self.overrides = {}
        self.lock = threading.Lock()
        self.on_call = None

    def done(self, rid):
        return (self.base / rid / "output.txt").exists()

    def output(self, rid):
        path = self.base / rid / "output.txt"
        return path.read_text(encoding="utf-8") if path.exists() else None

    def put(self, rid, answer):
        path = self.base / rid
        path.mkdir(parents=True, exist_ok=True)
        text = answer if isinstance(answer, str) else json.dumps(answer, ensure_ascii=False)
        (path / "output.txt").write_text(text, encoding="utf-8")
        return text

    def answer(self, rid):
        if rid in self.overrides:
            return self.overrides[rid]
        parts = rid.split("_")
        prefix, w = parts[:2]
        segs = draft10.segs(w)
        if prefix in ("v6w", "v6wr"):
            return whole_answer(w, revised=prefix == "v6wr")
        if prefix in ("v6k", "v6sk"):
            sec = parts[2]
            return check_answer(sec, needs_revision=sec == segs[1]["id"], radical=prefix == "v6sk")
        if prefix in ("v6s", "v6sr"):
            sec = parts[2]
            i = next(i for i, s in enumerate(segs) if s["id"] == sec)
            return segment(segs[i], segs[i - 1]["id"] if i else None, revised=prefix == "v6sr")
        if prefix == "v6sc":
            # Missing the last relation exercises the specified default + error record.
            return {"center": "犹豫仍然影响着等待。", "why": "贯穿全曲",
                    "relations": {s["id"]: "还说不清" for s in segs[:-1]}}
        raise AssertionError(f"Unexpected model call: {rid}")

    def call(self, rid, message, model, meta):
        with self.lock:
            if self.done(rid):
                raise AssertionError(f"Completed run called again: {rid}")
            self.calls.append({"rid": rid, "message": message, "model": model, "meta": meta})
        if self.on_call:
            self.on_call(rid, message)
        path = self.base / rid
        path.mkdir(parents=True, exist_ok=True)
        (path / "input.txt").write_text(message, encoding="utf-8")
        (path / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
        return self.put(rid, self.answer(rid))


class OfflineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="v6dirs_test_")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.out = self.base / "evaluations" / "v6fix"
        self.fake = FakeModel(self.base / "runs")
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stdout, self.stderr = io.StringIO(), io.StringIO()
        self.stack.enter_context(redirect_stdout(self.stdout))
        self.stack.enter_context(redirect_stderr(self.stderr))
        self.writes = []
        # Both pathlib and builtins writes are guarded, including unchanged join.
        def guard(original):
            def opened(file, mode="r", *args, **kwargs):
                if isinstance(mode, str) and any(c in mode for c in "wax+"):
                    path = Path(file).resolve()
                    if not path.is_relative_to(self.base):
                        raise AssertionError(f"Write outside temporary directory: {path}")
                    self.writes.append(path)
                return original(file, mode, *args, **kwargs)
            return opened
        self.stack.enter_context(patch("io.open", guard(io.open)))
        self.stack.enter_context(patch("builtins.open", guard(builtins.open)))
        for obj, name, value in ((evo, "RUNS", self.fake.base), (evo, "call", self.fake.call),
                                 (evo, "done", self.fake.done), (evo, "output", self.fake.output),
                                 (v6fix, "OUT", self.out)):
            self.stack.enter_context(patch.object(obj, name, value))
        self.parallel = self.stack.enter_context(patch.object(evo, "run_parallel", wraps=evo.run_parallel))

    def read(self, w, tag):
        return json.loads((self.out / f"{w}_{tag}.json").read_text(encoding="utf-8"))

    def assert_graph(self, w, tag, direction):
        data = self.read(w, tag)
        graph = v6fix.graph_of(w, tag)
        self.assertEqual(data["graph"], graph)
        self.assertEqual([s["sec"] for s in graph["segments"]], [s["id"] for s in draft10.segs(w)])
        self.assertEqual(list(data["rows"]), [s["id"] for s in draft10.segs(w)])
        md = (self.out / f"{w}_{tag}.md").read_text(encoding="utf-8")
        self.assertEqual(md, f"# Op.{w[2:]}｜关系图（{direction} {tag}）\n\n" + v6fix.view(graph))
        seen = set()
        for s in graph["segments"]:
            here = {x["id"] for x in s["items"]}
            self.assertTrue(all(x["from"] in seen and x["to"] in here for x in s["because"]))
            seen |= here
            self.assertEqual(set(data["rows"][s["sec"]]), {"edit", "check", "notes", "revised"})
        # The exact assembly used by blind: old/new graph -> view -> BLIND.format.
        message = v6fix.BLIND.format(NAME=covjudge.NAME[w], WHAT=v6fix.WHAT,
                                    X=v6fix.view(v6fix.v6(w)), Y=v6fix.view(graph), BEADS=v6fix.beads(w))
        self.assertIn(graph["center"], message)
        return data

    def assert_routes(self):
        for call in self.fake.calls:
            prefix = call["rid"].split("_")[0]
            stage = {"v6w": "v6-whole", "v6wr": "v6-whole-rev", "v6k": "v6-check",
                     "v6s": "v6-rad", "v6sr": "v6-rad-rev", "v6sk": "v6-rad-check",
                     "v6sc": "v6-rad-center"}[prefix]
            writing = prefix in ("v6w", "v6wr", "v6s", "v6sr")
            self.assertEqual(call["meta"], {"stage": stage, **({"web": True} if writing else {})})
            fallback = call["rid"].endswith("b")
            expected = evo.G56 if prefix in ("v6k", "v6sk") or fallback else evo.G6
            self.assertEqual(call["model"], expected)

    def test_whole_full_both_pieces_fallback_revision_cache_and_join(self):
        self.fake.overrides["v6w_op60_w1"] = "not json"
        for w in ("op60", "op61"):
            v6dirs.whole(w)
            data = self.assert_graph(w, "w1", "A2 整首修补")
            self.assertEqual(data["graph"]["center"], v6fix.v6(w)["center"])
            self.assertTrue(all(row["revised"] for row in data["rows"].values()))
            self.assertEqual(data["changes"][0]["why"], "退改版")
            self.assertEqual(len(data["rows"]["S02"]["notes"]), 1)
            self.assertEqual(data["rows"]["S01"]["notes"], [])
            for call in self.fake.calls:
                if call["rid"].startswith(f"v6k_{w}_"):
                    sec = call["rid"].split("_")[2]
                    done = call["message"].split("【前面已经修好的段】\n", 1)[1].split("\n\n【这一段 v6", 1)[0]
                    n = int(sec[1:])
                    for i in range(1, len(data["rows"]) + 1):
                        self.assertEqual(f"### S{i:02d}｜" in done, i < n)
            rev = next(x for x in self.fake.calls if x["rid"] == f"v6wr_{w}_w1")
            note_block = rev["message"].split("【上一次的修补被核对者退回的地方】", 1)[1].split("上一次的修补结果：", 1)[0]
            self.assertIn("### S02", note_block)
            self.assertNotIn("### S01", note_block)
        self.assertEqual(self.parallel.call_count, 2)
        self.assertTrue(all(c.args[1] == 4 for c in self.parallel.call_args_list))
        joined = v6fix.join("w1").read_text(encoding="utf-8")
        self.assertIn("肖邦《船歌》Op.60", joined)
        self.assertIn("肖邦《幻想波兰舞曲》Op.61", joined)
        self.assertIn("线没有单独说明的听感", joined)
        before = len(self.fake.calls)
        v6dirs.whole("op60")
        v6dirs.whole("op61")
        self.assertEqual(len(self.fake.calls), before)
        self.assert_routes()
        self.assertTrue(self.writes)

    def test_rad_full_both_pieces_fallback_progress_revision_center_cache_and_join(self):
        self.fake.overrides["v6s_op60_S01_s1"] = "not json"
        snapshots = []
        def inspect(rid, message):
            if rid.startswith("v6s_") or rid.startswith("v6sc_"):
                w = rid.split("_")[1]
                if rid.startswith("v6sc_"):
                    data = self.read(w, "s1")
                    self.assertEqual(len(data["graph"]["segments"]), len(draft10.segs(w)))
                else:
                    sec = rid.split("_")[2]
                    n = int(sec[1:])
                    if n == 1:
                        return
                    data = self.read(w, "s1")
                    self.assertEqual(len(data["graph"]["segments"]), n - 1)
                    previous = data["graph"]["segments"][-1]
                    self.assertIn(previous["items"][0]["text"], message)
                self.assertEqual(data["graph"]["center"], "")
                self.assertTrue(all(s["relation"] == "" for s in data["graph"]["segments"]))
                self.assertNotIn("（没在想）", message)
                self.assertNotIn("（正在面对）", message)
                snapshots.append(copy.deepcopy(data))
        self.fake.on_call = inspect
        for w in ("op60", "op61"):
            with patch.object(v6fix, "v6", side_effect=AssertionError("B1 must not load v6")):
                v6dirs.rad(w)
            data = self.assert_graph(w, "s1", "B1 激进逐段")
            self.assertTrue(data["rows"]["S02"]["revised"])
            self.assertEqual(data["rows"]["S02"]["notes"], ["- 递进不够：需要接上前段"])
            self.assertFalse(data["rows"]["S01"]["revised"])
            self.assertEqual(data["graph"]["segments"][-1]["relation"], "正在面对")
            self.assertTrue(any("Center 缺少 relation" in x for x in data["errors"]))
            center_call = next(c for c in self.fake.calls if c["rid"] == f"v6sc_{w}_s1")
            self.assertNotRegex(center_call["message"], r"\[S\d+-\d+\]")
            order = [c["rid"] for c in self.fake.calls]
            self.assertLess(order.index(f"v6sr_{w}_S02_s1"), order.index(f"v6s_{w}_S03_s1"))
        self.assertEqual(len(snapshots), 27)
        self.assertIn("犹豫仍然影响着等待。", v6fix.join("s1").read_text(encoding="utf-8"))
        self.fake.on_call = None
        before = len(self.fake.calls)
        v6dirs.rad("op60")
        v6dirs.rad("op61")
        self.assertEqual(len(self.fake.calls), before)
        self.assert_routes()

    def test_whole_no_notes_no_revision(self):
        for s in draft10.segs("op60"):
            self.fake.overrides[f"v6k_op60_{s['id']}_clean"] = check_answer(s["id"])
        v6dirs.whole("op60", "clean")
        self.assertFalse(any(c["rid"].startswith("v6wr_") for c in self.fake.calls))
        self.assertFalse(any(r["revised"] for r in self.read("op60", "clean")["rows"].values()))

    def test_whole_missing_segment_revision_failure_preserves_first(self):
        first = whole_answer("op60")
        first["segments"] = [s for s in first["segments"] if s["sec"] != "S03"]
        self.fake.overrides.update(v6w_op60_missing=first, v6wr_op60_missing="broken")
        v6dirs.whole("op60", "missing")
        data = self.assert_graph("op60", "missing", "A2 整首修补")
        self.assertEqual(data["graph"]["segments"][2]["items"], [])
        self.assertEqual(data["rows"]["S03"]["edit"]["items"], [])
        self.assertFalse(any(r["revised"] for r in data["rows"].values()))
        self.assertEqual(data["changes"], first["changes"])
        self.assertEqual(len(data["errors"]), 2)

    def test_generation_both_parse_failures_stop(self):
        for direction, rid in (("whole", "v6w_op60_bad"), ("rad", "v6s_op60_S01_bad")):
            self.fake.overrides.update({rid: "bad", rid + "b": "bad"})
            with self.assertRaisesRegex(RuntimeError, "G6 和 G56"):
                getattr(v6dirs, direction)("op60", "bad")
        self.assertFalse(self.out.exists())
        self.assertEqual(len(self.fake.calls), 4)
        self.assert_routes()

    def test_rad_revision_failure_and_center_failure_preserve_progress(self):
        self.fake.overrides.update(v6sr_op60_S02_failcenter="bad", v6sc_op60_failcenter="bad")
        with self.assertRaisesRegex(RuntimeError, "Center"):
            v6dirs.rad("op60", "failcenter")
        data = self.read("op60", "failcenter")
        self.assertEqual(len(data["graph"]["segments"]), 14)
        self.assertEqual(data["graph"]["center"], "")
        self.assertFalse(data["rows"]["S02"]["revised"])
        self.assertIn("他还想再等一会儿。", v6fix.view(data["graph"]))
        self.assertTrue(any("逐段退改解析失败" in x for x in data["errors"]))
        self.assertTrue((self.out / "op60_failcenter.md").exists())

    def test_check_failure_stops_without_accepting_unchecked_output(self):
        self.fake.overrides["v6sk_op60_S02_checkfail"] = "bad"
        with self.assertRaisesRegex(RuntimeError, "核对"):
            v6dirs.rad("op60", "checkfail")
        self.assertEqual(len(self.read("op60", "checkfail")["graph"]["segments"]), 1)
        self.assertFalse(any(c["rid"].startswith("v6sc_") for c in self.fake.calls))
        self.fake.overrides["v6k_op60_S01_checkfailwhole"] = "bad"
        with self.assertRaisesRegex(RuntimeError, "核对"):
            v6dirs.whole("op60", "checkfailwhole")
        self.assertFalse((self.out / "op60_checkfailwhole.json").exists())

    def test_center_relations_entirely_missing_use_recorded_defaults(self):
        self.fake.overrides["v6sc_op61_norelations"] = {"center": "等待和犹豫一直有关。"}
        v6dirs.rad("op61", "norelations")
        data = self.read("op61", "norelations")
        self.assertTrue(all(s["relation"] == "正在面对" for s in data["graph"]["segments"]))
        self.assertEqual(len(data["errors"]), 13)

    def test_rad_review_criteria_without_lost(self):
        k = {"items": [{"id": "S02-1", "label": "越界", "why": "新增事件"}],
             "links": [{"from": "S01-1", "to": "S02-1", "label": "勉强", "why": "不能推出"}],
             "readable": "否", "readable_why": "难懂", "lost": [{"v6": ["R1"], "what": "不应出现"}],
             "unexplained": [{"bead": "B4", "why": "已在 gaps"}, {"bead": "B5", "why": "未解释"}],
             "wordy": [{"ids": ["S02-1"], "why": "重复"}], "progress": "否", "progress_why": "没有前因"}
        edit = {"gaps": [{"bead": "B4", "why": "尚未解释"}]}
        notes = v6dirs.rad_notes(k, {}, edit)
        expected = v6fix.review_notes({**k, "lost": []}, {}, edit) + ["- 递进不够：没有前因"]
        self.assertEqual(notes, expected)
        self.assertEqual(len(notes), 6)
        self.assertFalse(any("丢了 v6" in n or "B4" in n for n in notes))

    def test_dry_offline_and_placeholders(self):
        with patch.object(evo, "ROOT", self.base):
            for w in ("op60", "op61"):
                messages = v6dirs.dry(w)
                self.assertEqual(len(messages), 5)
                for name, message in messages.items():
                    self.assertEqual(message, (self.base / "_codex" / f"dry_{w}_{name}.txt").read_text(encoding="utf-8"))
                    self.assertNotRegex(message, r"\{[A-Z_]+\}")
                    self.assertNotIn("{{", message)
                    # Nested JSON objects legitimately end in }}; parse the
                    # sample instead of treating closing braces as placeholders.
                    blocks = re.findall(r"```json\s*(.*?)```", message, re.S)
                    self.assertEqual(len(blocks), 1)
                    json.loads(blocks[0])
                self.assertIn(v6dirs.FIRST, messages["rad_first"])
                self.assertIn("[S01-1]", messages["rad_second"])
                self.assertNotIn("（正在面对）", messages["rad_second"])
        self.assertEqual(self.fake.calls, [])

    def test_reserved_tag_and_path_escape_do_not_call_or_write(self):
        for fn in (v6dirs.whole, v6dirs.rad):
            for tag in ("r2", "../r2", "..\\r2", "", "a/b"):
                with self.assertRaises(ValueError):
                    fn("op60", tag)
        self.assertEqual(self.fake.calls, [])
        self.assertEqual(self.writes, [])


class BaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = json.loads((ROOT / "_codex" / "v6dirs_baseline.json").read_text(encoding="utf-8"))

    def test_protected_files_and_all_v6fix_code_except_view_unchanged(self):
        for name, digest in self.baseline["sha256"].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest, name)
        source = (ROOT / "v6fix.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        stripped = ast.Module(body=[n for n in tree.body if not (isinstance(n, ast.FunctionDef) and n.name == "view")], type_ignores=[])
        self.assertEqual(ast.dump(stripped, include_attributes=False), self.baseline["v6fix_without_view_ast"])
        original = '            md += [f"### {s[\'sec\']}｜{s[\'bars\']} 小节　（{s.get(\'relation\')}）", ""]'
        changed = ('            relation = f"　（{s.get(\'relation\')}）" if s.get("relation") else ""\n'
                   '            md += [f"### {s[\'sec\']}｜{s[\'bars\']} 小节{relation}", ""]')
        expected = self.baseline["view_source"].replace(original, changed)
        self.assertNotEqual(expected, self.baseline["view_source"])
        self.assertEqual(ast.get_source_segment(source, next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "view")), expected)

    def test_both_real_v6_views_exactly_match_before_change(self):
        namespace = dict(vars(v6fix))
        exec(self.baseline["view_source"], namespace)
        old_view = namespace["view"]
        for w in ("op60", "op61"):
            graph = v6fix.v6(w)
            self.assertTrue(all(s.get("relation") for s in graph["segments"]))
            for ids in (False, True):
                self.assertEqual(v6fix.view(graph, ids=ids), self.baseline["views"][w][str(ids)])
            for ids, center, head, secs in itertools.product((False, True), (False, True), (False, True), (None, ["S02", "S03"])):
                opts = dict(ids=ids, center=center, head=head, secs=secs)
                self.assertEqual(v6fix.view(graph, **opts), old_view(graph, **opts), (w, opts))
        for relation in (None, ""):
            graph = {"center": "", "segments": [{"sec": "S01", "bars": "1–3", "relation": relation, "items": [], "because": []}]}
            self.assertEqual(v6fix.view(graph, center=False), "### S01｜1–3 小节")


if __name__ == "__main__":
    unittest.main(verbosity=2)
