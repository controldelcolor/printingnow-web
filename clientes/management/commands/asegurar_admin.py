"""python manage.py asegurar_admin

Crea o actualiza el superusuario usando las variables de entorno:
  DJANGO_SUPERUSER_USERNAME
  DJANGO_SUPERUSER_EMAIL
  DJANGO_SUPERUSER_PASSWORD
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Crea o actualiza el superusuario desde variables de entorno.'

    def handle(self, *args, **opts):
        User = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', '').strip()
        email    = os.environ.get('DJANGO_SUPERUSER_EMAIL', '').strip()
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '').strip()

        if not username or not password:
            self.stdout.write(self.style.WARNING(
                'DJANGO_SUPERUSER_USERNAME o DJANGO_SUPERUSER_PASSWORD no están '
                'definidas. No se creará ningún admin.'
            ))
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email, 'is_staff': True, 'is_superuser': True},
        )

        user.email = email or user.email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(
                f'✓ Superusuario "{username}" CREADO.'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'✓ Superusuario "{username}" actualizado (contraseña reseteada).'
            ))
