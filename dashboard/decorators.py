from django.contrib.auth.decorators import user_passes_test

staff_required = user_passes_test(lambda u: u.is_active and u.is_staff, login_url="accounts:login")
