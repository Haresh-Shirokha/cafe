import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model.
    is_staff (built-in Django field) is used to mark the ADMIN portal user.
    Normal customers sign up from the website; admin is created via
    createsuperuser / makeadmin management command and logs in from the
    SAME portal login page — the view then redirects based on is_staff.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)

    # Profile photo (uploaded file, stored under MEDIA_ROOT/profiles/)
    picture = models.ImageField(upload_to="profiles/", blank=True, null=True)

    points = models.PositiveIntegerField(default=0)
    referral_code = models.CharField(max_length=30, unique=True, blank=True, null=True)
    referred_by = models.CharField(max_length=30, blank=True, null=True)
    yearly_reward_unlocked = models.BooleanField(default=False)
    yearly_reward_expires = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.username

    @property
    def orders_count(self):
        return self.orders.count()

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)


class PhoneOTP(models.Model):
    """
    Phone-based signup/login ke liye OTP record. Dev mode me OTP terminal/console
    par print hota hai (jaise email console backend). Production me isko kisi
    real SMS gateway (Twilio, MSG91, Fast2SMS, etc.) se bhejna hoga —
    'accounts/services.py' me sirf woh integration jodni hogi.
    """
    PURPOSE_CHOICES = [("signup", "Signup"), ("login", "Login")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "phone_otps"
        ordering = ["-created_at"]

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.phone} - {self.otp_code} ({self.purpose})"
