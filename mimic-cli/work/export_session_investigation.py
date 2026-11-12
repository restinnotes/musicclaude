"""Export a redacted incident report from immutable run evidence and fake-cookie tests."""
from datetime import datetime
from zoneinfo import ZoneInfo
import json
from pathlib import Path
import subprocess
import hashlib

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = Path('C:/Users/zuoyi/Documents/Codex/2026-10-03/new-chat/outputs')
OUTPUT.mkdir(exist_ok=True)
CONTAINER = 'yi-mimicgate-20261002'
NY = ZoneInfo('America/New_York')


def fixture(name, *arguments):
    result = subprocess.run(['docker','exec','-w','/app',CONTAINER,'/opt/venv/bin/python','/app/'+name] + list(arguments),
        capture_output=True,text=True,encoding='utf-8',timeout=45)
    if result.returncode:
        raise RuntimeError('Isolated fixture failed: ' + name)
    return json.loads(result.stdout)


def local_time(unix):
    return datetime.fromtimestamp(unix, NY).isoformat()


two = json.loads((ROOT/'runs/parallel-20261005T020748Z-2/report.json').read_text(encoding='utf-8'))
four = json.loads((ROOT/'runs/parallel-20261005T021038Z-4/report.json').read_text(encoding='utf-8'))
prior_path = OUTPUT / '登录态异常调查.json'
prior = json.loads(prior_path.read_text(encoding='utf-8')) if prior_path.exists() else {}
live_hash = subprocess.run(['docker','exec',CONTAINER,'/opt/venv/bin/python','-c',
    "from pathlib import Path; import hashlib; print(hashlib.sha256(Path('/app/src/browser/manager.py').read_bytes()).hexdigest())"],
    capture_output=True,text=True,timeout=10,check=True).stdout.strip()
live_canonical_hash = subprocess.run(['docker','exec',CONTAINER,'/opt/venv/bin/python','-c',
    "from pathlib import Path; import hashlib; print(hashlib.sha256(Path('/app/src/browser/manager.py').read_text().encode('utf-8')).hexdigest())"],
    capture_output=True,text=True,timeout=10,check=True).stdout.strip()
backup_hash = hashlib.sha256((ROOT/'backups/browser_manager_before_profile_preservation.py').read_text(encoding='utf-8').encode('utf-8')).hexdigest()
events = []
for request in two['requests']:
    diag = request['diagnostics']
    events += [{'time':local_time(diag['submitted_at']),'kind':'submitted','stage_limit':2,'request_index':request['index']},
               {'time':local_time(diag['completed_at']),'kind':'complete','stage_limit':2,'request_index':request['index']}]
for request in four['requests']:
    diag = request['diagnostics']
    events.append({'time':local_time(diag['preparation_started_at']),'kind':'preparation_started',
        'stage_limit':4,'request_index':request['index'],'error':request['error'],'model_verified':bool(diag.get('model')),
        'prompt_submission_verified':diag.get('prompt_submitted',False)})
