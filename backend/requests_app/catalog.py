"""Acceso al catálogo de tiendas y materiales (gestionado desde el admin).

Las tiendas y los materiales viven en la base de datos (modelos Store y
Material) y se editan desde el panel de administración de Django. Cualquier
cambio se refleja de inmediato, sin necesidad de redesplegar.
"""
from .models import Material, Store


def get_config():
    """Catálogo para el frontend: tiendas y materiales activos."""
    stores = list(
        Store.objects.filter(active=True).values_list("name", flat=True)
    )
    materials = [
        {"id": m.code, "name": m.name, "units": m.units_list()}
        for m in Material.objects.filter(active=True)
    ]
    return {"stores": stores, "materials": materials}


def store_names():
    """Nombres de tiendas activas (para validación)."""
    return set(Store.objects.filter(active=True).values_list("name", flat=True))


def material_ids():
    """Códigos de materiales activos (para validación)."""
    return set(
        Material.objects.filter(active=True).values_list("code", flat=True)
    )


def allowed_units():
    """Mapa {código_material: set(unidades permitidas)} de materiales activos."""
    return {
        m.code: set(m.units_list())
        for m in Material.objects.filter(active=True)
    }
