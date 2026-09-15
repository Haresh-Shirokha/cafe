import uuid
from django.conf import settings
from django.db import models
from menu.models import MenuItem


class Order(models.Model):

    STATUS_CHOICES = [
        ("queue", "In Queue"),
        ("preparing", "Preparing"),
        ("prepared", "Prepared"),
        ("delivered", "Delivered"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    bill_number = models.CharField(max_length=100, unique=True, blank=True)

    table_number = models.CharField(max_length=10, blank=True, default="")

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="queue")

    points_awarded = models.BooleanField(default=False)
    reward_points = models.PositiveIntegerField(default=0)  # is order par milne wale points (bill paid hone par credit hote hain)

    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(blank=True, null=True)  # set jab status 'delivered' set hota hai — ADMIN ka timer yahin ruk jaata hai
    paid_at = models.DateTimeField(blank=True, null=True)       # set jab admin 'Bill Paid' mark karta hai — CUSTOMER ka timer yahin ruk jaata hai

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]

    def __str__(self):
        return self.bill_number

    def save(self, *args, **kwargs):
        if not self.bill_number:
            self.bill_number = f"BILL-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.items.all())

    @staticmethod
    def _format_duration(delta):
        total_seconds = int(delta.total_seconds())
        h, rem = divmod(total_seconds, 3600)
        m, s = divmod(rem, 60)
        parts = []
        if h:
            parts.append(f"{h}h")
        parts.append(f"{m}m")
        parts.append(f"{s}s")
        return " ".join(parts)

    @property
    def delivery_duration_display(self):
        """Order place hone se DELIVER hone tak kitni der lagi — ADMIN side ke liye."""
        if not self.delivered_at:
            return None
        return self._format_duration(self.delivered_at - self.created_at)

    @property
    def payment_duration_display(self):
        """Order place hone se BILL PAID hone tak kitni der lagi — CUSTOMER side ke liye."""
        if not self.paid_at:
            return None
        return self._format_duration(self.paid_at - self.created_at)


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True, related_name="order_items")
    item_name = models.CharField(max_length=255)  # snapshot, in case menu item is later edited/deleted
    price = models.DecimalField(max_digits=8, decimal_places=2)  # snapshot unit price INCLUDING selected add-ons
    quantity = models.PositiveIntegerField(default=1)
    addons_summary = models.CharField(max_length=500, blank=True)  # e.g. "Extra Cheese (+₹30), Extra Sauce (+₹20)"

    class Meta:
        db_table = "order_items"

    def __str__(self):
        return f"{self.item_name} x {self.quantity}"

    @property
    def subtotal(self):
        return self.price * self.quantity


class PaymentDetail(models.Model):
    """
    Admin bill 'Paid' mark karte waqt payment method choose karta hai.
    Cash select karne par denomination-wise breakdown bhi record hota hai —
    customer ne kaunse note diye, aur admin ne change me kaunse note diye.
    """
    METHOD_CHOICES = [
        ("gpay", "GPay"),
        ("cash", "Cash"),
        ("card", "Credit/Debit Card"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment_detail")
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)

    cash_received = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    change_given = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cash_received_breakdown = models.CharField(max_length=255, blank=True)  # e.g. "1×500"
    change_given_breakdown = models.CharField(max_length=255, blank=True)   # e.g. "2×100"

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payment_details"

    def __str__(self):
        return f"{self.order.bill_number} - {self.method}"
