"""Configuración ficticia: no conecta ni despliega servicios."""
import secrets
import pytest
from app.core.config import Settings,ConfigurationError

def valid_values():
    return dict(app_env='production',postgres_password='ficticia-sin-conexion',csrf_signing_key=secrets.token_urlsafe(48),review_signing_key=secrets.token_urlsafe(48),alert_fingerprint_key=secrets.token_urlsafe(48),session_cookie_secure=True,public_origin='https://demo.example.invalid',smtp_starttls=True,smtp_user='ficticio',smtp_password='ficticia-sin-smtp')

def test_valid_production_configuration_without_network():
    s=Settings(_env_file=None,**valid_values());s.validate_access();s.validate_reviews()

@pytest.mark.parametrize('changes',[
    {'session_cookie_secure':False},{'public_origin':'http://demo.example.invalid'},
    {'smtp_starttls':False},{'smtp_user':''},{'smtp_password':None},
    {'seed_demo_data':True},{'log_request_bodies':True},{'postgres_password':None},
    {'csrf_signing_key':None},{'review_signing_key':None},{'alert_fingerprint_key':None},
    {'alert_fingerprint_key_version':0},{'csrf_signing_key':'example'+'x'*40},
    {'review_signing_key':'example'+'x'*40},{'alert_fingerprint_key':'ejemplo'+'x'*40},
    {'password_min_length':8},{'password_max_length':64},
])
def test_unsafe_production_configuration_is_rejected(changes):
    values=valid_values();values.update(changes);s=Settings(_env_file=None,**values)
    with pytest.raises(ConfigurationError):s.validate_access();s.validate_reviews()

def test_production_keys_must_be_independent():
    values=valid_values();values['review_signing_key']=values['csrf_signing_key']
    with pytest.raises(ConfigurationError):Settings(_env_file=None,**values).validate_reviews()
