from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .decorators import staff_required
from .forms import MenuItemForm, RewardForm, NostalgiaForm, ScratchCardOverrideForm, WalletItemForm, WeeklyEventForm, SiteConfigForm

from orders.models import Order, PaymentDetail
from menu.models import MenuItem
from rewards.models import Reward, Nostalgia, ScratchCard
from accounts.models import User


@login_required
@staff_required
def home(request):
    from pages.models import RSVP, Contact
    context = {
        "pending_orders": Order.objects.exclude(status="delivered").count(),
        "total_orders": Order.objects.count(),
        "total_users": User.objects.filter(is_staff=False).count(),
        "recent_orders": Order.objects.select_related("user").all()[:10],
        "recent_rsvps": RSVP.objects.all()[:5],
        "recent_contacts": Contact.objects.all()[:5],
    }
    return render(request, "dashboard/home.html", context)


# ---------------- ORDERS ----------------

@login_required
@staff_required
def order_list(request):
    status = request.GET.get("status")
    orders = Order.objects.select_related("user").all()
    if status:
        orders = orders.filter(status=status)
    return render(request, "dashboard/order_list.html", {
        "orders": orders, "status_choices": Order.STATUS_CHOICES, "active_status": status,
    })


@login_required
@staff_required
def order_manage(request, order_id):
    order = get_object_or_404(Order.objects.select_related("user"), id=order_id)
    return render(request, "dashboard/order_manage.html", {
        "order": order, "status_choices": Order.STATUS_CHOICES,
    })


@login_required
@staff_required
def update_order_status(request, order_id, new_status):
    order = get_object_or_404(Order, id=order_id)
    valid = dict(Order.STATUS_CHOICES)
    if new_status in valid:
        order.status = new_status
        if new_status == "delivered":
            if not order.delivered_at:
                order.delivered_at = timezone.now()  # ADMIN ka timer yahin ruk jaata hai
        else:
            order.delivered_at = None  # agar galti se delivered se hataya, timer dobara chalu ho jaayega
        order.save(update_fields=["status", "delivered_at"])
        messages.success(request, f"Order status set to '{valid[new_status]}'.")
    return redirect("dashboard:order_manage", order_id=order.id)


@login_required
@staff_required
def mark_bill_paid(request, order_id):
    """
    Admin bill payment yahan se process karta hai:
      GET  -> payment method dropdown (GPay/Cash/Card) form dikhata hai.
              Cash select karne par denomination-wise fields (JS se) khulte hain.
      POST -> payment method + (agar cash) denomination breakdown save karta hai,
              order.paid_at set karta hai (customer ka timer ruk jaata hai),
              aur reward_points wallet me credit karta hai.
    """
    from django.db import transaction as db_transaction
    from wallet.models import WalletTransaction

    order = get_object_or_404(Order, id=order_id)
    if order.paid_at:
        messages.info(request, "This bill is already marked as paid.")
        return redirect("dashboard:order_manage", order_id=order.id)

    DENOMINATIONS = [2000, 500, 200, 100, 50, 20, 10]

    if request.method == "POST":
        method = request.POST.get("method")
        valid_methods = dict(PaymentDetail.METHOD_CHOICES)
        if method not in valid_methods:
            messages.error(request, "Please select a payment method.")
            return redirect("dashboard:mark_bill_paid", order_id=order.id)

        cash_received = None
        change_given = None
        received_breakdown = ""
        change_breakdown = ""

        if method == "cash":
            received_parts = []
            cash_received = Decimal("0")
            for d in DENOMINATIONS:
                count = int(request.POST.get(f"recv_{d}", 0) or 0)
                if count > 0:
                    cash_received += Decimal(d) * count
                    received_parts.append(f"{count}×{d}")
            received_breakdown = ", ".join(received_parts)

            change_parts = []
            change_given = Decimal("0")
            for d in DENOMINATIONS:
                count = int(request.POST.get(f"change_{d}", 0) or 0)
                if count > 0:
                    change_given += Decimal(d) * count
                    change_parts.append(f"{count}×{d}")
            change_breakdown = ", ".join(change_parts)

            if cash_received < order.total_amount:
                messages.error(request, f"Cash received (₹{cash_received}) is less than the bill total (₹{order.total_amount}).")
                return redirect("dashboard:mark_bill_paid", order_id=order.id)

            expected_change = cash_received - order.total_amount
            if change_given != expected_change:
                messages.warning(
                    request,
                    f"Note: Expected change was ₹{expected_change}, but ₹{change_given} was recorded — saved anyway.",
                )

        with db_transaction.atomic():
            PaymentDetail.objects.create(
                order=order, method=method,
                cash_received=cash_received, change_given=change_given,
                cash_received_breakdown=received_breakdown,
                change_given_breakdown=change_breakdown,
            )

            order.paid_at = timezone.now()
            order.save(update_fields=["paid_at"])

            if not order.points_awarded and order.reward_points > 0:
                user = order.user
                user.points += order.reward_points
                user.save(update_fields=["points"])
                order.points_awarded = True
                order.save(update_fields=["points_awarded"])
                WalletTransaction.objects.create(
                    user=user, type="earn", points=order.reward_points,
                    description=f"Order {order.bill_number} — Bill paid, reward credited",
                )

        messages.success(
            request,
            f"Bill marked as paid via {valid_methods[method]} — {order.reward_points} points credited to the wallet.",
        )
        return redirect("dashboard:order_manage", order_id=order.id)

    # GET -> form dikhao
    return render(request, "dashboard/mark_bill_paid.html", {
        "order": order, "denominations": DENOMINATIONS,
    })


