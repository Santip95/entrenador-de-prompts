# Entrenador de prompts

Aplicación web en español para practicar la redacción de prompts, revisar sus componentes y comparar versiones. Proyecto de Trabajo Final de Grado de la Licenciatura en Informática.

La revisión utiliza reglas determinísticas. No ejecuta los prompts ni consulta modelos generativos. El porcentaje expresa cumplimiento de los criterios configurados; no mide calidad semántica ni demuestra aprendizaje.

## Funciones

- Prácticas por desafío del catálogo u objetivo propio.
- Redacción guiada y libre. En el modo libre, el usuario declara y confirma los componentes; el sistema no los infiere del texto.
- Revisión de tarea, contexto, destinatario, restricciones, formato y posibles datos sensibles.
- Alertas de correo, teléfono y documento según patrones configurados, más secuencias de exactamente 7, 8 o 10 dígitos ASCII consecutivos. Los patrones no detectan toda la información sensible.
- Guardado de versiones, resultados, comparación, historial y progreso por configuración comparable.
- Registro, ingreso, recuperación de contraseña por correo, cierre y revocación de sesiones.
- Administración de desafíos, criterios, versiones de reglas y cuentas.
- Borrado de prácticas y cuenta, diario cifrado de borrados, respaldos cifrados y restauración aislada.

## Estado y alcance

Las etapas 01–06 y la ampliación del detector numérico están implementadas. Motor **1.1.0**; esquema Alembic **20261107_0004**.

Los informes del entorno original de Windows registran **358 pruebas aprobadas**, corpus **33/33**, tipos y build del frontend correctos. La ejecución diaria del respaldo del **9 de noviembre de 2026** y un ensayo con la sesión de Windows cerrada tienen evidencia específica. Son resultados de esos ensayos; no garantizan ejecuciones futuras ni certifican una instalación nueva.

**NF-02 no está aprobado.** El registro histórico detectó dos textos ficticios en el cuerpo visible de un POST a un hostname ajeno a la aplicación. Una repetición acotada no reprodujo la coincidencia. No se reconstruyó la solicitud exacta ni se acreditó su atribución, ruta física o tratamiento. No se modificó el antivirus para aprobar la prueba.

También están pendientes la operación real en Backblaze B2, la custodia externa de claves, la revisión externa de las reglas y la validación educativa con participantes. La revisión manual de accesibilidad básica está registrada; no equivale a una certificación WCAG.

- [Ampliación numérica y regresión de 358 pruebas](docs/evidencias/EVIDENCIA_DETECTOR_NUMERICO.md).
- [Ejecución diaria observada](docs/evidencias/EVIDENCIA_DISPARADOR_DIARIO_20261109.md).
- [Contraste y límites de NF-02](docs/evidencias/EVIDENCIA_NF02_CONTRASTE.md).
- [Matriz de requisitos y casos de etapa 06](docs/evidencias/INFORME_FINAL_ETAPA06.md).

## Instalación y ejecución

El entorno documentado es **Windows x64 y PowerShell**, con Python 3.11, Node.js/npm y PostgreSQL 18. No requiere Docker ni WSL. Las versiones concretas y los pasos de preparación están en la [guía de instalación](docs/INSTALACION_WINDOWS.md).

**En una instalación nueva, completar primero esa guía.** El repositorio no incluye `.env`, contraseñas, bases de datos, claves, respaldos, `.venv`, `node_modules` ni los ejecutables de Mailpit/age. Conserva los archivos de dependencias y los instaladores locales de esas herramientas.

Después de instalar y configurar, abrir tres terminales PowerShell desde la raíz.

**Mailpit** — reutilizarlo si ya está abierto:

```powershell
& .\local-data\mailpit\mailpit.exe --listen 127.0.0.1:8025 --smtp 127.0.0.1:1025 --disable-version-check --smtp-disable-rdns --quiet
```

**Backend**:

```powershell
Push-Location .\backend
& ..\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --no-access-log --no-proxy-headers
```

**Frontend**:

```powershell
Push-Location .\frontend
& "$env:ProgramFiles\nodejs\npm.cmd" run dev
```

| Servicio | Dirección local |
|---|---|
| Aplicación | <http://127.0.0.1:5173> |
| Correo de pruebas | <http://127.0.0.1:8025> |
| Estado básico de la API | <http://127.0.0.1:8000/health> |

Detener cada proceso con **Ctrl+C** en su terminal. PostgreSQL funciona como servicio; no necesita una ventana de pgAdmin. Usar datos ficticios para las comprobaciones.

## Pruebas

El corpus y las pruebas del motor no necesitan PostgreSQL ni servicios abiertos:

```powershell
Push-Location .\backend
& ..\.venv\Scripts\python.exe -m app.scripts.check_motor
& ..\.venv\Scripts\python.exe -m pytest tests/motor -q --tb=short
Pop-Location
```

La suite completa requiere bases de pruebas separadas, Mailpit y herramientas de operación. Ver [PRUEBAS.md](docs/PRUEBAS.md) antes de ejecutarla.

## Organización

| Ruta | Contenido |
|---|---|
| `backend/` | API FastAPI, motor, persistencia, migraciones y pruebas. |
| `frontend/` | Interfaz React/TypeScript y configuración de Vite. |
| `scripts/` | Preparación de Windows, comprobaciones y operación local. |
| `seeds/` | Catálogos y reglas iniciales, sin cuentas ni contraseñas. |
| `fixtures/` | Casos ficticios y resultados esperados. |
| `docs/tecnica/` | Contratos funcionales, API, datos, seguridad y decisiones. |
| `docs/operacion/` | Respaldos, recuperación y procedimientos de Windows. |
| `docs/evidencias/` | Informes de ensayos realizados y sus limitaciones. |
| `docs/diseno/` | Diagramas editables y referencias visuales históricas. |
| `docs/historico/` | Seguimiento y guías de las etapas anteriores. |

[Índice de documentación](docs/README.md) · [Reglas para contribuir al código](AGENTS.md) · [Seguridad](docs/tecnica/SECURITY.md)

## Nombre y configuración local

El nombre de esta distribución es `entrenador-de-prompts`. No cambia los nombres de las bases PostgreSQL ni los directorios privados de claves.

Si ya existe una instalación funcional en otra carpeta, conservarla hasta verificar la nueva. Renombrar su carpeta requiere recrear `.venv` y actualizar las rutas absolutas de la tarea programada; extraer este ZIP no realiza esos cambios. Una segunda copia tampoco crea automáticamente bases, claves o diarios independientes.

Esta distribución no incluye el historial `.git` del equipo de desarrollo. Los informes conservan fechas y referencias de los ensayos originales. Preparar esta copia no publica ni despliega el sistema.
