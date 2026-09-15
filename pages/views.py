from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import RSVPForm, PartnerForm, NewsletterForm, ContactForm
from .models import WeeklyEvent


def home(request):
    events = WeeklyEvent.objects.all()[:6]
    return render(request, "pages/home.html", {"events": events})


def about_view(request):
    return render(request, "pages/about.html")


def community_view(request):
    return render(request, "pages/community.html")


def experiences_view(request):
    events = WeeklyEvent.objects.all()
    return render(request, "pages/experiences.html", {"events": events})


def weekly_events(request):
    events = WeeklyEvent.objects.all()
    return render(request, "pages/weekly_events.html", {"events": events})


def rsvp_view(request):
    form = RSVPForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "RSVP submitted successfully!")
        return redirect("pages:rsvp")
    return render(request, "pages/rsvp.html", {"form": form})


def partner_view(request):
    form = PartnerForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Partner request submitted successfully!")
        return redirect("pages:partner")
    return render(request, "pages/partner.html", {"form": form})


def newsletter_signup(request):
    form = NewsletterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Subscribed to the newsletter successfully!")
        return redirect("pages:home")
    return render(request, "pages/newsletter.html", {"form": form})


def contact_view(request):
    form = ContactForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your message has been sent!")
        return redirect("pages:contact")
    return render(request, "pages/contact.html", {"form": form})
