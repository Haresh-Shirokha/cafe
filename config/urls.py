from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('django-admin/', admin.site.urls),  # Django's built-in admin (superuser use only)

    path('', include('pages.urls')),
    path('accounts/', include('accounts.urls')),
    path('menu/', include('menu.urls')),
    path('orders/', include('orders.urls')),
    path('dashboard/', include('dashboard.urls')),  # this IS the admin portal users log in to
    path('rewards/', include('rewards.urls')),
    path('photobooth/', include('gallery.urls')),
    path('wallet/', include('wallet.urls')),
    path('invoice/', include('invoices.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
