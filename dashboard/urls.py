from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),

    path("orders/", views.order_list, name="order_list"),
    path("orders/<uuid:order_id>/", views.order_manage, name="order_manage"),
    path("orders/<uuid:order_id>/status/<str:new_status>/", views.update_order_status, name="update_status"),
    path("orders/<uuid:order_id>/mark-paid/", views.mark_bill_paid, name="mark_bill_paid"),

    path("menu/", views.menu_manage, name="menu_manage"),
    path("menu/add/", views.menu_item_add, name="menu_item_add"),
    path("menu/<uuid:item_id>/edit/", views.menu_item_edit, name="menu_item_edit"),
    path("menu/<uuid:item_id>/delete/", views.menu_item_delete, name="menu_item_delete"),

    path("addons/", views.addon_manage, name="addon_manage"),
    path("addons/add/", views.addon_add, name="addon_add"),
    path("addons/<uuid:addon_id>/edit/", views.addon_edit, name="addon_edit"),
    path("addons/<uuid:addon_id>/delete/", views.addon_delete, name="addon_delete"),

    path("rewards/", views.reward_pool, name="reward_pool"),
    path("rewards/add/", views.reward_add, name="reward_add"),
    path("nostalgia/add/", views.nostalgia_add, name="nostalgia_add"),

    path("scratch-cards/", views.scratch_card_list, name="scratch_card_list"),
    path("scratch-cards/<uuid:card_id>/override/", views.scratch_card_override, name="scratch_card_override"),

    path("photos/", views.photo_gallery, name="photo_gallery"),
    path("photos/<uuid:photo_id>/mark-downloaded/", views.mark_photo_downloaded, name="mark_photo_downloaded"),

    path("wallet-items/", views.wallet_item_manage, name="wallet_item_manage"),
    path("wallet-items/add/", views.wallet_item_add, name="wallet_item_add"),
    path("wallet-items/<uuid:item_id>/edit/", views.wallet_item_edit, name="wallet_item_edit"),
    path("wallet-items/<uuid:item_id>/delete/", views.wallet_item_delete, name="wallet_item_delete"),

    path("wallet-redemptions/", views.wallet_redemption_list, name="wallet_redemption_list"),
    path("wallet-redemptions/<uuid:redemption_id>/fulfil/", views.wallet_redemption_fulfil, name="wallet_redemption_fulfil"),

    path("weekly-events/", views.weekly_event_manage, name="weekly_event_manage"),
    path("weekly-events/add/", views.weekly_event_add, name="weekly_event_add"),
    path("weekly-events/<int:event_id>/edit/", views.weekly_event_edit, name="weekly_event_edit"),
    path("weekly-events/<int:event_id>/delete/", views.weekly_event_delete, name="weekly_event_delete"),

    path("orders/<uuid:order_id>/email-invoice/", views.email_invoice, name="email_invoice"),

    path("reports/", views.reports_home, name="reports_home"),
    path("reports/export/<str:period>/", views.export_orders_excel, name="export_orders_excel"),

    path("reward-settings/", views.reward_settings, name="reward_settings"),

    path("users/", views.user_list, name="user_list"),

    path("rsvps/", views.rsvp_list, name="rsvp_list"),
    path("contact-messages/", views.contact_list, name="contact_list"),
    path("partner-applications/", views.partner_list, name="partner_list"),
    path("newsletter-subscribers/", views.newsletter_list, name="newsletter_list"),

]
