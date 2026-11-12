from pathlib import Path

root = Path(__file__).parent
source = (root / 'detector_live_1819.py').read_text(encoding='utf-8')
unsafe = '''        if (root.matches('[data-content-search-unit-key$=":assistant"]')) {
            const turn = root.closest('[data-content-search-turn-key]');
            const matches = Array.from(turn?.querySelectorAll('button[aria-label="Copy" i], button[aria-label="Copy response" i]') || [])
                .filter(isTurnCopyButton);
            if (matches.length) return matches[matches.length - 1];
        }
'''
assert source.count(unsafe) == 2
source = source.replace(unsafe, '')
assert source.count('    if (!btn) {\n') == 1
source = source.replace('    if (!btn) {\n', '''    if (!btn && !latest.root.matches('[data-content-search-unit-key$=":assistant"]')) {
''')
# The remaining sibling walk already checks that every search unit is owned
# by this assistant, and requires buttons to follow the assistant in DOM order.
(root / 'detector_copy_boundary_fixed.py').write_text(source, encoding='utf-8')
print('Removed two unsafe whole-turn lookups; scoped sibling walk retained')
