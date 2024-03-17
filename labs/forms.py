from .models import Test
from .models import Order

from django import forms


class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ["name", "description", "price", "available"]


class CompleteOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["attachment"]
