"""Retention must never touch login, ordinary, active, or other-domain cookies."""
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from src.cookie_capacity import inactive_temporary_cookies, temporary_conversation_id, ensure_cookie_headroom

OLD = '11111111-1111-1111-1111-111111111111'
ACTIVE = '22222222-2222-2222-2222-222222222222'
ORDINARY = '33333333-3333-3333-3333-333333333333'


def cookie(name, domain='chatgpt.com'):
    return {'name': name, 'domain': domain, 'path': '/', 'value': 'PUBLIC_FAKE', 'expires': 9999999999}


class RetentionTests(unittest.IsolatedAsyncioTestCase):
    def test_active_ordinary_auth_and_other_domain_are_excluded(self):
        values = [cookie('__Secure-next-auth.session-token'), cookie('oai-did'),
            cookie('conv_key_' + ORDINARY), cookie('history_off_' + OLD), cookie('conv_key_' + OLD),
            cookie('history_off_' + ACTIVE), cookie('conv_key_' + ACTIVE),
            cookie('history_off_' + OLD, 'example.com')]
        candidates = inactive_temporary_cookies(values, {ACTIVE})
        self.assertEqual({c['name'] for c in candidates}, {'history_off_' + OLD, 'conv_key_' + OLD})
        self.assertTrue(all(c['domain'] == 'chatgpt.com' for c in candidates))

    def test_only_exact_temporary_chat_url_can_authorize_retirement(self):
        self.assertEqual(temporary_conversation_id('https://chatgpt.com/c/' + OLD + '?temporary-chat=true'), OLD)
        self.assertIsNone(temporary_conversation_id('https://chatgpt.com/c/' + OLD))
        self.assertIsNone(temporary_conversation_id('https://example.com/c/' + OLD + '?temporary-chat=true'))

    async def test_capacity_guard_refuses_when_no_safe_temporary_cookies_exist(self):
        class Context:
            pages = []
            async def cookies(self, *args):
                return [cookie('ordinary_' + str(i)) for i in range(179)]
        with patch('src.session_observer.emit'):
            with self.assertRaisesRegex(RuntimeError, 'no safe inactive'):
                await ensure_cookie_headroom(Context(), '/unused')

    async def test_exact_deletion_never_calls_clear_entire_cookie_jar(self):
        class Context:
            def __init__(self):
                self.pages = [SimpleNamespace(url='https://chatgpt.com/')]
                self.values = [cookie('__Secure-next-auth.session-token')]
                for i in range(90):
                    guid = f'{i:08x}-1111-1111-1111-111111111111'
                    self.values += [cookie('history_off_' + guid), cookie('conv_key_' + guid)]
                self.deleted = []
            async def cookies(self, *args):
                return list(self.values)
            async def new_cdp_session(self, page):
                return self
            async def send(self, method, params):
                assert method == 'Network.deleteCookies'
                assert params['name'].startswith(('conv_key_', 'history_off_'))
                self.deleted.append(params)
                self.values = [c for c in self.values if not all(c[k] == params[k] for k in params)]
            async def detach(self):
                pass
        context = Context()
        with patch('src.session_observer.emit'), patch('src.cookie_capacity.backup_encrypted_cookie_database', return_value='encrypted.sqlite'):
            result = await ensure_cookie_headroom(context, '/unused')
        self.assertEqual(result['cookie_count'], 99)
        self.assertIn('__Secure-next-auth.session-token', [c['name'] for c in context.values])
        self.assertEqual(len(context.deleted), 82)


if __name__ == '__main__':
    unittest.main()
