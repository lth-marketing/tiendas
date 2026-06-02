"""Carga del catálogo editable de tiendas y materiales.

El equipo de marketing edita ``backend/catalog/config.json`` para cambiar las
tiendas disponibles y el catálogo de materiales sin tocar el código.
"""
import json
from functools import lru_cache
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent.parent / "catalog" / "config.json"


@lru_cache(maxsize=1)
def _load():
    with open(CONFIG_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    stores = list(data.get("stores", []))
    materials = list(data.get("materials", []))
    return {"stores": stores, "materials": materials}


def get_config():
    """Devuelve el catálogo completo {stores, materials}."""
    return _load()


def store_names():
    return set(_load()["stores"])


def material_ids():
    return {m["id"] for m in _load()["materials"]}


def reload_config():
    """Limpia la caché (útil tras editar el config.json)."""
    _load.cache_clear()
    return _load()
