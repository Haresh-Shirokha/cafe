import uuid
from django.conf import settings
from django.db import models
from orders.models import Order


class OrderPhoto(models.Model):
    """
    Jab order 'delivered' ho jaata hai, user apne food ki ek photo click
    karta hai (mobile camera se). Us par ek generic artistic filter apply
    hota hai, phir user use social media par share kar sakta hai — aur
    yehi photo admin ke paas bhi save rehti hai (admin apne brand ke
    social media par bhi post kar sake).

    NOTE: Filter ek generic "warm painterly" effect hai — kisi specific
    studio/brand ke copyrighted art style ki nakal nahi hai.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="photo")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="food_photos")

    original_image = models.ImageField(upload_to="order_photos/original/")
    filtered_image = models.ImageField(upload_to="order_photos/filtered/", blank=True, null=True)

    shared_to_instagram = models.BooleanField(default=False)
    admin_downloaded = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_photos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Photo for {self.order.bill_number}"
