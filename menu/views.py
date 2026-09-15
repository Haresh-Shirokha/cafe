from django.shortcuts import render
from django.db.models import Prefetch
from .models import Category, MenuItem, AddOn


def menu_list(request):
    """
    Public menu page - normal user login karke yahi se price dekh k
    order karega (add to cart -> checkout -> payment). Har item ke saath
    uske available add-ons (extra cheese, extra sauce, etc.) bhi dikhte hain.
    """
    addon_prefetch = Prefetch("addons", queryset=AddOn.objects.filter(is_active=True))
    categories = Category.objects.prefetch_related(
        Prefetch("items", queryset=MenuItem.objects.prefetch_related(addon_prefetch))
    ).all()
    uncategorised = MenuItem.objects.filter(category__isnull=True, is_available=True).prefetch_related(addon_prefetch)
    return render(request, "menu/menu_list.html", {
        "categories": categories,
        "uncategorised": uncategorised,
    })
