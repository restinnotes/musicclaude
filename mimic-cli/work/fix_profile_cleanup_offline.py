"""Prepare a source-only preservation fix; never deploy or open a live profile."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
source = root / 'src/browser/manager.py'
text = source.read_text(encoding='utf-8')
start = text.index('def _cleanup_stale_locks(data_dir: Path) -> None:')
end = text.index('\ndef _env_int(', start)
backup = root / 'backups/browser_manager_before_profile_preservation.py'
if not backup.exists():
    backup.write_text(text, encoding='utf-8')
replacement = '''def _cleanup_stale_locks(data_dir: Path) -> None:
    """Remove only stale singleton markers; preserve all browser data.

    SQLite journals and WAL are committed data, not disposable lock files.
    Never kill a browser, remove cookie database companions, or erase caches,
    service workers, localStorage or IndexedDB during startup.
    """
    profile = data_dir.resolve()
    # Refuse to touch singleton markers when this profile is still in use.
    # The production browser runs on Linux; read process metadata only.
    proc = Path('/proc')
    if proc.is_dir():
        for entry in proc.iterdir():
            if not entry.name.isdigit():
                continue
            try:
                executable = (entry / 'exe').resolve().name.lower()
                if 'chrome' not in executable and 'chromium' not in executable:
                    continue
                args = (entry / 'cmdline').read_bytes().split(b'\\0')
                profile_args = [arg.split(b'=', 1)[1].decode(errors='replace')
                                for arg in args if arg.startswith(b'--user-data-dir=')]
                if any(Path(arg).resolve() == profile for arg in profile_args):
                    raise RuntimeError('Browser profile is already in use; startup will not modify it')
            except (OSError, PermissionError):
                continue
    for name in ('SingletonLock', 'SingletonSocket', 'SingletonCookie'):
        marker = profile / name
        if marker.is_symlink() or marker.is_file():
            marker.unlink()
            log.info('Removed stale browser singleton marker: %s', name)

'''
source.write_text(text[:start] + replacement + text[end:], encoding='utf-8')
print('Prepared profile-preservation fix in local source only; production was not modified.')
