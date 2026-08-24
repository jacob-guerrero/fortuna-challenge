from datetime import date
from src.legacy.legacy_module import filtrar_por_periodo, resumir_por_area, contar_reaperturas

# Síntoma 1: El informe mensual "siempre pierde algunos tickets".
# Causa Raíz: La condición `fc > inicio and fc < fin` era estricta y excluía los tickets creados exactamente en el día de inicio o fin.
def test_filtrar_por_periodo_incluye_extremos():
    tickets = [
        {"id": 1, "fecha_creacion": "2025-01-01"}, # Día exacto de inicio
        {"id": 2, "fecha_creacion": "2025-01-15"},
        {"id": 3, "fecha_creacion": "2025-01-31"}, # Día exacto de fin
    ]
    inicio = date(2025, 1, 1)
    fin = date(2025, 1, 31)
    
    resultado = filtrar_por_periodo(tickets, inicio, fin)
    assert len(resultado) == 3 # ANTES FALLABA: devolvía 1 porque excluía el 1 y el 31.

# Síntoma 2: Cuando se generan varios resúmenes seguidos, las cifras salen infladas.
# Causa Raíz: El argumento por defecto `acumulador={}` es mutable en Python y persiste su estado en memoria entre llamadas a la función.
def test_resumir_por_area_no_infla_cifras():
    tickets_mes_1 = [{"area": "TI"}, {"area": "TI"}]
    tickets_mes_2 = [{"area": "Ventas"}]
    
    # Primera llamada
    res1 = resumir_por_area(tickets_mes_1)
    assert res1["TI"] == 2
    
    # Segunda llamada (Aislada de la primera)
    res2 = resumir_por_area(tickets_mes_2)
    assert "TI" not in res2 # ANTES FALLABA: "TI" se quedaba guardado en el diccionario estático.
    assert res2["Ventas"] == 1

# Síntoma 3: El indicador de reaperturas da por debajo de lo real.
# Causa Raíz: Solo se contaba si el estado actual era textualmente "reabierto". Ignoraba tickets que fueron reabiertos pero que ya están Cerrados, y también ignoraba diferencias de mayúsculas ("REABIERTO"). Se debe usar el campo 'reaperturas'.
def test_contar_reaperturas():
    tickets = [
        {"id": 1, "estado": "REABIERTO", "reaperturas": "1"}, # Error de mayúsculas
        {"id": 2, "estado": "reabierto", "reaperturas": "2"}, # Normal
        {"id": 3, "estado": "Cerrado", "reaperturas": "1"},   # Fue reabierto, pero ya se cerró
        {"id": 4, "estado": "Abierto", "reaperturas": "0"},   # Nunca reabierto
    ]
    # Deberían contarse 3 tickets que han sido reabiertos en algún momento
    assert contar_reaperturas(tickets) == 3 # ANTES FALLABA: devolvía 1
