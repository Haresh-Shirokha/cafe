from django.contrib import admin
from .models import WalletItem, WalletTransaction, WalletRedemption

admin.site.register(WalletItem)
admin.site.register(WalletTransaction)

@admin.register(WalletRedemption)
class WalletRedemptionAdmin(admin.ModelAdmin):
    list_display = ("user", "item", "points_spent", "redemption_code", "fulfilled", "created_at")
    list_filter = ("fulfilled",)
