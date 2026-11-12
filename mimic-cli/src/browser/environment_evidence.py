"""Read non-secret browser properties in explicitly chosen execution worlds."""
EXPRESSION='''() => ({
 userAgent:navigator.userAgent.slice(0,256),platform:navigator.platform.slice(0,64),
 language:navigator.language.slice(0,32),languages:Array.from(navigator.languages).slice(0,8),
 webdriver:navigator.webdriver,hardwareConcurrency:navigator.hardwareConcurrency,
 deviceMemory:navigator.deviceMemory??null,
 notificationPermission:typeof Notification==='undefined'?null:Notification.permission,
 timezone:Intl.DateTimeFormat().resolvedOptions().timeZone,
 chromeRuntimePresent:!!window.chrome&&!!window.chrome.runtime,
 uaData:navigator.userAgentData?{platform:navigator.userAgentData.platform,
  mobile:navigator.userAgentData.mobile,brands:navigator.userAgentData.brands}:null
})'''


async def observe_environment(page):
    worlds={}
    for name,isolated in [('main',False),('isolated',True)]:
        try:
            value=await page.evaluate(EXPRESSION,isolated_context=isolated)
            worlds[name]={'available':True,'properties':value}
        except Exception as error:
            worlds[name]={'available':False,'error_class':type(error).__name__}
    return {'execution_worlds':worlds,'cookies_or_app_storage_read':False,
            'browser_driver_added':False,'request_body_or_headers_changed':False}
