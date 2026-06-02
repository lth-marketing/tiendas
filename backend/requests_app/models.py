"""Histórico opcional de solicitudes de material.

Se guarda un registro en SQLite por cada solicitud enviada, como copia de
seguridad para marketing. La fuente principal sigue siendo el webhook de N8N.
"""
from django.db import models


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
