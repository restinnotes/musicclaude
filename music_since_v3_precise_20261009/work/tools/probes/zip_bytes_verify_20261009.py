"""把 ZIP 当数据逐字节比较；不解压、不运行包中脚本、不记录凭证。"""
import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path, PurePosixPath


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def inventory(path):
    with zipfile.ZipFile(path) as archive:
        files = [i for i in archive.infolist() if not i.is_dir()]
        names = [i.filename for i in files]
        if len(set(names)) != len(names):
            raise ValueError("ZIP 含重复 member 名称，不能自动选择")
        prefixes = {PurePosixPath(n).parts[0] for n in names}
        strip = len(prefixes) == 1 and all(len(PurePosixPath(n).parts) > 1 for n in names)
        result = {}
        for info in files:
            p = PurePosixPath(info.filename)
            if p.is_absolute() or ".." in p.parts or "\\" in info.filename:
                raise ValueError("ZIP member 路径不安全")
            rel = str(PurePosixPath(*p.parts[1:])) if strip else str(p)
            if rel in result:
                raise ValueError("规范路径冲突")
            raw = archive.read(info)
            result[rel] = {"member": info.filename, "sha256": sha(raw), "size_bytes": len(raw), "bytes": raw}
        return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("left")
    ap.add_argument("right")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    target = Path(args.output)
    if target.exists():
        raise FileExistsError("取证输出必须用新的文件名")
    left, right = inventory(args.left), inventory(args.right)
    rows = []
    for rel in sorted(set(left) | set(right)):
        a, b = left.get(rel), right.get(rel)
        rows.append({"path": rel, "left": {k: v for k, v in (a or {}).items() if k != "bytes"},
                     "right": {k: v for k, v in (b or {}).items() if k != "bytes"},
                     "byte_match": bool(a is not None and b is not None and a["bytes"] == b["bytes"])})
    result = {"scope": "ZIP 数据逐字节核证，不执行任何包内代码", "date": "2026-10-09",
              "left": {"path": args.left, "zip_sha256": sha(Path(args.left).read_bytes()), "files": len(left)},
              "right": {"path": args.right, "zip_sha256": sha(Path(args.right).read_bytes()), "files": len(right)},
              "rows": rows, "matched": sum(r["byte_match"] for r in rows),
              "all_match": all(r["byte_match"] for r in rows), "model_submissions": 0}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print(json.dumps({"all_match": result["all_match"], "matched": result["matched"],
                      "files": len(rows), "output": str(target)}, ensure_ascii=False))
    return 0 if result["all_match"] else 2


if __name__ == "__main__":
    sys.exit(main())
