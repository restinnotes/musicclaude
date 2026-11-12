"""Apply the minimal reader fixes to the deployed source snapshot, retaining guards."""
from pathlib import Path

root=Path(__file__).parent
s=(root/'detector.py').read_text(encoding='utf-8')
old='''        return null;
    };
'''
addition='''        // New layouts put the action bar beside the assistant search unit.
        // Walk only through a container owned by this one assistant; never
        // borrow a user/older turn's Copy button.
        if (root.matches('[data-content-search-unit-key$=":assistant"]')) {
            for (let scope = root.parentElement; scope && !scope.matches('main, body'); scope = scope.parentElement) {
                const units = Array.from(scope.querySelectorAll('[data-content-search-unit-key]'));
                if (units.some(unit => unit !== root)) break;
                const matches = Array.from(scope.querySelectorAll(copySelectors.join(',')))
                    .filter(isTurnCopyButton)
                    .filter(button => Boolean(root.compareDocumentPosition(button) & Node.DOCUMENT_POSITION_FOLLOWING));
                if (matches.length) return matches.find(isVisible) || matches[matches.length - 1];
            }
        }
        return null;
    };
'''
# Both the snapshot reader and Copy action must use the same turn boundary.
needle='''        return null;
    };

    const '''
positions=[]
offset=0
while True:
    start=s.find('    const findTurnCopyButton = (root) => {',offset)
    if start<0:break
    end=s.index('        return null;\n    };',start)
    positions.append(end)
    offset=end+len(needle)
assert len(positions)==2
for pos in reversed(positions):
    s=s[:pos]+s[pos:].replace(old,addition,1)
needle='''        const selectors = role === "assistant" ? [
'''
assert s.count(needle)==2
s=s.replace(needle,needle+'''            '[data-markdown-text-style="assistant-message"]',
''')
# Capture the assistant itself: a long user prompt used to consume the entire
# 30k mainHtml diagnostic budget before the response was reached.
needle="""                    mainHtml: ((main && main.outerHTML) || '').slice(0, 30000),
"""
assert s.count(needle)==1
s=s.replace(needle,needle+'''                    assistantUnits: Array.from(document.querySelectorAll('[data-content-search-unit-key$=":assistant"], [data-message-author-role="assistant"]')).slice(-2).map(root => ({
                        html: root.outerHTML.slice(0, 250000),
                        innerText: root.innerText, textContent: root.textContent,
                        rect: {height:root.getBoundingClientRect().height, width:root.getBoundingClientRect().width},
                        display:getComputedStyle(root).display,
                        parentTail: root.parentElement?.outerHTML.slice(-16000)
                    })),
''')
needle='''        await page.evaluate("navigator.clipboard.writeText('').catch(() => {})")'''
assert s.count(needle)==1
s=s.replace(needle,'''        clipboard_cleared = await page.evaluate("navigator.clipboard.writeText('').then(() => true).catch(() => false)")''')
s=s.replace('''            if content and content.strip() and content.strip() != str(pre_clipboard).strip():''','''            if (content and content.strip()
                    and (clipboard_cleared is True or content.strip() != str(pre_clipboard).strip())):''')
(root/'detector.fixed.py').write_text(s,encoding='utf-8')
print('Built fix preserving deployed response-error guards')
guard=(root/'completion_guard.py').read_text(encoding='utf-8')
assert guard.count('pre, code, blockquote, .markdown, .prose, #prompt-textarea')==1
guard=guard.replace('pre, code, blockquote, .markdown, .prose, #prompt-textarea', 'pre, code, blockquote, .markdown, .prose, [data-markdown-text-style="assistant-message"], #prompt-textarea')
guard=guard.replace('''    const patterns = [
''','''    const patterns = [
        [/^(?:(?:We(?:'ve| have)|The system has|Our systems have) detected )?(?:suspicious (?:behaviou?r|(?:user )?activity)|unusual activity)\\b/i, 'suspicious_behavior'],
        [/^(?:检测到|发现)(?:可疑行为|可疑活动)/, 'suspicious_behavior'],
''')
guard=guard.replace("{None, 'message_stream_error', 'network_error', 'response_error'}", "{None, 'message_stream_error', 'network_error', 'response_error', 'suspicious_behavior'}")
guard=guard.replace("    if state['error']:\n", "    if state['error'] == 'suspicious_behavior':\n        raise StandardStateError('suspicious_behavior', 'ChatGPT displayed an explicit suspicious behavior warning; no further submission was made')\n    if state['error']:\n")
(root/'completion_guard.fixed.py').write_text(guard,encoding='utf-8')
