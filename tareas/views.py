import hashlib

from django.db.models import QuerySet
from django.http import HttpResponseNotModified
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


def _version_lista(tareas) -> str:
    """A short fingerprint of the rows the list shows: equal means the HTML would be identical,
    so the phone/PC polling can leave the DOM untouched."""
    payload = "\n".join(
        f"{t.pk}|{int(t.completada)}|{t.titulo}|{t.prioridad}|{t.fecha_limite or ''}|{t.creada_en.isoformat()}"
        for t in tareas
    )
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]


def _contexto_lista() -> dict:
    tareas = list(_lista())
    return {"tareas": tareas, "lista_version": _version_lista(tareas)}


@require_GET
def index(request):
    return render(
        request,
        "tareas/index.html",
        {"form": TareaForm(), **_contexto_lista(), **_contadores()},
    )


@require_GET
def lista(request):
    """The list fragment alone, for the 5-second background refresh. A matching If-None-Match
    answers 304 so the client never re-renders an unchanged list."""
    contexto = _contexto_lista()
    etag = f'"{contexto["lista_version"]}"'
    if request.headers.get("If-None-Match") == etag:
        response = HttpResponseNotModified()
        response["ETag"] = etag
        response["Cache-Control"] = "no-cache"
        return response
    response = render(
        request,
        "tareas/partials/_lista_tareas.html",
        {**contexto, "hay": bool(contexto["tareas"])},
    )
    response["ETag"] = etag
    response["Cache-Control"] = "no-cache"
    return response


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
        {
            "tarea": tarea,
            "form": TareaForm(),
            "oob": True,
            "limpiar_form": True,
            **_contexto_lista(),
            **_contadores(),
        },
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
        {"tarea": tarea, "form": TareaForm(), "oob": True, **_contexto_lista(), **_contadores()},
    )


@require_http_methods(["DELETE"])
def eliminar(request, pk: int):
    tarea = get_object_or_404(Tarea, pk=pk)
    tarea.delete()
    return render(
        request,
        "tareas/partials/_tras_eliminar.html",
        {"oob": True, **_contexto_lista(), **_contadores()},
    )
