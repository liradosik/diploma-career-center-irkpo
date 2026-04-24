from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import StudentProfile, User


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email')


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ('phone', 'city', 'about', 'photo')


class UserStudentForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('full_name', 'group', 'specialty', 'admission_year')
