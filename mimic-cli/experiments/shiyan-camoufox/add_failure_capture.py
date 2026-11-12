from pathlib import Path
path = Path(__file__).resolve().parent / 'src' / 'api' / 'standard_completion.py'
source = path.read_text(encoding='utf-8')
needle = '        except Exception as exc:\n            kind = classify_error(exc)\n'
assert source.count(needle) == 1
source = source.replace(needle, needle + "            screenshot_evidence = await capture_probe_evidence(client, 'failure')\n", 1)
needle = '            diagnostics.update({"elapsed_seconds": round(time.monotonic() - started, 3),\n                                "response_complete": False'
assert needle in source
source = source.replace(needle, "            diagnostics['request_id'] = client._standard_request_id\n"
                        "            diagnostics['screenshot_evidence'] = screenshot_evidence\n" + needle, 1)
path.write_text(source, encoding='utf-8')
compile(source, str(path), 'exec')
print('Added failure screenshots before stopping an incomplete generation.')
