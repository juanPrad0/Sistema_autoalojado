from django.urls import path

from nube import views

app_name = "nube"

urlpatterns = [
    path("", views.index, name="index"),
]
