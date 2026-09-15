from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from .models import WalletItem, WalletTransaction, WalletRedemption


@login_required
def wallet_home(request):
    """
    Wallet tab: current points balance, earn/redeem history, aur redeemable
    items (jaise 1000 points = Free Chai).
    """
    user = request.user
    items = WalletItem.objects.filter(is_active=True)
    transactions = user.wallet_transactions.all()[:50]
    redemptions = user.wallet_redemptions.select_related("item").all()

    return render(request, "wallet/home.html", {
        "items": items,
        "transactions": transactions,
        "redemptions": redemptions,
    })


@login_required
def redeem_item(request, item_id):
    item = get_object_or_404(WalletItem, id=item_id, is_active=True)
    user = request.user

    if user.points < item.points_required:
        messages.error(request, f"Not enough points. You have {user.points} points, {item.points_required} required.")
        return redirect("wallet:home")

    with transaction.atomic():
        user.points -= item.points_required
        user.save(update_fields=["points"])

        WalletTransaction.objects.create(
            user=user, type="redeem", points=-item.points_required,
            description=f"Redeemed: {item.name}",
        )
        redemption = WalletRedemption.objects.create(
            user=user, item=item, points_spent=item.points_required,
        )

    messages.success(request, f"{item.name} redeemed! Show this code at the counter: {redemption.redemption_code}")
    return redirect("wallet:home")
