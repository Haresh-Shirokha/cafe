from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("post-login-redirect/", views.post_login_redirect, name="post_login_redirect"),
    path("profile/", views.profile_view, name="profile"),

    # Phone + OTP signup (naya default flow — phone + email se signup)
    path("signup/phone/", views.signup_phone_start, name="signup_phone_start"),
    path("signup/phone/verify/", views.signup_verify_otp, name="signup_verify_otp"),
    path("signup/phone/complete/", views.signup_complete_profile, name="signup_complete_profile"),

    # Phone + OTP login (naya default flow — normal users ke liye)
    path("login/phone/", views.login_phone_start, name="login_phone_start"),
    path("login/phone/verify/", views.login_verify_otp, name="login_verify_otp"),
]
