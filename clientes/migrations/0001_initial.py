"""Migración inicial generada manualmente para clientes app."""
import django.db.models.deletion
from django.db import migrations, models
import clientes.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=80, unique=True)),
                ('orden', models.PositiveSmallIntegerField(default=0, help_text='Orden geográfico norte→sur')),
            ],
            options={
                'verbose_name': 'Región',
                'verbose_name_plural': 'Regiones',
                'ordering': ['orden', 'nombre'],
            },
        ),
        migrations.CreateModel(
            name='Comuna',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=80)),
                ('lat', models.FloatField(blank=True, help_text='Coordenada centroide aproximada', null=True)),
                ('lng', models.FloatField(blank=True, null=True)),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comunas', to='clientes.region')),
            ],
            options={
                'ordering': ['region__orden', 'nombre'],
                'unique_together': {('nombre', 'region')},
            },
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('razon_social', models.CharField(help_text='Nombre comercial o razón social del cliente.', max_length=200, verbose_name='Razón social')),
                ('direccion', models.CharField(blank=True, help_text='Dirección completa (calle, número, oficina).', max_length=250, verbose_name='Dirección')),
                ('contacto', models.CharField(blank=True, max_length=150, verbose_name='Persona de contacto')),
                ('telefono', models.CharField(blank=True, help_text='Ej: +56 9 1234 5678 (se formatea automáticamente).', max_length=30, verbose_name='Teléfono')),
                ('equipos', models.TextField(blank=True, help_text='Separar por barras (/) si hay varios.', verbose_name='Equipos instalados')),
                ('eco_friendly', models.BooleanField(default=False, help_text='Marcar si el cliente es parte del programa.', verbose_name='EcoFriendly')),
                ('fecha_instalacion', models.DateField(blank=True, null=True, verbose_name='Fecha de instalación')),
                ('web', models.URLField(blank=True, verbose_name='Sitio web / Instagram')),
                ('foto', models.ImageField(blank=True, help_text='Se redimensiona automáticamente a 400x400.', null=True, upload_to=clientes.models.cliente_foto_path, verbose_name='Foto o logo')),
                ('lat', models.FloatField(blank=True, null=True)),
                ('lng', models.FloatField(blank=True, null=True)),
                ('activo', models.BooleanField(default=True, verbose_name='Activo (visible en sitio público)')),
                ('fecha_creado', models.DateTimeField(auto_now_add=True)),
                ('fecha_modificado', models.DateTimeField(auto_now=True)),
                ('comuna', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='clientes', to='clientes.comuna', verbose_name='Comuna')),
            ],
            options={
                'verbose_name': 'Cliente',
                'verbose_name_plural': 'Clientes',
                'ordering': ['razon_social'],
                'indexes': [
                    models.Index(fields=['razon_social'], name='clientes_cl_razon_s_idx'),
                    models.Index(fields=['eco_friendly'], name='clientes_cl_eco_friendly_idx'),
                ],
            },
        ),
    ]
