from django.apps import AppConfig


class ClientesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clientes'
    verbose_name = 'Clientes Printing Now'

    def ready(self):
        """Se ejecuta cuando Django terminó de cargar todas las apps."""
        from django.contrib import admin
        admin.site.site_header = 'Printing Now · Administración'
        admin.site.site_title  = 'Printing Now Admin'
        admin.site.index_title = 'Panel de control'