# ---------------- MENU ----------------

@login_required
@staff_required
def menu_manage(request):
    items = MenuItem.objects.select_related("category").all()
    return render(request, "dashboard/menu_manage.html", {"items": items})


@login_required
@staff_required
def menu_item_add(request):
    form = MenuItemForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Menu item added.")
        return redirect("dashboard:menu_manage")
    return render(request, "dashboard/menu_item_form.html", {"form": form, "title": "Add Menu Item"})


@login_required
@staff_required
def menu_item_edit(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)
    form = MenuItemForm(request.POST or None, request.FILES or None, instance=item)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Menu item updated.")
        return redirect("dashboard:menu_manage")
    return render(request, "dashboard/menu_item_form.html", {"form": form, "title": "Edit Menu Item"})


@login_required
@staff_required
def menu_item_delete(request, item_id):
    MenuItem.objects.filter(id=item_id).delete()
    messages.success(request, "Menu item deleted.")
    return redirect("dashboard:menu_manage")


# ---------------- ADD-ONS (extras like Zomato/Swiggy customizations) ----------------

@login_required
@staff_required
def addon_manage(request):
    from menu.models import AddOn
    addons = AddOn.objects.prefetch_related("applicable_items").all()
    return render(request, "dashboard/addon_manage.html", {"addons": addons})


@login_required
@staff_required
def addon_add(request):
    from .forms import AddOnForm
    form = AddOnForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Add-on created.")
        return redirect("dashboard:addon_manage")
    return render(request, "dashboard/addon_form.html", {"form": form, "title": "Add New Add-on"})


@login_required
@staff_required
def addon_edit(request, addon_id):
    from menu.models import AddOn
    from .forms import AddOnForm
    addon = get_object_or_404(AddOn, id=addon_id)
    form = AddOnForm(request.POST or None, instance=addon)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Add-on updated.")
        return redirect("dashboard:addon_manage")
    return render(request, "dashboard/addon_form.html", {"form": form, "title": "Edit Add-on"})


@login_required
@staff_required
def addon_delete(request, addon_id):
    from menu.models import AddOn
    AddOn.objects.filter(id=addon_id).delete()
    messages.success(request, "Add-on deleted.")
    return redirect("dashboard:addon_manage")


# ---------------- REWARDS ----------------

@login_required
@staff_required
def reward_pool(request):
    rewards = Reward.objects.all()
    nostalgias = Nostalgia.objects.all()
    return render(request, "dashboard/reward_pool.html", {"rewards": rewards, "nostalgias": nostalgias})


@login_required
@staff_required
def reward_add(request):
    form = RewardForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Added to the reward pool.")
        return redirect("dashboard:reward_pool")
    return render(request, "dashboard/reward_form.html", {"form": form})


@login_required
@staff_required
def nostalgia_add(request):
    form = NostalgiaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Nostalgia story added.")
        return redirect("dashboard:reward_pool")
    return render(request, "dashboard/nostalgia_form.html", {"form": form})


# ---------------- SCRATCH CARDS ----------------

@login_required
@staff_required
def scratch_card_list(request):
    cards = ScratchCard.objects.select_related("user", "order", "reward", "nostalgia").all()
    return render(request, "dashboard/scratch_card_list.html", {"cards": cards})


