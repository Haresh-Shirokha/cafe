from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from .models import ScratchCard


@login_required
def reveal_card(request, card_id):
    """
    Scratch card reveal karna sirf COSMETIC hai -- is se koi wallet points
    nahi milte. Real wallet points ab sirf tab milte hain jab admin order
    ka bill payment 'Paid' mark karta hai (dashboard/views.py -> mark_bill_paid).

    GET  -> interactive "scratch the card" page (canvas scratch-off).
    POST -> called by that page's JS once the user has actually scratched
            enough of the card; marks it revealed and returns JSON.
    """
    card = get_object_or_404(ScratchCard, id=card_id, user=request.user)

    if not card.reward:
        messages.warning(request, "Please wait, your reward is being assigned.")
        return redirect("accounts:profile")

    if request.method == "POST":
        if not card.revealed:
            card.revealed = True
            card.save(update_fields=["revealed"])
        return JsonResponse({"ok": True, "reward_label": card.reward_label, "reward_code": card.reward_code})

    if card.revealed:
        # Already scratched earlier -- nothing left to do, back to profile.
        return redirect("accounts:profile")

    return render(request, "rewards/scratch_card.html", {"card": card})
