#!/usr/bin/env python3
"""历史 SSE 归档的路由字段普查（离线脚本，仅 Python 3 标准库，不联网）.

输入 : SRC_DIR 下全部 *.jsonl（只读，不修改/移动/删除）。
       每行 {"received_at": ISO时间, "event": <字符串|对象>}，
       event 字符串通常是一段 JSON，也可能是 "[DONE]" 等非 JSON 文本。
输出 : OUT_DIR/archive_census.jsonl      （每输入文件一行记录）
       OUT_DIR/archive_census_summary.md （汇总表）
"""

import json
import os
from datetime import datetime, timezone

SRC_DIR = r"D:\ai-stack\gpt2agent\.sse-archive"
OUT_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")
)
OUT_JSONL = os.path.join(OUT_DIR, "archive_census.jsonl")
OUT_MD = os.path.join(OUT_DIR, "archive_census_summary.md")

# 需要收集的所有出现值（去重，保持首次出现顺序）的键（按任务给定顺序）。
TARGET_KEYS = (
    "model_slug",
    "resolved_model_slug",
    "default_model_slug",
    "requested_model_slug",
    "thinking_effort",
    "requested_model_experience",
    "turn_use_case",
    "turn_mode",
    "tool_invoked",
    "tool_name",
    "fast_convo",
    "warmup_state",
    "server_ttfvt_ms",
    "content_type",
    "channel",
    "reasoning_status",
    "marker",
    "recipient",
)
TARGET_SET = set(TARGET_KEYS)

# server_ste_metadata 清洗规则：键名含这些子串（大小写不敏感）或值为 eyJ 开头字符串则删除。
TOKEN_KEY_SUBSTRS = ("token", "cookie", "authorization", "sentinel", "conduit")

EMPTY = "\0EMPTY"  # 某文件某键一次都未出现时的计数占位


def parse_iso(s):
    return datetime.fromisoformat(s)


def decode_frame(raw_event):
    """把 event 还原为 JSON 对象；非 JSON 文本返回 None。"""
    if isinstance(raw_event, dict):
        return raw_event
    if isinstance(raw_event, str):
        try:
            obj = json.loads(raw_event)
        except Exception:
            return None
        if isinstance(obj, (dict, list)):
            return obj
        return None
    return None


def walk_collect(node, acc, seen):
    """递归遍历帧 JSON，收集 TARGET_KEYS 的所有出现值。

    含 {"p":.., "o":.., "v":..} 形式的 patch 帧时深入 v；
    v 为 list 时视为批量 patch，逐个遍历。
    """
    if isinstance(node, dict):
        if "p" in node and "o" in node and "v" in node:
            v = node["v"]
            if isinstance(v, list):
                for item in v:
                    walk_collect(item, acc, seen)
            else:
                walk_collect(v, acc, seen)
            for k2, v2 in node.items():
                if k2 == "v":
                    continue
                walk_collect(v2, acc, seen)
            return
        for k, v in node.items():
            if k in TARGET_SET:
                # token 类的值一律不写入输出。
                if not (isinstance(v, str) and v.startswith("eyJ")):
                    ident = json.dumps(v, sort_keys=True, ensure_ascii=False)
                    if ident not in seen[k]:
                        seen[k].add(ident)
                        acc[k].append(v)
            walk_collect(v, acc, seen)
    elif isinstance(node, list):
        for item in node:
            walk_collect(item, acc, seen)


def sanitize(obj):
    """递归删除 token/JWT 类字段：值是 eyJ 开头字符串，或键名含
    token/cookie/authorization/sentinel/conduit（大小写不敏感）。"""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            kl = k.lower() if isinstance(k, str) else ""
            if any(s in kl for s in TOKEN_KEY_SUBSTRS):
                continue
            if isinstance(v, str) and v.startswith("eyJ"):
                continue
            out[k] = sanitize(v)
        return out
    if isinstance(obj, list):
        res = []
        for item in obj:
            if isinstance(item, str) and item.startswith("eyJ"):
                continue
            res.append(sanitize(item))
        return res
    return obj


def message_text(msg):
    content = msg.get("content")
    if not isinstance(content, dict):
        return ""
    parts = content.get("parts")
    if not isinstance(parts, list):
        return ""
    return "".join(p for p in parts if isinstance(p, str))


