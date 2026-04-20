"""Configuración del Django admin para Clientes."""
from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect

from .models import Region, Comuna, Cliente
from .importer import procesar_excel


# ═══════════════════════════════════════════════════════════════════════════
#  REGIÓN Y COMUNA
# ═══════════════════════════════════════════════════════════════════════════
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'orden', 'total_comunas', 'total_clientes')
    list_editable = ('orden',)
    search_fields = ('nombre',)
    ordering = ('orden',)

    @admin.display(description='Comunas')
    def total_comunas(self, obj):
        return obj.comunas.count()

    @admin.display(description='Clientes')
    def total_clientes(self, obj):
        return Cliente.objects.filter(comuna__region=obj).count()


@admin.register(Comuna)
class ComunaAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'region', 'lat', 'lng', 'total_clientes')
    list_filter   = ('region',)
    search_fields = ('nombre', 'region__nombre')
    autocomplete_fields = ['region']

    @admin.display(description='Clientes')
    def total_clientes(self, obj):
        return obj.clientes.count()


# ═══════════════════════════════════════════════════════════════════════════
#  CLIENTE
# ═══════════════════════════════════════════════════════════════════════════
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        'foto_thumb', 'razon_social', 'comuna', 'region_display',
        'telefono_display', 'eco_badge', 'activo',
    )
    list_display_links = ('foto_thumb', 'razon_social')
    list_filter = ('activo', 'eco_friendly', 'comuna__region', 'comuna')
    search_fields = ('razon_social', 'contacto', 'direccion', 'equipos', 'telefono')
    autocomplete_fields = ['comuna']
    list_per_page = 30
    save_on_top = True
    list_select_related = ('comuna', 'comuna__region')
    date_hierarchy = 'fecha_creado'

    fieldsets = (
        ('Identificación', {
            'fields': ('razon_social', 'foto', 'activo'),
        }),
        ('Ubicación', {
            'fields': ('direccion', 'comuna', 'lat', 'lng'),
        }),
        ('Contacto', {
            'fields': ('contacto', 'telefono', 'web'),
        }),
        ('Equipamiento y programa', {
            'fields': ('equipos', 'fecha_instalacion', 'eco_friendly'),
        }),
    )
    readonly_fields = ()

    # ── Thumbs y badges ────────────────────────────────────────────────────
    @admin.display(description='')
    def foto_thumb(self, obj):
        if obj.foto:
            return format_html(
                '<img src="{}" style="width:42px;height:42px;border-radius:6px;object-fit:cover" />',
                obj.foto.url
            )
        iniciales = ''.join(p[0] for p in obj.razon_social.split()[:2]).upper() or '?'
        return format_html(
            '<div style="width:42px;height:42px;border-radius:6px;background:#173fd4;'
            'color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px">{}</div>',
            iniciales
        )

    @admin.display(description='Región', ordering='comuna__region__nombre')
    def region_display(self, obj):
        return obj.comuna.region.nombre if obj.comuna_id else '—'

    @admin.display(description='Teléfono')
    def telefono_display(self, obj):
        return obj.telefono or '—'

    @admin.display(description='Eco', ordering='eco_friendly')
    def eco_badge(self, obj):
        if obj.eco_friendly:
            return format_html('<span style="color:#16a34a;font-size:16px">🌿</span>')
        return format_html('<span style="color:#cbd5e1">—</span>')

    # ── Acciones en lote ───────────────────────────────────────────────────
    actions = ['marcar_eco', 'desmarcar_eco', 'desactivar', 'activar']

    @admin.action(description='🌿 Marcar como EcoFriendly')
    def marcar_eco(self, request, qs):
        n = qs.update(eco_friendly=True)
        self.message_user(request, f'{n} clientes marcados como EcoFriendly.', messages.SUCCESS)

    @admin.action(description='Quitar sello EcoFriendly')
    def desmarcar_eco(self, request, qs):
        n = qs.update(eco_friendly=False)
        self.message_user(request, f'{n} clientes sin sello EcoFriendly.', messages.SUCCESS)

    @admin.action(description='🔴 Desactivar (ocultar del sitio público)')
    def desactivar(self, request, qs):
        n = qs.update(activo=False)
        self.message_user(request, f'{n} clientes desactivados.', messages.WARNING)

    @admin.action(description='🟢 Activar')
    def activar(self, request, qs):
        n = qs.update(activo=True)
        self.message_user(request, f'{n} clientes activados.', messages.SUCCESS)

    # ── URL custom para importar Excel ─────────────────────────────────────
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('importar-excel/', self.admin_site.admin_view(self.importar_excel_view),
                 name='clientes_importar_excel'),
        ]
        return my_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['importar_excel_url'] = reverse('admin:clientes_importar_excel')
        return super().changelist_view(request, extra_context=extra_context)

    def importar_excel_view(self, request):
        """Página custom del admin para subir un xlsx e importar en batch."""
        context = {
            **self.admin_site.each_context(request),
            'title': 'Importar clientes desde Excel',
            'opts': self.model._meta,
            'has_permission': True,
        }

        if request.method == 'POST':
            archivo = request.FILES.get('archivo')
            confirmar = request.POST.get('confirmar') == '1'

            if not archivo:
                messages.error(request, 'Debes seleccionar un archivo .xlsx.')
                return render(request, 'admin/clientes/importar_excel.html', context)

            try:
                preview, errores = procesar_excel(archivo)
            except Exception as e:
                messages.error(request, f'Error al leer el archivo: {e}')
                return render(request, 'admin/clientes/importar_excel.html', context)

            if confirmar:
                # Crear los clientes válidos
                creados, omitidos = 0, 0
                for row in preview:
                    if not row.get('valido'):
                        omitidos += 1
                        continue
                    # Evitar duplicados por razón social + comuna
                    comuna_obj = row['_comuna_obj']
                    exists = Cliente.objects.filter(
                        razon_social__iexact=row['razon_social'],
                        comuna=comuna_obj,
                    ).exists()
                    if exists:
                        omitidos += 1
                        continue
                    Cliente.objects.create(
                        razon_social=row['razon_social'],
                        direccion=row.get('direccion', ''),
                        comuna=comuna_obj,
                        contacto=row.get('contacto', ''),
                        telefono=row.get('telefono', ''),
                        equipos=row.get('equipos', ''),
                        eco_friendly=row.get('eco_friendly', False),
                    )
                    creados += 1
                msg = f'Importación completa. {creados} clientes creados.'
                if omitidos:
                    msg += f' {omitidos} omitidos (duplicados o inválidos).'
                messages.success(request, msg)
                return redirect('admin:clientes_cliente_changelist')

            # Mostrar preview
            context['preview'] = preview
            context['errores'] = errores
            context['validos'] = sum(1 for r in preview if r.get('valido'))
            context['archivo_nombre'] = archivo.name

        return render(request, 'admin/clientes/importar_excel.html', context)
