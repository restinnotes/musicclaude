"""Export verified timings, hashes and the limits of the yi comparison evidence."""
import csv
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'experiments' / 'yi-rootcause' / '20261006T0746Z'
NATIVE = ROOT / 'experiments' / 'yi-desktop-chrome' / '20261006T065841Z'
AUTO = ROOT / 'runs' / '20261006T080343.308291Z-13c003bc'
MANUAL = ROOT / 'runs' / '20261006T083356.848658Z-f21fd6bc'
NY = timezone(timedelta(hours=-4), name='America/New_York EDT')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def verify(path, expected):
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual == expected, str(path)
    return actual


def ny(utc):
    return datetime.fromisoformat(utc.replace('Z', '+00:00')).astimezone(NY).isoformat()


rows = []
native = read(NATIVE / 'results.json') + read(NATIVE / 'diagnostic-results.json')
for r in native:
    shot = r['finalScreenshot']
    verify(Path(shot['path']), shot['sha256'])
    rows.append({'trial': r['group'] + str(r['sequence']), 'environment': 'yi native Chrome',
                 'answer': r['answer'], 'submitted_utc': r['submissionStartedUtc'],
                 'submitted_new_york': ny(r['submissionStartedUtc']),
                 'completion_utc': r['firstCompletionObservedUtc'],
                 'completion_kind': 'first_observed_complete_answer',
                 'wall_seconds': r['elapsedToFirstCompletionObservedSeconds'],
                 'thinking_ui': r['thinkingUi'], 'model_ui': r['modelUi'],
                 'screenshot': shot['path'], 'screenshot_sha256': shot['sha256']})

audit = [json.loads(line) for line in (OUT / 'docker-session-observer.jsonl').read_text(encoding='utf-8').splitlines()]
recent = [r for r in audit if r.get('utc', '') >= '2026-10-06T07:51:00']
(OUT / 'recent-passive-audit.json').write_text(json.dumps(recent, indent=2, ensure_ascii=False), encoding='utf-8')
wire_requests = [r for r in recent if r.get('event') == 'generation_request_metadata'
                 and r.get('endpoint') == '/backend-api/f/conversation'
                 and r.get('metadata', {}).get('text_sha256') == '6941db951890638011b431dc77b33bccbe691c7628484308a252956549814d15']
assert len(wire_requests) == 2
request_native = read(NATIVE / 'D1-request-evidence.json')[0]
paired = []
for label, run, wire in zip(['Docker auto send', 'Docker remote UI send'], [AUTO, MANUAL], wire_requests):
    record = read(run / 'diagnostics.json')
    d = record['diagnostics']
    screenshot = d['screenshot_evidence']
    screenshot_file = next(x for x in screenshot['files'] if x['filename'] == 'response-full.jpg')
    screenshot_path = run / 'screenshots' / screenshot_file['filename']
    verify(screenshot_path, screenshot_file['sha256'])
    sent = datetime.fromisoformat(wire['utc'])
    complete = datetime.fromtimestamp(d['completed_at'], timezone.utc)
    row = {'trial': label, 'environment': 'yi original Docker Chrome',
           'answer': record['probe_assessment']['observed_answer'], 'submitted_utc': wire['utc'],
           'submitted_new_york': ny(wire['utc']), 'completion_utc': complete.isoformat(),
           'completion_kind': 'backend_detected_complete_answer',
           'wall_seconds': round((complete - sent).total_seconds(), 3),
           'thinking_ui': ' / '.join(screenshot.get('thinking_time_ui_labels', [])),
           'model_ui': d['model']['actual_label'], 'screenshot': str(screenshot_path),
           'screenshot_sha256': screenshot_file['sha256']}
    assert d['prompt_content_verified'] and d['response_complete']
    assert d['temporary_chat']['verified'] and d['non_personalized']['verified']
    if label.endswith('UI send'):
        assert d['diagnostic_manual_send']['automatic_send_executed'] is False
        assert d['worker_page_id'] == wire['page_object_id']
        row['automatic_send_executed'] = False
    rows.append(row)
    m = wire['metadata']
    fields = {'model': m['model'] == request_native['model'],
              'thinking_effort': m['thinking_effort'] == request_native['thinking_effort'],
              'prompt_sha256': m['text_sha256'] == request_native['promptCanonicalSha256'],
              'workspace_sha256': wire['workspace_header_sha256'] == request_native['workspaceHeaderSha256'],
              'history_and_training_disabled': m['history_and_training_disabled'] == request_native['history_and_training_disabled'],
              'temporary_chat_requests_personalization': m['temporary_chat_requests_personalization'] == request_native['temporary_chat_requests_personalization'],
              'is_do_not_remember': m['is_do_not_remember'] == request_native['is_do_not_remember']}
    assert all(fields.values())
    paired.append({'trial': label, 'answer': row['answer'], 'actual_request': wire,
                   'core_fields_match_native': fields,
                   'response_body_metadata_available': False})

