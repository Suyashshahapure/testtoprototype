from django import forms
from .models import User
from allauth.account.forms import SignupForm
import json


class CustomerUserForm(forms.ModelForm):
    address = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "name": "address",
                "autocomplete": "shipping address-line1",
                "placeholder": "Address",
            }
        )
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "address", "email", "password"]

    def save(self, commit=True):
        user = super(CustomerUserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.is_lab_user = False
            user.save()
        return user

    def clean_address(self):
        address = self.cleaned_data["address"]
        try:
            address = json.loads(address)
        except:
            raise forms.ValidationError("Invalid address")
        return address


class LabForm(CustomerUserForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "address",
            "email",
            "password",
            "pincode",
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.is_lab_user = True
            user.save()
        return user

    def clean_address(self):
        address = self.cleaned_data["address"]
        try:
            address = json.loads(address)
        except:
            raise forms.ValidationError("Invalid address")
        return address
