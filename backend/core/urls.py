"""Rutas raíz del proyecto.

Expone la API bajo /api/ y delega el resto de rutas al SPA de React
(index.html), de modo que el enrutado del cliente funcione correctamente.
"""
from django.urls import include, path, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path("api/", include("requests_app.urls")),
    # Catch-all: sirve el index.html del build de React para cualquier ruta
    # que no sea de la API ni un archivo estático.
    re_path(r"^.*$", TemplateView.as_view(template_name="index.html")),
]
