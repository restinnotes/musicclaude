"""
Human-like behavior simulation — typing, clicking, delays, mouse movement.

Makes browser automation look organic to anti-bot systems.
"""

from __future__ import annotations

import asyncio
import random
import re

from patchright.async_api import Page

from src.config import Config
from src.log import setup_logging

log = setup_logging("human")


async def random_delay(min_ms: int | None = None, max_ms: int | None = None) -> None:
    """Sleep for a random duration (milliseconds)."""
    lo = min_ms or Config.THINKING_PAUSE_MIN
    hi = max_ms or Config.THINKING_PAUSE_MAX
    ms = random.randint(lo, hi)
    log.debug(f"Random delay: {ms}ms")
    await asyncio.sleep(ms / 1000)


async def human_type(page: Page, selector: str, text: str) -> None:
    """
    Insert text into a contenteditable input field.

    Uses execCommand('insertText') which fires proper beforeinput/input
    events that ProseMirror-based editors (like ChatGPT's) require.
    Falls back to clipboard paste, then keyboard.insert_text().
    """
    element = page.locator(selector).first
    await element.click()
    await asyncio.sleep(random.uniform(0.1, 0.25))

    # Clear any stale text in the input before inserting new text
    try:
        await element.evaluate(
            """(el) => {
                    el.focus();
                    // Select all existing text and delete it
                    document.execCommand('selectAll', false, null);
                    document.execCommand('delete', false, null);
            }""",
        )
        await asyncio.sleep(0.05)
    except Exception as e:
        log.debug(f"Could not clear input: {e}")

    log.debug(f"Inserting {len(text)} chars into {selector}")

    if Config.BROWSER_CHANNEL == 'camoufox':
        # Match the reference project's trusted per-character input and pauses.
        # Shift+Enter preserves line breaks without submitting the composer.
        await element.press('Control+A')
        await element.press('Backspace')
        prefix_guard = None
        for idx, character in enumerate(text):
            # ProseMirror turns "1. " into an ordered list, including after
            # Undo + native insert_text. A temporary leading character keeps
            # that rule from matching; delete it by native keys immediately
            # after the numbered prefix. The verified final text is unchanged.
            line_start = text.rfind('\n', 0, idx) + 1
            if idx == line_start:
                prefix = re.match(r'\d+\. ', text[idx:])
                if prefix:
                    prefix_guard = (idx + len(prefix.group(0)) - 1, len(prefix.group(0)))
                    await element.press_sequentially('x', delay=0)
            if character == '\n':
                await element.press('Shift+Enter')
            else:
                await element.press_sequentially(character, delay=0)
            if prefix_guard and idx == prefix_guard[0]:
                for _ in range(prefix_guard[1] + 1):
                    await element.press('ArrowLeft')
                await element.press('Delete')
                for _ in range(prefix_guard[1]):
                    await element.press('ArrowRight')
                prefix_guard = None
            if (idx + 1) % random.randint(5, 8) == 0 and idx + 1 < len(text):
                await asyncio.sleep(random.uniform(.12, .30))
            else:
                await asyncio.sleep(random.uniform(.03, .12))
        return

    # Strategy 1: execCommand — fires beforeinput + input events
    try:
        result = await element.evaluate(
            """(el, text) => {
                el.focus();
                const ok = document.execCommand('insertText', false, text);
                return ok ? 'ok' : 'failed';
            }""",
            text,
        )
        if result == "ok":
            log.debug("Insert via execCommand succeeded")
            return
        log.debug(f"execCommand result: {result}")
    except Exception as e:
        log.debug(f"execCommand failed: {e}")

    # Strategy 2: Clipboard paste event
    try:
        result = await element.evaluate(
            """(el, text) => {
                el.focus();
                const dt = new DataTransfer();
                dt.setData('text/plain', text);
                const event = new ClipboardEvent('paste', {
                    bubbles: true, cancelable: true, clipboardData: dt
                });
                el.dispatchEvent(event);
                return 'ok';
            }""",
            text,
        )
        if result == "ok":
            log.debug("Insert via paste event succeeded")
            return
    except Exception as e:
        log.debug(f"Paste event failed: {e}")

    # Strategy 3: keyboard.insert_text() — legacy fallback
    log.debug("Falling back to keyboard.insert_text()")
    await page.keyboard.insert_text(text)
    log.debug("insert_text complete")

    # Verify text was actually inserted
    await asyncio.sleep(0.1)
    try:
        actual = await element.evaluate(
            """(el) => {
                return el ? (el.innerText || el.textContent || '').trim() : '';
            }""",
        )
        if not actual:
            log.warning(f"Text insertion verification failed — input appears empty after all strategies")
        elif len(actual) < len(text) * 0.5:
            log.warning(f"Text insertion may be partial — expected {len(text)} chars, got {len(actual)}")
        else:
            log.debug(f"Text insertion verified: {len(actual)} chars in input")
    except Exception as e:
        log.debug(f"Could not verify text insertion: {e}")


async def human_click(page: Page, selector: str) -> None:
    """
    Click an element with human-like behavior:
    1. Hover over element (triggers mouseover)
    2. Brief pause
    3. Click

    Uses .first to handle cases where multiple elements match.
    """
    element = page.locator(selector).first
    await element.hover()
    await asyncio.sleep(random.uniform(0.05, 0.15))
    await element.click()
    log.debug(f"Human-clicked: {selector}")


async def idle_mouse_movement(page: Page) -> None:
    """
    Simulate idle mouse movement — small random movements to look alive.
    Call this periodically while waiting for responses.
    """
    try:
        viewport = page.viewport_size
        if viewport:
            x = random.randint(100, viewport["width"] - 100)
            y = random.randint(100, viewport["height"] - 100)
            await page.mouse.move(x, y, steps=random.randint(5, 15))
            log.debug(f"Idle mouse move to ({x}, {y})")
    except Exception:
        pass  # Non-critical — don't break the flow


async def thinking_pause() -> None:
    """Simulate a 'thinking' pause before the user starts typing."""
    ms = random.randint(Config.THINKING_PAUSE_MIN, Config.THINKING_PAUSE_MAX)
    log.debug(f"Thinking pause: {ms}ms")
    await asyncio.sleep(ms / 1000)
