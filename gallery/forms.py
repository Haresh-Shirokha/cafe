from django import forms
from .models import OrderPhoto


class OrderPhotoForm(forms.ModelForm):
    class Meta:
        model = OrderPhoto
        fields = ["original_image"]
        widgets = {
            # capture="environment" -> mobile browsers seedha camera kholte hain
            "original_image": forms.ClearableFileInput(attrs={"capture": "environment", "accept": "image/*"}),
        }
