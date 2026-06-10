"""Modelos: catálogo (tiendas y materiales) e histórico de solicitudes.

El catálogo se gestiona desde el admin de Django. Cada solicitud enviada se
guarda como copia de seguridad; la fuente principal sigue siendo N8N.
"""
from django.core.exceptions import ValidationError
from django.db import models


def parse_units_spec(spec):
    """Convierte una especificación de unidades en una lista de enteros.

    Admite números sueltos, listas separadas por comas y rangos con guion:
        "1000"        -> [1000]
        "1,2,3,4,5"   -> [1, 2, 3, 4, 5]
        "1-30"        -> [1, 2, ..., 30]
        "1,2,5-7"     -> [1, 2, 5, 6, 7]
    """
    units = []
    for token in str(spec).split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            lo, hi = token.split("-", 1)
            units.extend(range(int(lo), int(hi) + 1))
        else:
            units.append(int(token))
    # Elimina duplicados conservando el orden.
    seen = set()
    result = []
    for u in units:
        if u not in seen:
            seen.add(u)
            result.append(u)
    return result


class Store(models.Model):
    name = models.CharField("Nombre", max_length=120, unique=True)
    order = models.PositiveIntegerField("Orden", default=0)
    active = models.BooleanField("Activa", default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Tienda"
        verbose_name_plural = "Tiendas"

    def __str__(self):
        return self.name


class Material(models.Model):
    code = models.SlugField(
        "Código",
        max_length=60,
        unique=True,
        help_text="Identificador interno que se envía al webhook (ej. peanas).",
    )
    name = models.CharField("Nombre", max_length=120)
    units_spec = models.CharField(
        "Unidades",
        max_length=200,
        help_text="Números, comas y/o rangos. Ej: 1000  ·  1,2,3,4,5  ·  1-30",
    )
    order = models.PositiveIntegerField("Orden", default=0)
    active = models.BooleanField("Activo", default=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "Material"
        verbose_name_plural = "Materiales"

    def __str__(self):
        return self.name

    def units_list(self):
        return parse_units_spec(self.units_spec)

    def clean(self):
        try:
            units = parse_units_spec(self.units_spec)
        except (ValueError, TypeError):
            raise ValidationError(
                {
                    "units_spec": "Formato no válido. Usa números, comas y "
                    "rangos (ej. 1,2,3 o 1-30)."
                }
            )
        if not units:
            raise ValidationError(
                {"units_spec": "Debes indicar al menos una unidad."}
            )


class MaterialRequest(models.Model):
    store = models.CharField("Tienda", max_length=120)
    requester = models.CharField("Comercial", max_length=120, blank=True)
    reason = models.TextField("Motivo")
    items = models.JSONField("Materiales", default=list)
    forwarded = models.BooleanField("Reenviado al webhook", default=False)
    created_at = models.DateTimeField("Fecha", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Solicitud de material"
        verbose_name_plural = "Solicitudes de material"

    def __str__(self):
        return f"{self.store} - {self.created_at:%Y-%m-%d %H:%M}"
