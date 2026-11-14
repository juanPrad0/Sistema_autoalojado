from django.shortcuts import render
from django.utils import timezone

from nube import services
from tareas.models import Tarea


def resumen(request):
    ahora = timezone.localtime()
    hoy = ahora.date()
    tareas = Tarea.objects.all()
    pendientes = tareas.filter(completada=False)
    contexto = {
        "hoy": hoy,
        "ahora": ahora,
        "tareas_pendientes": pendientes.count(),
        "tareas_completadas": tareas.filter(completada=True).count(),
        "tareas_alta": pendientes.filter(prioridad=Tarea.Prioridad.ALTA).count(),
        "tareas_vencidas": sum(1 for tarea in pendientes if tarea.vencida),
        "tareas_recientes": pendientes.order_by("fecha_limite", "-creada_en")[:4],
        "archivos_nube": services.contar_archivos(),
    }
    return render(request, "home.html", contexto)
