import uuid
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import (
    SignUpForm, LoginForm, ProfileForm,
    PhoneSignupStartForm, OTPVerifyForm, CompleteProfileForm, PhoneLoginStartForm,
)
from .models import User
from .services import generate_and_send_otp, verify_otp


def _generate_username_from_phone(phone):
    """Turns a phone number into a unique, safe default username so the
    account can be created the instant OTP is verified — no forced form."""
    digits = "".join(ch for ch in phone if ch.isdigit())
    base = f"user{digits[-10:]}" if digits else f"user{uuid.uuid4().hex[:8]}"
    username = base
    suffix = 1
    while User.objects.filter(username=username).exists():
        suffix += 1
        username = f"{base}{suffix}"
    return username


def signup_view(request):
    """
    Purana username/password signup — ab is URL se seedha phone-based
    signup par redirect kar diya jaata hai (naya default flow).
    """
    return redirect("accounts:signup_phone_start")


def login_view(request):
    """
    Purana username/password login — ADMIN/STAFF ke liye rakha hai.
    Normal users ab phone+OTP se login karte hain (accounts:login_phone_start).
    """
    if request.user.is_authenticated:
        return redirect("accounts:post_login_redirect")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user_obj = User.objects.filter(email__iexact=identifier).first()
            username = user_obj.username if user_obj else identifier

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                request.session.set_expiry(60 * 60 * 24 * 365)  # 1 saal — dobara login na karna pade
                return redirect("accounts:post_login_redirect")
            messages.error(request, "Incorrect username/email or password.")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("pages:home")


@login_required
def post_login_redirect(request):
    if request.user.is_staff:
        return redirect("dashboard:home")
    return redirect("accounts:profile")


@login_required
def profile_view(request):
    """
    Normal user: apna naam, profile photo, order history, reward history dekhta hai.
    Admin/staff: yahi profile page par sab users ke recent orders ka LIVE FEED dikhta
    hai — jaise hi koi order aata hai, admin ko yahin dikh jaata hai (naya order,
    status, live timer, delivered orders ka final time — sab kuch).
    """
    from orders.models import Order

    user = request.user
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=user)

    if user.is_staff:
        recent_orders = Order.objects.select_related("user").prefetch_related("items")[:30]
        pending_orders = Order.objects.exclude(status="delivered").count()
        return render(request, "accounts/profile.html", {
            "form": form,
            "is_admin_view": True,
            "recent_orders": recent_orders,
            "pending_orders": pending_orders,
        })

    orders = user.orders.all().prefetch_related("items")
    scratch_cards = user.scratch_cards.select_related("reward", "nostalgia", "order")

    # Reward expiry popup — jo unrevealed cards expire ho chuke hain ya jaldi honge (7 din ke andar)
    expiring_soon = [c for c in scratch_cards if not c.revealed and c.days_left is not None and c.days_left <= 7]
    already_expired = [c for c in scratch_cards if c.is_expired]

    return render(request, "accounts/profile.html", {
        "form": form,
        "orders": orders,
        "scratch_cards": scratch_cards,
        "expiring_soon": expiring_soon,
        "already_expired": already_expired,
        "show_reward_popup": bool(expiring_soon or already_expired),
    })


# =====================================================================
# PHONE + OTP SIGNUP FLOW
#   Step 1: phone + email daalo -> OTP jaata hai
#   Step 2: OTP verify karo
#   Step 3: baaki profile (username, password, naam) fill karo -> account ban jaata hai
# =====================================================================

def signup_phone_start(request):
    if request.user.is_authenticated:
        return redirect("accounts:post_login_redirect")

    form = PhoneSignupStartForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        phone = form.cleaned_data["phone"]
        email = form.cleaned_data["email"]
        generate_and_send_otp(phone, purpose="signup")
        request.session["signup_phone"] = phone
        request.session["signup_email"] = email
        messages.info(request, f"OTP sent to {phone} (dev mode: check the terminal/console).")
        return redirect("accounts:signup_verify_otp")
    return render(request, "accounts/signup_phone.html", {"form": form})


def signup_verify_otp(request):
    phone = request.session.get("signup_phone")
    email = request.session.get("signup_email")
    if not phone:
        messages.error(request, "Please enter your phone number and email first.")
        return redirect("accounts:signup_phone_start")

    form = OTPVerifyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        ok, msg = verify_otp(phone, form.cleaned_data["otp_code"], purpose="signup")
        if ok:
            # OTP is verified -> create the account and log the user in
            # immediately. No extra form standing in the way. They can add
            # their name, photo etc. any time later from their profile page.
            username = _generate_username_from_phone(phone)
            user = User.objects.create_user(username=username, email=email, phone=phone)

            for key in ["signup_phone", "signup_email"]:
                request.session.pop(key, None)

            login(request, user)
            request.session.set_expiry(60 * 60 * 24 * 365)  # 1 saal — dobara login na karna pade
            messages.success(
                request,
                "You're in! Add your name and photo any time from your profile.",
            )
            return redirect("accounts:profile")
        messages.error(request, msg)
    return render(request, "accounts/verify_otp.html", {"form": form, "phone": phone, "purpose": "signup"})


def signup_complete_profile(request):
    # Kept only so any old bookmarked/shared link doesn't 404 — the signup
    # flow no longer forces this step (see signup_verify_otp above).
    if request.user.is_authenticated:
        return redirect("accounts:profile")
    return redirect("accounts:signup_phone_start")


# =====================================================================
# PHONE + OTP LOGIN FLOW
#   Step 1: phone number daalo -> OTP jaata hai
#   Step 2: OTP verify karo -> login ho jaata hai
# =====================================================================

def login_phone_start(request):
    if request.user.is_authenticated:
        return redirect("accounts:post_login_redirect")

    form = PhoneLoginStartForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        phone = form.cleaned_data["phone"]
        generate_and_send_otp(phone, purpose="login")
        request.session["login_phone"] = phone
        messages.info(request, f"OTP sent to {phone} (dev mode: check the terminal/console).")
        return redirect("accounts:login_verify_otp")
    return render(request, "accounts/login_phone.html", {"form": form})


def login_verify_otp(request):
    phone = request.session.get("login_phone")
    if not phone:
        messages.error(request, "Please enter your phone number first.")
        return redirect("accounts:login_phone_start")

    form = OTPVerifyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        ok, msg = verify_otp(phone, form.cleaned_data["otp_code"], purpose="login")
        if ok:
            user = User.objects.filter(phone=phone).first()
            if user:
                request.session.pop("login_phone", None)
                login(request, user)
                request.session.set_expiry(60 * 60 * 24 * 365)  # 1 saal — dobara login na karna pade
                return redirect("accounts:post_login_redirect")
            messages.error(request, "Account not found.")
        else:
            messages.error(request, msg)
    return render(request, "accounts/verify_otp.html", {"form": form, "phone": phone, "purpose": "login"})
