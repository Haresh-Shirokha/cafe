from django.urls import path
from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about_view, name="about"),
    path("community/", views.community_view, name="community"),
    path("experiences/", views.experiences_view, name="experiences"),
    path("events/", views.weekly_events, name="weekly_events"),
    path("rsvp/", views.rsvp_view, name="rsvp"),
    path("partner-with-us/", views.partner_view, name="partner"),
    path("newsletter/", views.newsletter_signup, name="newsletter"),
    path("contact/", views.contact_view, name="contact"),
]
