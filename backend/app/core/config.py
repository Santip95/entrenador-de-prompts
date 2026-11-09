from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL, make_url


ROOT_DIR = Path(__file__).resolve().parents[3]


class ConfigurationError(RuntimeError):
    """Indica una configuración incompleta sin revelar secretos."""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
    )

    app_env: str = "development"
    app_name: str = "Entrenador de Prompts"
    api_prefix: str = "/api/v1"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    public_origin: str = "http://127.0.0.1:5173"

    database_url: SecretStr | None = Field(default=None, validation_alias="DATABASE_URL")
    postgres_host: str = "127.0.0.1"
    postgres_port: int = 5432
    postgres_db: str = "entrenador_prompts"
    postgres_test_db: str = "entrenador_prompts_test"
    postgres_user: str = "entrenador_app"
    postgres_password: SecretStr | None = None
    migration_user: str = "entrenador_migracion"
    migration_password: SecretStr | None = None
    csrf_signing_key: SecretStr | None = None
    review_signing_key: SecretStr | None = None
    alert_fingerprint_key: SecretStr | None = None
    alert_fingerprint_key_version: int = 1
    app_timezone: str = "America/Argentina/Cordoba"
    deletion_journal_location: str = ''
    deletion_journal_key_file: str = ''
    deletion_journal_anchor_file: str = ''
    backup_directory: str = ''
    backup_encryption_recipient: str = ''
    backup_identity_file: str = ''
    b2_bucket: str = ''
    b2_bucket_id: str = ''
    b2_key_id: str = ''
    b2_application_key: SecretStr | None = None
    b2_enabled: bool = False

    def validate_reviews(self):
        keys = [self.review_signing_key, self.alert_fingerprint_key, self.csrf_signing_key]
        values = [k.get_secret_value().encode() if k else b"" for k in keys]
        if any(len(k) < 32 or k.lower().startswith((b'example',b'ejemplo')) for k in values) or len(set(values)) != 3 or self.alert_fingerprint_key_version < 1:
            raise ConfigurationError("Configurar claves independientes de revisión, huellas y CSRF (mínimo 32 bytes) y versión de huellas positiva.")
    session_cookie_name: str = "ep_session"
    session_cookie_secure: bool = False
    session_cookie_samesite: str = "lax"
    session_idle_minutes: int = 30
    session_absolute_hours: int = 8
    login_max_failures: int = 5
    login_window_minutes: int = 15
    login_block_minutes: int = 15
    password_reset_minutes: int = 15
    smtp_host: str = "127.0.0.1"
    smtp_port: int = 1025
    smtp_user: str = ""
    smtp_password: SecretStr | None = None
    smtp_starttls: bool = False
    mail_from: str = "no-reply@example.invalid"
    password_min_length: int = 15
    password_max_length: int = 128
    argon2_memory_kib: int = 65536
    argon2_time_cost: int = 3
    argon2_parallelism: int = 1
    log_request_bodies: bool = False
    seed_demo_data: bool = False
    test_database_url: SecretStr | None = Field(
        default=None, validation_alias="TEST_DATABASE_URL"
    )

    def resolved_database_url(self) -> str:
        if self.database_url is not None and self.database_url.get_secret_value():
            return self.database_url.get_secret_value()
        if self.postgres_password is None or not self.postgres_password.get_secret_value():
            raise ConfigurationError(
                "Falta configurar POSTGRES_PASSWORD o DATABASE_URL en .env."
            )
        return self._url(self.postgres_db)

    def _url(self, database: str) -> str:
        return URL.create(
            "postgresql+psycopg", username=self.postgres_user,
            password=self.postgres_password.get_secret_value(),
            host=self.postgres_host, port=self.postgres_port, database=database,
        ).render_as_string(hide_password=False)

    def resolved_test_database_url(self) -> str:
        if self.test_database_url is not None and self.test_database_url.get_secret_value():
            url = self.test_database_url.get_secret_value()
            self._validate_url(url, test=True)
            return url
        if self.postgres_password is None or not self.postgres_password.get_secret_value():
            raise ConfigurationError(
                "Falta configurar POSTGRES_PASSWORD o TEST_DATABASE_URL en .env."
            )
        url = self._url(self.postgres_test_db)
        self._validate_url(url, test=True)
        return url

    def resolved_migration_url(self, *, test: bool = False) -> str:
        if self.migration_password is None or not self.migration_password.get_secret_value():
            raise ConfigurationError("Falta configurar MIGRATION_PASSWORD en .env.")
        if self.migration_user != "entrenador_migracion":
            raise ConfigurationError("MIGRATION_USER debe ser entrenador_migracion.")
        value = URL.create("postgresql+psycopg", username=self.migration_user,
                           password=self.migration_password.get_secret_value(),
                           host=self.postgres_host, port=self.postgres_port,
                           database=self.postgres_test_db if test else self.postgres_db,
                           ).render_as_string(hide_password=False)
        self._validate_url(value, test=test)
        return value

    def validate_access(self) -> None:
        self.validate_runtime()
        if (self.password_min_length, self.password_max_length) != (15, 128):
            raise ConfigurationError("La política implementada requiere PASSWORD_MIN_LENGTH=15 y PASSWORD_MAX_LENGTH=128.")
        if self.argon2_memory_kib < 19456 or self.argon2_time_cost < 2 or self.argon2_parallelism < 1:
            raise ConfigurationError("Argon2id requiere al menos 19456 KiB, tiempo 2 y paralelismo 1.")
        if self.log_request_bodies:
            raise ConfigurationError("No se permite registrar cuerpos de solicitudes.")
        if (self.session_idle_minutes, self.session_absolute_hours, self.login_max_failures,
            self.login_window_minutes, self.login_block_minutes, self.password_reset_minutes,
            self.session_cookie_samesite) != (30, 8, 5, 15, 15, 15, "lax"):
            raise ConfigurationError("Los límites de acceso deben coincidir con SECURITY.md: 30 min/8 h, 5 fallos/15 min, bloqueo y recuperación de 15 min, SameSite=lax.")
        key = self.csrf_signing_key.get_secret_value() if self.csrf_signing_key else ""
        if len(key.encode("utf-8")) < 32 or key.lower().startswith(("example", "ejemplo")):
            raise ConfigurationError("Configurar CSRF_SIGNING_KEY aleatoria de al menos 32 bytes.")
        if self.app_env == "production":
            if self.seed_demo_data:
                raise ConfigurationError("Producción no permite datos de demostración.")
            if not self.session_cookie_secure or not self.public_origin.startswith("https://"):
                raise ConfigurationError("Producción requiere HTTPS y cookie Secure.")
            if not self.smtp_starttls or not self.smtp_user or not self.smtp_password:
                raise ConfigurationError("Producción requiere SMTP autenticado con TLS.")
        elif self.smtp_host != "127.0.0.1" or self.smtp_port != 1025:
            raise ConfigurationError("El correo local requiere Mailpit en 127.0.0.1:1025.")

    def _validate_url(self, value: str, *, test: bool = False) -> None:
        try:
            url = make_url(value)
            valid = url.drivername == "postgresql+psycopg"
            if self.app_env in {"development", "test"}:
                valid = valid and url.host == "127.0.0.1" and url.port == 5432
                allowed={"entrenador_prompts", "entrenador_prompts_test"}
                if self.app_env=='test':
                    allowed|={'entrenador_prompts_ops_test','entrenador_prompts_restore_test','entrenador_prompts_contingencia_test','entrenador_prompts_demo'}
                valid = valid and url.database in allowed
            if test:
                valid = valid and url.database == "entrenador_prompts_test"
            valid = valid and url.username not in {None, "postgres"} and bool(url.password)
        except Exception:
            valid = False
        if not valid:
            raise ConfigurationError(
                "Conexión inválida: usá PostgreSQL, el rol propio y las bases del proyecto; "
                "las pruebas requieren entrenador_prompts_test en 127.0.0.1:5432."
            )

    def validate_runtime(self) -> None:
        if self.app_env not in {"development", "test", "production"}:
            raise ConfigurationError("APP_ENV debe ser development, test o production.")
        if self.postgres_host != "127.0.0.1" and self.app_env in {"development", "test"}:
            raise ConfigurationError("En desarrollo y pruebas POSTGRES_HOST debe ser 127.0.0.1.")
        self._validate_url(self.resolved_database_url())


@lru_cache
def get_settings() -> Settings:
    return Settings()
