"""Create immutable r6 drivers/tests from r5; strengthen receipt equality only.
No model/provider/production call. Historical files are never overwritten.
"""
import argparse
import hashlib
import json
from pathlib import Path


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def put(path, raw):
    with path.open("xb") as stream:
        stream.write(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    plans = []
    for old, new, suffix in (("144", "146", "e7_flash_diag"), ("145", "147", "thread_resume")):
        old_id, new_id = "run" + old + "_" + suffix + "_r5", "run" + new + "_" + suffix + "_r6"
        sources = [root / "runs" / old_id / "go.py", root / "tools/tests" / ("test_" + old_id + ".py")]
        destinations = [root / "runs" / new_id / "go.py", root / "tools/tests" / ("test_" + new_id + ".py")]
        texts = [path.read_text(encoding="utf-8") for path in sources]
        transformed = [text.replace(old_id, new_id).replace("run" + old, "run" + new).replace("Run" + old, "Run" + new) for text in texts]
        if old == "144":
            before = "        if receipt.get(field) != expected_value:\n"
            after = "        if type(receipt.get(field)) is not type(expected_value) or receipt.get(field) != expected_value:\n"
            anchor = "        required = set(receipt)\n"
            extra = '''        for field in ("verified", "source_bound", "seed", "raw_output_size"):
            for malformed in ((1, 1.0, False, "true", None) if field in ("verified", "source_bound")
                              else (True, float(receipt[field]))):
                changed = dict(receipt, **{field: malformed})
                with self.subTest(exact_receipt_type_field=field, malformed=malformed):
                    with self.assertRaises(self.go.IntegrityError):
                        self.go._validate_external_muse_receipt(pack, first, results[0], raw_bytes, terminal, changed)
                    def malformed_verifier(result, meta, terminal, raw_output):
                        row = verifier(result, meta, terminal, raw_output)
                        row[field] = malformed
                        return row
                    with self.assertRaises(self.go.IntegrityError):
                        self.go.validate_external_review_results(pack, results, "muse", malformed_verifier)
'''
        else:
            before = "        if receipt.get(key) != value:\n"
            after = "        if type(receipt.get(key)) is not type(value) or receipt.get(key) != value:\n"
            anchor = "        expected_fields = set(receipt)\n"
            extra = '''        for field in ("verified", "bytes_verified", "source_bound", "seed", "raw_response_size"):
            for malformed in ((1, 1.0, False, "true", None) if field in ("verified", "bytes_verified", "source_bound")
                              else (True, float(receipt[field]))):
                changed = dict(receipt, **{field: malformed})
                with self.subTest(exact_receipt_type_field=field, malformed=malformed):
                    with self.assertRaises(GO["IntegrityError"]):
                        GO["_validate_trusted_muse_receipt"](pack, raw_bytes, changed)
                    def malformed_verifier(actual_pack, actual_bytes):
                        row = mock_archive_verifier(actual_pack, actual_bytes)
                        row[field] = malformed
                        return row
                    with self.assertRaises(GO["IntegrityError"]):
                        GO["validate_muse_return"](pack, result, malformed_verifier)
'''
        if transformed[0].count(before) != 1 or transformed[1].count(anchor) != 1:
            raise RuntimeError("Expected one exact edit anchor for " + new_id)
        transformed[0] = transformed[0].replace(before, after)
        transformed[1] = transformed[1].replace(anchor, extra + anchor)
        for destination, text in zip(destinations, transformed):
            compile(text, str(destination), "exec")
            if destination.exists():
                raise RuntimeError("Refusing to overwrite " + str(destination))
        folder = destinations[0].parent
        if folder.exists():
            raise RuntimeError("Refusing to adopt existing revision directory")
        manifest = json.loads((root / "runs" / old_id / "manifest.json").read_bytes())
        readme = ("# " + new_id + "\n\n"
            "2026-10-09：主会话从只读 r5 生成新修订，仅修复 Muse 收据的精确类型边界。\n\n"
            "主 r5 离线回归 25+24 PASS 不足以放行：完整入口仍接受 verified/source_bound/bytes_verified=1 或 1.0；10 个定向反例失败。\n\n"
            "本修订对 expected receipt 字段先比较 exact Python type，再比较值；拒绝数字冒充布尔及 float/bool 冒充整型 seed/size。原26/27字段接口、trusted verifier 必需条件、TEST_ONLY 与真实返回分界不变。\n\n"
            "仅 run 标识/模块测试引用机械改名；没有修改音乐 prompt、宪法、旧样本或 production。r5 历史代码及失败证据不覆盖。\n\n"
            "COMPLETION_PENDING；独立 review、主动态核验及实际协议仍需分别处置。real gate 与 two-w hold 保留；mock 不等后端调用，工程通过不等音乐验收。\n")
        plans.append((folder, destinations, transformed, readme, manifest, sources, before, after, old_id, new_id))
    for folder, destinations, texts, readme, old_manifest, sources, before, after, old_id, new_id in plans:
        folder.mkdir()
        for destination, text in zip(destinations, texts):
            put(destination, text.encode("utf-8"))
        put(folder / "README.md", readme.encode("utf-8"))
        manifest = {"schema": "offline-main-revision-manifest/1", "date": "2026-10-09", "revision": new_id,
            "based_on": {"source_revision": old_id, "source_driver_sha256": sha(sources[0].read_bytes()),
                "source_tests_sha256": sha(sources[1].read_bytes())},
            "artifacts": {"go_py_sha256": sha(destinations[0].read_bytes()), "test_py_sha256": sha(destinations[1].read_bytes()),
                "readme_sha256": sha((folder / "README.md").read_bytes())},
            "frozen_input_sha256": old_manifest["frozen_input_sha256"],
            "frozen_prompt_sha256": old_manifest["frozen_prompt_sha256"],
            "changes": ["Mechanical run/module identity rename only; legacy run124/run130/run132 evidence unchanged.",
                {"old": before.strip(), "new": after.strip(), "reason": "r5 complete ingress accepted numeric substitutes for true flags."},
                "Added exact-type negative subtests both through receipt helper and full ingestion entry."],
            "boundaries": {"completion": "COMPLETION_PENDING", "independent_review": "required", "music_acceptance": "NOT_PERFORMED",
                "production_ready": False, "real_model_submissions": 0, "provider_or_model_cli_invocations": 0},
            "verification": "PENDING_AT_CREATION; append evidence without rewriting this creation-time manifest."}
        put(folder / "manifest.json", (json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8"))
        print(json.dumps({"revision": new_id, "driver_sha256": manifest["artifacts"]["go_py_sha256"],
            "tests_sha256": manifest["artifacts"]["test_py_sha256"], "completion": "COMPLETION_PENDING"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
