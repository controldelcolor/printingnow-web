"""WSGI para producción (Railway / gunicorn)."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'printingnow.settings')
application = get_wsgi_application()
