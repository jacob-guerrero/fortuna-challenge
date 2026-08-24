# Mesa de Ayuda Inteligente (La Fortuna S.A.)

Este repositorio contiene la solución a la Prueba Técnica de Nivelación para la familia de cargos IA. La solución ha sido construida siguiendo los principios de Clean Architecture y priorizando el manejo de errores, la trazabilidad y la escalabilidad (apuntando al perfil Middle II).

---

## Etapa 1: Fundamentos (Completada)

### ¿Qué hace esta etapa?
1. **Limpieza de Datos (`scripts/clean_data.py`)**: Lee un histórico de tickets en CSV con ruido (fechas en distintos formatos, valores vacíos), normaliza la información (fechas a ISO 8601, categorías a Title Case), elimina duplicados por ID y corrige inconsistencias del negocio (ej. fechas de cierre anteriores a creación). Genera un CSV limpio y un reporte agrupado por área y prioridad.
2. **Consumo de API Segura (`scripts/api_consumption.py`)**: Consume un servicio simulado que falla intencionalmente. Implementa un cliente robusto en `src/infrastructure/external_api/mock_client.py` con políticas de reintento exponencial (`tenacity`) para tolerar el 12% de caídas (HTTP 500), límites de tasa (HTTP 429) y latencias de hasta 2.5s.
3. **Consultas SQL (`scripts/sql_queries.py`)**: Inicializa una base de datos SQLite en memoria a partir de `esquema.sql` y ejecuta tres consultas analíticas (Agregación, JOIN de 3 tablas y tickets reabiertos).

### Instalación y Ejecución

**1. Preparar el entorno virtual (Recomendado Python 3.10+)**
```bash
python -m venv venv
# Activar en Windows
.\venv\Scripts\activate
# Activar en Linux/Mac
source venv/bin/activate
```

**2. Instalar dependencias**
```bash
pip install -r requirements.txt
```

**3. Ejecutar Scripts de la Etapa 1**
```bash
# Limpieza de datos (Lee de data/raw y escribe en data/processed)
python -m scripts.clean_data

# Levantar el servicio Mock (en otra terminal)
python -m uvicorn servicio_mock.app:app --port 8080

# Ejecutar consumo de API
python -m scripts.api_consumption

# Ejecutar Consultas SQL
python -m scripts.sql_queries
```

**4. Ejecutar Pruebas Unitarias**
```bash
pytest tests/unit/ -v
```

### Supuestos y Decisiones
- **Fechas**: Para fechas tipo `DD/MM/YYYY`, se asume que el formato europeo (`dayfirst=True`) es la norma. Si una fecha está corrupta al punto de no ser parseable, se anula y la fila se descarta o reasigna según la regla de negocio.
- **API Mock**: La URL y el token se leen de `.env`, que está ignorado por Git. Copie `.env.example` a `.env` y configure `MOCK_API_TOKEN` con el token de prueba indicado en `servicio_mock/README.md`.
- **SQL**: Se utilizó SQLite en memoria para la validación y evitar que se requiera una instancia de motor pesado como PostgreSQL/MySQL.

### Qué quedó fuera (Etapa 1)
- Por ahora, las métricas y logs no están siendo enviados a un sistema externo, solo se emiten por consola.
- No se realizan validaciones adicionales de formato (no presentes en la prueba) en campos diferentes a los mencionados en el Anexo A.

---

## Etapa 2: Autonomía e integración

La API propia expone tres operaciones sobre solicitudes: crear (`POST /tickets/`), consultar por identificador (`GET /tickets/{id}`) y listar con filtros de estado y área (`GET /tickets/?estado=Abierto&area=Tecnología`). Todas las respuestas de error tienen el contrato `error`, `message` y `path`.

La clasificación depende de `LLMPort`, no de un proveedor concreto. En desarrollo, `AI_PROVIDER=dummy` permite ejecutar una clasificación determinista sin credenciales. Para un proveedor compatible con OpenAI, configure en `.env` `AI_PROVIDER=openai_compatible`, `AI_API_BASE_URL` y `AI_API_KEY`; el adaptador aplica timeout de 5 segundos y hasta tres intentos ante timeout, red, 429 o 5xx. Si el proveedor falla definitivamente, la solicitud se crea en modo degradado, marcada para clasificación manual.

Ejecute la API con:

```bash
python -m uvicorn src.api.main:app --reload --port 8000
```

La documentación interactiva queda disponible en `http://localhost:8000/docs`. Las pruebas de la API y del modo degradado se ejecutan con `pytest -v`.

