"""Modelos de la app clientes."""
import re
from django.db import models
from django.utils.text import slugify
from PIL import Image


# ═══════════════════════════════════════════════════════════════════════════
#  REGIONES Y COMUNAS DE CHILE
# ═══════════════════════════════════════════════════════════════════════════
class Region(models.Model):
    """Una región de Chile (16 oficiales)."""
    nombre = models.CharField(max_length=80, unique=True)
    orden  = models.PositiveSmallIntegerField(default=0, help_text="Orden geográfico norte→sur")

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = 'Región'
        verbose_name_plural = 'Regiones'

    def __str__(self):
        return self.nombre


class Comuna(models.Model):
    """Comuna dentro de una región."""
    nombre = models.CharField(max_length=80)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='comunas')
    lat    = models.FloatField(null=True, blank=True, help_text="Coordenada centroide aproximada")
    lng    = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['region__orden', 'nombre']
        unique_together = [('nombre', 'region')]

    def __str__(self):
        return f"{self.nombre}"


# ═══════════════════════════════════════════════════════════════════════════
#  CLIENTE
# ═══════════════════════════════════════════════════════════════════════════
def cliente_foto_path(instance, filename):
    """Ruta de la foto: media/clientes/<id>-<slug>.<ext>"""
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'jpg'
    stub = slugify(instance.razon_social)[:40] or 'cliente'
    return f"clientes/{stub}.{ext}"


class Cliente(models.Model):
    """Cliente de la red Printing Now."""

    razon_social = models.CharField(
        'Razón social', max_length=200,
        help_text="Nombre comercial o razón social del cliente."
    )
    direccion = models.CharField(
        'Dirección', max_length=250, blank=True,
        help_text="Dirección completa (calle, número, oficina)."
    )
    comuna = models.ForeignKey(
        Comuna, on_delete=models.PROTECT,
        related_name='clientes', verbose_name='Comuna'
    )
    contacto = models.CharField(
        'Persona de contacto', max_length=150, blank=True
    )
    telefono = models.CharField(
        'Teléfono', max_length=30, blank=True,
        help_text="Ej: +56 9 1234 5678 (se formatea automáticamente)."
    )
    equipos = models.TextField(
        'Equipos instalados', blank=True,
        help_text="Separar por barras (/) si hay varios."
    )
    eco_friendly = models.BooleanField(
        'EcoFriendly', default=False,
        help_text="Marcar si el cliente es parte del programa."
    )
    fecha_instalacion = models.DateField(
        'Fecha de instalación', null=True, blank=True
    )
    web = models.URLField(
        'Sitio web / Instagram', blank=True
    )
    foto = models.ImageField(
        'Foto o logo', upload_to=cliente_foto_path, blank=True, null=True,
        help_text="Se redimensiona automáticamente a 400x400."
    )

    # Coordenadas (se geocodifican al guardar si no están)
    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    # Metadata
    activo      = models.BooleanField('Activo (visible en sitio público)', default=True)
    fecha_creado   = models.DateTimeField(auto_now_add=True)
    fecha_modificado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['razon_social']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        indexes = [
            models.Index(fields=['razon_social']),
            models.Index(fields=['eco_friendly']),
        ]

    def __str__(self):
        return self.razon_social

    # ── Helpers ────────────────────────────────────────────────────────────
    @property
    def region(self):
        return self.comuna.region if self.comuna else None

    def telefono_internacional(self):
        """Devuelve el tel en formato '+56 9 XXXX XXXX' normalizado."""
        if not self.telefono:
            return ''
        digits = re.sub(r'\D', '', self.telefono)
        d = digits.replace('', '')
        if d.startswith('56'):
            d = d[2:]
        if len(d) == 9 and d.startswith('9'):
            return f"+56 {d[0]} {d[1:5]} {d[5:]}"
        if len(d) == 8:
            return f"+56 9 {d[:4]} {d[4:]}"
        return self.telefono

    def whatsapp_url(self):
        """Genera link wa.me si hay teléfono válido."""
        if not self.telefono:
            return ''
        d = re.sub(r'\D', '', self.telefono)
        if len(d) >= 11 and d.startswith('56'):
            return f"https://wa.me/{d}"
        if len(d) == 9:
            return f"https://wa.me/56{d}"
        if len(d) == 8:
            return f"https://wa.me/569{d}"
        return ''

    def tel_link(self):
        """Genera link tel: (elimina espacios)."""
        if not self.telefono:
            return ''
        d = re.sub(r'\D', '', self.telefono)
        if len(d) >= 11 and d.startswith('56'):
            return f"tel:+{d}"
        if len(d) == 9:
            return f"tel:+56{d}"
        if len(d) == 8:
            return f"tel:+569{d}"
        return f"tel:+{d}"

    # ── Auto-redimensionar foto ────────────────────────────────────────────
    def save(self, *args, **kwargs):
        # Formatear teléfono antes de guardar
        if self.telefono:
            self.telefono = self.telefono_internacional() or self.telefono
        # Copiar coords desde la comuna si no se especifican
        if (not self.lat or not self.lng) and self.comuna_id and self.comuna.lat:
            self.lat = self.comuna.lat
            self.lng = self.comuna.lng
        super().save(*args, **kwargs)
        # Redimensionar foto si existe
        if self.foto:
            try:
                img_path = self.foto.path
                img = Image.open(img_path)
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')
                size = 400
                # Cover-fit
                scale = max(size / img.width, size / img.height)
                new_w, new_h = int(img.width * scale), int(img.height * scale)
                img = img.resize((new_w, new_h), Image.LANCZOS)
                left = (new_w - size) // 2
                top  = (new_h - size) // 2
                img  = img.crop((left, top, left + size, top + size))
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                img.save(img_path, format='JPEG', quality=85, optimize=True)
            except Exception:
                pass  # si Pillow falla, dejamos la original
