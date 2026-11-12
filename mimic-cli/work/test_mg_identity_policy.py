import importlib.util
from pathlib import Path

spec=importlib.util.spec_from_file_location('mg_identity_policy',Path(__file__).resolve().parents[1]/'src/browser/identity_policy.py')
policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy)


def test_production_cannot_enable_diagnostic(tmp_path,monkeypatch):
    file=tmp_path/'mode.json';file.write_text('{"additional_stealth":false}')
    monkeypatch.setattr(policy,'MODE_FILE',file)
    monkeypatch.delenv('MIMICGATE_NATIVE_BROWSER_IDENTITY',raising=False)
    assert not policy.patchright_only_mode()


def test_only_explicit_false_changes_policy(tmp_path,monkeypatch):
    file=tmp_path/'mode.json'
    monkeypatch.setattr(policy,'MODE_FILE',file)
    monkeypatch.setenv('MIMICGATE_NATIVE_BROWSER_IDENTITY','1')
    for text in ('{}','{"additional_stealth":true}','{"additional_stealth":0}','{"additional_stealth":"false"}','{"additional_stealth":false,"other":true}','x'*129,'invalid'):
        file.write_text(text)
        assert not policy.patchright_only_mode()
    file.write_text('{"additional_stealth":false}')
    assert policy.patchright_only_mode()
