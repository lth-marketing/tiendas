"""Siembra el catálogo inicial de tiendas y materiales.

A partir de aquí el catálogo se gestiona desde el admin. Esta migración solo
crea los valores iniciales (idempotente con get_or_create).
"""
from django.db import migrations

STORES = [
    "Alfafar",
    "Gandía",
    "Finestrat",
    "Lombard",
    "Murcia",
    "Barcelona",
    "San Sebastián de los Reyes",
    "Elche",
    "Marbella",
    "Málaga",
    "Arganda del Rey",
    "Fuenlabrada",
]

MATERIALS = [
    ("tarjetas_visita", "Tarjetas de visita", "1000"),
    ("cartel_packs", "Cartel de packs", "1,2,3,4,5"),
    ("cartel_resenas", "Cartel de reseñas", "1,2,3,4,5"),
    ("peanas", "Peanas", "1-30"),
]


def seed(apps, schema_editor):
    Store = apps.get_model("requests_app", "Store")
    Material = apps.get_model("requests_app", "Material")

    for i, name in enumerate(STORES):
        Store.objects.get_or_create(name=name, defaults={"order": i})

    for i, (code, name, units_spec) in enumerate(MATERIALS):
        Material.objects.get_or_create(
            code=code,
            defaults={"name": name, "units_spec": units_spec, "order": i},
        )


def unseed(apps, schema_editor):
    # No borramos nada al revertir para no perder datos editados.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("requests_app", "0002_material_store"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
