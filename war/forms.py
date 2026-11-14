from django import forms
from .models import FighterUnit

class FighterUnitForm(forms.ModelForm):
    class Meta:
        model = FighterUnit
        fields = ['name', 'unit_type', 'team', 'health', 'attack_points', 'profile_image_link']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: General Deadlock'}),
            'unit_type': forms.Select(attrs={'class': 'form-select'}),
            'team': forms.Select(attrs={'class': 'form-select'}),
            'health': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100, 'value': 100}),
            'attack_points': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 50}),
            'profile_image_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }

    # Metodă opțională de validare custom, deși validatoarele din model își fac deja treaba
    def clean_health(self):
        health = self.cleaned_data.get('health')
        if health < 0 or health > 100:
            raise forms.ValidationError("Sănătatea trebuie să fie între 0 și 100.")
        return health