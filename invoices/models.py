import uuid
from django.conf import settings
from django.db import models
from orders.models import Order


class Invoice(models.Model):
    """
    Order place hote hi (checkout complete hote hi) automatically bin jaati hai.
    GST (CGST + SGST) calculate karke total_amount me include kiya jaata hai.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="invoice")

    invoice_number = models.CharField(max_length=30, unique=True)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    cgst_rate = models.DecimalField(max_digits=5, decimal_places=2)
    cgst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    sgst_rate = models.DecimalField(max_digits=5, decimal_places=2)
    sgst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    # Email tracking — user aur admin dono ko pata rahe ki mail bheja gaya ya nahi
    emailed_at = models.DateTimeField(blank=True, null=True)
    emailed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="invoices_emailed",
    )
    emailed_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "invoices"
        ordering = ["-created_at"]

    def __str__(self):
        return self.invoice_number
