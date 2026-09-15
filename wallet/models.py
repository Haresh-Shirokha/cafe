import uuid
from django.conf import settings
from django.db import models


class WalletItem(models.Model):
    """
    Redeemable item — admin banata/manage karta hai. e.g. 'Free Chai' @ 1000 points.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    points_required = models.PositiveIntegerField()
    image = models.ImageField(upload_to="wallet_items/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "wallet_items"
        ordering = ["points_required"]

    def __str__(self):
        return f"{self.name} ({self.points_required} pts)"


class WalletTransaction(models.Model):
    """Points ledger — har earn/redeem yahan record hota hai, taaki user apni history dekh sake."""
    TYPE_CHOICES = [
        ("earn", "Earned"),
        ("redeem", "Redeemed"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet_transactions")
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    points = models.IntegerField()  # positive for earn, negative for redeem
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "wallet_transactions"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.points}"


class WalletRedemption(models.Model):
    """
    Jab user wallet se koi item redeem karta hai (jaise Free Chai), ek record
    yahan ban jaata hai jise admin fulfil (deliver) karke tick kar deta hai.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet_redemptions")
    item = models.ForeignKey(WalletItem, on_delete=models.SET_NULL, null=True)
    points_spent = models.PositiveIntegerField()
    redemption_code = models.CharField(max_length=20, unique=True)
    fulfilled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "wallet_redemptions"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.redemption_code:
            self.redemption_code = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.item} - {self.redemption_code}"
