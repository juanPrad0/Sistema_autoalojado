from django.urls import path

from portafolio import views

app_name = "portafolio"

urlpatterns = [
    path("", views.index, name="index"),
]
