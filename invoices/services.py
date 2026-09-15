from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from .models import Invoice


def _next_invoice_number():
    last = Invoice.objects.order_by("-created_at").first()
    n = Invoice.objects.count()
    return f"INV-{n + 1:06d}"


def generate_invoice_for_order(order):
    """
    Order ke total_amount par CGST + SGST calculate karke Invoice bana deta hai.
    settings.py me CGST_RATE / SGST_RATE se percentages customize kar sakte ho.
    """
    subtotal = order.total_amount
    cgst_rate = Decimal(str(getattr(settings, "CGST_RATE", 2.5)))
    sgst_rate = Decimal(str(getattr(settings, "SGST_RATE", 2.5)))

    cgst_amount = (subtotal * cgst_rate / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    sgst_amount = (subtotal * sgst_rate / Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total = subtotal + cgst_amount + sgst_amount

    invoice, _ = Invoice.objects.get_or_create(order=order, defaults={
        "invoice_number": _next_invoice_number(),
        "subtotal": subtotal,
        "cgst_rate": cgst_rate,
        "cgst_amount": cgst_amount,
        "sgst_rate": sgst_rate,
        "sgst_amount": sgst_amount,
        "total_amount": total,
    })
    return invoice
