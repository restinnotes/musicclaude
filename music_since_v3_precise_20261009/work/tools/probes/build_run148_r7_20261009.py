"""Create a new r7 revision for C6; never overwrite r5/r6 or musical inputs."""
import argparse
import hashlib
import json
from pathlib import Path


OLD = "run146_e7_flash_diag_r6"
NEW = "run148_e7_flash_diag_r7"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def replace_one(text, old, new):
    if text.count(old) != 1:
        raise RuntimeError("Expected one exact source anchor: " + old[:100])
    return text.replace(old, new, 1)


def put(path, raw):
    with path.open("xb") as stream:
        stream.write(raw)


IDENTITY_HELPER = '''def _same_json_identity(actual: Any, expected: Any) -> bool:
    """Exact recursive identity: bool/float never stand in for JSON integers."""
    if type(actual) is not type(expected):
        return False
    if type(expected) is dict:
        return (all(type(key) is str for key in actual) and
                all(type(key) is str for key in expected) and
                set(actual) == set(expected) and
                all(_same_json_identity(actual[key], expected[key]) for key in expected))
    if type(expected) is list:
        return (len(actual) == len(expected) and
                all(_same_json_identity(left, right) for left, right in zip(actual, expected)))
    if type(expected) in (str, int, bool, type(None)):
        return actual == expected
    return False


'''

