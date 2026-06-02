"""Crea o actualiza el superusuario del admin a partir de variables de entorno.

Se ejecuta al arrancar el contenedor. Es idempotente: si el usuario ya existe,
actualiza su contraseña; si no hay credenciales definidas, no hace nada.

Variables:
    DJANGO_SUPERUSER_USERNAME
    DJANGO_SUPERUSER_PASSWORD
    DJANGO_SUPERUSER_EMAIL (opcional)
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea/actualiza el superusuario desde variables de entorno."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")

        if not username or not password:
            self.stdout.write(
                "Sin credenciales de superusuario (DJANGO_SUPERUSER_*); "
                "se omite la creación."
            )
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username, defaults={"email": email}
        )
        if email:
            user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        accion = "Creado" if created else "Actualizado"
        self.stdout.write(f"{accion} superusuario '{username}'.")
