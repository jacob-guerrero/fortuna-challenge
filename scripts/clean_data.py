import logging
from pathlib import Path
import pandas as pd
from src.core.data_cleaning import parse_mixed_dates, normalize_category, normalize_priority

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "tickets_historicos.csv"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
CLEAN_DATA_PATH = PROCESSED_DIR / "tickets_limpios.csv"
SUMMARY_PATH = PROCESSED_DIR / "resumen.csv"

def clean_data(input_path: Path, output_clean: Path, output_summary: Path):
    if not input_path.exists():
        logger.error(f"El archivo {input_path} no existe. (Caso de borde)")
        raise FileNotFoundError(f"No se encontró {input_path}")
    
    logger.info("Cargando datos raw...")
    df = pd.read_csv(input_path)

    if df.empty:
        raise ValueError("El archivo CSV está vacío.")

    required_columns = {'id', 'fecha_creacion', 'fecha_cierre', 'area', 'categoria', 'prioridad'}
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(f"El CSV no contiene las columnas requeridas: {', '.join(sorted(missing_columns))}")

    # 1. Eliminar duplicados
    initial_len = len(df)
    df = df.drop_duplicates(subset=['id'], keep='first')
    logger.info(f"Se eliminaron {initial_len - len(df)} registros duplicados.")

    # 2. Manejo de valores vacíos
    if 'reaperturas' in df.columns:
        df['reaperturas'] = pd.to_numeric(df['reaperturas'], errors='coerce').fillna(0).astype(int)

    # 3. Normalización de Fechas
    df['fecha_creacion'] = parse_mixed_dates(df['fecha_creacion'])
    df['fecha_cierre'] = parse_mixed_dates(df['fecha_cierre'])
    
    # Fechas de creación inválidas
    invalid_dates = df['fecha_creacion'].isna()
    if invalid_dates.any():
        logger.warning(f"Descartando {invalid_dates.sum()} registros por fecha de creación corrupta.")
        df = df[~invalid_dates]

    # Inconsistencias (fecha cierre < fecha creación)
    invalid_closure = (df['fecha_cierre'].notna()) & (df['fecha_cierre'] < df['fecha_creacion'])
    if invalid_closure.any():
        logger.warning(f"Anulando fecha de cierre en {invalid_closure.sum()} registros (cierre anterior a creación).")
        df.loc[invalid_closure, 'fecha_cierre'] = pd.NaT

    # 4. Normalización Categóricas
    df['categoria'] = normalize_category(df['categoria'])
    df['prioridad'] = normalize_priority(df['prioridad'])
    df['area'] = df['area'].fillna('').astype(str).str.strip().replace('', 'Sin área')

    # 5. Guardar archivos
    output_clean.parent.mkdir(parents=True, exist_ok=True)
    output_summary.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_clean, index=False)
    logger.info(f"Archivo limpio en {output_clean}")

    # 6. Generar resumen
    resumen = df.groupby(['area', 'prioridad']).size().reset_index(name='cantidad_tickets')
    resumen = resumen.sort_values(by=['area', 'cantidad_tickets'], ascending=[True, False])
    resumen.to_csv(output_summary, index=False)
    logger.info(f"Resumen guardado en {output_summary}")

if __name__ == "__main__":
    clean_data(RAW_DATA_PATH, CLEAN_DATA_PATH, SUMMARY_PATH)
