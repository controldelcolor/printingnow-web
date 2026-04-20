"""python manage.py cargar_regiones

Carga las 16 regiones oficiales de Chile y un set base de comunas con
coordenadas aproximadas. Es idempotente: se puede correr varias veces.
"""
from django.core.management.base import BaseCommand
from clientes.models import Region, Comuna


REGIONES_COMUNAS = [
    # (orden, nombre_region, [(comuna, lat, lng), ...])
    (1,  "Arica y Parinacota", [
        ("Arica",      -18.4783, -70.3126),
        ("Camarones",  -19.0000, -69.8333),
        ("Putre",      -18.1955, -69.5597),
        ("General Lagos", -17.6333, -69.4833),
    ]),
    (2,  "Tarapacá", [
        ("Iquique",       -20.2208, -70.1431),
        ("Alto Hospicio", -20.2633, -70.1011),
        ("Pozo Almonte",  -20.2589, -69.7872),
        ("Pica",          -20.4915, -69.3322),
        ("Huara",         -19.9969, -69.7703),
        ("Colchane",      -19.2781, -68.6361),
        ("Camiña",        -19.3083, -69.4342),
    ]),
    (3,  "Antofagasta", [
        ("Antofagasta", -23.6509, -70.3975),
        ("Calama",      -22.4667, -68.9333),
        ("Tocopilla",   -22.0911, -70.2003),
        ("Mejillones",  -23.0963, -70.4480),
        ("Taltal",      -25.4069, -70.4864),
        ("Ollagüe",     -21.2217, -68.2525),
        ("San Pedro de Atacama", -22.9119, -68.1997),
        ("María Elena", -22.3500, -69.6667),
        ("Sierra Gorda",-22.8833, -69.3167),
    ]),
    (4,  "Atacama", [
        ("Copiapó",      -27.3667, -70.3333),
        ("Caldera",      -27.0653, -70.8222),
        ("Vallenar",     -28.5708, -70.7575),
        ("Chañaral",     -26.3464, -70.6194),
        ("Diego de Almagro", -26.3672, -70.0506),
        ("Huasco",       -28.4603, -71.2172),
        ("Freirina",     -28.5064, -71.0636),
        ("Tierra Amarilla", -27.4700, -70.2828),
    ]),
    (5,  "Coquimbo", [
        ("La Serena",    -29.9027, -71.2519),
        ("Coquimbo",     -29.9533, -71.3436),
        ("Ovalle",       -30.6000, -71.2000),
        ("Illapel",      -31.6300, -71.1700),
        ("Andacollo",    -30.2333, -71.0833),
        ("Vicuña",       -30.0333, -70.7167),
        ("Combarbalá",   -31.1833, -71.0000),
        ("Los Vilos",    -31.9167, -71.5167),
        ("Salamanca",    -31.7833, -70.9667),
        ("Monte Patria", -30.7000, -70.9500),
    ]),
    (6,  "Valparaíso", [
        ("Valparaíso",    -33.0458, -71.6197),
        ("Viña del Mar",  -33.0153, -71.5500),
        ("Quilpué",       -33.0475, -71.4442),
        ("Villa Alemana", -33.0411, -71.3734),
        ("San Antonio",   -33.5959, -71.6130),
        ("Quillota",      -32.8833, -71.2500),
        ("Los Andes",     -32.8333, -70.5833),
        ("San Felipe",    -32.7500, -70.7167),
        ("Concón",        -32.9244, -71.5233),
        ("Limache",       -33.0131, -71.2664),
        ("Olmué",         -33.0167, -71.1833),
        ("La Ligua",      -32.4500, -71.2333),
        ("Cartagena",     -33.5500, -71.6167),
        ("El Quisco",     -33.4000, -71.7000),
        ("El Tabo",       -33.4500, -71.6833),
        ("Algarrobo",     -33.3667, -71.6667),
    ]),
    (7,  "Metropolitana", [
        ("Santiago",           -33.4489, -70.6693),
        ("Providencia",        -33.4246, -70.6137),
        ("Las Condes",         -33.4172, -70.5476),
        ("Ñuñoa",              -33.4521, -70.5961),
        ("La Reina",           -33.4418, -70.5376),
        ("Maipú",              -33.5117, -70.7581),
        ("La Florida",         -33.5165, -70.5979),
        ("Macul",              -33.4872, -70.6039),
        ("Huechuraba",         -33.3672, -70.6395),
        ("Recoleta",           -33.4089, -70.6396),
        ("Peñalolén",          -33.4868, -70.5353),
        ("San Bernardo",       -33.5950, -70.7000),
        ("La Cisterna",        -33.5353, -70.6658),
        ("Padre Hurtado",      -33.5651, -70.8247),
        ("Estación Central",   -33.4547, -70.6905),
        ("Quilicura",          -33.3655, -70.7294),
        ("Independencia",      -33.4182, -70.6561),
        ("Cerrillos",          -33.4953, -70.7221),
        ("Talagante",          -33.6667, -70.9333),
        ("Buin",               -33.7333, -70.7500),
        ("Puente Alto",        -33.6167, -70.5833),
        ("Vitacura",           -33.3917, -70.5750),
        ("Lo Barnechea",       -33.3500, -70.5167),
        ("La Granja",          -33.5336, -70.6275),
        ("San Miguel",         -33.4953, -70.6539),
        ("Pedro Aguirre Cerda",-33.4931, -70.6775),
        ("Pudahuel",           -33.4300, -70.7678),
        ("El Bosque",          -33.5608, -70.6736),
        ("San Ramón",          -33.5419, -70.6403),
        ("La Pintana",         -33.5825, -70.6336),
        ("Conchalí",           -33.3856, -70.6786),
        ("Renca",              -33.4033, -70.7239),
        ("Cerro Navia",        -33.4228, -70.7392),
        ("Quinta Normal",      -33.4339, -70.6950),
        ("Lo Prado",           -33.4439, -70.7261),
        ("Lo Espejo",          -33.5256, -70.6950),
        ("Colina",             -33.2000, -70.6833),
        ("Lampa",              -33.2833, -70.8833),
        ("Tiltil",             -33.0833, -70.9333),
        ("Pirque",             -33.6333, -70.5667),
        ("San José de Maipo",  -33.6417, -70.3517),
        ("Calera de Tango",    -33.6333, -70.7833),
        ("El Monte",           -33.6833, -70.9833),
        ("Isla de Maipo",      -33.7500, -70.9000),
        ("Peñaflor",           -33.6067, -70.8828),
        ("Melipilla",          -33.6867, -71.2158),
        ("Curacaví",           -33.4050, -71.1444),
        ("Alhué",              -34.0333, -71.1167),
        ("María Pinto",        -33.5333, -71.1000),
        ("San Pedro",          -33.9000, -71.4667),
        ("Paine",              -33.8122, -70.7447),
    ]),
    (8,  "O'Higgins", [
        ("Rancagua",    -34.1708, -70.7444),
        ("San Fernando", -34.5833, -70.9833),
        ("Pichilemu",   -34.3867, -72.0094),
        ("Pichidegua",  -34.3333, -71.3000),
        ("Santa Cruz",  -34.6333, -71.3667),
        ("Machalí",     -34.1833, -70.6500),
        ("Graneros",    -34.0667, -70.7333),
        ("Rengo",       -34.4167, -70.8667),
        ("San Vicente", -34.4333, -71.0833),
        ("Chimbarongo", -34.7167, -71.0500),
        ("Nancagua",    -34.6500, -71.2000),
    ]),
    (9,  "Maule", [
        ("Talca",       -35.4264, -71.6554),
        ("Curicó",      -34.9853, -71.2394),
        ("Linares",     -35.8464, -71.5936),
        ("Molina",      -35.1167, -71.2833),
        ("San Javier",  -35.5942, -71.7272),
        ("Constitución",-35.3333, -72.4167),
        ("Cauquenes",   -35.9667, -72.3167),
        ("Maule",       -35.5167, -71.7167),
        ("Parral",      -36.1417, -71.8306),
        ("Longaví",     -35.9667, -71.6833),
        ("Teno",        -34.8667, -71.1667),
        ("Romeral",     -34.9667, -71.1167),
        ("Rauco",       -34.9333, -71.3000),
    ]),
    (10, "Ñuble", [
        ("Chillán",        -36.6064, -72.1036),
        ("San Carlos",     -36.4236, -71.9589),
        ("Quirihue",       -36.2833, -72.5333),
        ("Bulnes",         -36.7417, -72.2986),
        ("Chillán Viejo",  -36.6217, -72.1325),
    ]),
    (11, "Biobío", [
        ("Concepción",     -36.8270, -73.0498),
        ("Los Ángeles",    -37.4667, -72.3500),
        ("Talcahuano",     -36.7244, -73.1169),
        ("Coronel",        -37.0333, -73.1333),
        ("Hualpén",        -36.7944, -73.1161),
        ("Chiguayante",    -36.9183, -73.0186),
        ("San Pedro de la Paz", -36.8417, -73.1017),
        ("Penco",          -36.7408, -72.9933),
        ("Tomé",           -36.6167, -72.9500),
        ("Lota",           -37.0883, -73.1550),
        ("Lebu",           -37.6111, -73.6500),
        ("Cañete",         -37.8000, -73.4000),
        ("Curanilahue",    -37.4667, -73.3333),
    ]),
    (12, "Araucanía", [
        ("Temuco",     -38.7359, -72.5904),
        ("Villarrica", -39.2861, -72.2281),
        ("Pucón",      -39.2722, -71.9778),
        ("Angol",      -37.8000, -72.7167),
        ("Victoria",   -38.2333, -72.3333),
        ("Loncoche",   -39.3667, -72.6333),
        ("Nueva Imperial", -38.7453, -72.9483),
        ("Padre Las Casas", -38.7656, -72.6019),
    ]),
    (13, "Los Ríos", [
        ("Valdivia", -39.8142, -73.2459),
        ("La Unión", -40.2908, -73.0822),
        ("Río Bueno",-40.3333, -72.9500),
        ("Panguipulli", -39.6383, -72.3358),
    ]),
    (14, "Los Lagos", [
        ("Puerto Montt", -41.4717, -72.9361),
        ("Osorno",       -40.5667, -73.1500),
        ("Castro",       -42.4827, -73.7619),
        ("Ancud",        -41.8697, -73.8203),
        ("Puerto Varas", -41.3195, -72.9861),
        ("Frutillar",    -41.1255, -73.0419),
    ]),
    (15, "Aysén", [
        ("Coyhaique",     -45.5752, -72.0681),
        ("Puerto Aysén",  -45.4000, -72.6833),
        ("Chile Chico",   -46.5436, -71.7242),
    ]),
    (16, "Magallanes", [
        ("Punta Arenas",   -53.1638, -70.9171),
        ("Puerto Natales", -51.7236, -72.5039),
        ("Porvenir",       -53.2969, -70.3683),
    ]),
]


class Command(BaseCommand):
    help = 'Carga las regiones y comunas oficiales de Chile con coordenadas.'

    def handle(self, *args, **opts):
        total_reg, total_com = 0, 0
        for orden, nombre_reg, comunas in REGIONES_COMUNAS:
            region, created = Region.objects.get_or_create(
                nombre=nombre_reg,
                defaults={'orden': orden}
            )
            if not created and region.orden != orden:
                region.orden = orden
                region.save()
            total_reg += 1 if created else 0

            for nombre_com, lat, lng in comunas:
                _, c = Comuna.objects.get_or_create(
                    nombre=nombre_com,
                    region=region,
                    defaults={'lat': lat, 'lng': lng},
                )
                total_com += 1 if c else 0

        self.stdout.write(self.style.SUCCESS(
            f'✓ Listo. Regiones: {Region.objects.count()} · Comunas: {Comuna.objects.count()}'
        ))
