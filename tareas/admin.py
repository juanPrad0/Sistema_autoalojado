from django.contrib import admin

from tareas.models import Tarea


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "prioridad", "completada", "fecha_limite", "creada_en")
    list_filter = ("completada", "prioridad")
    search_fields = ("titulo",)
    date_hierarchy = "creada_en"
