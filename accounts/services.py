import random
from datetime import timedelta
from django.utils import timezone
from .models import PhoneOTP


def generate_and_send_otp(phone, purpose):
    """
    Ek 6-digit OTP banata hai, DB me save karta hai (5 min expiry), aur
    'bhejta' hai — DEV MODE me sirf console/terminal par print hota hai.

    PRODUCTION me: yahan apna SMS gateway (Twilio / MSG91 / Fast2SMS / etc.)
    ka API call add kar dena, jaise:
        requests.post("https://api.msg91.com/...", data={"mobile": phone, "otp": otp_code})
    """
    otp_code = f"{random.randint(100000, 999999)}"
    expires_at = timezone.now() + timedelta(minutes=5)
    PhoneOTP.objects.create(phone=phone, otp_code=otp_code, purpose=purpose, expires_at=expires_at)

    print(f"\n{'='*50}\nOTP for {phone} ({purpose}): {otp_code}\n(This is dev console only — no real SMS was sent)\n{'='*50}\n")
    return otp_code


def verify_otp(phone, otp_code, purpose):
    """Latest matching, non-expired, unverified OTP dhoondh kar verify karta hai."""
    record = PhoneOTP.objects.filter(
        phone=phone, purpose=purpose, is_verified=False
    ).order_by("-created_at").first()

    if not record:
        return False, "No OTP found. Please request again."
    if record.is_expired():
        return False, "OTP has expired. Please request again."
    if record.otp_code != otp_code:
        return False, "Incorrect OTP."

    record.is_verified = True
    record.save(update_fields=["is_verified"])
    return True, "OTP verify ho gaya."
