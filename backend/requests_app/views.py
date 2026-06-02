"""Vistas de la API: catálogo y envío de solicitudes de material."""
import logging
from datetime import datetime, timezone

import requests as http
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .catalog import get_config
from .models import MaterialRequest
from .serializers import MaterialRequestSerializer

logger = logging.getLogger(__name__)

WEBHOOK_TIMEOUT_SECONDS = 15


@api_view(["GET"])
def config_view(request):
    """Devuelve las tiendas y el catálogo de materiales para el frontend."""
    return Response(get_config())


@api_view(["POST"])
def material_request_view(request):
    """Valida la solicitud, la guarda y la reenvía al webhook de N8N."""
    serializer = MaterialRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

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
