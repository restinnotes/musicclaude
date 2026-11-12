from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

out=Path(r'C:\Users\zuoyi\Documents\Codex\2026-10-03\new-chat\outputs\20261005登录态调查')
root=Path(__file__).resolve().parents[1]
for remote,name in [('/app/state/yi-session-observer.jsonl','修复后的会话记录.jsonl'),
                    ('/app/state/yi-session-restored.json','本次登录态恢复.json'),
                    ('/app/state/yi-session-status.json','修复后会话状态.json')]:
    subprocess.run(['docker','cp','yi-mimicgate-20261002:'+remote,str(out/name)],
                   check=True,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
validation=json.loads((out/'已生效保护的标准调用验证.json').read_text(encoding='utf-8'))
first=json.loads((out/'保护生效后第一次TEST_OK.json').read_text(encoding='utf-8'))
status=json.loads((out/'修复后会话状态.json').read_text(encoding='utf-8'))
assert validation['success'] and first['success'] and status['session_cookie_count']>0
report={'captured_utc':datetime.now(timezone.utc).isoformat(),
  'changes_loaded_in_current_yi_backend':True,'yi_session_restored':True,
  'yi_new_calls_frozen':(root/'config/session-investigation.freeze').exists(),
  'max_concurrency':8,'standard_submission_min_interval_seconds':5,
  'original_chrome_fresh_reload_authenticated_after_recovery':True,
  'original_chrome_reload_did_not_immediately_invalidate_container_session':True,
  'standard_test_ok_checks_passed':2,'temporary_chat_verified':True,
  'unpersonalized_verified':True,'model':'gpt-5.6-sol','effort':'xhigh','high_fallback':False,
  'backend_auth_preflight_active':True,'cli_fresh_session_preflight_active':True,
  'first_navigation_response_listener_active':True,'observer_restarted_automatically_with_container':True,
  'renewal_observed_in_container':True,'renewal_max_age_seconds':7776000,
  'current_session_cookie_count':status['session_cookie_count'],
  'current_database_auth_rows':status['database_session_rows'],
  'no_automatic_prompt_replay':True,'no_automatic_account_switch':True,
  'auth_temporary_files_deleted':True,'experiments_and_successful_caches_modified':False,
  'container_recreated':False,'volumes_replaced':False,'browser_profile_replaced':False,
  'validation':{'pacing_unit_tests':3,'cli_guards_tests':8,'auth_preflight_container_tests':2,
                'observer_metadata_and_first_response_tests':6,'standard_contract_tests':2,
                'isolated_browser_response_integration':True},
  'historical_root_trigger':'UNPROVEN',
  'limits':['A future server-side session revocation cannot be prevented by these local guards.',
            'These changes preserve normal request content and modes, add pacing/observability and stop missing-auth requests.',
            'Two live TEST_OK calls are not an 8-concurrent endurance validation.']}
(out/'保护已生效与恢复结果.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
text='''本次修复已经实际加载到 yi 服务（2026-10-05，纽约时间）。

前一次本 agent 测试和本次实验运行均出现过容器会话丢失，不能归因于另一 agent。
此前完成了安全 profile 清理修复与 cookie 恢复，但未证明运行中失效的触发源已消除。

当前已生效：
- 保留 Cookie 数据库/WAL/SHM 与其他登录存储的启动清理。
- CLI 读取新鲜的脱敏会话状态；明确缺失时在 completion HTTP 前停止。
- 后台独立核对真实浏览器会话；缺失时不进行页面准备或发送 prompt。
- 同一 MimicGate 实例的所有标准 worker 共享至少 5 秒的发送尝试间隔。
  UI 准备已经超过 5 秒时不额外等待。回答等待继续并发，最大并发仍为 8。
- 每次记录点击发送尝试和确认提交两个时间戳，认证失败记录故障文件/函数/行号。
- 首次导航之前监听认证 cookie 响应；被动观察器随容器启动自动恢复。
- 记录会话存在/更新/消失、续签/清除指令、401/403、页面认证和连接变化。
  不记录 cookie 值、认证头、请求/响应正文，不静默切换账号或重放 prompt。

恢复与验证：用已授权的原 Chrome Default 登录态恢复 yi，保留原容器、卷与 profile。
空闲时优雅重启同一容器加载保护。首次加载漏掉配套配置导致 AttributeError，
失败在发送 prompt 前；已补齐配置并通过后续验证。认证在此期间一直存在。
两次真实标准调用均返回 TEST_OK，确认 Temporary Chat、Unpersonalized、
GPT-5.6 Sol Extra High、认证预检和 5 秒间隔机制。第二次在原 Chrome 正常刷新后进行，
原 Chrome 与容器都保持登录。新日志已捕获容器正常续签响应，Max-Age 为 90 天。
已解除临时调查暂停，原调用入口恢复使用；实验代码和成功缓存未被修改。

范围：这是登录数据保护、认证故障止损、发送节奏控制、诊断记录与本次恢复。
历史掉登录的最终触发源仍未证实，也不能保证本地保护能阻止网站未来撤销会话。
两次 TEST_OK 不是新的 8 并发长期稳定性验收。
'''
(out/'已生效修复说明.txt').write_text(text,encoding='utf-8')
print(json.dumps({'yi_usable':True,'frozen':report['yi_new_calls_frozen'],'test_ok_checks':2,
                  'session_cookie_count':status['session_cookie_count'],'max_concurrency':8,'min_send_gap':5},ensure_ascii=False))