def process_file(path):
    basename = os.path.basename(path)
    if "-handoff-" in basename:
        kind = "handoff"
    elif "-sse-" in basename:
        kind = "sse"
    else:
        kind = "unknown"

    first_received = None
    last_received = None
    acc = {k: [] for k in TARGET_KEYS}
    seen = {k: set() for k in TARGET_KEYS}
    last_ste = None
    has_patch = False
    user_prompt_head = None
    last_asst_text = None
    longest_asst_text = ""

    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if not isinstance(rec, dict):
                continue
            r_at = rec.get("received_at")
            if isinstance(r_at, str):
                if first_received is None:
                    first_received = r_at
                last_received = r_at
            frame = decode_frame(rec.get("event"))
            if frame is None:
                continue
            walk_collect(frame, acc, seen)
            if isinstance(frame, dict):
                if "p" in frame and "o" in frame and "v" in frame:
                    has_patch = True
                # server_ste_metadata 对象：取 type 为 server_ste_metadata 的帧整体，
                # 以最后一次出现为准（清洗后存入输出）。
                if frame.get("type") == "server_ste_metadata":
                    last_ste = frame
                for wkey in ("message", "input_message"):
                    m = frame.get(wkey)
                    if not isinstance(m, dict):
                        continue
                    author = m.get("author")
                    if not isinstance(author, dict):
                        continue
                    role = author.get("role")
                    text = message_text(m)
                    if role == "user" and user_prompt_head is None:
                        para = text.strip().split("\n\n")[0].strip()
                        user_prompt_head = para[:80]
                    if role == "assistant":
                        # channel 缺失时按 null 处理。
                        ch = m.get("channel", None)
                        if ch in ("final", None):
                            last_asst_text = text
                            if len(text) > len(longest_asst_text):
                                longest_asst_text = text

    duration_s = 0.0
    if first_received is not None and last_received is not None:
        try:
            duration_s = round(
                (parse_iso(last_received) - parse_iso(first_received)).total_seconds(),
                3,
            )
        except Exception:
            duration_s = 0.0

    # 本批归档中 patch 帧语义未知；若存在 patch 帧也无法按未知语义拼接，
    # 统一回退到“出现过的最长 assistant parts 文本”。
    if longest_asst_text:
        assistant_tail = longest_asst_text[-200:]
        tail_method = "longest"
    elif last_asst_text is not None:
        assistant_tail = last_asst_text[-200:]
        tail_method = "longest"
    else:
        assistant_tail = None
        tail_method = "none"
    if has_patch and tail_method != "patch":
        # 如未来出现 patch 帧，此处保持回退行为（语义未知，不做拼接）。
        pass

    out = {
        "file": basename,
        "kind": kind,
        "start": first_received,
        "duration_s": duration_s,
    }
    for k in TARGET_KEYS:
        out[k] = acc[k]
    out["server_ste_metadata"] = sanitize(last_ste) if last_ste is not None else None
    out["has_cot_token"] = "cot_token" in acc["marker"]
    out["has_reasoning_recap"] = "reasoning_recap" in acc["content_type"]
    out["user_prompt_head"] = user_prompt_head
    out["assistant_tail"] = assistant_tail
    out["assistant_tail_method"] = tail_method
    return out


# ---------------- 汇总 ----------------

def utc_date(start):
    try:
        return parse_iso(start).astimezone(timezone.utc).date().isoformat()
    except Exception:
        return (start or "")[:10] or "(unknown)"


def disp(v):
    if v is None:
        return "null"
    if v is True:
        return "true"
    if v is False:
        return "false"
    if isinstance(v, str):
        return v if v != "" else "(empty)"
    return json.dumps(v, ensure_ascii=False)


def identities(lst):
    if not lst:
        return [EMPTY]
    return [json.dumps(v, sort_keys=True, ensure_ascii=False) for v in lst]


def show_ident(ident):
    if ident == EMPTY:
        return "(none)"
    return disp(json.loads(ident))


def cell(s):
    if not isinstance(s, str):
        s = json.dumps(s, ensure_ascii=False)
    return s.replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def md_table(headers, rows):
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for r in rows:
        lines.append("| " + " | ".join(r) + " |")
    return "\n".join(lines)


def join_vals(lst):
    return ", ".join(show_ident(i) for i in identities(lst))


