from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction

from menu.models import MenuItem, AddOn
from .models import Order, OrderItem
from invoices.services import generate_invoice_for_order

CART_SESSION_KEY = "cart"


def _get_cart(session):
    return session.setdefault(CART_SESSION_KEY, {})


def _cart_key(item_id, addon_ids):
    """
    Same item with a DIFFERENT combination of add-ons is a separate cart
    line (e.g. 'Burger + Extra Cheese' vs plain 'Burger'), so the key
    includes a sorted, deduped list of add-on ids.
    """
    addon_part = "-".join(sorted(set(str(a) for a in addon_ids)))
    return f"{item_id}|{addon_part}"


@login_required
def add_to_cart(request, item_id):
    """
    Menu page se user quantity + optional add-ons (extra cheese, extra
    sauce, etc.) select karke "Add to Cart" karta hai. Price automatically
    add-ons ke price ke saath badh jaata hai — Zomato/Swiggy jaisa.
    """
    item = get_object_or_404(MenuItem, id=item_id, is_available=True)
    try:
        qty = int(request.POST.get("quantity", request.GET.get("quantity", 1)))
    except (TypeError, ValueError):
        qty = 1
    qty = max(1, qty)

    addon_ids = request.POST.getlist("addons")
    # sirf woh add-ons allow karo jo isi item ke liye valid + active hain
    valid_addons = list(AddOn.objects.filter(id__in=addon_ids, is_active=True, applicable_items=item))
    valid_addon_ids = [str(a.id) for a in valid_addons]

    cart = _get_cart(request.session)
    key = _cart_key(item_id, valid_addon_ids)

    if key in cart:
        cart[key]["quantity"] += qty
    else:
        cart[key] = {
            "item_id": str(item_id),
            "quantity": qty,
            "addon_ids": valid_addon_ids,
        }
    request.session.modified = True

    if valid_addons:
        addon_names = ", ".join(a.name for a in valid_addons)
        messages.success(request, f"{item.name} x{qty} (with {addon_names}) added to cart.")
    else:
        messages.success(request, f"{item.name} x{qty} added to cart.")
    return redirect("menu:list")


@login_required
def remove_from_cart(request, key):
    cart = _get_cart(request.session)
    cart.pop(key, None)
    request.session.modified = True
    return redirect("orders:cart")


def _resolve_cart_line(entry):
    """Ek cart entry ko display-ready dict me convert karta hai: menu_item, addons, unit_price, subtotal."""
    try:
        menu_item = MenuItem.objects.get(id=entry["item_id"])
    except MenuItem.DoesNotExist:
        return None

    addons = list(AddOn.objects.filter(id__in=entry.get("addon_ids", [])))
    addons_total = sum((a.price for a in addons), Decimal("0"))
    unit_price = menu_item.price + addons_total
    quantity = entry["quantity"]

    return {
        "menu_item": menu_item,
        "addons": addons,
        "unit_price": unit_price,
        "quantity": quantity,
        "subtotal": unit_price * quantity,
    }


@login_required
def cart_view(request):
    cart = _get_cart(request.session)
    items = []
    total = Decimal("0")
    for key, entry in cart.items():
        line = _resolve_cart_line(entry)
        if not line:
            continue
        line["key"] = key
        total += line["subtotal"]
        items.append(line)
    return render(request, "orders/cart.html", {"items": items, "total": total})


@login_required
def checkout(request):
    """
    Payment step nahi hai — order seedha place ho jaata hai (Order +
    OrderItems create hote hi). Add-ons ka price OrderItem.price me hi
    include ho jaata hai, aur addons_summary me naam snapshot ho jaate hain
    (invoice/bill par dikhane ke liye). Table number bhi yahin capture hota
    hai taaki staff ko pata rahe order kis table par deliver karna hai.
    """
    cart = _get_cart(request.session)
    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect("menu:list")

    table_number = request.POST.get("table_number", "").strip()
    if not table_number:
        messages.error(request, "Please enter your table number before placing the order.")
        return redirect("orders:cart")

    with transaction.atomic():
        order = Order.objects.create(
            user=request.user,
            table_number=table_number,
            reward_points=getattr(settings, "SCRATCH_CARD_BONUS_POINTS", 40),
        )
        for key, entry in cart.items():
            line = _resolve_cart_line(entry)
            if not line:
                continue
            addons_summary = ", ".join(f"{a.name} (+₹{a.price})" for a in line["addons"])
            OrderItem.objects.create(
                order=order,
                menu_item=line["menu_item"],
                item_name=line["menu_item"].name,
                price=line["unit_price"],
                quantity=line["quantity"],
                addons_summary=addons_summary,
            )
        generate_invoice_for_order(order)  # GST (CGST+SGST) ke saath invoice ban jaati hai

    request.session[CART_SESSION_KEY] = {}
    request.session.modified = True
    messages.success(request, "Order placed successfully! Points will be credited to your wallet after payment.")
    return redirect("orders:detail", order_id=order.id)


@login_required
def order_history(request):
    orders = request.user.orders.prefetch_related("items")
    return render(request, "orders/history.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    if request.user.is_staff:
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "orders/detail.html", {"order": order})
