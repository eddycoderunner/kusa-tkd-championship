from django import forms
from .models import Competitor


class CompetitorForm(forms.ModelForm):
    class Meta:
        model = Competitor
        fields = [
            'full_name',
            'reg_no',
            'weight_category',
            'gender',
            'school',
            'phone',
            'is_seeded',
        ]
        labels = {
            'is_seeded': 'Is black belt',
        }
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'reg_no': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 15}),
            'weight_category': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'school': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 10}),
        }