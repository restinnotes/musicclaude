from inspect_mg_offline_settings import safe_name, shape
import json


def test_account_ids_are_not_returned_in_setting_names():
    assert safe_name('oai/recommendation/user-AbCdEfGhIjKlMnOp') == 'oai/recommendation/user-<id>'
    assert safe_name('account/0123456789abcdef0123456789abcdef') == 'account/<id>'
    assert safe_name('someone@example.com') == '<redacted-key>'


def test_setting_values_are_shapes_without_credentials_or_text():
    text=json.dumps(shape({'sessionToken':'SECRET-TOKEN','email':'SECRET@HOST',
        'isPersonalized':False,'model':'SECRET-MODEL','draft':['SECRET-TEXT']}))
    assert 'SECRET' not in text
    assert 'false' in text


def test_structure_is_bounded():
    result=shape({str(i):str(i) for i in range(1000)})
    assert len(result['fields'])==32
    assert result['field_count']==1000
