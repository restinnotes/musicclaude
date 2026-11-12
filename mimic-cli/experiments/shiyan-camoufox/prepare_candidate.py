from pathlib import Path
root = Path(__file__).resolve().parent
browser = root / 'src' / 'browser'
manager = browser / 'manager.py'
(browser / 'chromium_manager.py').write_bytes(manager.read_bytes())
manager.write_text('from src.browser.camoufox_manager import BrowserManager\n', encoding='utf-8')
human = browser / 'human.py'
source = human.read_text(encoding='utf-8')
needle = '    # Strategy 1: execCommand'
assert needle in source
addition = '''    if Config.BROWSER_CHANNEL == 'camoufox':
        # Match the reference project's trusted per-character input and pauses.
        # Shift+Enter preserves line breaks without submitting the composer.
        await element.press('Control+A')
        await element.press('Backspace')
        for idx, character in enumerate(text):
            if character == '\\n':
                await element.press('Shift+Enter')
            else:
                await element.press_sequentially(character, delay=0)
            if (idx + 1) % random.randint(5, 8) == 0 and idx + 1 < len(text):
                await asyncio.sleep(random.uniform(.12, .30))
            else:
                await asyncio.sleep(random.uniform(.03, .12))
        return

'''
source = source.replace(needle, addition + needle, 1)
human.write_text(source, encoding='utf-8')
compile(source, str(human), 'exec')
print('Candidate uses baseline MimicGate source with isolated Camoufox and reference typing delays.')
