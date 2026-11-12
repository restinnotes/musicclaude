"""Current-turn UI error checks, independent of copy-button readiness."""
from __future__ import annotations

from src.chatgpt.standard_mode import StandardStateError


_RESPONSE_ERROR_JS = r"""() => {
    const main = document.querySelector('main');
    if (!main) return {checked: false, error: null};
    const users = Array.from(main.querySelectorAll(
        '[data-content-search-unit-key$=":user"], [data-message-author-role="user"], [data-turn="user"]'));
    const user = users.length ? users[users.length - 1] : null;
    const userTurn = user && (user.closest('[data-content-search-turn-key], article') || user);
    const patterns = [
        [/^Error in message stream[.!]?$/i, 'message_stream_error'],
        [/^(?:A )?network error (?:occurred|has occurred)[.!]?$/i, 'network_error'],
        [/^Something went wrong(?: while generating the response)?[.!]?$/i, 'response_error'],
        [/^(?:消息流出错|消息流错误|消息流中出现错误|生成回复时出错|生成回答时出错)[。！]?$/, 'message_stream_error'],
    ];
    const walker = document.createTreeWalker(main, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
        const text = (node.textContent || '').trim();
        const match = patterns.find(([pattern]) => pattern.test(text));
        if (!match) continue;
        const el = node.parentElement;
        if (!el || el.closest('pre, code, blockquote, .markdown, .prose, #prompt-textarea, [contenteditable="true"], [data-message-author-role="user"], [data-content-search-unit-key$=":user"]')) continue;
        // Old failed turns must not invalidate a later successful response.
        if (userTurn && (userTurn.contains(el) || !(userTurn.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING))) continue;
        const rect = el.getBoundingClientRect(), style = getComputedStyle(el);
        if (rect.width <= 0 || rect.height <= 0 || style.display === 'none' || style.visibility === 'hidden') continue;
        return {checked: true, error: match[1]};
    }
    return {checked: true, error: null};
}"""


async def read_response_error(page):
    try:
        state = await page.evaluate(_RESPONSE_ERROR_JS, isolated_context=True)
    except Exception as exc:
        raise StandardStateError('completion_state', 'Could not verify current response error state') from exc
    if not isinstance(state, dict) or state.get('checked') is not True:
        raise StandardStateError('completion_state', 'Invalid current response error state')
    if state.get('error') not in {None, 'message_stream_error', 'network_error', 'response_error'}:
        raise StandardStateError('completion_state', 'Unknown current response error state')
    return state


async def raise_on_response_error(page):
    state = await read_response_error(page)
    if state['error']:
        raise StandardStateError('incomplete_response', 'ChatGPT displayed a response error; no complete answer was accepted')
    return state
