"""Explicit, isolated diagnostic policy for additional fingerprint scripts."""
import json
import os
from pathlib import Path

MODE_FILE=Path('/app/state/.mg-patchright-only.json')


def patchright_only_mode():
    if os.environ.get('MIMICGATE_NATIVE_BROWSER_IDENTITY')!='1':
        return False
    try:
        if MODE_FILE.is_symlink() or not MODE_FILE.is_file() or MODE_FILE.stat().st_size>128:
            return False
        value=json.loads(MODE_FILE.read_text())
        return (isinstance(value,dict) and set(value)=={'additional_stealth'}
                and value['additional_stealth'] is False)
    except (OSError,ValueError):
        return False
