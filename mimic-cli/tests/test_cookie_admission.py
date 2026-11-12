import asyncio
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from src.api.browser_gate import BrowserTabPool
from src.config import Config

ID = '22222222-2222-2222-2222-222222222222'

class Context:
    pages = []
    async def cookies(self):
        return []

class AdmissionTests(unittest.IsolatedAsyncioTestCase):
    async def test_drain_then_recycle_before_next_admission_and_protect_saved_session(self):
        browser = SimpleNamespace(context=Context())
        pool = BrowserTabPool(browser)
        pool._urls['saved-session'] = 'https://chatgpt.com/c/' + ID + '?temporary-chat=true'
        count = 40
        calls = []
        async def cookies(context):
            return [{}] * count
        async def recycle(context, profile, **kwargs):
            nonlocal count
            calls.append((pool._in_flight, kwargs))
            count = 99
        with patch.object(Config, 'MAX_CONCURRENT_REQUESTS', 10), patch('src.cookie_capacity.site_cookies', cookies), patch('src.cookie_capacity.ensure_cookie_headroom', recycle), patch('src.session_observer.emit'):
            await pool._acquire_slot()
            count = 160
            waiter = asyncio.create_task(pool._acquire_slot())
            await asyncio.sleep(.03)
            self.assertFalse(waiter.done())
            self.assertTrue(pool.concurrency_stats()['cookie_maintenance'])
            self.assertEqual(calls, [])
            pool._release_slot()
            await asyncio.wait_for(waiter, 1)
            self.assertEqual(calls[0][0], 0)
            self.assertIn(ID, calls[0][1]['protected_ids'])
            self.assertEqual(calls[0][1]['recycle_at'], 136)
            self.assertEqual(pool._in_flight, 1)
            pool._release_slot()
            self.assertFalse(pool.concurrency_stats()['cookie_maintenance'])
            self.assertTrue(pool._idle.is_set())

    async def test_twenty_requests_still_reach_ten_parallel_generations(self):
        from test_browser_parallel import Browser
        with patch.object(Config, 'MAX_CONCURRENT_REQUESTS', 10), patch.object(Config, 'MAX_ACTIVE_TABS', 10):
            pool = BrowserTabPool(Browser())
            active = 0
            peak = 0
            async def request():
                nonlocal active, peak
                async with pool.acquire(None):
                    active += 1
                    peak = max(peak, active)
                    await asyncio.sleep(.15)
                    active -= 1
            await asyncio.gather(*(request() for _ in range(20)))
            self.assertEqual(peak, 10)
            self.assertEqual(pool._in_flight, 0)
            self.assertEqual(pool._semaphore._value, 10)

    async def test_cancelled_maintenance_wait_releases_reserved_slot(self):
        pool = BrowserTabPool(SimpleNamespace(context=Context()))
        original = pool._semaphore._value
        count = 20
        async def cookies(context):
            return [{}] * count
        with patch('src.cookie_capacity.site_cookies', cookies), patch('src.session_observer.emit'):
            await pool._acquire_slot()
            count = 160
            task = asyncio.create_task(pool._acquire_slot())
            await asyncio.sleep(.03)
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
            self.assertEqual(pool._in_flight, 1)
            self.assertEqual(pool._semaphore._value, original - 1)
            self.assertEqual(pool._waiting_requests, 0)
            self.assertFalse(pool._cookie_maintenance)
            pool._release_slot()
            self.assertEqual(pool._semaphore._value, original)

    async def test_saved_temporary_cookie_pair_is_not_deleted(self):
        from src.cookie_capacity import ensure_cookie_headroom
        from test_cookie_capacity import cookie
        values = [cookie('__Secure-next-auth.session-token'), cookie('history_off_' + ID), cookie('conv_key_' + ID)]
        for i in range(90):
            guid = f'{i:08x}-1111-1111-1111-111111111111'
            values.extend([cookie('history_off_' + guid), cookie('conv_key_' + guid)])
        deleted = []
        class Store:
            pages = [SimpleNamespace(url='https://chatgpt.com/')]
            async def cookies(self, *args):
                return list(values)
            async def new_cdp_session(self, page):
                return self
            async def send(self, method, params):
                deleted.append(params['name'])
                values[:] = [c for c in values if not all(c[k] == params[k] for k in params)]
            async def detach(self):
                pass
        with patch('src.session_observer.emit'), patch('src.cookie_capacity.backup_encrypted_cookie_database', return_value='encrypted.sqlite'):
            result = await ensure_cookie_headroom(Store(), '/unused', protected_ids={ID})
        self.assertLess(result['cookie_count'], 100)
        self.assertNotIn('history_off_' + ID, deleted)
        self.assertNotIn('conv_key_' + ID, deleted)
        self.assertIn('__Secure-next-auth.session-token', [c['name'] for c in values])

    async def test_cleanup_failure_leaks_no_slot_and_admits_no_generation(self):
        pool = BrowserTabPool(SimpleNamespace(context=Context()))
        original = pool._semaphore._value
        async def cookies(context):
            return [{}] * 160
        async def recycle(*args, **kwargs):
            raise RuntimeError('No safe candidates')
        with patch('src.cookie_capacity.site_cookies', cookies), patch('src.cookie_capacity.ensure_cookie_headroom', recycle), patch('src.session_observer.emit'):
            with self.assertRaises(RuntimeError):
                await pool._acquire_slot()
            self.assertEqual(pool._in_flight, 0)
            self.assertEqual(pool._semaphore._value, original)
            self.assertEqual(pool._waiting_requests, 0)
            self.assertFalse(pool._cookie_maintenance)

if __name__ == '__main__':
    unittest.main()
