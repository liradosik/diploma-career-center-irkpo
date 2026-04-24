from django import forms

from .models import PortfolioEntry


class PortfolioEntryForm(forms.ModelForm):
    class Meta:
        model = PortfolioEntry
        fields = ('type', 'title', 'description', 'date', 'link', 'file')
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}
