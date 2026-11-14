from pathlib import Path

from django.conf import settings
from django.contrib import admin
from django.http import FileResponse, Http404
from django.urls import include, path

from config.views import resumen


def service_worker(request):
    """Serve the PWA service worker from the site root so its scope covers every page."""
    archivo = Path(settings.BASE_DIR) / "static" / "sw.js"
    if not archivo.exists():
        raise Http404("sw.js")
    return FileResponse(open(archivo, "rb"), content_type="application/javascript")


urlpatterns = [
    path("sw.js", service_worker, name="service-worker"),
    path("admin/", admin.site.urls),
    path("", resumen, name="resumen"),
    path("portafolio/", include("portafolio.urls")),
    path("tareas/", include("tareas.urls")),
    path("horarios/", include("horarios.urls")),
    path("nube/", include("nube.urls")),
]
