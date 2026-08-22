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
