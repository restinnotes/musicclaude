"""Offline regressions for response evidence on independently leased tabs."""
import unittest
import copy
from types import SimpleNamespace

from src.chatgpt.client import ChatGPTClient


class Page:
    def __init__(self):
        self.handlers = []

    def on(self, event, callback):
        assert event == 'response'
        self.handlers.append(callback)

    def respond(self, number=0):
        response = SimpleNamespace(
            url=f'https://chatgpt.com/backend-api/conversation/{number}?secret=HIDDEN', status=200)
        for callback in self.handlers:
            callback(response)


class WorkerLoggingTests(unittest.TestCase):
    def test_worker_receives_own_evidence_and_base_stays_separate(self):
        base_page, worker_page = Page(), Page()
        base = ChatGPTClient(base_page)
        worker = base.bind_page(worker_page)
        worker_page.respond()
        self.assertEqual(len(worker._backend_events_snapshot()), 1)
        self.assertEqual(base._backend_events_snapshot(), [])
        self.assertNotIn('HIDDEN', str(worker._backend_events_snapshot()))
        base_page.respond()
        self.assertEqual(len(base._backend_events_snapshot()), 1)
        self.assertEqual(len(worker._backend_events_snapshot()), 1)

    def test_reused_worker_has_one_listener_and_shared_bounded_evidence(self):
        base = ChatGPTClient(Page())
        page = Page()
        first, second = base.bind_page(page), base.bind_page(page)
        for number in range(100):
            page.respond(number)
        self.assertEqual(len(page.handlers), 1)
        self.assertEqual(len(first._recent_backend_events), 80)
        self.assertEqual(first._backend_events_snapshot(), second._backend_events_snapshot())
        self.assertEqual(len(second._backend_events_snapshot()), 40)

    def test_two_workers_do_not_mix_events(self):
        base = ChatGPTClient(Page())
        a, b = Page(), Page()
        wa, wb = base.bind_page(a), base.bind_page(b)
        a.respond(1)
        b.respond(2)
        self.assertTrue(wa._backend_events_snapshot()[0]['url'].endswith('/1'))
        self.assertTrue(wb._backend_events_snapshot()[0]['url'].endswith('/2'))

    def test_request_copy_keeps_listener_after_clearing_prior_evidence(self):
        base = ChatGPTClient(Page())
        page = Page()
        worker = base.bind_page(page)
        page.respond(1)
        request = copy.copy(base.bind_page(page))
        request._recent_backend_events.clear()
        page.respond(2)
        self.assertEqual(len(request._backend_events_snapshot()), 1)
        self.assertTrue(request._backend_events_snapshot()[0]['url'].endswith('/2'))


if __name__ == '__main__':
    unittest.main()
