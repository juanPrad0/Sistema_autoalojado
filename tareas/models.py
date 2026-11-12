from django.db import models
from django.utils import timezone


class Tarea(models.Model):
    class Prioridad(models.TextChoices):
        BAJA = "B", "Baja"
        MEDIA = "M", "Media"
        ALTA = "A", "Alta"

    titulo = models.CharField("título", max_length=200)
    completada = models.BooleanField(default=False)
    prioridad = models.CharField(
        max_length=1,
        choices=Prioridad.choices,
        default=Prioridad.MEDIA,
    )
    fecha_limite = models.DateField("fecha límite", null=True, blank=True)
    creada_en = models.DateTimeField("creada el", auto_now_add=True)

    class Meta:
        ordering = ["-creada_en"]
        verbose_name = "tarea"
        verbose_name_plural = "tareas"

    def __str__(self) -> str:
        return self.titulo

    @property
    def vencida(self) -> bool:
        return bool(
            self.fecha_limite
            and not self.completada
            and self.fecha_limite < timezone.localdate()
        )

    @property
    def para_hoy(self) -> bool:
        return bool(self.fecha_limite and self.fecha_limite == timezone.localdate())
