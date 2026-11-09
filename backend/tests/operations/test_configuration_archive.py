from pathlib import Path
import pytest
from app.core.config import ConfigurationError
from app.operations.configuration_archive import export_configuration,verify_configuration,extract_configuration
from test_backups import setup_settings

def test_configuration_encrypted_roundtrip_and_no_overwrite(tmp_path):
    settings,journal=setup_settings(tmp_path)
    source=tmp_path/'source.env';source.write_text('POSTGRES_PASSWORD=ficticia-exclusiva-de-prueba\n',encoding='utf-8')
    destination=tmp_path/'recovery';path=export_configuration(settings,destination,source)
    assert b'ficticia-exclusiva' not in path.read_bytes()
    assert verify_configuration(settings,path)['archivos_verificados']==4
    recovered=tmp_path/'recovered';result=extract_configuration(settings,path,recovered)
    assert result['activo_modificado'] is False
    assert (recovered/'local.env').read_bytes()==source.read_bytes()
    assert (recovered/'journal.key').read_bytes()==journal.key_file.read_bytes()
    assert (recovered/'journal-state/borrados.fernet').read_bytes()==journal.path.read_bytes()
    with pytest.raises(ConfigurationError):extract_configuration(settings,path,recovered)

def test_configuration_export_rejects_repo_backup_and_keys_destinations(tmp_path):
    settings,journal=setup_settings(tmp_path)
    from app.core.config import ROOT_DIR
    for path in (ROOT_DIR,settings.backup_directory,Path(settings.backup_identity_file).parent):
        with pytest.raises(ConfigurationError):export_configuration(settings,path)
