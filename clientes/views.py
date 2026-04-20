"""Views públicas."""
from django.shortcuts import render
from django.http import JsonResponse
from .models import Cliente


def home(request):
    """Home público con mapa, buscador y lista de clientes."""
    stats = {
        'total': Cliente.objects.filter(activo=True).count(),
        'regiones': Cliente.objects.filter(activo=True).values('comuna__region').distinct().count(),
        'comunas': Cliente.objects.filter(activo=True).values('comuna').distinct().count(),
    }
    return render(request, 'clientes/home.html', {'stats': stats})


def api_clientes(request):
    """Devuelve todos los clientes activos como JSON para el frontend."""
    region = request.GET.get('region')
    comuna = request.GET.get('comuna')
    eco    = request.GET.get('eco')

    qs = (Cliente.objects
          .filter(activo=True)
          .select_related('comuna', 'comuna__region'))

    if region:
        qs = qs.filter(comuna__region__nombre=region)
    if comuna:
        qs = qs.filter(comuna__nombre=comuna)
    if eco == '1':
        qs = qs.filter(eco_friendly=True)

    data = []
    for c in qs:
        data.append({
            'id': c.id,
            'razon_social': c.razon_social,
            'direccion': c.direccion,
            'comuna': c.comuna.nombre,
            'region': c.comuna.region.nombre,
            'contacto': c.contacto,
            'telefono': c.telefono,
            'telefono_raw': c.telefono,
            'whatsapp': c.whatsapp_url(),
            'tel_link': c.tel_link(),
            'equipos': c.equipos,
            'eco_friendly': c.eco_friendly,
            'web': c.web,
            'fecha_instalacion': c.fecha_instalacion.isoformat() if c.fecha_instalacion else None,
            'foto': c.foto.url if c.foto else None,
            'lat': c.lat,
            'lng': c.lng,
        })
    return JsonResponse({'clientes': data})
