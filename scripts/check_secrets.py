"""Comprueba que los secretos locales no aparezcan en archivos versionables."""

from pathlib import Path
import subprocess
import sys
import os
import json

from dotenv import dotenv_values


def main():
    staged='--staged' in sys.argv
    root = Path(__file__).resolve().parents[1]
    git = ["git", "-c", f"safe.directory={root.as_posix()}"]
    files = subprocess.check_output(
        [*git, "ls-files", "--cached", *([] if staged else ["--others", "--exclude-standard"]), "-z"], cwd=root,
    ).decode("utf-8").split("\0")
    names = {"POSTGRES_PASSWORD", "MIGRATION_PASSWORD", "SMTP_PASSWORD", "REVIEW_SIGNING_KEY", "CSRF_SIGNING_KEY",
             "ALERT_FINGERPRINT_KEY", "B2_APPLICATION_KEY", "DATABASE_URL", "TEST_DATABASE_URL"}
    local = dotenv_values(root / ".env")
    secrets = [value.encode() for name, value in local.items() if name in names and value]
    if os.environ.get('LOCALAPPDATA'):
        demo=Path(os.environ['LOCALAPPDATA'])/'EntrenadorPromptsDemo/credenciales.json'
        if demo.is_file():
            secrets.extend(account['password'].encode() for account in json.loads(demo.read_text(encoding='utf-8')).values())
    for variable in ('DELETION_JOURNAL_KEY_FILE','BACKUP_IDENTITY_FILE'):
        path=Path(local[variable]) if local.get(variable) else None
        if path and path.is_file():
            secrets.extend(line for line in path.read_bytes().splitlines() if line and not line.startswith((b'#',b'age1')))
    bad = []
    for name in filter(None, files):
        path = root / name
        data=subprocess.check_output([*git,'show',':'+name],cwd=root) if staged else path.read_bytes() if path.is_file() else b''
        if name == ".env" or any(secret in data for secret in secrets):
            bad.append(name)
    if bad:
        print("Revisar archivos con valores locales (sin mostrar valores):", ", ".join(bad))
        return 1
    print("Secretos locales ausentes del índice preparado." if staged else "Secretos locales ausentes de los archivos versionables; .env excluido.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
