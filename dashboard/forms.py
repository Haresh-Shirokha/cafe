from django import forms
from menu.models import MenuItem, Category, AddOn
from rewards.models import Reward, Nostalgia
from wallet.models import WalletItem
from pages.models import WeeklyEvent


class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ["category", "name", "description", "price", "image", "is_available"]


class AddOnForm(forms.ModelForm):
    applicable_items = forms.ModelMultipleChoiceField(
        queryset=MenuItem.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Which menu items can this add-on be applied to?",
    )

    class Meta:
        model = AddOn
        fields = ["name", "price", "applicable_items", "is_active"]


class RewardForm(forms.ModelForm):
    class Meta:
        model = Reward
        fields = ["cards", "code", "reward", "is_active"]


class NostalgiaForm(forms.ModelForm):
    class Meta:
        model = Nostalgia
        fields = ["title", "story"]


class ScratchCardOverrideForm(forms.Form):
    reward = forms.ModelChoiceField(queryset=Reward.objects.filter(is_active=True), required=False)
    nostalgia = forms.ModelChoiceField(queryset=Nostalgia.objects.all(), required=False)


class WalletItemForm(forms.ModelForm):
    class Meta:
        model = WalletItem
        fields = ["name", "description", "points_required", "image", "is_active"]


class WeeklyEventForm(forms.ModelForm):
    class Meta:
        model = WeeklyEvent
        fields = ["day", "title", "tag", "description", "time"]
        widgets = {
            # Native clock picker instead of free typing. The model field
            # stays a plain CharField (e.g. "19:00"), so this needs no
            # migration and still accepts whatever the browser sends.
            "time": forms.TimeInput(attrs={"type": "time"}),
        }


class SiteConfigForm(forms.ModelForm):
    class Meta:
        from rewards.models import SiteConfig
        model = SiteConfig
        fields = ["reward_expiry_days"]
