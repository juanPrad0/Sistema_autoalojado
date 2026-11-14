from django.shortcuts import render
from django.views.decorators.http import require_GET

from nube import services


@require_GET
def index(request):
    return render(
        request,
        "nube/index.html",
        {
            "fase": 4,
            "raiz": services.raiz(),
            "archivos": services.contar_archivos(),
        },
    )
