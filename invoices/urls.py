from django.urls import path
from . import views

app_name = "invoices"

urlpatterns = [
    path("<uuid:order_id>/", views.invoice_view, name="detail"),
    path("<uuid:order_id>/pdf/", views.invoice_pdf, name="pdf"),
    path("qr-code.png", views.qr_code_view, name="qr_code"),
]
