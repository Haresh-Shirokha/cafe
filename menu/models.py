import uuid
from django.db import models


class Category(models.Model):
    """Menu category e.g. Starters, Main Course, Beverages."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "menu_categories"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """
    A purchasable item shown to the normal user in the menu.
    Not part of the original schema you gave me, but Orders need
    something to actually contain — added so 'menu me price dikhna'
    and 'order karna' can actually work.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="items")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to="menu/", blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "menu_items"
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.name} - ₹{self.price}"


class AddOn(models.Model):
    """
    Extra customizations a user can add to a menu item, like Zomato/Swiggy —
    e.g. 'Extra Cheese' (+₹30), 'Extra Sauce' (+₹20). Each add-on can be
    linked to one or more menu items via 'applicable_items'.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    applicable_items = models.ManyToManyField(MenuItem, related_name="addons", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "menu_addons"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} (+₹{self.price})"
