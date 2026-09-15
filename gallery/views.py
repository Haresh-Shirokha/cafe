from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from orders.models import Order
from .models import OrderPhoto
from .forms import OrderPhotoForm


@login_required
def capture_photo(request, order_id):
    """
    Sirf DELIVERED orders ke liye available. User apni food ki photo
    click/upload karta hai -> filter automatically apply hoke
    filtered_image ban jaati hai (gallery/signals.py dekho).
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != "delivered":
        messages.warning(request, "You can only add a photo for a delivered order.")
        return redirect("orders:detail", order_id=order.id)

    photo = getattr(order, "photo", None)
    if photo:
        return redirect("gallery:view", order_id=order.id)

    form = OrderPhotoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        photo = form.save(commit=False)
        photo.order = order
        photo.user = request.user
        photo.save()
        messages.success(request, "Photo uploaded! Applying filter...")
        return redirect("gallery:view", order_id=order.id)

    return render(request, "gallery/capture.html", {"form": form, "order": order})


@login_required
def view_photo(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    photo = get_object_or_404(OrderPhoto, order=order)
    return render(request, "gallery/view.html", {"order": order, "photo": photo})


@login_required
def mark_shared(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    photo = get_object_or_404(OrderPhoto, order=order)
    photo.shared_to_instagram = True
    photo.save(update_fields=["shared_to_instagram"])
    messages.success(request, "Great! Shared successfully.")
    return redirect("gallery:view", order_id=order.id)
