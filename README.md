# Printing Now · Red de Clientes — Django

Aplicación web funcional que reemplaza el prototipo HTML por un sitio real con base de datos, panel admin, importador de Excel y frontend público con mapa.

## ¿Qué hay aquí?

- **Backend:** Django 5 con PostgreSQL (o SQLite en local).
- **Admin:** Django admin extendido con importador de Excel y subida de fotos con auto-redimensión.
- **Frontend público:** el mismo diseño del prototipo visual, ahora alimentado por la base de datos.
- **Listo para Railway** (hosting gestionado con PostgreSQL incluido).

## Probarlo en tu computador (local)

Requisitos: Python 3.11+ instalado.

```bash
# 1. Entrar a la carpeta
cd printingnow_django

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate            # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables (solo para local; Railway las lee de su panel)
cp .env.example .env
# Edita .env si quieres

# 5. Crear la base de datos local (SQLite)
python manage.py migrate

# 6. Cargar las regiones y comunas de Chile
python manage.py cargar_regiones

# 7. Crear tu usuario admin
python manage.py createsuperuser
# (te pedirá username, email y contraseña)

# 8. Importar los 62 clientes desde el Excel
python manage.py importar_excel "../LISTADOS CLIENTE CDELCOLOR  P NOW.xlsx" --confirmar

# 9. Arrancar el servidor local
python manage.py runserver

# 10. Abrir en el navegador:
#     Sitio público:   http://localhost:8000/
#     Panel admin:     http://localhost:8000/admin/
```

## Desplegarlo a Railway (hosting gratis/barato)

Railway es un hosting tipo Heroku — sube el código, ellos se encargan de todo lo demás. La cuenta gratuita te da 5 USD de crédito al mes (suficiente para el inicio) y después cuesta ~5 USD/mes con uso moderado.

### Paso 1 — Crear cuenta y subir el código

1. Abre [railway.app](https://railway.app) y haz **Sign Up** (usa tu Google o GitHub).
2. Sube este proyecto a GitHub (puedo guiarte si no sabes git), o usa el botón **"Deploy from local"** en Railway.
3. En Railway, haz click en **New Project** → **Deploy from GitHub repo** (o **Empty project**).

### Paso 2 — Agregar base de datos PostgreSQL

1. Dentro de tu proyecto Railway, click en **+ New** → **Database** → **Add PostgreSQL**.
2. Railway creará una instancia y automáticamente expondrá la variable `DATABASE_URL` a tu app.

### Paso 3 — Agregar las variables de entorno

En tu servicio Django (no en la DB), ve a **Variables** y agrega:

| Variable | Valor |
|---|---|
| `SECRET_KEY` | Una cadena larga aleatoria. Genera una con: `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.up.railway.app,test.printingnow.cl` (el subdominio que uses) |
| `CUSTOM_DOMAIN` | `test.printingnow.cl` (cuando configures tu dominio) |

`DATABASE_URL` se configura **automáticamente** al agregar PostgreSQL — no la toques.

### Paso 4 — Primera ejecución

Railway detecta el `Procfile` y ejecuta:
1. `release: python manage.py migrate` → crea las tablas.
2. `web: gunicorn printingnow.wsgi` → arranca el sitio.

Espera 2-3 minutos. Railway te dará una URL tipo `printingnow-production.up.railway.app`.

### Paso 5 — Cargar regiones y crear tu usuario admin

En Railway, abre el **terminal web** del servicio (ícono `>_` o pestaña Shell) y ejecuta:

```bash
python manage.py cargar_regiones
python manage.py createsuperuser
# te pedirá usuario, email y contraseña
```

Luego entra a `https://tu-url.up.railway.app/admin/` con esas credenciales.

### Paso 6 — Importar los 62 clientes

Hay dos opciones:

**A) Desde el admin web (recomendado):**
1. Entra a `/admin/clientes/cliente/`
2. Click en **📥 Importar desde Excel** (arriba a la derecha)
3. Sube el archivo `.xlsx` → previsualiza → confirma

**B) Desde la terminal (más rápido):**
```bash
# Sube el xlsx a Railway primero (drag & drop en el shell o con un commit)
python manage.py importar_excel /app/LISTADOS.xlsx --confirmar
```

### Paso 7 — Configurar el subdominio test.printingnow.cl

1. En Railway: **Settings** → **Networking** → **Custom Domain** → añade `test.printingnow.cl`.
2. Railway te dará un registro `CNAME` del tipo `xxxxx.up.railway.app`.
3. Entra a tu **DirectAdmin** → DNS del dominio → crea un registro `CNAME`:
   - Nombre: `test`
   - Valor: el CNAME que te dio Railway
4. Espera 5-30 minutos (propagación DNS). Railway emite un certificado SSL automático.
5. Listo: `https://test.printingnow.cl` apunta a tu app.

## Estructura del proyecto

```
printingnow_django/
├── manage.py                          # CLI de Django
├── requirements.txt                   # Dependencias Python
├── Procfile                          # Cómo arranca Railway
├── runtime.txt                       # Versión de Python
├── .env.example                      # Ejemplo de variables
│
├── printingnow/                      # Configuración del proyecto
│   ├── settings.py                   # Configuración principal
│   ├── urls.py                       # URLs raíz
│   └── wsgi.py                       # Punto de entrada producción
│
├── clientes/                         # App principal
│   ├── models.py                     # Region, Comuna, Cliente
│   ├── admin.py                      # Admin Django personalizado
│   ├── views.py                      # Home + API JSON
│   ├── urls.py                       # URLs de la app
│   ├── importer.py                   # Lógica de importación Excel
│   ├── management/commands/
│   │   ├── cargar_regiones.py        # python manage.py cargar_regiones
│   │   └── importar_excel.py         # python manage.py importar_excel file.xlsx
│   └── templates/
│       ├── clientes/home.html        # Sitio público
│       └── admin/clientes/
│           └── importar_excel.html   # UI del importador
│
├── static/                           # CSS, JS, imágenes
└── media/                            # Fotos de clientes (subidas)
```

## Qué incluye el admin

- **Listado de clientes** con thumbnail, filtros por región/comuna/activo/eco, búsqueda full-text.
- **Edición de cliente** con campos organizados en secciones (identificación, ubicación, contacto, equipamiento).
- **Subida de foto** con redimensión automática a 400×400 (JPEG 85% optimizado).
- **Importador Excel** con preview y confirmación.
- **Acciones en lote**: marcar/desmarcar EcoFriendly, activar/desactivar, eliminar.
- **Regiones y comunas** administrables (cargas las 16 regiones + ~220 comunas con un comando).

## Endpoints públicos

- `GET /` → Home con mapa y buscador.
- `GET /api/clientes/` → JSON con todos los clientes activos.
- `GET /api/clientes/?region=Metropolitana` → Filtrado por región.
- `GET /api/clientes/?comuna=Providencia` → Filtrado por comuna.
- `GET /api/clientes/?eco=1` → Solo EcoFriendly.
- `GET /admin/` → Panel de administración.

## Próximos pasos (roadmap)

- [ ] Geocodificación automática al guardar un cliente nuevo (Nominatim API).
- [ ] Exportación a Excel desde el admin.
- [ ] Página detalle por cliente (URLs amigables tipo `/cliente/totalprint`).
- [ ] Google Analytics / Meta Pixel para medir tráfico.
- [ ] Backup automático semanal de la base de datos al correo.
- [ ] Formulario de contacto público ("Solicita ser parte de la red").

## Soporte

Para dudas técnicas o problemas con el deploy, vuelve a esta conversación con el mensaje de error exacto y yo te guío.
