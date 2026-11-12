from django.urls import path

from horarios import views

app_name = "horarios"

urlpatterns = [
    path("", views.index, name="index"),
]
