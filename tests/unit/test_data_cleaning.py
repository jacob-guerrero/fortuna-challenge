import pandas as pd
import numpy as np
from src.core.data_cleaning import parse_mixed_dates, normalize_category, normalize_priority

def test_parse_mixed_dates_and_edge_cases():
    # Incluye formatos validos y un caso de borde (fecha corrupta y string vacio)
    raw_dates = pd.Series(["2025-03-08", "30-Jun-2025", "31/05/2026", "Fecha Invalida", ""])
    
    parsed = parse_mixed_dates(raw_dates)
    
    # 2025-03-08
    assert parsed.iloc[0].year == 2025
    assert parsed.iloc[0].month == 3
    # 30-Jun-2025
    assert parsed.iloc[1].year == 2025
    assert parsed.iloc[1].month == 6
    # 31/05/2026
    assert parsed.iloc[2].year == 2026
    assert parsed.iloc[2].month == 5
    # Corrupta -> NaT
    assert pd.isna(parsed.iloc[3])
    # Vacía -> NaT
    assert pd.isna(parsed.iloc[4])

def test_normalize_category():
    raw_cats = pd.Series(["hardware", "VACACIONES", "", "Nan", " Gestión "])
    norm = normalize_category(raw_cats)
    
    assert norm.iloc[0] == "Hardware"
    assert norm.iloc[1] == "Vacaciones"
    assert norm.iloc[2] == "Sin Clasificar" # Caso borde vacio
    assert norm.iloc[3] == "Sin Clasificar" # Caso borde string NaN
    assert norm.iloc[4] == "Gestión"

def test_normalize_priority():
    raw_prio = pd.Series(["alta", "1-Alta", "CRITICA", "No existe", "2-media"])
    norm = normalize_priority(raw_prio)
    
    assert norm.iloc[0] == "Alta"
    assert norm.iloc[1] == "Alta"
    assert norm.iloc[2] == "Crítica"
    assert norm.iloc[3] == "Sin Clasificar" # Caso borde no mapeado
    assert norm.iloc[4] == "Media"