events.sort(key=lambda e:e['time'])
report = {'timestamp':datetime.now(NY).isoformat(),'status':'ROOT_TRIGGER_UNPROVEN',
    'production_actions_during_investigation':{'container_restarted':False,'control_page_reloaded':False,
        'session_cookie_restored':False,'temporary_cookie_export_deleted':True},
    'last_known_good':{'limit':2,'requests_passed':2,'peak_submitted_uncompleted':two['peak_submitted_uncompleted']},
    'first_failed_stage':{'limit':4,'requests_failed_before_submission':4,'peak_submitted_uncompleted':four['peak_submitted_uncompleted']},
    'timeline':events,'isolated_tab_lifecycle':prior.get('isolated_tab_lifecycle') or fixture('test_cookie_lifecycle_isolated.py'),
    'isolated_startup_cleanup':prior.get('isolated_startup_cleanup') or fixture('test_profile_cleanup_isolated.py'),
    'local_profile_preservation_fix':{
        'deployed':False,'tested_with_fake_database':True,'fake_cookie_rows_before':1,'fake_cookie_rows_after':1,
        'wal_retained':True,'localstorage_indexeddb_cache_serviceworker_retained':True,'global_pkill_calls':0,
        'local_source_sha256':hashlib.sha256((ROOT/'src/browser/manager.py').read_bytes()).hexdigest(),
        'production_source_sha256':live_hash,'production_source_still_matches_pre_fix_backup':live_canonical_hash==backup_hash,
        'backup_comparison_normalizes_line_endings':True},
    'local_incident_freeze':{'active':(ROOT/'config/session-investigation.freeze').exists(),
        'blocks_new_cli_browser_calls':True,'blocks_deployment':True,'blocks_concurrency_changes':True,
        'read_only_status_available':True,'guard_test_verified_no_http_and_no_auth_reads':True},
    'observed_auth_state':{'container_session_cookie_present':False,'other_container_cookies_present':True,
        'windows_original_default_source_logged_in':True,'windows_source_session_cookie_present_and_unexpired':True,
        'scope':'metadata and visible UI only; no credential values in report'},
    'root_cause_limits':[
        'No cookie-presence snapshot or redacted Set-Cookie deletion event was recorded between the last successful request and first failed preparation.',
        'Production log level is ERROR; INFO browser and network events were not retained.',
        'Successful calls after restart prevent treating the reproduced startup defect as a proven cause of this specific loss.',
        'Fake-cookie lifecycle tests cover browser mechanics, not real-site authentication refresh or server-side invalidation.',
        'Container OOMKilled is false and no intervening container restart was observed; renderer-level incidents are not excluded by that alone.'],
    'requirements_before_resuming':[
        'Remove destructive SQLite journal/WAL cleanup before any future production browser restart.',
        'Preserve and validate the imported session before and after every page lifecycle action.',
        'Capture authentication cookie deletion/expiry metadata and passive authentication-response status without storing cookie values.',
        'Do not use the production login to reproduce failures or increase concurrency while cause is unresolved.']}
OUTPUT.joinpath('登录态异常调查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
lines = ['登录态异常调查（纽约时间）','状态：精确触发原因尚未证实，扩容暂停。','',
    '已确认：2 并发两个请求成功；随后 4 并发四个请求均在发送前缺少 Temporary 控件，未验证发送。',
    '已确认：原 Windows Default 来源仍登录，会话 cookie 存在且未过期；容器里会话 cookie 缺失，其余 cookie 数据仍在。',
    '已确认：没有更换浏览器 volume；容器没有在两轮测试之间重启，Docker OOMKilled=false。', '',
    '隔离复测：仅使用假 cookie，不打开生产 profile，不访问真实 ChatGPT。',
    'about:blank、额外 CDP 连接/断开、2→4 tabs、关闭空闲 tab 的假 cookie 均保留。',
    '继承的启动清理删除 Cookie WAL 后，假数据库中的会话记录从 1 条变成 0 条。这是已复现的数据破坏风险。',
    '该风险是本次精确根因的候选，尚未得到本次事件的直接证据；重启后两个请求成功，不能忽略。','',
    '关键时间线：']
lines += [json.dumps(e,ensure_ascii=False) for e in events]
lines += ['', '证据缺口：当时没有记录 cookie 消失前后的快照或去值的 Set-Cookie 删除事件；日志为 ERROR 级别。',
    '因此不能声称“4 并发把账号挤掉线”，也不能保证已确定是重启清理或站点会话刷新造成。',
    '调查期间没有再次重启容器、刷新原控制页或恢复会话 cookie；未使用的临时导出已删除。',
    '本地源码已移除全局 pkill、SQLite journal/WAL 删除和 profile cache/Service Worker 删除；修复未部署到生产容器。',
    '修复的隔离验证：假会话记录 1→1，WAL、Local Storage、IndexedDB、Cache、Service Worker 保留，不调用 pkill。',
    '生产 browser/manager.py 与修复前备份在规范化换行后的内容哈希相同，确认运行代码未被替换。',
    '本地 CLI、并发修改和部署入口由临时冻结文件保护；新请求不读取认证、不发 HTTP，不触碰网页。状态查看仍可用。',
    '在移除启动数据破坏路径、建立无密钥的登录态审计及确认恢复步骤之前，不继续 4、6、8 实测。']
OUTPUT.joinpath('登录态异常调查.txt').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'reports_exported':True,'status':report['status'],
    'fake_cookie_lifecycle_passed':report['isolated_tab_lifecycle']['all_cookie_checks_passed'],
    'unsafe_startup_cleanup_reproduced':report['isolated_startup_cleanup']['inherited_startup_cleanup_can_destroy_uncheckpointed_cookies']}))