assert read(OUT / 'docker-account-evidence.json')['matchesNativeAccount'] is True
original_client_hash = hashlib.sha256((OUT / 'client.original.py').read_bytes()).hexdigest()
verify(OUT / 'client.restored.py', original_client_hash)
verify(ROOT / 'src' / 'chatgpt' / 'client.py', original_client_hash)
observer_hash = hashlib.sha256((ROOT / 'src' / 'request_observer.py').read_bytes()).hexdigest()
verify(OUT / 'request_observer.deployed.py', observer_hash)
shutdown = read(OUT / 'shutdown-and-deployment.json')
assert shutdown['request_observer_sha256'] == observer_hash
assert shutdown['browser_close_confirmed'] and shutdown['container_status'] == 'exited'

report = {'status': 'client_evidence_collected_exact_root_cause_unconfirmed',
          'expected_answer_from_user': 8, 'proof_independently_verified': False,
          'new_trials': rows, 'paired_requests': paired,
          'native_request_evidence': str(NATIVE / 'D1-request-evidence.json'),
          'same_account_and_workspace_verified': True,
          'prior_results': {'yi_original_docker': [6, 6, 6], 'yi_camoufox_docker': [6, 6, 6],
                            'shiyan_original_docker_high': [8, 'timeout', 8],
                            'shiyan_camoufox_high': [8, 8, 8]},
          'strongest_working_hypothesis': 'Imported browser/session context interacts with this Business account/workspace; exact mechanism unconfirmed',
          'findings': [
              'Native yi is normal in four complete trials with the same prompt and Extra High.',
              'Original Docker is abnormal in interleaved trials with matched core outgoing request fields.',
              'Changing only the final send-button action to a remote UI mouse click did not restore answer 8 in this trial.',
              'The native and Docker visible login account hashes and selected Business workspace match.',
              'These cup trials are sequential; the abnormal result reproduces with one generation in flight.',
              'Prior Docker answer 6 also occurred after 10m27s thinking; short thinking duration alone is not the root cause.',
              'shiyan uses High whereas yi uses Extra High; cross-account comparison is confounded by plan and effort.',
              'No missing session cookie, deletion directive, or HTTP 401/403 was observed during these new trials.'
          ],
          'limits': [
              'Server-side actual weights, compute allocation, risk assessment and experiment assignment are unavailable.',
              'SSE response body readback failed in both observed native Chrome and Docker.',
              'The matched fields are a whitelist, not proof that the entire request payload and browser/session state match.',
              'Full profile state, actual public network egress, browser fingerprint and server routing have not been isolated individually.',
              'Native wall time ends at the first observation of completion and includes polling delay.',
              'The experimental manual pause triggered the existing submission heuristic early; its submitted_at precedes the real mouse click and POST. This report uses the actual observed POST time. No automatic send click was executed.'
          ],
          'passive_audit': {'source': str(ROOT / 'src' / 'request_observer.py'),
                            'sha256': observer_hash, 'unit_tests_passed': 4,
                            'real_page_and_request_correlation_observed': True,
                            'real_http_status_observed': 200, 'auth_headers_or_values_logged': False,
                            'content_logged': False, 'missing_sse_body_explicitly_recorded': True},
          'cleanup': {'temporary_client_restored_sha256': original_client_hash,
                      'temporary_viewport_reset': True, 'native_result_tabs_kept': 4,
                      'shutdown': shutdown}}
