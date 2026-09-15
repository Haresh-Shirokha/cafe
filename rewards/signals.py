import random
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from orders.models import Order
from rewards.models import ScratchCard, Reward, Nostalgia, SiteConfig


@receiver(post_save, sender=Order)
def auto_generate_scratch_card(sender, instance, created, **kwargs):
    """
    Order place hote hi (Order create hote hi) automatically:
      1. Order par ek ScratchCard bana deta hai
      2. Random active Reward + random Nostalgia assign kar deta hai (cosmetic prize)
      3. Card ka expires_at set kar deta hai — SiteConfig.reward_expiry_days
         (admin dashboard se customizable, default 60 din) ke hisaab se.

    NOTE: Ab yahan WALLET POINTS award NAHI hote. Points sirf tab milte hain
    jab admin BILL PAID mark karta hai — dekho dashboard/views.py -> mark_bill_paid().
    Admin baad me dashboard se scratch card ka reward MANUALLY override bhi
    kar sakta hai (jab tak user ne use reveal na kiya ho).
    """
    if not created:
        return

    order = instance
    card, _ = ScratchCard.objects.get_or_create(order=order, user=order.user)

    if not card.reward:
        active_rewards = list(Reward.objects.filter(is_active=True))
        if active_rewards:
            chosen = random.choice(active_rewards)
            card.reward = chosen
            card.reward_code = chosen.code
            card.reward_label = chosen.reward

    if not card.nostalgia:
        nostalgias = list(Nostalgia.objects.all())
        if nostalgias:
            card.nostalgia = random.choice(nostalgias)

    if not card.expires_at:
        config = SiteConfig.get_solo()
        card.expires_at = timezone.now() + timedelta(days=config.reward_expiry_days)

    card.save()
