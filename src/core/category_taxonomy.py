import unicodedata


CANONICAL_CATEGORIES = {
    "Accesos",
    "Aplicaciones",
    "Capacitación",
    "Compras",
    "Conectividad",
    "Hardware",
    "Incidentes",
    "Informes",
    "Nómina",
    "Otros",
    "Vacaciones",
    "Viáticos",
}


def canonicalize_category(value: object) -> str:
    """Mapea variantes históricas al catálogo operativo de doce categorías."""
    text = "" if value is None else str(value).strip().lower()
    normalized = "".join(
        character
        for character in unicodedata.normalize("NFD", text)
        if unicodedata.category(character) != "Mn"
    )
    aliases = {
        "acceso": "Accesos",
        "accesos": "Accesos",
        "gestion de accesos": "Accesos",
        "aplicaciones": "Aplicaciones",
        "software": "Aplicaciones",
        "capacitacion": "Capacitación",
        "compras": "Compras",
        "ordenes de compra": "Compras",
        "conectividad": "Conectividad",
        "red": "Conectividad",
        "hardware": "Hardware",
        "equipos": "Hardware",
        "incidente": "Incidentes",
        "incidentes": "Incidentes",
        "informes": "Informes",
        "reportes": "Informes",
        "nomina": "Nómina",
        "otros": "Otros",
        "vacaciones": "Vacaciones",
        "viaticos": "Viáticos",
    }
    return aliases.get(normalized, "Sin Clasificar")
