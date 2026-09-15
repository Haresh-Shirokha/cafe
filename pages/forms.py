from django import forms
from .models import RSVP, Partner, Newsletter, Contact


class RSVPForm(forms.ModelForm):
    class Meta:
        model = RSVP
        fields = ["name", "email", "phone", "event", "guests", "visit_date", "message"]
        widgets = {"visit_date": forms.DateInput(attrs={"type": "date"})}


class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = ["name", "email", "phone", "partner_type", "brand_name", "message"]


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ["email"]


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["name", "email", "subject", "message"]
