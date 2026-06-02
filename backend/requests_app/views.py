"""Vistas de la API: catálogo y envío de solicitudes de material."""
import logging
from datetime import datetime, timedelta, timezone

import requests as http
from django.conf import settings
from django.utils import timezone as dj_timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .catalog import get_config
from .models import MaterialRequest
from .serializers import MaterialRequestSerializer

logger = logging.getLogger(__name__)

WEBHOOK_TIMEOUT_SECONDS = 15
# Ventana para avisar de materiales ya solicitados para la misma tienda.
RECENT_REQUEST_DAYS = 14


@api_view(["GET"])
def config_view(request):
    """Devuelve las tiendas y el catálogo de materiales para el frontend."""
    return Response(get_config())


def _find_recent_duplicates(store, items):
    """Materiales del pedido ya solicitados para la tienda en los últimos días.

    Solo cuenta solicitudes ya reenviadas al equipo de marketing (forwarded),
    es decir, que realmente se pidieron.
    """
    since = dj_timezone.now() - timedelta(days=RECENT_REQUEST_DAYS)
    recent = (
        MaterialRequest.objects.filter(
            store=store, forwarded=True, created_at__gte=since
        )
        .order_by("-created_at")
    )

    # Fecha del último pedido por material (recorremos de más reciente a más
    # antiguo, así la primera vez que vemos un material es la más reciente).
    last_by_material = {}
    for req in recent:
        for it in req.items or []:
            mid = it.get("material")
            if mid and mid not in last_by_material:
                last_by_material[mid] = req.created_at

    names = {m["id"]: m["name"] for m in get_config()["materials"]}
    now = dj_timezone.now()
    duplicates = []
    for it in items:
        mid = it["material"]
        if mid in last_by_material:
            last_dt = last_by_material[mid]
            duplicates.append(
                {
                    "material": mid,
                    "name": names.get(mid, mid),
                    "last_requested_at": last_dt.isoformat(),
                    "days_ago": (now - last_dt).days,
                }
            )
    return duplicates


@api_view(["POST"])
def material_request_view(request):
    """Valida la solicitud, avisa de duplicados, la guarda y la reenvía."""
    serializer = MaterialRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    # Si el usuario no ha confirmado, avisamos de materiales ya pedidos
    # recientemente para esta misma tienda (sin guardar nada todavía).
    confirm = bool(request.data.get("confirm", False))
    if not confirm:
        duplicates = _find_recent_duplicates(data["store"], data["items"])
        if duplicates:
            return Response(
                {
                    "detail": "Algunos materiales ya se han solicitado para "
                    "esta tienda en los últimos "
                    f"{RECENT_REQUEST_DAYS} días.",
                    "duplicates": duplicates,
                },
                status=status.HTTP_409_CONFLICT,
            )

    payload = {
        "store": data["store"],
        "requester": data.get("requester", ""),
        "reason": data["reason"],
        "items": data["items"],
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }

    # Histórico opcional en SQLite.
    record = MaterialRequest.objects.create(
        store=payload["store"],
        requester=payload["requester"],
        reason=payload["reason"],
        items=payload["items"],
    )

    webhook_url = settings.N8N_WEBHOOK_URL
    if not webhook_url:
        logger.warning("N8N_WEBHOOK_URL no está configurada.")
        return Response(
            {
                "detail": "El webhook de N8N aún no está configurado. "
                "La solicitud se ha guardado pero no se ha reenviado.",
                "saved": True,
                "forwarded": False,
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    try:
        resp = http.post(
            webhook_url, json=payload, timeout=WEBHOOK_TIMEOUT_SECONDS
        )
        resp.raise_for_status()
    except http.RequestException as exc:
        logger.error("Fallo al reenviar al webhook de N8N: %s", exc)
        return Response(
            {
                "detail": "No se pudo enviar la solicitud al equipo de "
                "marketing. Inténtalo de nuevo más tarde.",
                "saved": True,
                "forwarded": False,
            },
            status=status.HTTP_502_BAD_GATEWAY,
        )

    record.forwarded = True
    record.save(update_fields=["forwarded"])

    return Response(
        {"detail": "Solicitud enviada correctamente.", "forwarded": True},
        status=status.HTTP_201_CREATED,
    )
