"""Registro del histórico de solicitudes en el admin de Django."""
from django.contrib import admin

from .models import MaterialRequest


@admin.register(MaterialRequest)
class MaterialRequestAdmin(admin.ModelAdmin):
    list_display = (
        "created_at",
        "store",
        "requester",
        "items_resumen",
        "forwarded",
    )
    list_filter = ("store", "forwarded", "created_at")
    search_fields = ("store", "requester", "reason")
    readonly_fields = (
        "store",
        "requester",
        "reason",
        "items",
        "forwarded",
        "created_at",
    )
    ordering = ("-created_at",)

    @admin.display(description="Materiales")
    def items_resumen(self, obj):
        return ", ".join(
            f"{it.get('material')} (x{it.get('units')})"
            for it in (obj.items or [])
        )

    def has_add_permission(self, request):
        # Las solicitudes solo se crean desde el formulario, no a mano.
        return False
