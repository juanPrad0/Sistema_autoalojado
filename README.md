# Panel personal autoalojado

Un panel para el día a día que corre en tu propio equipo: tareas, horarios, portafolio y archivos
en una sola aplicación Django, con SQLite como única base de datos y acceso desde la PC y el
teléfono por la red local o Tailscale.

Fase 1: núcleo del proyecto, diseño base (escritorio con barra lateral, teléfono con barra inferior
y PWA instalable) y el módulo de tareas completo con HTMX.

## Stack

- Python 3.10+ y Django 5.2 (LTS).
- SQLite (`db.sqlite3`).
- Django Templates + HTMX 2 + Tailwind CSS 4 (compilado localmente).
- PWA: `static/manifest.json` y `static/sw.js` (servicio en `/sw.js`).
- Diseño: design-taste-frontend 2.5.1 (sistema, tipografía y movimiento en `static/vendor/taste/`).

## Puesta en marcha

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env          # completá SECRET_KEY y FINNHUB_API_KEY
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver 0.0.0.0:8000
```

Abrí <http://localhost:8000/> en la PC. Desde el teléfono, entrá con la IP de Tailscale
(`http://100.x.y.z:8000/`) o con la IP de la red local.

### Variables de entorno (`.env`)

| Variable | Para qué |
| --- | --- |
| `SECRET_KEY` | Clave de Django. Generala con `python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"`. |
| `DEBUG` | `True` en desarrollo. |
| `FINNHUB_API_KEY` | Cotizaciones del portafolio (Fase 3). |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,100.*`. El comodín `100.*` cubre las IP del rango Tailscale; Django no acepta comodines de IP, así que los valida `config.middleware.PrefixHostMiddleware` antes de `get_host()`. |
| `TAILSCALE_CIDR` | Opcional, por defecto `100.64.0.0/10`. |

### PWA y caché en desarrollo

El service worker se registra solo con `DEBUG=False`; `PWA_ENABLED=True` lo fuerza para probar la
instalación. Mientras desarrollás no hay caché de por medio. Si una versión anterior dejó un service
worker registrado, la primera carga lo desregistra, borra sus cachés y recarga sola una vez.

El CSS y los scripts se piden con `?v=` (el mtime más nuevo de `static/css/app.css` y
`static/js/*.js`), así ningún navegador ni service worker conserva una versión vieja.

### Estilos

El CSS compilado (`static/css/app.css`) está versionado para que el servidor no necesite Node.
Si cambiás `static/src/app.css` o las plantillas:

```bash
npm install
npx tailwindcss -i static/src/app.css -o static/css/app.css --minify
```

## Uso

- **Escritorio (≥768 px):** barra lateral fija con Resumen, Portafolio, Tareas, Horarios y Nube.
- **Teléfono (<768 px):** barra inferior fija con los mismos cinco destinos, más el encabezado con
  la fecha del día.
- **PWA:** abrí el sitio en el navegador del teléfono y elegí "Agregar a la pantalla de inicio". El
  service worker cachea la interfaz y los archivos estáticos; las páginas se piden a la red y caen
  al caché si el servidor no responde.
- **Tareas:** crear, completar/pendiente y eliminar sin recargar la página (HTMX). Cada operación
  responde su propio fragmento; los contadores se actualizan con un intercambio fuera de banda.
- **Lista viva:** cada 5 segundos se pide `GET /tareas/lista/` con el `ETag` anterior. Si nada cambió
  el servidor responde `304` y el DOM queda intacto (sin parpadeo); si cambió, se reemplaza solo el
  contenedor de la lista. El formulario nunca se toca, así que un borrador en el campo no se pierde.

## Pruebas

```bash
.venv/bin/python manage.py test          # 18 pruebas (modelo, vistas HTMX, nube, hosts)
CHROME_PATH=/ruta/a/chrome node scripts/e2e.mjs http://127.0.0.1:8000
```

La prueba e2e usa Playwright con el Chrome for Testing del proyecto y verifica en un navegador real
que crear, alternar y eliminar tareas actualizan solo el fragmento, sin recargar la página, y que la
barra inferior aparece en el teléfono.

## Gate visual (design-taste-frontend)

```bash
export CHROME_PATH="$PWD/../.taste-skill/browser/chrome/linux-157.0.8103.50/chrome-linux64/chrome"
node ../.agents/skills/design-taste-frontend/scripts/gate.mjs          # con el servidor en :8765
```

Resultado de la Fase 1: `GATE: FAIL 1 (round 2 of 3)`. El único hallazgo abierto es `nav` ("no hay
barra de navegación superior"), consecuencia directa de la barra lateral fija que pide el proyecto:
el verificador espera una barra superior de sitio de marketing. Los cinco hallazgos de
`container-edges` están exceptuados en `.taste-skill/waivers.json` con su motivo (la barra lateral
es chrome de la aplicación, fuera de la columna de contenido; cada sección usa un único `.wrap`).

El chequeo de layout (`assets/layout/check.mjs`) no encuentra hallazgos en 1440x900, 1024x768,
820x1180, 768x1024 ni 390x844.

## Estructura

```
config/            settings, urls, middleware de hosts, contexto de navegación, vista de resumen
tareas/            módulo 2: modelo Tarea, CRUD HTMX
horarios/          módulo 3 (Fase 2)
portafolio/        módulo 1 (Fase 3)
nube/              módulo 4 (Fase 4); services.py valida las rutas dentro de almacenamiento_nube/
almacenamiento_nube/  carpeta aislada de la nube personal
templates/         base.html (shell) y home.html (resumen)
static/            manifest, service worker, iconos, fuentes, CSS compilado y vendor
scripts/e2e.mjs    prueba de navegador
```

## Fases

1. **Fase 1 (esta entrega):** proyecto, `.env`, shell adaptable, PWA, resumen y CRUD de tareas.
2. Fase 2: horarios semanales vinculados a tareas.
3. Fase 3: portafolio con Finnhub y patrón observer.
4. Fase 4: explorador de la nube personal con rutas verificadas.
