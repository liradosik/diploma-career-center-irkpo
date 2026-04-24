from django import forms

from .models import ResumeSettings


class ResumeSettingsForm(forms.ModelForm):
    class Meta:
        model = ResumeSettings
        fields = ('title', 'about', 'template', 'is_public')
