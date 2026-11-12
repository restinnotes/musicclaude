"""Verified one-shot UI policy for the standalone MimicGate CLI.

Only visible DOM controls are read. No cookies, storage or network auth data.
"""
from __future__ import annotations

import asyncio
import re
import time
from urllib.parse import parse_qs, urlparse


class StandardStateError(RuntimeError):
    def __init__(self, kind: str, message: str):
        super().__init__(message)
        self.kind = kind


class StandardModeMixin:
    async def read_standard_composer_text(self):
        editor = await self._visible_control([
            self._page.get_by_role("textbox", name="Ask ChatGPT", exact=True),
            self._page.locator('#prompt-textarea:visible'),
            self._page.locator('[contenteditable="true"]:visible'),
        ])
        if editor is None:
            raise StandardStateError("ui_selector", "The visible prompt editor was not found")
        # innerText includes CSS paragraph spacing in the current ProseMirror
        # layout (one blank line renders as several newlines). Serialize actual
        # text/BR/paragraph nodes so verification preserves the original lines.
        return await editor.evaluate(r"""e => {
            if (e.tagName === 'TEXTAREA') return e.value;
            const read = node => {
                if (node.nodeType === Node.TEXT_NODE) return node.textContent;
                if (node.nodeType !== Node.ELEMENT_NODE) return '';
                if (node.tagName === 'BR') return node.classList.contains('ProseMirror-trailingBreak') ? '' : '\n';
                return Array.from(node.childNodes).map(read).join('');
            };
            const children = Array.from(e.children);
            if (children.length && children.every(node => node.tagName === 'P')) {
                return children.map(read).join('\n');
            }
            return e.innerText || e.textContent || '';
        }""")

    async def _visible_control(self, candidates):
        for locator in candidates:
            for index in range(await locator.count()):
                item = locator.nth(index)
                if await item.is_visible():
                    return item
        return None

    def _temporary_controls(self, active: bool):
        names = (r"^(Turn off temporary chat|Exit temporary chat|关闭临时聊天|退出临时聊天)$"
                 if active else r"^(Temporary chat|Turn on temporary chat|临时聊天|开启临时聊天)$")
        testids = ("temporary-chat-active", "temporary-chat-toggle") if active else ("temporary-chat-button", "temporary-chat-toggle")
        # A generic toggle is only activation evidence when aria-pressed=true.
        state = '[aria-pressed="true"]' if active else ''
        return [self._page.get_by_role("button", name=re.compile(names, re.I)),
                self._page.locator(f'[data-testid="{testids[0]}"]'),
                self._page.locator(f'[data-testid="{testids[1]}"]{state}')]

    async def temporary_chat_state(self):
        parsed = urlparse(self._page.url)
        query_active = parse_qs(parsed.query).get("temporary-chat") == ["true"]
        control = await self._visible_control(self._temporary_controls(True))
        label = (await control.get_attribute("aria-label") or await control.inner_text()).strip() if control else None
        # URL alone never authorizes a send: the active UI control is mandatory.
        return {"verified": bool(control and query_active), "url_flag": query_active,
                "active_control": label, "verified_at": time.time()}

    async def ensure_temporary_chat(self):
        state = await self.temporary_chat_state()
        if state["verified"]:
            return state
        control = await self._visible_control(self._temporary_controls(False))
        if control is None:
            raise StandardStateError("ui_selector", "Temporary Chat activation control was not found")
        await control.click(timeout=10000)
        for _ in range(50):
            state = await self.temporary_chat_state()
            if state["verified"]:
                return state
            await asyncio.sleep(.2)
        raise StandardStateError("temporary_state", "Temporary Chat active UI and URL were not both confirmed")

    def _personalization_controls(self):
        return [self._page.get_by_role("button", name=re.compile(
                    r"^(Personalized|Unpersonalized|Non-personalized|个性化|非个性化|未个性化)$", re.I)),
                self._page.locator('[data-testid="personalization-toggle"]'),
                self._page.get_by_role("button", name=re.compile(r"^Personalization$", re.I))]

    async def _personalization_state(self, allow_change=False):
        trigger = await self._visible_control(self._personalization_controls())
        if trigger is None:
            raise StandardStateError("ui_selector", "Personalization menu control was not found")
        await trigger.click(timeout=10000)
        negative = re.compile(r"^(Unpersonalized|Non-personalized|非个性化|未个性化)(?:\b|\s|$)", re.I)
        try:
            candidates = [self._page.get_by_role("menuitemradio", name=negative),
                          self._page.get_by_role("radio", name=negative),
                          self._page.locator('[data-testid="unpersonalized-option"]')]
            row = None
            for _ in range(20):
                row = await self._visible_control(candidates)
                if row:
                    break
                await asyncio.sleep(.1)
            if row is None:
                raise StandardStateError("ui_selector", "Unpersonalized option was not found")
            checked = await row.get_attribute("aria-checked") == "true"
            if not checked and allow_change:
                await row.click(timeout=10000)
                await asyncio.sleep(.2)
                # Reopen and verify a fresh checked radio; clicking is not proof.
                return await self._personalization_state(False)
            if not checked:
                raise StandardStateError("personalization_state", "Unpersonalized radio is not selected")
            label = (await row.inner_text()).splitlines()[0].strip()
        finally:
            await self._page.keyboard.press("Escape")
        trigger = await self._visible_control(self._personalization_controls())
        closed_label = (await trigger.inner_text()).strip() if trigger else ""
        if not negative.search(closed_label):
            raise StandardStateError("personalization_state", "Closed personalization control is not Unpersonalized")
        return {"verified": True, "selected_label": label, "aria_checked": True,
                "closed_label": closed_label, "verified_at": time.time()}

    async def ensure_non_personalized(self):
        return await self._personalization_state(allow_change=True)

    async def verify_standard_states(self, stage):
        temporary = await self.temporary_chat_state()
        self._standard_evidence["temporary_chat"] = temporary
        if not temporary["verified"]:
            raise StandardStateError("temporary_state", "Temporary Chat verification failed before submission")
        self._standard_evidence["non_personalized"] = await self._personalization_state(False)
        self._standard_evidence["verification_stage"] = stage

    async def prepare_standard_chat(self):
        self._standard_one_shot = True
        self._standard_evidence = {}
        self._standard_evidence["preparation_started_at"] = time.time()
        from src.chatgpt.detector import page_has_stop_button
        if await page_has_stop_button(self._page):
            raise StandardStateError("busy", "The browser still has an active generation; no new prompt was sent")
        # Reset the existing page, then activate Temporary via the actual UI.
        # No conversation-store recovery and no reuse of a previous temporary turn.
        await self._page.bring_to_front()
        await self._page.goto("https://chatgpt.com/", wait_until="domcontentloaded", timeout=45000)
        await self._wait_for_chat_input()
        for _ in range(50):
            if await self._visible_control(self._temporary_controls(False) + self._temporary_controls(True)):
                break
            await asyncio.sleep(.2)
        self._standard_evidence["temporary_chat"] = await self.ensure_temporary_chat()
        self._standard_evidence["non_personalized"] = await self.ensure_non_personalized()
        await self.ensure_model("gpt-5.6-sol", reasoning_effort="xhigh", verification_stage="standard_preparation")
        self._standard_evidence["model"] = self._last_yi_selection_evidence.copy()
        await self.verify_standard_states("standard_preparation")
