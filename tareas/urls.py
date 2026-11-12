from django.urls import path

from tareas import views

app_name = "tareas"

urlpatterns = [
    path("", views.index, name="index"),
    path("crear/", views.crear, name="crear"),
    path("<int:pk>/alternar/", views.alternar, name="alternar"),
    path("<int:pk>/eliminar/", views.eliminar, name="eliminar"),
]
