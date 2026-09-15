from django.urls import path
from . import views

app_name = "wallet"

urlpatterns = [
    path("", views.wallet_home, name="home"),
    path("redeem/<uuid:item_id>/", views.redeem_item, name="redeem"),
]
