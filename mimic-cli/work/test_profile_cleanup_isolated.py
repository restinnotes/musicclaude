"""Reproduce inherited startup data loss with a fake SQLite cookie database.

All files are inside an owned /tmp fixture. pkill is mocked and never runs.
The fake cookie value is public; no live browser/profile is inspected.
"""
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import tempfile
import importlib.util
import sys
from unittest.mock import patch
from src.browser.manager import _cleanup_stale_locks

safe_source = len(sys.argv) > 1 and sys.argv[1] == '--safe-source'
if safe_source:
    spec = importlib.util.spec_from_file_location('safe_manager_fixture', '/app/fixture_manager_safe.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    _cleanup_stale_locks = module._cleanup_stale_locks


with tempfile.TemporaryDirectory(prefix='mg-wal-fixture-', dir='/tmp') as directory:
    root = Path(directory).resolve()
    if root.parent != Path('/tmp') or not root.name.startswith('mg-wal-fixture-'):
        raise RuntimeError('Unexpected fixture path')
    original = root / 'original' / 'Default'
    copied = root / 'copied' / 'Default'
    original.mkdir(parents=True)
    copied.mkdir(parents=True)
    database = original / 'Cookies'
    writer = sqlite3.connect(database)
    writer.execute('create table cookies(name text, value text)')
    writer.commit()
    writer.execute('pragma journal_mode=wal')
    writer.execute('pragma wal_autocheckpoint=0')
    writer.execute("insert into cookies values ('fixture_session', 'PUBLIC_FAKE_COOKIE')")
    writer.commit()
    for name in ['Cookies', 'Cookies-wal', 'Cookies-shm']:
        shutil.copy2(original / name, copied / name)
    retained_paths = ['Local Storage/fixture-data','IndexedDB/fixture-data','Service Worker/fixture-data','Cache/fixture-data']
    for relative in retained_paths:
        path = copied / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('PUBLIC_FAKE_PROFILE_DATA')
    def row_count():
        reader = sqlite3.connect('file:' + str(copied / 'Cookies') + '?mode=ro', uri=True)
        try:
            return reader.execute('select count(*) from cookies').fetchone()[0]
        finally:
            reader.close()
    before = row_count()
    with patch('subprocess.run', return_value=subprocess.CompletedProcess([], 1)) as command:
        _cleanup_stale_locks(root / 'copied')
    wal_removed_before_read = not (copied / 'Cookies-wal').exists()
    after = row_count()
    writer.close()
    print(json.dumps({'production_profile_touched':False, 'real_credentials_used':False,
        'implementation':'local_preservation_fix' if safe_source else 'deployed_inherited_cleanup',
        'pkill_really_executed':False, 'mocked_pkill_calls':command.call_count,
        'fake_cookie_rows_before_cleanup':before,'fake_cookie_rows_after_cleanup':after,
        'wal_removed_before_database_read':wal_removed_before_read,
        'all_other_profile_data_retained':all((copied / relative).exists() for relative in retained_paths),
        'inherited_startup_cleanup_can_destroy_uncheckpointed_cookies':before == 1 and after == 0},indent=2))