@login_required
@staff_required
def scratch_card_override(request, card_id):
    """Admin manually reward/nostalgia choose kar sakta hai (agar user ne abhi reveal nahi kiya)."""
    card = get_object_or_404(ScratchCard, id=card_id)
    if card.revealed:
        messages.error(request, "The user has already revealed this card, it can no longer be overridden.")
        return redirect("dashboard:scratch_card_list")

    form = ScratchCardOverrideForm(request.POST or None, initial={"reward": card.reward, "nostalgia": card.nostalgia})
    if request.method == "POST" and form.is_valid():
        reward = form.cleaned_data.get("reward")
        nostalgia = form.cleaned_data.get("nostalgia")
        if reward:
            card.reward = reward
            card.reward_code = reward.code
            card.reward_label = reward.reward
        if nostalgia:
            card.nostalgia = nostalgia
        card.save()
        messages.success(request, "Scratch card reward has been overridden.")
        return redirect("dashboard:scratch_card_list")
    return render(request, "dashboard/scratch_card_override.html", {"form": form, "card": card})


# ---------------- USERS ----------------

@login_required
@staff_required
def user_list(request):
    users = User.objects.filter(is_staff=False)
    return render(request, "dashboard/user_list.html", {"users": users})


# ---------------- CUSTOMER FOOD PHOTOS ----------------

@login_required
@staff_required
def photo_gallery(request):
    """
    Sare users ki uploaded (filtered) food photos yahan dikhti hain.
    Admin yahan se download karke apne brand ke Instagram par post kar sakta hai.
    """
    from gallery.models import OrderPhoto
    photos = OrderPhoto.objects.select_related("user", "order").all()
    return render(request, "dashboard/photo_gallery.html", {"photos": photos})


@login_required
@staff_required
def mark_photo_downloaded(request, photo_id):
    from gallery.models import OrderPhoto
    photo = get_object_or_404(OrderPhoto, id=photo_id)
    photo.admin_downloaded = True
    photo.save(update_fields=["admin_downloaded"])
    messages.success(request, "Photo marked as downloaded.")
    return redirect("dashboard:photo_gallery")


# ---------------- WALLET ----------------

@login_required
@staff_required
def wallet_item_manage(request):
    from wallet.models import WalletItem
    items = WalletItem.objects.all()
    return render(request, "dashboard/wallet_item_manage.html", {"items": items})


@login_required
@staff_required
def wallet_item_add(request):
    form = WalletItemForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Wallet item added.")
        return redirect("dashboard:wallet_item_manage")
    return render(request, "dashboard/wallet_item_form.html", {"form": form, "title": "Add Wallet Item"})


@login_required
@staff_required
def wallet_item_edit(request, item_id):
    from wallet.models import WalletItem
    item = get_object_or_404(WalletItem, id=item_id)
    form = WalletItemForm(request.POST or None, request.FILES or None, instance=item)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Wallet item updated.")
        return redirect("dashboard:wallet_item_manage")
    return render(request, "dashboard/wallet_item_form.html", {"form": form, "title": "Edit Wallet Item"})


@login_required
@staff_required
def wallet_item_delete(request, item_id):
    from wallet.models import WalletItem
    WalletItem.objects.filter(id=item_id).delete()
    messages.success(request, "Wallet item deleted.")
    return redirect("dashboard:wallet_item_manage")


@login_required
@staff_required
def wallet_redemption_list(request):
    """Jo users ne wallet points se items redeem kiye hain, unko yahan fulfil (deliver) mark karo."""
    from wallet.models import WalletRedemption
    redemptions = WalletRedemption.objects.select_related("user", "item").all()
    return render(request, "dashboard/wallet_redemption_list.html", {"redemptions": redemptions})


@login_required
@staff_required
def wallet_redemption_fulfil(request, redemption_id):
    from wallet.models import WalletRedemption
    redemption = get_object_or_404(WalletRedemption, id=redemption_id)
    redemption.fulfilled = True
    redemption.save(update_fields=["fulfilled"])
    messages.success(request, "Redemption marked as fulfilled.")
    return redirect("dashboard:wallet_redemption_list")


# ---------------- WEEKLY EVENTS ----------------

@login_required
@staff_required
def weekly_event_manage(request):
    from pages.models import WeeklyEvent
    events = WeeklyEvent.objects.all()
    return render(request, "dashboard/weekly_event_manage.html", {"events": events})


@login_required
@staff_required
def weekly_event_add(request):
    form = WeeklyEventForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Weekly event added.")
        return redirect("dashboard:weekly_event_manage")
    return render(request, "dashboard/weekly_event_form.html", {"form": form, "title": "Add Weekly Event"})


@login_required
@staff_required
def weekly_event_edit(request, event_id):
    from pages.models import WeeklyEvent
    event = get_object_or_404(WeeklyEvent, id=event_id)
    form = WeeklyEventForm(request.POST or None, instance=event)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Weekly event updated.")
        return redirect("dashboard:weekly_event_manage")
    return render(request, "dashboard/weekly_event_form.html", {"form": form, "title": "Edit Weekly Event"})


