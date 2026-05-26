from django.urls import path
from apps.sales import views

app_name = "sales"

urlpatterns = [
    path("caja/", views.pos_view, name="pos"),
    path("caja/agregar/", views.add_to_cart, name="add_to_cart"),
    path("caja/actualizar/", views.update_cart, name="update_cart"),
    path("caja/eliminar/", views.remove_from_cart, name="remove_from_cart"),
    path("caja/vaciar/", views.clear_cart, name="clear_cart"),
    path("caja/pago/", views.payment_modal, name="payment_modal"),
    path("caja/confirmar/", views.confirm_sale, name="confirm_sale"),
    path("caja/ticket/<int:pk>/", views.ticket_view, name="ticket"),
]