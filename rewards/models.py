import uuid
from django.db import models
from django.conf import settings
from orders.models import Order


class Nostalgia(models.Model):
    title = models.CharField(max_length=255)
    story = models.TextField()

    class Meta:
        db_table = "nostalgia_pool"

    def __str__(self):
        return self.title


class Reward(models.Model):
    cards = models.PositiveIntegerField(unique=True)
    code = models.CharField(max_length=100, unique=True)
    reward = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)  # admin can retire a reward

    class Meta:
        db_table = "reward_pool"

    def __str__(self):
        return self.reward


class ScratchCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="scratch_cards")
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="scratch_card")
    nostalgia = models.ForeignKey(Nostalgia, on_delete=models.SET_NULL, null=True, blank=True)
    revealed = models.BooleanField(default=False)
    reward = models.ForeignKey(Reward, on_delete=models.SET_NULL, null=True, blank=True)
    reward_code = models.CharField(max_length=100, blank=True, null=True)
    reward_label = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)  # SiteConfig.reward_expiry_days se calculate hota hai

    class Meta:
        db_table = "scratch_cards"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.id}"

    @property
    def is_expired(self):
        from django.utils import timezone
        return bool(self.expires_at) and not self.revealed and timezone.now() > self.expires_at

    @property
    def days_left(self):
        from django.utils import timezone
        if not self.expires_at or self.revealed:
            return None
        delta = self.expires_at - timezone.now()
        return max(0, delta.days)


class SiteConfig(models.Model):
    """
    Singleton config jo admin dashboard se edit kar sakta hai — jaise
    reward expiry days. Django settings.py se alag isliye rakha hai
    kyunki admin ko RUNTIME me (bina code chhue) change karna hai.
    """
    reward_expiry_days = models.PositiveIntegerField(
        default=60, help_text="Number of days after which an unrevealed scratch card will be marked as 'expired'."
    )

    class Meta:
        db_table = "site_config"

    def __str__(self):
        return f"SiteConfig (reward expiry: {self.reward_expiry_days} days)"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