@login_required
@staff_required
def weekly_event_delete(request, event_id):
    from pages.models import WeeklyEvent
    WeeklyEvent.objects.filter(id=event_id).delete()
    messages.success(request, "Weekly event deleted.")
    return redirect("dashboard:weekly_event_manage")


# ---------------- INVOICE (email to customer) ----------------

@login_required
@staff_required
def email_invoice(request, order_id):
    """
    Admin yahan se ek click me customer ko unka invoice (PDF, GST breakup
    ke saath) email kar sakta hai. User ko iska record profile/order-detail
    page par bhi dikh jaata hai ('Invoice emailed on ...').
    """
    from django.core.mail import EmailMessage
    from django.utils import timezone
    from invoices.models import Invoice
    from invoices.pdf import generate_invoice_pdf

    order = get_object_or_404(Order, id=order_id)
    invoice = get_object_or_404(Invoice, order=order)

    pdf_bytes = generate_invoice_pdf(invoice)
    subject = f"Your Invoice {invoice.invoice_number} — Order {order.bill_number}"
    body = (
        f"Hi {order.user.first_name or order.user.username},\n\n"
        f"Please find attached the invoice for your order {order.bill_number}.\n\n"
        f"Total Paid: Rs. {invoice.total_amount} (incl. CGST + SGST)\n\n"
        f"Thank you for ordering with us!"
    )
    email = EmailMessage(subject, body, to=[order.user.email])
    email.attach(f"{invoice.invoice_number}.pdf", pdf_bytes, "application/pdf")
    email.send(fail_silently=False)

    invoice.emailed_at = timezone.now()
    invoice.emailed_by = request.user
    invoice.emailed_count = invoice.emailed_count + 1
    invoice.save(update_fields=["emailed_at", "emailed_by", "emailed_count"])

    messages.success(request, f"Invoice emailed to {order.user.email}.")
    return redirect("dashboard:order_manage", order_id=order.id)


# ---------------- EXCEL REPORTS (accounting) ----------------

@login_required
@staff_required
def reports_home(request):
    return render(request, "dashboard/reports_home.html")


@login_required
@staff_required
def export_orders_excel(request, period):
    """
    period: 'daily', 'monthly', 'yearly' — orders ko us period ke hisaab se
    filter karke .xlsx file download karata hai (accounting/tracking ke liye).
    """
    from django.http import HttpResponse
    from .excel_export import generate_orders_excel

    now = timezone.now()
    if period == "daily":
        orders = Order.objects.filter(created_at__date=now.date()).select_related(
            "user", "invoice", "payment_detail"
        )
        filename = f"orders_daily_{now.date()}.xlsx"
    elif period == "monthly":
        orders = Order.objects.filter(
            created_at__year=now.year, created_at__month=now.month
        ).select_related("user", "invoice", "payment_detail")
        filename = f"orders_monthly_{now.year}_{now.month:02d}.xlsx"
    elif period == "yearly":
        orders = Order.objects.filter(created_at__year=now.year).select_related(
            "user", "invoice", "payment_detail"
        )
        filename = f"orders_yearly_{now.year}.xlsx"
    else:
        messages.error(request, "Invalid period.")
        return redirect("dashboard:reports_home")

    excel_bytes = generate_orders_excel(orders)
    response = HttpResponse(
        excel_bytes,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


# ---------------- REWARD EXPIRY SETTINGS ----------------

# ---------------- WEBSITE SUBMISSIONS (RSVP / Contact / Partner / Newsletter) ----------------

@login_required
@staff_required
def rsvp_list(request):
    from pages.models import RSVP
    rsvps = RSVP.objects.all()
    return render(request, "dashboard/rsvp_list.html", {"rsvps": rsvps})


@login_required
@staff_required
def contact_list(request):
    from pages.models import Contact
    contacts = Contact.objects.all()
    return render(request, "dashboard/contact_list.html", {"contacts": contacts})


@login_required
@staff_required
def partner_list(request):
    from pages.models import Partner
    partners = Partner.objects.all()
    return render(request, "dashboard/partner_list.html", {"partners": partners})


@login_required
@staff_required
def newsletter_list(request):
    from pages.models import Newsletter
    subscribers = Newsletter.objects.all()
    return render(request, "dashboard/newsletter_list.html", {"subscribers": subscribers})


@login_required
@staff_required
def reward_settings(request):
    from rewards.models import SiteConfig
    config = SiteConfig.get_solo()
    form = SiteConfigForm(request.POST or None, instance=config)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Reward expiry set to {config.reward_expiry_days} days.")
        return redirect("dashboard:reward_settings")
    return render(request, "dashboard/reward_settings.html", {"form": form, "config": config})
