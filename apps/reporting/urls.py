from django.urls import path
from apps.reporting import views

app_name = "reporting"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("historial/", views.historial, name="historial"),
]