# Harness source-behaviour probe — S01 Pool (2026-10-29)

## What this is

One task, one segment, run in several harnesses, to see **where the sourcing goes wrong** when a
"bead" is first built.

- Task: **Pool for S01 (mm.1–3, 序奏)** of Chopin's Barcarolle Op.60.
- Input: the 24 historical A manuscripts in `input/A/` and the frozen `input/structure.json`.
- Output: the Pool JSON (items / excluded / sources_checked) plus an optional `web_sources` record.
- Prompt: `prompt_S01_files.md` (opencode, codex) and `prompt_S01_zip.md` (gpt3, same body,
  input delivered as `input_bundle.zip`). The only textual difference is the input-location sentence.

The task is deliberately *not* a web-research task: the 24 manuscripts are the only allowed source
of experience items. Web use is optional and is only for checking facts (measure numbers, segment
boundaries, work background). That is exactly the point: a model that never thinks to verify the
score will not search; a model that searches but cannot fetch will cite snippets; a model that
fetches but does not use the page will show it in the trace.

## Harnesses

| run | harness | model | note |
|---|---|---|---|
| `*_oc_luna_s01` | opencode v2.2.0 | `codex-proxy-azure/gpt-6-luna#max` | `#max` maps to `xhigh` on this provider |
| `*_cx_luna_s01` | codex CLI 0.164.0 | `gpt-6-luna` | `-c web_search="live"`; native `web_search` |
| `*_g3_thinking_s01` | local gpt3 bridge | `gpt-6-thinking` | fixed max; web always on; `--allow-topic-stream` |

Same model family, not the same checkpoint: gpt3 has no `gpt-6-luna`. Recorded rather than hidden.

## Files per run

```
runs/<utc>_<label>/
  prompt.txt        exact prompt
  cwd/input/        sources as the model saw them (opencode/codex)
  stdout.bin        raw stdout
  stderr.bin        raw stderr
  events.jsonl      raw event stream (opencode/codex)
  output.md         final assistant message
  output.json       parsed JSON block
  trace.json        normalized searches / fetches / file reads / errors + classification
  meta.json         argv, timing, exit code, hashes, quote/source coverage
```

## Classification used by `trace.json`

- `no_web_call` — no search, no fetch, no web source reported.
- `search_only` — search calls but no page fetch. (opencode `websearch` and codex `web_search`
  both return snippets/inline text; a separate fetch is the only way to read a full page.)
- `search_and_fetch_ok` — at least one successful fetch.
- `fetch_partly_failed` / `fetch_failed` — fetch attempts failed.
- `tool_errors` counts failed tool calls and harness errors separately.

`reported_web_sources` is what the model *claims* in its JSON. Comparing it with `trace.json`
separates "searched and used", "searched but did not use", and "invented a source".

## Known harness limits

- **gpt3** records only `toolsUsed` and `sources` in `result.json`; it does not expose the search
  query or the fetched URL. `web.run` means search happened, but query-level analysis is impossible
  from the artifacts. Its web path can also end in `INCOMPLETE_RESPONSE` when the turn moves to the
  websocket topic; `--allow-topic-stream` is used to follow the same turn.
- **codex** `web_search` returns result snippets; it has no separate page-fetch tool. A model that
  wants the full page must use `curl` via the shell, which is visible as `command_execution`.
- **opencode** exposes `websearch` and `webfetch`. Its code-mode `execute` tool can also call
  `tools.websearch`; a model that guesses `tools.search` gets the tool catalog back instead of
  results. That fumble is recorded, not hidden.
- **opencode/`openai`** returned `provider.quota` (ChatGPT Plus 5-hour window at 100%) during setup;
  the runs use `codex-proxy-azure` instead. This is a quota difference, not a model difference.

## Inputs are frozen

`input/A` and `input/structure.json` are copies of `_bead_gpt3_20261018/input`. `input_bundle.zip`
contains exactly those 25 files. The SHA-256 of the zip is in every `meta.json`.

## Prompt rebuild note (2026-10-29 01:45 local)

The first build of `prompt_S01_files.md` / `prompt_S01_zip.md` lost every CJK character in the
`{{INPUT}}` paragraph to `?` (the sentence had been written through a non-UTF-8 console). The
aborted 01:40 opencode run is kept under `runs_invalid/` as evidence and is **not** counted. Both
prompts were rebuilt from `prompt_S01_body.md` with `tools/build_prompts.py`; they differ only in
the input-location sentence (`input/A/` in the working directory vs. `input_bundle.zip` attachment).
The prompt SHA-256 in each `meta.json` identifies the version actually used.
