# Proyecto: Dashboard Personal Autoalojado (Portafolio, Tareas, Horarios y Nube)

Este archivo define el contexto arquitectónico, las reglas de negocio (basadas en la ERS del proyecto) y las directrices de diseño visual que **OpenCode** debe seguir durante todo el desarrollo.

---

Estamos trabajando en /home/juanprado/Documents/SISTEMA_AUTOALOJADO/Implementacion
Pero el repositorio esta aqui /home/juanprado/Documents/SISTEMA_AUTOALOJADO/Implementacion/Sistema_autoalojado

## 1. Taste Skill (`design-taste-frontend`) v2.5.1

Instalada **solo para este proyecto** (no global), con el CLI oficial de skills:

- Skill: `.agents/skills/design-taste-frontend/` (OpenCode la descubre automáticamente).
- Versión fijada en `skills-lock.json`.
- Se activa sola cuando se construye, rediseña o revisa una landing page, sitio de empresa, producto, tienda, restaurante, SaaS, dashboard, etc., o cuando se pide que una página no parezca "hecha por IA".

### Navegador (necesario para el gate visual)

Chrome for Testing está instalado dentro del proyecto, sin tocar el sistema:

```text
.taste-skill/browser/chrome/linux-157.0.8103.50/chrome-linux64/chrome
```

Los scripts de la skill buscan el navegador en `CHROME_PATH`. **Antes de ejecutar cualquier script de la skill, exporta la variable** (o pásala en la misma línea del comando):

```bash
export CHROME_PATH="$PWD/.taste-skill/browser/chrome/linux-157.0.8103.50/chrome-linux64/chrome"
```

```bash
CHROME_PATH="$PWD/.taste-skill/browser/chrome/linux-157.0.8103.50/chrome-linux64/chrome" \
  node .agents/skills/design-taste-frontend/scripts/gate.mjs index.html
```

### Entorno verificado

- Node v22.23.3 (la skill requiere 22+).
- Chrome for Testing 157.0.8103.50 (headless probado; todas las librerías del sistema presentes).
- ffmpeg disponible (opcional, para clips).

### Notas de la Skill

- Los archivos de trabajo de la skill se escriben en `.taste-skill/` dentro del proyecto; el historial de sorteos en `~/.taste-skill/history.json`.
- No edites nada dentro de `.agents/skills/design-taste-frontend/`: es una copia que se sobrescribe al actualizar.
- Actualizar: `npx skills add Leonxlnx/taste-skill -a opencode -y`
- Documentación: <https://www.tasteskill.dev/docs>
- **Integración con Django:** Al diseñar plantillas en `templates/`, aplica estrictamente las directrices de `design-taste-frontend` (tipografía intencional, jerarquía financiera/editorial clara, contraste limpio, cero estética genérica de IA). Para pasar el `gate.mjs`, puedes exportar el HTML renderizado de la vista de Django a un archivo temporal o validarlo directamente con el script de la skill.

---

## 2. Contexto General y Stack Tecnológico

El sistema es una aplicación web monolítica y modular autoalojada en un único servidor (PC personal) accesible desde **PC (monitor escritorio)** y **Teléfono Móvil (PWA instalada)** a través de una red privada virtual **Tailscale**.

- **Backend:** Python 3.10+ con **Django 5.x**.
- **Base de Datos:** **SQLite** (`db.sqlite3`) como fuente única de verdad (`RF-09`).
- **Frontend:** Django Templates + **HTMX** (actualización parcial de fragmentos sin recargar página, latencia $< 200\text{ ms}$, `RNF-05`) + **Tailwind CSS**.
- **Modo App Móvil (PWA):** Archivo `static/manifest.json` y `sw.js` para instalación directa en la pantalla de inicio del teléfono.
- **Diseño Adaptable (`RNF-02`):**
  - **Escritorio (PC):** Navegación lateral fija y paneles multicolumna.
  - **Móvil (Teléfono):** Vista compacta de 1 sola columna con barra de navegación inferior fija (`fixed bottom-0`) para las 4 secciones principales.
- **Dependencias clave (`requirements.txt`):** `django`, `requests`, `websocket-client`, `python-dotenv`.

---