def build_summary(records):
    from collections import Counter

    dates = sorted({utc_date(r["start"]) for r in records})

    # 1. 日期 x turn_use_case
    uc_vals = sorted(
        {i for r in records for i in identities(r["turn_use_case"])},
        key=lambda x: (x == EMPTY, x),
    )
    c1 = Counter()
    for r in records:
        d = utc_date(r["start"])
        for i in identities(r["turn_use_case"]):
            c1[(d, i)] += 1
    rows1 = [
        [d] + [str(c1.get((d, v), 0)) for v in uc_vals] for d in dates
    ]
    t1 = md_table(["date"] + [cell(show_ident(v)) for v in uc_vals], rows1)

    # 2. 日期 x tool_name
    tn_vals = sorted(
        {i for r in records for i in identities(r["tool_name"])},
        key=lambda x: (x == EMPTY, x),
    )
    c2 = Counter()
    for r in records:
        d = utc_date(r["start"])
        for i in identities(r["tool_name"]):
            c2[(d, i)] += 1
    rows2 = [
        [d] + [str(c2.get((d, v), 0)) for v in tn_vals] for d in dates
    ]
    t2 = md_table(["date"] + [cell(show_ident(v)) for v in tn_vals], rows2)

    # 3. 日期 x thinking_effort x has_cot_token
    c3 = Counter()
    for r in records:
        d = utc_date(r["start"])
        for i in identities(r["thinking_effort"]):
            c3[(d, i, bool(r["has_cot_token"]))] += 1
    rows3 = [
        [d, cell(show_ident(e)), "true" if c else "false", str(n)]
        for (d, e, c), n in sorted(c3.items())
    ]
    t3 = md_table(["date", "thinking_effort", "has_cot_token", "count"], rows3)

    # 4. turn_use_case 含 thinking 以外值的文件（无 turn_use_case 的文件不计入），按 start 排序取前 30。
    def has_non_thinking(r):
        vals = r["turn_use_case"]
        return any(v != "thinking" for v in vals)

    non_thinking = sorted(
        (r for r in records if has_non_thinking(r)),
        key=lambda r: (r["start"] or ""),
    )[:30]
    rows4 = [
        [
            cell(r["file"]),
            cell(r["start"] or ""),
            cell(join_vals(r["model_slug"])),
            cell(join_vals(r["turn_use_case"])),
            cell(join_vals(r["tool_name"])),
            cell(str(r["duration_s"])),
            cell(r["user_prompt_head"] or ""),
        ]
        for r in non_thinking
    ]
    t4 = md_table(
        ["file", "start", "model_slug", "turn_use_case", "tool_name",
         "duration_s", "user_prompt_head"],
        rows4,
    )

    # 5. duration_s 最长的 20 个 sse 文件。
    longest = sorted(
        (r for r in records if r["kind"] == "sse"),
        key=lambda r: r["duration_s"],
        reverse=True,
    )[:20]
    rows5 = [
        [
            cell(r["file"]),
            cell(r["start"] or ""),
            cell(join_vals(r["model_slug"])),
            cell(join_vals(r["turn_use_case"])),
            cell(join_vals(r["tool_name"])),
            cell(str(r["duration_s"])),
            cell("true" if r["has_cot_token"] else "false"),
            cell((r["user_prompt_head"] or "")),
            cell((r["assistant_tail"] or "")[:80]),
        ]
        for r in longest
    ]
    t5 = md_table(
        ["file", "start", "model_slug", "turn_use_case", "tool_name",
         "duration_s", "has_cot_token", "user_prompt_head",
         "assistant_tail_head80"],
        rows5,
    )

    md = []
    md.append("# archive_census 汇总")
    md.append("")
    md.append("共 %d 个文件（sse %d / handoff %d）。" % (
        len(records),
        sum(1 for r in records if r["kind"] == "sse"),
        sum(1 for r in records if r["kind"] == "handoff"),
    ))
    md.append("")
    md.append("口径说明（无分析结论）：")
    md.append(
        "- date 取 start 转 UTC 后的日期；计数表按“文件”计数，"
        "某文件在同一维度有多个去重值时每个值各计 1，一次未出现则计入 (none)。"
    )
    md.append(
        "- server_ste_metadata 取 type 为 server_ste_metadata 的最后一帧整体，"
        "已删除键名含 token/cookie/authorization/sentinel/conduit（大小写不敏感）"
        "或值为 eyJ 开头字符串的字段；resume_token 等 token 类值未写入任何输出。"
    )
    md.append(
        "- 本批归档中未发现 {\"p\",\"o\",\"v\"} 形式的 patch 帧，"
        "assistant_tail_method 恒为 longest（出现过的最长 assistant final/null 文本)"
        "或 none（无符合条件的 assistant 文本）。"
    )
    md.append("- channel 缺失时按 null 处理；user_prompt_head 取首个 user 消息首段前 80 字。")
    md.append("")
    md.append("## 1. 按日期 x turn_use_case 计数")
    md.append("")
    md.append(t1)
    md.append("")
    md.append("## 2. 按日期 x tool_name 计数")
    md.append("")
    md.append(t2)
    md.append("")
    md.append("## 3. 按日期 x thinking_effort x has_cot_token 计数")
    md.append("")
    md.append(t3)
    md.append("")
    md.append("## 4. turn_use_case 为 thinking 以外值的文件（前 30，按 start 排序）")
    md.append("")
    md.append(t4)
    md.append("")
    md.append("## 5. duration_s 最长的 20 个 sse 文件")
    md.append("")
    md.append(t5)
    md.append("")
    return "\n".join(md)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    names = sorted(
        n for n in os.listdir(SRC_DIR) if n.endswith(".jsonl")
    )
    records = []
    with open(OUT_JSONL, "w", encoding="utf-8") as out:
        for idx, name in enumerate(names, 1):
            rec = process_file(os.path.join(SRC_DIR, name))
            records.append(rec)
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            if idx % 200 == 0:
                print("processed %d/%d" % (idx, len(names)), flush=True)
    print("processed %d/%d" % (len(names), len(names)), flush=True)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(build_summary(records))
    print("wrote %s and %s" % (OUT_JSONL, OUT_MD), flush=True)


if __name__ == "__main__":
    main()