---

## Etapa 3: RAG, calidad y observabilidad

La ingesta indexa las políticas PDF en ChromaDB local con metadatos de documento, página y sección:

```bash
python -m scripts.ingest_policies
```

El endpoint `POST /politicas/consultas` recupera los tres fragmentos más relevantes y solo responde si alguno supera el umbral de similitud configurado. La respuesta incluye las fuentes; sin evidencia, devuelve `No encontré información vigente para esto.`. La base vectorial es generada y está ignorada por Git.

`GET /observabilidad/resumen` expone el acumulado local de latencia, tokens y costo estimado. La integración continua ejecuta `ruff check` y `pytest` en cada envío. Consulte [el informe de seguridad](docs/security_report.md) y [el estándar de IA](docs/ai_engineering_standard.md).

---

## Etapas 4: Arquitectura y orquestación

La etapa 4 añade un webhook idempotente y un flujo mínimo de orquestación:
clasificación, recuperación de evidencia RAG, respuesta con citas o escalamiento
y notificación al segundo sistema. El diseño de datos, ambientes, costo y ADRs
está en [docs/architecture](docs/architecture/).

---

## Etapas 5: Estrategia técnica y evaluación

La etapa 5 define cuándo usar ML clásico, RAG/LLM o automatización tradicional.
Incluye un conjunto de referencia, evaluación con umbrales en CI, baseline
TF-IDF + regresión logística, comparación de enfoques y revisión del PR en
[docs/n5](docs/n5/).

---

## Qué quedó fuera del alcance (Etapas 2 a 5)

En aras de entregar una solución robusta y bien fundamentada dentro de la ventana de tiempo estipulada, se tomaron decisiones conscientes para delimitar el alcance:
- **Etapa 2 (Opcional):** No se desarrolló la interfaz gráfica en Angular. El esfuerzo se centró netamente en la solidez del backend, el manejo de errores y los patrones arquitectónicos.
- **Etapa 3:** El pipeline de Integración Continua (CI) se abstrae a la ejecución mediante scripts (`ruff` y `pytest`). No se configuró un pipeline YAML real en un proveedor cloud (ej. GitHub Actions).
- **Etapa 4:** La orquestación completa con un Message Broker (Kafka/RabbitMQ) para soportar los 10.000 tickets asíncronos quedó a nivel de **Diseño (ADR-001)**. Se documentó cómo hacerlo, pero no se provisionó la infraestructura de colas para mantener el proyecto local y portable.
- **Etapa 5:** El modelo clásico de Machine Learning (Baseline) se desarrolló a nivel de validación comparativa, pero no se integró funcionalmente como endpoint activo en la API REST de FastAPI, priorizando el uso del LLM.

---

## Declaración de uso de asistentes de IA

De acuerdo con las reglas del reto y como parte integral de la ingeniería de software moderna, se utilizaron asistentes de Inteligencia Artificial para acelerar el desarrollo.

- **Herramientas utilizadas:** Codex (como motor de razonamiento / *brain*) y Antigravity / Gemini (como asistentes de generación de código / *workers*).
- **Rol del desarrollador vs. Rol de la IA:** Todo el diseño del sistema, la toma de decisiones técnicas (implementación de Clean Architecture, inyección de dependencias, definición del Modo Degradado) y la dirección del proyecto. **fueron realizados enteramente por mí**. Los asistentes de IA operaron estrictamente como herramientas subordinadas para materializar mis directrices.
- **¿Qué generé y conservé tal cual?** Esqueletos de clases (Pydantic), estructuras base de archivos Markdown y el *boilerplate* (andamiaje) estándar de los endpoints en FastAPI.
- **¿Qué generé, tuve que corregir y por qué?** Las IA tendían a acoplar la conexión de la base de datos vectorial (ChromaDB) directamente en la capa web. Lo corregí refactorizando ese código hacia los *Casos de Uso* para respetar la Inversión de Dependencias (SOLID). Errores de objetivos y alcances.
- **¿Qué decidí escribir a mano y por qué?** La lógica de resiliencia (`tenacity`), los *System Prompts* restrictivos del RAG y el manejo del Modo Degradado, ya que la precisión en estos componentes es crítica para evitar alucinaciones.
- **¿Cómo verifiqué lo generado?** Mediante la suite de pruebas automatizadas (`pytest`), validación manual intensiva a través de Swagger UI y revisión minuciosa línea por línea del código integrado.
