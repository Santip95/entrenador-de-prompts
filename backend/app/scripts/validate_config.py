from app.core.config import ConfigurationError, get_settings


def main() -> None:
    try:
        get_settings().validate_runtime()
    except ConfigurationError as error:
        raise SystemExit(f"Configuración inválida: {error}") from error
    print("Configuración de base de datos válida.")


if __name__ == "__main__":
    main()
