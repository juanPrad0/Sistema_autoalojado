"""Navigation shared by every page: one source for the rail and the phone bar."""

from dataclasses import dataclass
from pathlib import Path

from django.conf import settings
from django.utils import timezone


@dataclass(frozen=True)
class Modulo:
    clave: str
    nombre: str
    url_name: str
    icono: str
    resumen: str
    fase: int


MODULOS = (
    Modulo("resumen", "Resumen", "resumen", "icono-resumen", "El día en una pantalla", 1),
    Modulo("portafolio", "Portafolio", "portafolio:index", "icono-portafolio", "Acciones y valuación", 3),
    Modulo("tareas", "Tareas", "tareas:index", "icono-tareas", "Pendientes y prioridades", 1),
    Modulo("horarios", "Horarios", "horarios:index", "icono-horarios", "La semana en bloques", 2),
    Modulo("nube", "Nube", "nube:index", "icono-nube", "Archivos en casa", 4),
)


def _clave_actual(request) -> str:
    match = getattr(request, "resolver_match", None)
    if match is None:
        return ""
    if match.url_name == "resumen":
        return "resumen"
    return match.app_name or ""


def _version_assets() -> str:
    """The newest mtime of the CSS build and the app scripts: a changed file gets a new URL, so no
    browser or service worker can keep serving the old one."""
    base = Path(settings.BASE_DIR) / "static"
    archivos = [base / "css" / "app.css", *sorted((base / "js").glob("*.js"))]
    try:
        return str(int(max(p.stat().st_mtime for p in archivos if p.exists())))
    except ValueError:
        return "1"


def modulos(request):
    ahora = timezone.localtime()
    return {
        "modulos": MODULOS,
        "modulo_actual": _clave_actual(request),
        "hoy": ahora.date(),
        "ahora": ahora,
        "pwa_habilitada": getattr(settings, "PWA_ENABLED", False),
        "asset_version": _version_assets(),
    }
