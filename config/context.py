"""Navigation shared by every page: one source for the rail and the phone bar."""

from dataclasses import dataclass

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


def modulos(request):
    ahora = timezone.localtime()
    return {
        "modulos": MODULOS,
        "modulo_actual": _clave_actual(request),
        "hoy": ahora.date(),
        "ahora": ahora,
    }