## 3. Estructura Modular del Proyecto (`RNF-04`)

El código debe mantenerse desacoplado en 4 aplicaciones independientes dentro del proyecto Django, separando responsabilidades en `models.py`, `services.py`, `observers.py` (en portafolio), `views.py` y fragmentos HTML en `templates/<app>/partials/`:

```text
dashboard_personal/
├── manage.py
├── db.sqlite3
├── .env                              # FINNHUB_API_KEY, SECRET_KEY, ALLOWED_HOSTS
├── requirements.txt
├── almacenamiento_nube/              # Directorio físico aislado para la Nube Personal (RNF-06)
├── config/
│   ├── settings.py                   # Configuración general, Tailscale IPs, NUBE_ROOT_DIR
│   ├── urls.py
│   └── wsgi.py / asgi.py
├── static/
│   ├── manifest.json                 # Configuración PWA
│   └── sw.js
├── templates/
│   ├── base.html                     # Layout maestro adaptable (PC Sidebar / Mobile Bottom Nav)
│   └── home.html                     # Resumen ejecutivo del día
├── portafolio/                       # MÓDULO 1: Acciones y Finanzas (Patrón Observer)
│   ├── models.py                     # Modelo: PosicionAccion
│   ├── observers.py                  # Sujeto y Observadores (Caché y Valuación)
│   ├── services.py                   # Cliente híbrido Finnhub (WebSocket / REST)
│   ├── views.py & urls.py
│   └── templates/portafolio/
│       ├── index.html
│       └── partials/
│           ├── _resumen_totales.html
│           └── _tabla_posiciones.html
├── tareas/                           # MÓDULO 2: Administración de Tareas (CRUD HTMX)
│   ├── models.py                     # Modelo: Tarea
│   ├── views.py & urls.py
│   └── templates/tareas/
│       ├── index.html
│       └── partials/
│           ├── _form_tarea.html
│           └── _item_tarea.html
├── horarios/                         # MÓDULO 3: Horarios Semanales vinculados a Tareas
│   ├── models.py                     # Modelo: BloqueHorario (ManyToMany con Tarea)
│   ├── views.py & urls.py
│   └── templates/horarios/
│       ├── index.html
│       └── partials/
│           └── _bloque_horario.html
└── nube/                             # MÓDULO 4: Explorador de Nube Personal
    ├── services.py                   # Validador de rutas seguras dentro de almacenamiento_nube
    ├── views.py & urls.py
    └── templates/nube/
        ├── index.html
        └── partials/
            └── _lista_archivos.html
```

---

## 4. Reglas de Negocio y Requisitos por Módulo (ERS)

### Módulo 1: `portafolio` (Finnhub API + Patrón Observer)
- **Modelo `PosicionAccion` (`RF-01`):** Campos `ticker` (CharField, único, en mayúsculas, ej. `AAPL`, `VOO`, `NVDA`), `nombre` (opcional), `cantidad` (DecimalField, hasta 4 decimales para acciones fraccionadas), `precio_promedio_compra` (DecimalField, 2 decimales).
- **Verificación de Mercado y Conexión Híbrida (`RF-02`, `RNF-01`):**
  - El servicio debe verificar si la bolsa de EE. UU. está abierta (consultando horario bursátil 9:30 AM - 4:00 PM EST en días hábiles o endpoint de estado de Finnhub).
  - **Bolsa Abierta (Modo STREAM):** Conecta a `wss://ws.finnhub.io?token=API_KEY` en un hilo en segundo plano (`daemon=True`) para recibir operaciones *tick-by-tick* de forma fluida sin gastar cuota HTTP.
  - **Bolsa Cerrada (Modo REST):** Consulta `https://finnhub.io/api/v1/quote` respetando estrictamente el límite gratuito de **máximo 60 llamadas por minuto** mediante caché en memoria.
