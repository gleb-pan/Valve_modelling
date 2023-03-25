from django import forms
from .models import ValveParams


class UserInputForm(forms.ModelForm):
    class Meta:
        model = ValveParams
        fields = '__all__'
