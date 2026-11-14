from django.db.models import QuerySet
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from tareas.forms import TareaForm
from tareas.models import Tarea


def _contadores() -> dict:
    tareas = Tarea.objects.all()
    pendientes = tareas.filter(completada=False)
    pendientes = list(pendientes)
    completadas = tareas.filter(completada=True).count()
    return {
        "pendientes": len(pendientes),
        "completadas": completadas,
        "vencidas": sum(1 for tarea in pendientes if tarea.vencida),
        "hay": bool(pendientes) or bool(completadas),
    }


def _lista() -> QuerySet[Tarea]:
    return Tarea.objects.all()


@require_GET
def index(request):
    tareas = list(_lista())
    return render(
        request,
        "tareas/index.html",
        {
            "tareas": tareas,
            "form": TareaForm(),
            **_contadores(),
        },
    )


@require_POST
def crear(request):
    form = TareaForm(request.POST)
    if not form.is_valid():
        response = render(
            request,
            "tareas/partials/_form_tarea.html",
            {"form": form},
        )
        response["HX-Retarget"] = "#form-tarea"
        response["HX-Reswap"] = "outerHTML"
        return response

    tarea = form.save()
    response = render(
        request,
        "tareas/partials/_item_tarea.html",
        {"tarea": tarea, "form": TareaForm(), "oob": True, "limpiar_form": True, **_contadores()},
    )
    # the page listens for this to close the phone sheet (or refocus the inline form)
    response["HX-Trigger"] = "tarea-creada"
    return response


@require_POST
def alternar(request, pk: int):
    tarea = get_object_or_404(Tarea, pk=pk)
    tarea.completada = not tarea.completada
    tarea.save(update_fields=["completada"])
    return render(
        request,
        "tareas/partials/_item_tarea.html",
        {"tarea": tarea, "form": TareaForm(), "oob": True, **_contadores()},
    )


@require_http_methods(["DELETE"])
def eliminar(request, pk: int):
    tarea = get_object_or_404(Tarea, pk=pk)
    tarea.delete()
    return render(
        request,
        "tareas/partials/_tras_eliminar.html",
        {"oob": True, **_contadores()},
    )
