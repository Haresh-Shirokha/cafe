from django.contrib import admin
from .models import Nostalgia, Reward, ScratchCard, SiteConfig

admin.site.register(Nostalgia)
admin.site.register(Reward)
admin.site.register(SiteConfig)

@admin.register(ScratchCard)
class ScratchCardAdmin(admin.ModelAdmin):
    list_display = ("user", "order", "reward", "revealed", "expires_at", "created_at")
    list_filter = ("revealed",)
