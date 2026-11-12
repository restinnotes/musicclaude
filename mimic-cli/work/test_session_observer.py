import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

# The Linux lock module is needed only by the deployed collector's main().
sys.modules.setdefault('fcntl',types.SimpleNamespace())
spec=importlib.util.spec_from_file_location('observer',Path(__file__).with_name('yi_session_observer.py'))
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class MetadataTests(unittest.TestCase):
    def test_deletion_directive_without_value(self):
        result=module.auth_header_metadata('__Secure-next-auth.session-token=SECRET_TEST; Max-Age=0; Path=/')
        self.assertTrue(result['deletion_directive'])
        self.assertNotIn('SECRET_TEST',str(result))
    def test_live_cookie_is_not_deletion(self):
        result=module.auth_header_metadata('__Secure-next-auth.session-token.0=SECRET_TEST; Max-Age=86400')
        self.assertFalse(result['deletion_directive'])
        self.assertNotIn('SECRET_TEST',str(result))
    def test_expired_cookie_is_deletion(self):
        result=module.auth_header_metadata('__Secure-next-auth.session-token=; Expires=Thu, 01 Jan 1970 00:00:00 GMT')
        self.assertTrue(result['deletion_directive'])
    def test_unrelated_cookie_is_ignored(self):
        self.assertIsNone(module.auth_header_metadata('other=SECRET_TEST; Max-Age=0'))
    def test_url_contains_no_query_or_conversation_id(self):
        result=module.classify_url('https://chatgpt.com/c/PRIVATE_ID?token=SECRET_TEST')
        self.assertEqual(result,{'host':'chatgpt.com','path_category':'other'})

class FirstResponseTests(unittest.IsolatedAsyncioTestCase):
    async def test_startup_listener_captures_clear_directive_without_value(self):
        handlers={}
        context=types.SimpleNamespace(pages=[],on=lambda event,handler:handlers.update({event:handler}))
        async def headers():
            return [{'name':'Set-Cookie','value':'__Secure-next-auth.session-token=SECRET_TEST; Max-Age=0'}]
        response=types.SimpleNamespace(url='https://chatgpt.com/',status=200,headers_array=headers)
        events=[]
        with patch.object(module,'emit',side_effect=lambda event,**fields:events.append({'event':event,**fields})):
            module.attach_context_audit(context)
            await handlers['response'](response)
        self.assertEqual(events[0]['event'],'backend_context_audit_attached')
        self.assertTrue(events[1]['deletion_directive'])
        self.assertNotIn('SECRET_TEST',str(events))

if __name__=='__main__':
    unittest.main()
