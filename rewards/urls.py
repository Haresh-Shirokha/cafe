from django.urls import path
from . import views

app_name = "rewards"

urlpatterns = [
    path("reveal/<uuid:card_id>/", views.reveal_card, name="reveal"),
]
