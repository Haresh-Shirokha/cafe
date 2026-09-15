def admin_badges(request):
    """Small counts shown as badges in the admin sidebar (RSVP / Contact / Partner
    submissions). Only queried for logged-in staff users to avoid extra DB hits
    on every normal customer-facing page load."""
    user = getattr(request, "user", None)
    if not (user and user.is_authenticated and user.is_staff):
        return {}
    try:
        from pages.models import RSVP, Contact, Partner
        return {
            "open_rsvp_count": RSVP.objects.count(),
            "open_contact_count": Contact.objects.count(),
            "open_partner_count": Partner.objects.count(),
        }
    except Exception:
        return {}
