from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<uuid:item_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<str:key>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("history/", views.order_history, name="history"),
    path("<uuid:order_id>/", views.order_detail, name="detail"),
]
