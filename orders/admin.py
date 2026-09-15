from django.contrib import admin
from .models import Order, OrderItem, PaymentDetail

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("bill_number", "user", "status", "points_awarded", "paid_at", "created_at")
    list_filter = ("status",)
    inlines = [OrderItemInline]

admin.site.register(PaymentDetail)
