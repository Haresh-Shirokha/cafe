import qrcode
from io import BytesIO
from django.conf import settings


def generate_qr_png_bytes(data=None):
    """Business website ka QR code PNG bytes me generate karta hai (invoice page + PDF dono me use hota hai)."""
    url = data or getattr(settings, "BUSINESS_WEBSITE", "https://bombaychowkk.in/")
    img = qrcode.make(url, box_size=8, border=2)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
