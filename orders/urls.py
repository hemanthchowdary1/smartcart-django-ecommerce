from django.urls import path
from .views import checkout, order_success, my_orders

urlpatterns = [
    path("checkout/", checkout, name="checkout"),
    path("order-success/<int:order_id>/", order_success, name="order_success"),
    path("my-orders/", my_orders, name="my_orders"),
]