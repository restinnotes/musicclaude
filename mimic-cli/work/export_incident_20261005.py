from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo

root=Path(__file__).resolve().parents[1]
out=Path(r'C:\Users\zuoyi\Documents\Codex\2026-10-03\new-chat\outputs\20261005登录态调查')
out.mkdir(exist_ok=True)
for remote,name in [('/app/state/yi-incident-20261005.json','浏览器现场.json'),
                    ('/app/state/yi-incident-database-20261005.json','Cookie数据库现场.json'),
                    ('/app/state/yi-session-observer.jsonl','会话观察记录.jsonl')]:
    subprocess.run(['docker','cp','yi-mimicgate-20261002:'+remote,str(out/name)],check=True,
                   capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
source={'profile':'Chrome Default / 您的 Chrome','session_cookie_count':1,
        'fresh_page_profile_enabled':True,'fresh_page_login_present':False,
        'observed_utc':'2026-10-06T00:18:12.863Z',
        'source_cookie_expiry':1799021822.830762,
        'ordinary_reload_comparison':{'before_count':1,'after_count':1,'cookie_value_changed':True,
        'before_expiry':1799021822.830762,'after_expiry':1799022264.413374,
        'observed_utc':'2026-10-06T00:24:38.542Z','fresh_page_authenticated':True},
        'values_exported':False,'does_not_prove_old_cookie_server_revocation':True}
(out/'原浏览器对比.json').write_text(json.dumps(source,ensure_ascii=False,indent=2),encoding='utf-8')
report={'captured_utc':datetime.now(timezone.utc).isoformat(),
        'incident_confirmed':'container session token absent in both browser memory and cookie database; fresh page displays Log in',
        'root_cause':'UNPROVEN: no historical cookie response/deletion trace before incident',
        'container_started_new_york':'2026-10-05T17:52:57.632632-04:00',
        'last_success_request_started_new_york':'2026-10-05T18:29:23.702858-04:00',
        'last_success_elapsed_seconds':47.219,
        'first_failure_request_started_new_york':'2026-10-05T18:32:38.251866-04:00',
        'first_failure_elapsed_seconds':62.703,
        'manager_cleanup_safe_before_investigation':True,
        'docker_log_driver':'none','backend_log_level':'ERROR',
        'standard_errors_were_not_written_to_backend_logs':True,
        'container_restart_performed_by_this_investigation':False,
        'cookie_import_performed_by_this_investigation':False,
        'profile_cleanup_performed_by_this_investigation':False,
        'yi_new_calls_frozen':True,'configured_concurrency':8,
        'observer':{'active':True,'first_started_new_york':'2026-10-05T20:16:08-04:00',
          'sample_interval_seconds':5,'heartbeat_interval_seconds':60,
          'persistent_log':'/app/state/yi-session-observer.jsonl',
          'records':['presence/expiry and changes','cookie value change boolean only',
                     'auth-cookie Set-Cookie metadata and deletion directives','401/403 status and endpoint category',
                     'page login/profile control changes','CDP disconnect/reconnect','read-only cookie database row count'],
          'starts_again_on_next_container_boot':True,'next_boot_hook_installed_syntax_checked':True,
          'first_navigation_listener_source_installed':True,
          'first_navigation_listener_active_in_current_backend':False,
          'request_auth_preflight_source_installed':True,
          'request_auth_preflight_active_in_current_backend':False,
          'source_changes_take_effect_on_next_backend_start':True,
          'limitations':['Cannot reconstruct the missing historical event',
                         'Local cookie deletion may be detected without identifying its external caller',
                         'Cookie value changes alone do not prove server revocation']},
        'validation':{'observer_unit_tests':6,'auth_preflight_container_tests':2,
                      'standard_contract_container_tests':2,'cli_guard_tests':5,'all_passed':True}}
(out/'调查结果.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
text='''本次登录态异常调查（2026-10-05，纽约时间）

已确认：yi 容器的会话 token 在浏览器内存和 Cookies 数据库中都不存在，新页面显示 Log in。
旧控制页仍显示账号菜单，是旧页面状态，不能用它证明新请求仍有认证。
原 Chrome Default 新页面仍登录。正常刷新一次后，会话 cookie 值变化、过期时间延长。
后者说明原浏览器会更新会话 cookie；导入的容器副本不会自动同步原浏览器后续的新值。
它不能单独证明旧 cookie 已被服务器作废。

时间：容器 17:52:57 启动；最后成功调用 18:29:23 发起、约 18:30:10 完成；
18:32:38 发起的请求约一分钟后报告 Temporary Chat activation control was not found。
因此此次异常并非只有 19:57 之后才开始，也不符合重启时立即丢失的解释。
当前启动清理代码与此前安全修复一致，未发现本次仍在使用删除 Cookie WAL 的旧代码。

关键记录缺口：Docker log driver 为 none；后台日志级别为 ERROR；标准调用异常此前
被转成 HTTP/CLI 错误而没有写后台日志。原有调用日志能给出成功/失败时间，不能说明
cookie 到底由哪个响应或哪个本地动作删除。过去的这一步没有记录，无法补造证据。

已启用被动观察器，每 5 秒检查会话状态、每 60 秒落心跳，实时记录认证 cookie
响应的过期/删除指令、cookie 值是否变化（只记布尔值）、401/403、登录控件状态、
数据库行数、浏览器断开和重连。实时日志位于容器持久卷：
/app/state/yi-session-observer.jsonl。本文件夹的 jsonl 是导出时的快照。
不记录 cookie 值、Authorization、请求正文、响应正文或完整查询 URL。

已安装下次启动自动拉起观察器的钩子，并准备了首个导航之前的认证响应监听、
请求前会话检查和标准请求失败落盘。当前正在运行的后端尚未重新加载这些源代码，
只有独立观察器已经实际运行；新检查在下次后端启动时生效。
6 个观察器测试、2 个会话预检测试、2 个原有标准契约测试、5 个 CLI 保护测试均通过。

调查没有重启容器、清理 profile 或重新导入 cookie。yi 仍配置 8 并发，
新的 CLI 请求被调查保护暂时拦住；实验运行成功缓存没有被修改。

最终触发原因：尚未证实。优先追踪网站清除/续签会话响应、导入副本与原浏览器的
会话更新差异；本地删除也需排查。若没有删除响应而观察器捕获 cookie 消失，仍可能
只能确定时间而不能直接识别实施本地操作的外部进程。不能把推测写成根因。
'''
(out/'调查说明.txt').write_text(text,encoding='utf-8')
print(json.dumps({'output_folder':str(out),'root_cause':report['root_cause'],'observer_active':True},ensure_ascii=False))
