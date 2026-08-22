import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

MESES_ESP = {
    'Ene': '01', 'Feb': '02', 'Mar': '03', 'Abr': '04', 'May': '05', 'Jun': '06',
    'Jul': '07', 'Ago': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dic': '12'
}

def parse_mixed_dates(date_series: pd.Series) -> pd.Series:
    """
    Normaliza fechas de múltiples formatos a datetime.
    Maneja: YYYY-MM-DD, DD/MM/YYYY, DD-MMM-YYYY.
    Caso de borde: Valores no parseables retornan pd.NaT.
    """
    if date_series.empty:
        return date_series

    s = date_series.astype(str).str.strip().replace('nan', '')
    
    # Manejar formato DD-MMM-YYYY
    for mes_letras, mes_num in MESES_ESP.items():
        s = s.str.replace(f"-{mes_letras}-", f"-{mes_num}-", case=False, regex=False)
    
    # Usar dayfirst=True porque formatos como 12/05/2026 suelen referirse a DD/MM
    return pd.to_datetime(s, format='mixed', dayfirst=True, errors='coerce')

def normalize_category(category_series: pd.Series) -> pd.Series:
    """
    Normaliza categorías a Title Case.
    Caso de borde: Campos nulos o vacíos se clasifican como 'Sin Clasificar'.
    """
    s = category_series.astype(str).str.strip().str.title()
    s = s.replace(['Nan', 'None', '', 'Null'], 'Sin Clasificar')
    return s.fillna('Sin Clasificar')

def normalize_priority(priority_series: pd.Series) -> pd.Series:
    """
    Limpia las prioridades removiendo prefijos numéricos ('1-Alta' -> 'Alta').
    Caso de borde: Valores irreconocibles van a 'Sin Clasificar'.
    """
    s = priority_series.astype(str).str.strip().str.lower()
    s = s.str.replace(r'^\d+-?', '', regex=True)
    
    mapping = {
        'alta': 'Alta',
        'media': 'Media',
        'baja': 'Baja',
        'critica': 'Crítica',
        'crítica': 'Crítica'
    }
    return s.map(mapping).fillna('Sin Clasificar')