- **Patrón de Diseño Observer (`RF-03`, `RNF-04`):**
  - `FinnhubMarketSubject`: Publicador que recibe los ticks (de WebSocket o REST) y ejecuta `notificar(ticker, datos_mercado)`.
  - `MarketObserver`: Interfaz abstracta con el método `actualizar(ticker, datos_mercado)`.
  - `CacheCotizacionesObserver`: Guarda en RAM la última cotización y timestamp de cada ticker.
  - `ValuacionPortafolioObserver`: Recalcula automáticamente las fórmulas financieras del **Apéndice A** para cada posición con cantidad $C$, precio de compra $P_{\text{compra}}$ y precio actual $P_{\text{actual}}$:
    - Costo de Inversión: $\text{Costo\_pos} = C \times P_{\text{compra}}$
    - Valor Actual de Mercado: $\text{Valor\_actual} = C \times P_{\text{actual}}$
    - Ganancia o Pérdida Neta: $G_{\text{neta}} = \text{Valor\_actual} - \text{Costo\_pos}$
    - Rendimiento Porcentual: $\text{Rendimiento \%} = \left(\frac{\text{Valor\_actual} - \text{Costo\_pos}}{\text{Costo\_pos}}\right) \times 100$
    - Valor Total del Portafolio: $\sum \text{Valor\_actual}$ de todas las posiciones.

### Módulo 2: `tareas` (CRUD Dinámico con HTMX)
- **Modelo `Tarea` (`RF-04`):** Campos `titulo`, `completada` (bool), `prioridad` (`B` Baja, `M` Media, `A` Alta), `fecha_limite` (opcional), `creada_en`.
- **Interactividad (`RNF-05`):** Añadir tarea, alternar estado completada/pendiente y eliminar tarea deben responder únicamente el fragmento HTML (`_item_tarea.html`) usando atributos `hx-post`, `hx-patch`/`hx-post` y `hx-delete` con `hx-target` y `hx-swap`, sin recargar toda la pantalla.
- **Refresco en segundo plano (`RNF-05`):** La lista se actualiza sola cada 5 segundos con `GET /tareas/lista/`, que devuelve únicamente el fragmento de la lista y un `ETag` calculado sobre las filas. Si nada cambió responde `304 Not Modified` y el navegador no toca el DOM (cero parpadeo); si cambió, reemplaza solo el contenedor de la lista. El formulario nunca participa del refresco, así que no se pierde lo que el usuario está escribiendo.

### Módulo 3: `horarios` (Calendario Semanal Vinculado)
- **Modelo `BloqueHorario` (`RF-05`, `RF-06`):** Campos `dia_semana` (0=Lunes a 6=Domingo), `hora_inicio`, `hora_fin`, `titulo_actividad`, `color_hex` y relación `ManyToManyField(Tarea, blank=True, related_name='bloques_horario')`.
- Permite visualizar la semana, asignar tareas pendientes a un bloque horario y marcarlas como completadas desde el mismo horario.

### Módulo 4: `nube` (Almacenamiento Personal Local)
- **Explorador y Transferencia (`RF-07`, `RF-08`):** Lista carpetas y archivos dentro de `settings.NUBE_ROOT_DIR` (`almacenamiento_nube/`), permite crear subcarpetas, subir múltiples archivos desde el teléfono o PC y descargarlos con `FileResponse`.
- **Aislamiento de Seguridad (`RNF-06`):** Toda ruta recibida por parámetro debe resolverse con `Path.resolve()` y verificarse que sea hija estricta de `NUBE_ROOT_DIR` para bloquear cualquier intento de *Path Traversal* (`../`).

---

## 5. Plan de Fases de Desarrollo

1. **Fase 1 (Núcleo, Diseño Base con Taste-Skill y Módulo de Tareas):** Inicialización del proyecto Django, `.env`, `base.html` adaptable (PC + Móvil PWA) diseñado y validado con `design-taste-frontend`, vista `home.html`, CRUD completo de `tareas` con HTMX y refresco automático de la lista cada 5 segundos.
2. **Fase 2 (Módulo de Horarios y Vinculación):** Modelo, vistas y fragmentos HTMX de `horarios` vinculados en tiempo real con `tareas`.
3. **Fase 3 (Módulo de Portafolio Financiero con Patrón Observer):** Implementación de `PosicionAccion`, `observers.py`, `services.py` (conector híbrido WebSocket + REST para Finnhub) y vistas reactivas con HTMX.
4. **Fase 4 (Módulo de Nube Personal):** Implementación del explorador seguro de archivos locales, carga multiparte y descarga directa.

---
