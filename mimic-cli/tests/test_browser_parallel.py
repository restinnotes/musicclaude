"""Pool invariants with simulated tabs; run using the existing container runtime."""
import asyncio
import unittest
from unittest.mock import patch
from src.config import Config
from src.api.browser_gate import BrowserTabPool, BrowserBusyError


class Page:
    def __init__(self):
        self.closed = False
        self.url = 'about:blank'
    def is_closed(self):
        return self.closed
    async def goto(self, url, **kwargs):
        self.url = url
    async def close(self):
        self.closed = True
    async def bring_to_front(self):
        pass


class Browser:
    def __init__(self):
        self.page = Page()
        self.context = self
        self.pages = [self.page]
        self.peak = 0
    async def new_page(self):
        await asyncio.sleep(.01)
        page = Page()
        self.pages.append(page)
        self.peak = max(self.peak, sum(not p.closed for p in self.pages) - 1)
        return page


class PoolTests(unittest.IsolatedAsyncioTestCase):
    async def test_twelve_requests_never_exceed_eight_and_idle_tabs_are_bounded(self):
        with patch.object(Config, 'MAX_CONCURRENT_REQUESTS', 8), patch.object(Config, 'MAX_ACTIVE_TABS', 8):
            browser = Browser()
            pool = BrowserTabPool(browser)
            active = set()
            peak = 0
            async def request():
                nonlocal peak
                async with pool.acquire(None) as lease:
                    self.assertNotIn(lease.page, active)
                    active.add(lease.page)
                    peak = max(peak, len(active))
                    await asyncio.sleep(.12)
                    active.remove(lease.page)
            await asyncio.gather(*(request() for _ in range(12)))
            self.assertEqual(peak, 8)
            self.assertEqual(browser.peak, 8)
            self.assertLessEqual(pool._worker_tab_count(), 2)
            self.assertEqual(pool.concurrency_stats()['in_flight'], 0)
            self.assertTrue(all(p.url == 'about:blank' for p in browser.pages if not p.closed))

    async def test_cancelled_waiter_leaks_no_slot_or_session_lock(self):
        with patch.object(Config, 'MAX_CONCURRENT_REQUESTS', 1), patch.object(Config, 'MAX_ACTIVE_TABS', 1):
            pool = BrowserTabPool(Browser())
            async with pool.acquire(None):
                async def waiter():
                    async with pool.acquire('cancelled-session'):
                        self.fail('Waiter entered while slot occupied')
                task = asyncio.create_task(waiter())
                await asyncio.sleep(.02)
                task.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await task
                self.assertFalse(pool._session_lock('cancelled-session').locked())
                self.assertEqual(pool.concurrency_stats()['waiting'], 0)
            self.assertEqual(pool.concurrency_stats()['available'], 1)

    async def test_queue_limit_and_busy_tab_protection(self):
        with patch.object(Config, 'MAX_CONCURRENT_REQUESTS', 1), patch.object(Config, 'MAX_ACTIVE_TABS', 1), patch.object(Config, 'MAX_QUEUED_REQUESTS', 0):
            pool = BrowserTabPool(Browser())
            async with pool.acquire(None):
                with self.assertRaises(BrowserBusyError):
                    async with pool.acquire(None):
                        self.fail('Full queue admitted another request')
                with self.assertRaises(BrowserBusyError):
                    await pool.close_tab_by_index(1)
                with self.assertRaises(BrowserBusyError):
                    await pool.reset_tab_by_index(1)
                with self.assertRaises(BrowserBusyError):
                    await pool.set_concurrency(8)

    async def test_capacity_failure_does_not_create_an_extra_tab(self):
        with patch.object(Config, 'MAX_CONCURRENT_REQUESTS', 2), patch.object(Config, 'MAX_ACTIVE_TABS', 1):
            browser = Browser()
            pool = BrowserTabPool(browser)
            async with pool.acquire(None):
                with self.assertRaises(BrowserBusyError):
                    async with pool.acquire(None):
                        self.fail('Tab capacity exceeded')
            self.assertEqual(browser.peak, 1)
            self.assertEqual(pool.concurrency_stats()['available'], 2)


if __name__ == '__main__':
    unittest.main()
