"""Carga del catálogo editable de tiendas y materiales.

El equipo de marketing edita ``backend/catalog/config.json`` para cambiar las
tiendas disponibles y el catálogo de materiales sin tocar el código.

Cada material define qué unidades se pueden solicitar, de una de estas formas:

    { "id": "tarjetas_visita", "name": "...", "units": [1000] }
    { "id": "peanas",          "name": "...", "units_range": [1, 30] }

- ``units``: lista explícita de cantidades seleccionables.
- ``units_range``: rango inclusivo [min, max] que se expande automáticamente.
"""
import json
from functools import lru_cache
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "catalog" / "config.json"


def _expand_units(material):
    """Devuelve la lista de unidades permitidas para un material."""
    if "units" in material:
        return [int(u) for u in material["units"]]
    if "units_range" in material:
        lo, hi = material["units_range"]
        return list(range(int(lo), int(hi) + 1))
    return []


@lru_cache(maxsize=1)
def _load():
    with open(CONFIG_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    stores = list(data.get("stores", []))
    materials = []
    for m in data.get("materials", []):
        materials.append(
            {
                "id": m["id"],
                "name": m["name"],
                "units": _expand_units(m),
            }
        )
    return {"stores": stores, "materials": materials}


def get_config():
    """Devuelve el catálogo completo {stores, materials} con unidades expandidas."""
    return _load()


def store_names():
    return set(_load()["stores"])


def material_ids():
    return {m["id"] for m in _load()["materials"]}


def allowed_units():
    """Mapa {material_id: set(unidades permitidas)}."""
    return {m["id"]: set(m["units"]) for m in _load()["materials"]}


def reload_config():
    """Limpia la caché (útil tras editar el config.json)."""
    _load.cache_clear()
    return _load()
