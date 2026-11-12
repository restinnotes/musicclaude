"""离线证明 run137 cache log 可绕过真实产物/producer 验证；不写历史 run。"""
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("run137_cache_repro", ROOT / "runs/run137_e7_flash_diag/go.py")
R = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = R
spec.loader.exec_module(R)


def main():
    with tempfile.TemporaryDirectory(prefix="run137_cache_repro_") as tmp:
        R.OUT_DIR = Path(tmp)
        record = {"key": [2], "model": "gflash", "prompt_sha256": R.sha256s("冻结输入"),
                  "parse_ok": True, "parsed": {"differs": True, "sentence": "缓存正文"},
                  "output_file": "outputs/missing.md", "producer_identity": {"route": "obsolete"}}
        (R.OUT_DIR / "cache_why_exact.json").write_text(
            json.dumps({"records": [record]}, ensure_ascii=False), encoding="utf-8")
        with mock.patch.object(R.experiment_calls, "call", side_effect=AssertionError("不得提交模型")) as call:
            hit = R.call137("why", "probe", "gflash", "冻结输入", lambda _: (None, "bad"), [2], "WHY_GATE_v4")
        result = {"reproduced": hit.get("parse_ok") is True and not call.called,
                  "cache_only_accepted": hit.get("cached") is True,
                  "meta_exists": (R.OUT_DIR / "meta").exists(),
                  "prompt_exists": (R.OUT_DIR / "prompts").exists(),
                  "output_exists": (R.OUT_DIR / record["output_file"]).exists(),
                  "obsolete_producer_accepted": hit.get("producer_identity") == {"route": "obsolete"},
                  "model_submissions": 0}
        if not result["reproduced"]:
            raise AssertionError(result)
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
