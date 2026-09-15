from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from orders.models import Order
from .models import Invoice
from .pdf import generate_invoice_pdf
from .qr import generate_qr_png_bytes


def _get_order_for_user(request, order_id):
    if request.user.is_staff:
        return get_object_or_404(Order, id=order_id)
    return get_object_or_404(Order, id=order_id, user=request.user)


@login_required
def invoice_view(request, order_id):
    order = _get_order_for_user(request, order_id)
    invoice = get_object_or_404(Invoice, order=order)
    return render(request, "invoices/invoice_detail.html", {
        "order": order,
        "invoice": invoice,
        "business_name": getattr(settings, "BUSINESS_NAME", "RewardsApp"),
        "business_tagline": getattr(settings, "BUSINESS_TAGLINE", ""),
        "business_address": getattr(settings, "BUSINESS_ADDRESS", ""),
        "business_gstin": getattr(settings, "BUSINESS_GSTIN", ""),
        "business_phone": getattr(settings, "BUSINESS_PHONE", ""),
        "business_food_tagline": getattr(settings, "BUSINESS_FOOD_TAGLINE", ""),
    })


@login_required
def invoice_pdf(request, order_id):
    order = _get_order_for_user(request, order_id)
    invoice = get_object_or_404(Invoice, order=order)
    pdf_bytes = generate_invoice_pdf(invoice)
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{invoice.invoice_number}.pdf"'
    return response


def qr_code_view(request):
    """Business website ka QR code — invoice HTML page isse load karta hai."""
    png_bytes = generate_qr_png_bytes()
    return HttpResponse(png_bytes, content_type="image/png")
