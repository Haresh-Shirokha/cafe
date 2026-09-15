from django.contrib import admin
from .models import Invoice

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "order", "total_amount", "emailed_at", "created_at")
    list_filter = ("emailed_at",)