REGRESSIONS = '''        # C6: valid artifacts cannot turn numeric equality into typed identity.
        binding_cases = (
            "pack_seed_float_and_receipt_float", "pack_order_index_float",
            "pack_order_index_bool", "result_seed_float", "meta_raw_size_float",
            "meta_identity_seed_float", "terminal_identity_seed_float",
            "pack_seed_bool", "result_seed_bool", "meta_raw_size_bool",
            "meta_identity_seed_bool", "terminal_identity_seed_bool",
            "meta_identity_extra_field", "terminal_identity_extra_field",
            "result_requested_identity_extra_field", "pack_requested_identity_extra_field",
        )
        for task_index in range(len(tasks)):
            for mutation in binding_cases:
                altered_pack = json.loads(json.dumps(pack, ensure_ascii=False))
                altered_results = json.loads(json.dumps(results, ensure_ascii=False))
                altered_task = altered_pack["tasks"][task_index]
                altered_result = altered_results[task_index]
                files = {name: Path(path) for name, path in altered_result["artifacts"].items()}
                old_meta, old_terminal = files["meta"].read_bytes(), files["terminal"].read_bytes()
                changed_meta, changed_terminal = self.go.read_json(files["meta"]), self.go.read_json(files["terminal"])
                if mutation == "pack_seed_float_and_receipt_float":
                    altered_task["seed"] = float(altered_task["seed"])
                elif mutation == "pack_order_index_float":
                    altered_task["order_index"] = float(altered_task["order_index"])
                elif mutation == "pack_order_index_bool":
                    altered_task["order_index"] = bool(altered_task["order_index"])
                elif mutation == "result_seed_float":
                    altered_result["seed"] = float(altered_result["seed"])
                elif mutation == "meta_raw_size_float":
                    changed_meta["raw_output_size"] = float(changed_meta["raw_output_size"])
                elif mutation == "meta_identity_seed_float":
                    changed_meta["identity"]["seed"] = float(changed_meta["identity"]["seed"])
                elif mutation == "terminal_identity_seed_float":
                    changed_terminal["identity"]["seed"] = float(changed_terminal["identity"]["seed"])
                elif mutation == "pack_seed_bool":
                    altered_task["seed"] = True
                elif mutation == "result_seed_bool":
                    altered_result["seed"] = True
                elif mutation == "meta_raw_size_bool":
                    changed_meta["raw_output_size"] = True
                elif mutation == "meta_identity_seed_bool":
                    changed_meta["identity"]["seed"] = True
                elif mutation == "terminal_identity_seed_bool":
                    changed_terminal["identity"]["seed"] = True
                elif mutation == "meta_identity_extra_field":
                    changed_meta["identity"]["unexpected"] = 1
                elif mutation == "terminal_identity_extra_field":
                    changed_terminal["identity"]["unexpected"] = 1
                elif mutation == "result_requested_identity_extra_field":
                    altered_result["requested_identity"]["unexpected"] = 1
                elif mutation == "pack_requested_identity_extra_field":
                    altered_pack["requested_identity"]["unexpected"] = 1
                changed_terminal_bytes = self.go.json_bytes(changed_terminal)
                changed_meta["terminal_sha256"] = self.go.sha256_bytes(changed_terminal_bytes)
                files["terminal"].write_bytes(changed_terminal_bytes)
                files["meta"].write_bytes(self.go.json_bytes(changed_meta))
                calls = []
                def counting_verifier(result, meta, terminal, raw_output):
                    calls.append(result["task_id"])
                    row = verifier(result, meta, terminal, raw_output)
                    if mutation == "pack_seed_float_and_receipt_float" and result["task_id"] == altered_task["task_id"]:
                        row["seed"] = altered_task["seed"]
                    return row
                try:
                    with self.subTest(c6_mutation=mutation, task_index=task_index):
                        with self.assertRaises(self.go.IntegrityError):
                            self.go.validate_external_review_results(altered_pack, altered_results, "muse", counting_verifier)
                        self.assertNotIn(altered_task["task_id"], calls)
                finally:
                    files["meta"].write_bytes(old_meta)
                    files["terminal"].write_bytes(old_terminal)
        for value in (float(first["seed"]), True):
            bad_task = dict(first, seed=value)
            bad_receipt = dict(receipt, seed=value)
            with self.subTest(c6_standalone_receipt_seed=value):
                with self.assertRaises(self.go.IntegrityError):
                    self.go._validate_external_muse_receipt(pack, bad_task, results[0], raw_bytes, terminal, bad_receipt)
        for order in (0, 1, 2):
            self.assertTrue(self.go._same_json_identity({"nested": [order, None, True]}, {"nested": [order, None, True]}))
            self.assertFalse(self.go._same_json_identity({"nested": [float(order)]}, {"nested": [order]}))
        self.assertFalse(self.go._same_json_identity({"nested": [False]}, {"nested": [0]}))
        self.assertFalse(self.go._same_json_identity({"nested": [True]}, {"nested": [1]}))
        self.assertFalse(self.go._same_json_identity(1.0, 1.0))
        self.assertFalse(self.go._same_json_identity((0, 1), [0, 1]))
        self.assertEqual(len(self.go.validate_external_review_results(pack, results, "muse", verifier)), 6)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    old_driver = root / "runs" / OLD / "go.py"
    old_tests = root / "tools/tests" / ("test_" + OLD + ".py")
    old_manifest = json.loads((root / "runs" / OLD / "manifest.json").read_bytes())
    raw_driver, raw_tests = old_driver.read_bytes(), old_tests.read_bytes()
    if (sha(raw_driver) != old_manifest["artifacts"]["go_py_sha256"] or
            sha(raw_tests) != old_manifest["artifacts"]["test_py_sha256"]):
        raise RuntimeError("r6 source is no longer the recorded source; do not adopt silently")
    rename = lambda text: text.replace(OLD, NEW).replace("run146", "run148").replace("Run146", "Run148")
    driver, tests = rename(raw_driver.decode("utf-8")), rename(raw_tests.decode("utf-8"))
    driver = replace_one(driver, "def _validate_external_pack(pack: dict[str, Any])", IDENTITY_HELPER + "def _validate_external_pack(pack: dict[str, Any])")
    driver = replace_one(driver,
        '            pack.get("requested_identity") != expected_muse_identity):',
        '            not _same_json_identity(pack.get("requested_identity"), expected_muse_identity)):')
    driver = replace_one(driver,
        '            if task.get("set") != set_name or task.get("order_index") != order or task.get("seed") != seed:',
        '            if not _same_json_identity({key: task.get(key) for key in ("set", "order_index", "seed")},\n'
        '                                       {"set": set_name, "order_index": order, "seed": seed}):')
    driver = replace_one(driver,
        '            if task.get("mapping") != expected_mappings[(set_name, CFG["judges"][0], order)]:',
        '            if not _same_json_identity(task.get("mapping"), expected_mappings[(set_name, CFG["judges"][0], order)]):')
    driver = replace_one(driver,
        '            if task.get("order") != [task["mapping"][position] for position in POSITIONS]:',
        '            if not _same_json_identity(task.get("order"), [task["mapping"][position] for position in POSITIONS]):')
    driver = replace_one(driver,
        '                if task.get(field) != base[field]:',
        '                if not _same_json_identity(task.get(field), base[field]):')
    driver = replace_one(driver,
        '    requested = canonical_muse_identity("Muse", "external Muse")\n    reported = canonical_muse_identity(str(result.get("reported_provider", "")),',
        '    if (type(task.get("set")) is not str or task["set"] not in BASELINE_MODELS or\n'
        '            type(task.get("order_index")) is not int or not 0 <= task["order_index"] <= 2 or\n'
        '            type(task.get("seed")) is not int or\n'
        '            task["seed"] != SEED_COMPARE + 100 * sorted(BASELINE_MODELS).index(task["set"])):\n'
        '        raise IntegrityError("external Muse receipt task coordinates must be frozen strict integers")\n'
        '    requested = canonical_muse_identity("Muse", "external Muse")\n    reported = canonical_muse_identity(str(result.get("reported_provider", "")),')
    driver = replace_one(driver,
        '                "seed": task["seed"], "raw_output_sha256": sha256_bytes(raw_output),',
        '                "seed": SEED_COMPARE + 100 * sorted(BASELINE_MODELS).index(task["set"]),\n'
        '                "raw_output_sha256": sha256_bytes(raw_output),')
    driver = replace_one(driver,
        '        if type(receipt.get(field)) is not type(expected_value) or receipt.get(field) != expected_value:',
        '        if not _same_json_identity(receipt.get(field), expected_value):')
    before = '''        if (result.get("logical_task_id") != task["logical_task_id"] or
                result.get("request_id") != task["request_id"] or
                result.get("requested_identity") != pack["requested_identity"] or
                result.get("mapping") != task["mapping"] or result.get("seed") != task["seed"] or
                result.get("prompt_sha256") != task["prompt_sha256"]):'''
    after = '''        result_binding = {"logical_task_id": task["logical_task_id"], "request_id": task["request_id"],
                          "requested_identity": canonical_muse_identity("Muse", "external Muse"),
                          "mapping": task["mapping"], "seed": task["seed"], "prompt_sha256": task["prompt_sha256"]}
        if not _same_json_identity({key: result.get(key) for key in result_binding}, result_binding):'''
    driver = replace_one(driver, before, after)
    driver = replace_one(driver,
        '        if meta.get("schema") != "run148-external-muse-meta-v1" or meta.get("identity") != receipt_binding:',
        '        if meta.get("schema") != "run148-external-muse-meta-v1" or not _same_json_identity(meta.get("identity"), receipt_binding):')
    driver = replace_one(driver,
        '                meta.get("raw_output_size") != len(output_bytes)):',
        '                not _same_json_identity(meta.get("raw_output_size"), len(output_bytes))):')
    driver = replace_one(driver,
        '                terminal.get("identity") != receipt_binding or terminal.get("status") != "completed" or',
        '                not _same_json_identity(terminal.get("identity"), receipt_binding) or terminal.get("status") != "completed" or')
    tests = replace_one(tests, "        required = set(receipt)\n", REGRESSIONS + "        required = set(receipt)\n")
    folder = root / "runs" / NEW
    test_path = root / "tools/tests" / ("test_" + NEW + ".py")
    if folder.exists() or test_path.exists():
        raise RuntimeError("New revision destination already exists; never overwrite or adopt")
    for path, source in ((folder / "go.py", driver), (test_path, tests)):
        compile(source, str(path), "exec")
    for relative, digest in old_manifest["frozen_input_sha256"].items():
        if sha((root / relative).read_bytes()) != digest:
            raise RuntimeError("Frozen input changed: " + relative)
    readme = ("# " + NEW + "\n\n"
        "2026-10-09：C6 新修订，从只读 run146 r6 派生；不覆盖 r5/r6 失败。\n\n"
        "仅收紧 Muse pack/result/meta/terminal/receipt 的递归类型身份，seed/order/size 拒 bool/float；"
        "expected seed 从冻结 set 计算，不由错误 caller seed 决定。内部同域 pack 字段比较也收紧。\n\n"
        "原26字段收据、trusted verifier 必须条件、TEST_ONLY realcount=0、逐引文校验、六任务集合、"
        "默认 parsefail STOP 与持久 hold、音乐逻辑和正式 prompt 不变。run147 未改、不推断同缺陷。\n\n"
        "新增16类×6任务完整入口反例、standalone receipt 及递归比较正负控；创建时均未核验。\n\n"
        "COMPLETION_PENDING；必须追加主动态核证和独立 review。实际 CLI/服务认证、音乐与production 未放行。\n")
    folder.mkdir()
    put(folder / "go.py", driver.encode("utf-8"))
    put(test_path, tests.encode("utf-8"))
    put(folder / "README.md", readme.encode("utf-8"))
    manifest = {"schema": "offline-main-revision-manifest/1", "date": "2026-10-09", "revision": NEW,
        "based_on": {"source_revision": OLD, "source_driver_sha256": sha(raw_driver), "source_tests_sha256": sha(raw_tests)},
        "artifacts": {"go_py_sha256": sha(driver.encode("utf-8")), "test_py_sha256": sha(tests.encode("utf-8")),
            "readme_sha256": sha(readme.encode("utf-8"))},
        "frozen_input_sha256": old_manifest["frozen_input_sha256"], "frozen_prompt_sha256": old_manifest["frozen_prompt_sha256"],
        "changes": ["Mechanical namespace/run rename; run124/run130/run132 lineage untouched.",
            "C6: exact recursive JSON identity in external pack/result/meta/terminal/receipt and same-domain internal pack validation.",
            "Frozen strict integer coordinates before deriving receipt expected; frozen seed independently recomputed.",
            "Existing 25 methods/assertions retained; new 16x6 ingress mutation subtests and helper controls."],
        "boundaries": {"completion": "COMPLETION_PENDING", "independent_review": "required", "music_acceptance": "NOT_PERFORMED",
            "production_ready": False, "real_model_submissions": 0, "provider_or_model_cli_invocations": 0},
        "verification": "PENDING_AT_CREATION; append evidence without rewriting creation-time manifest."}
    put(folder / "manifest.json", (json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n").encode("utf-8"))
    print(json.dumps({"revision": NEW, "driver_sha256": manifest["artifacts"]["go_py_sha256"],
        "tests_sha256": manifest["artifacts"]["test_py_sha256"], "completion": "COMPLETION_PENDING"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
