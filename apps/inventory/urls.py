from django.urls import path
from apps.inventory import views

app_name = "inventory"

urlpatterns = [
    # Productos
    path("", views.product_list, name="product_list"),
    path("crear/", views.product_create, name="product_create"),
    path("editar/<int:pk>/", views.product_edit, name="product_edit"),
    path("toggle/<int:pk>/", views.product_toggle, name="product_toggle"),

    # Categorías
    path("categorias/", views.category_list, name="category_list"),
    path("categorias/crear/", views.category_create, name="category_create"),
    path("categorias/editar/<int:pk>/", views.category_edit, name="category_edit"),
]