"""Official Chrome for Testing download into a diagnostic container only."""
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request
import zipfile

VERSION = '154.0.8037.92'
URL = 'https://storage.googleapis.com/chrome-for-testing-public/' + VERSION + '/linux64/chrome-linux64.zip'
DESTINATION = Path('/opt/mg-diagnostic/chrome154')
ARCHIVE = Path('/tmp/mg-chrome154-official.zip')
DESTINATION.mkdir(parents=True, exist_ok=False)
digest = hashlib.sha256()
with urllib.request.urlopen(URL, timeout=60) as response, ARCHIVE.open('wb') as file:
    while chunk := response.read(1024 * 1024):
        digest.update(chunk)
        file.write(chunk)
with zipfile.ZipFile(ARCHIVE) as archive:
    for entry in archive.infolist():
        target = (DESTINATION / entry.filename).resolve()
        assert target.is_relative_to(DESTINATION.resolve())
        archive.extract(entry, DESTINATION)
        if not entry.is_dir():
            mode = (entry.external_attr >> 16) & 0o777
            if mode:
                target.chmod(mode)
binary = DESTINATION / 'chrome-linux64/chrome'
binary.chmod(0o755)
version = subprocess.run([str(binary), '--version'], capture_output=True, text=True, check=True).stdout.strip()
assert VERSION in version
print(json.dumps({'official_download_url': URL, 'archive_sha256': digest.hexdigest(),
    'binary_version': version, 'binary_path': str(binary), 'browser_launched': False,
    'production_browser_modified': False}))
ARCHIVE.unlink()
