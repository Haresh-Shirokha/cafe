from django.urls import path
from . import views

app_name = "gallery"

urlpatterns = [
    path("capture/<uuid:order_id>/", views.capture_photo, name="capture"),
    path("view/<uuid:order_id>/", views.view_photo, name="view"),
    path("mark-shared/<uuid:order_id>/", views.mark_shared, name="mark_shared"),
]
