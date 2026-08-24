import sqlite3
from pathlib import Path
import logging

# Configuramos un formato limpio para imprimir resultados
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = BASE_DIR / "data" / "raw" / "esquema.sql"

def run_queries():
    if not SCHEMA_PATH.exists():
        logger.error(f"No se encontró el esquema en {SCHEMA_PATH}")
        return

    # Usaremos una base de datos en memoria para la prueba
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    # 1. Inicializar la DB con el esquema y datos de prueba provistos
    try:
        cursor.executescript(schema_sql)
        logger.info("✅ Base de datos en memoria inicializada con esquema.sql\n")
    except Exception as e:
        logger.error(f"Error al ejecutar el esquema SQL: {e}")
        return

    # --- Consulta 1: Agregación por área (Total de tickets por área) ---
    query_1 = """
    SELECT a.nombre AS Area, COUNT(t.id_ticket) AS Total_Tickets
    FROM areas a
    LEFT JOIN tickets t ON a.id_area = t.id_area
    GROUP BY a.id_area, a.nombre
    ORDER BY Total_Tickets DESC;
    """
    logger.info("--- Consulta 1: Agregación de Tickets por Área ---")
    for row in cursor.execute(query_1):
        logger.info(f"Área: {row[0]} | Total Tickets: {row[1]}")
        
    # --- Consulta 2: JOIN de tres tablas (Ticket, Usuario, Area) ---
    query_2 = """
    SELECT t.codigo, u.nombre AS Solicitante, a.nombre AS Area_Solicitante, t.asunto
    FROM tickets t
    JOIN usuarios u ON t.id_usuario = u.id_usuario
    JOIN areas a ON u.id_area = a.id_area
    LIMIT 5;
    """
    logger.info("\n--- Consulta 2: JOIN de 3 Tablas (Muestra de 5 tickets) ---")
    for row in cursor.execute(query_2):
        logger.info(f"Ticket: {row[0]} | Usuario: {row[1]} | Área: {row[2]} | Asunto: {row[3]}")

    # --- Consulta 3: Tickets reabiertos ---
    query_3 = """
    SELECT codigo, asunto, reaperturas, estado
    FROM tickets
    WHERE reaperturas > 0
    ORDER BY reaperturas DESC;
    """
    logger.info("\n--- Consulta 3: Tickets Reabiertos (reaperturas > 0) ---")
    rows = cursor.execute(query_3).fetchall()
    if rows:
        for row in rows:
            logger.info(f"Ticket: {row[0]} | Reaperturas: {row[2]} | Estado: {row[3]}")
    else:
        logger.info("No se encontraron tickets reabiertos en los datos de prueba del esquema.")

    conn.close()

if __name__ == "__main__":
    run_queries()
