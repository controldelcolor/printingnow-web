"""python manage.py importar_excel archivo.xlsx [--confirmar]

Importa clientes desde un Excel. Sin --confirmar muestra preview,
con --confirmar ejecuta la creación.
"""
from django.core.management.base import BaseCommand, CommandError
from clientes.importer import procesar_excel
from clientes.models import Cliente


class Command(BaseCommand):
    help = 'Importa clientes desde un archivo Excel (.xlsx).'

    def add_arguments(self, parser):
        parser.add_argument('archivo', type=str, help='Ruta al archivo .xlsx')
        parser.add_argument('--confirmar', action='store_true',
                            help='Ejecutar la importación (sin esta flag, solo muestra preview).')

    def handle(self, *args, **opts):
        try:
            with open(opts['archivo'], 'rb') as f:
                preview, errores = procesar_excel(f)
        except FileNotFoundError:
            raise CommandError(f'Archivo no encontrado: {opts["archivo"]}')

        for e in errores:
            self.stderr.write(self.style.ERROR(f'ERROR: {e}'))
        if errores:
            return

        validos = [r for r in preview if r['valido']]
        invalidos = [r for r in preview if not r['valido']]

        self.stdout.write(f'\nArchivo procesado: {opts["archivo"]}')
        self.stdout.write(f'  · Filas totales:  {len(preview)}')
        self.stdout.write(self.style.SUCCESS(f'  · Válidas:        {len(validos)}'))
        if invalidos:
            self.stdout.write(self.style.WARNING(f'  · Con advertencia: {len(invalidos)}'))
            for r in invalidos[:5]:
                self.stdout.write(f'    - {r["razon_social"]}: {r["_warn"]}')
            if len(invalidos) > 5:
                self.stdout.write(f'    ... y {len(invalidos)-5} más')

        if not opts['confirmar']:
            self.stdout.write(self.style.NOTICE(
                '\nEste es un preview. Ejecuta con --confirmar para crear los clientes.'
            ))
            return

        creados, omitidos = 0, 0
        for r in validos:
            exists = Cliente.objects.filter(
                razon_social__iexact=r['razon_social'],
                comuna=r['_comuna_obj'],
            ).exists()
            if exists:
                omitidos += 1
                continue
            Cliente.objects.create(
                razon_social=r['razon_social'],
                direccion=r['direccion'],
                comuna=r['_comuna_obj'],
                contacto=r['contacto'],
                telefono=r['telefono'],
                equipos=r['equipos'],
                eco_friendly=r['eco_friendly'],
            )
            creados += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Importación completa. {creados} creados, {omitidos} omitidos (duplicados).'
        ))
