from django.urls import path

from . import views

urlpatterns = [
    path("config/", views.config_view, name="config"),
    path(
        "material-requests/",
        views.material_request_view,
        name="material-request",
    ),
]
