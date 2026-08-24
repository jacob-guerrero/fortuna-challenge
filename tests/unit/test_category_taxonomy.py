import pytest

from src.core.category_taxonomy import canonicalize_category


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Gestión de Accesos", "Accesos"),
        ("equipos", "Hardware"),
        ("RED", "Conectividad"),
        ("Órdenes de Compra", "Compras"),
        ("desconocida", "Sin Clasificar"),
    ],
)
def test_canonicaliza_variantes_historicas(raw: str, expected: str):
    assert canonicalize_category(raw) == expected