(OUT / 'ROOTCAUSE.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
fields = ['trial', 'environment', 'answer', 'submitted_utc', 'submitted_new_york',
          'completion_utc', 'completion_kind', 'wall_seconds', 'thinking_ui', 'model_ui', 'screenshot', 'screenshot_sha256']
with (OUT / 'RESULTS.csv').open('w', encoding='utf-8-sig', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(rows)
text = '''yi 本机 Chrome 与 Docker 对照调查，2026-10-06

请求的本机三轮已完成：8、8、8。另加一轮被动请求观测，本机仍为 8。
随后的原 Docker 自动发送为 6，远程界面点击发送为 7，均未达到约定正常值 8。
每轮均保存完整回答、时间和未经编辑的原始截图，并核对截图 SHA256。

关键新证据
1. 已通过可见账号菜单的标识摘要核实：本机和原 Docker 确为同一账号，均在 Joy-group Business 工作区。
2. 被动观察网页真实 POST：题目摘要、gpt-5-6-thinking、max、临时/不个性化核心标志及工作区摘要一致。
3. 远程鼠标点击发送的对照也异常，不能靠改最后一次按钮点击恢复本轮表现。
4. 当前水杯题是逐轮运行、单请求生成，降低并发无法解释这里已经重现的异常。
5. 旧 Docker 曾在思考 10分27秒后仍答6，思考短不能单独解释全部异常。
6. 新轮次未观测到 Cookie 消失、删除指令或 HTTP 401/403；每次正常停止均确认浏览器上下文先关闭。

目前判断
最优先怀疑的是导入后的浏览器/会话环境与此 Business 账号或工作区条件的交互。
本机同一账号的正常结果表明，该账号在原生浏览器条件下具备正常完成本题的能力。
具体是浏览器指纹、完整 profile 状态、客户端上下文、网络出口、工作区实验分组或服务端资源分配，仍未确认。
shiyan 的 Plus/High 与 yi 的 Business/Extra High 存在混杂，不能仅凭账号对比锁定套餐原因。
原 Docker 与 Camoufox 都异常，现有数据不支持“仅换 Firefox/慢打字即可恢复”的结论。

证据限制
两侧 SSE 响应正文均无法读回，不能声称验证了服务端实际模型权重或计算额度。
匹配的是记录的核心白名单字段，并非整个请求或完整浏览器状态完全相同。
本机总耗时含轮询观察误差；网页思考时长单独保留。
远程点击轮的实验暂停触发了原提交确认启发式的提前判断，submitted_at早于实际鼠标点击和POST；本报告 RESULTS.csv 采用真实网页 POST 时间。原自动发送按钮点击未执行。
最初纯远程键盘/剪贴板尝试未能完整输入中文，未提交残缺题目；后续通过准备后暂停已完成有效对照。

后续可用记录
src/request_observer.py 已部署并在有效手动对照中观察到页面ID、请求ID及真实HTTP200。
记录实际模型、强度、题目摘要、临时/个性化标志和工作区摘要，正文不可用时明确记错误。
不保存 Cookie、认证头或提示词正文。4项针对性测试通过。
原自动发送代码已按 SHA256 恢复，临时显示尺寸与调试设置已复原。
原 yi 容器在无请求时正常关闭，确认浏览器关闭、进程退出、退出码0、无OOM；profile和state卷保留。

详细证据：ROOTCAUSE.json、RESULTS.csv、recent-passive-audit.json，以及其中链接的逐轮原始文件。
'''
(OUT / 'REPORT.txt').write_text(text, encoding='utf-8')
print(json.dumps({'report': str(OUT / 'ROOTCAUSE.json'), 'trials': len(rows),
                  'screenshot_hashes_verified': len(rows), 'native_answers': [r['answer'] for r in rows[:4]],
                  'docker_answers': [r['answer'] for r in rows[4:]],
                  'manual_wire_to_complete_seconds': rows[-1]['wall_seconds'],
                  'same_account_verified': True, 'temporary_client_restored': True}, ensure_ascii=False))
