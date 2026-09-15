from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class SignUpForm(UserCreationForm):
    """Purana username/password based signup — abhi admin/staff creation ke liye rakha hai."""
    email = forms.EmailField(required=True)
    referred_by = forms.CharField(required=False, help_text="Referral code (optional)")

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "referred_by", "password1", "password2")


class LoginForm(forms.Form):
    """Purana username/password login — admin/staff ke liye."""
    username = forms.CharField(label="Username or Email")
    password = forms.CharField(widget=forms.PasswordInput)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "phone", "picture")

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        qs = User.objects.filter(username=username).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("That username is already taken.")
        return username


# ---------------- PHONE + OTP FLOW (normal users) ----------------

class PhoneSignupStartForm(forms.Form):
    phone = forms.CharField(label="Phone Number", max_length=15)
    email = forms.EmailField(label="Email")

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("An account already exists with this phone number. Please log in.")
        return phone

    def clean_email(self):
        email = self.cleaned_data["email"].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account already exists with this email.")
        return email


class OTPVerifyForm(forms.Form):
    otp_code = forms.CharField(label="OTP", max_length=6, min_length=6)


class CompleteProfileForm(forms.Form):
    """OTP verify hone ke baad user apni baaki details (username, password, naam) fill karta hai."""
    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150, required=False)
    last_name = forms.CharField(max_length=150, required=False)
    referred_by = forms.CharField(required=False, help_text="Referral code (optional)")
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("The passwords do not match.")
        return cleaned


class PhoneLoginStartForm(forms.Form):
    phone = forms.CharField(label="Phone Number", max_length=15)

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if not User.objects.filter(phone=phone).exists():
            raise forms.ValidationError("No account found with this phone number. Please sign up first.")
        return phone
