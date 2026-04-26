from django import forms
from django.contrib.auth.forms import AuthenticationForm

from apps.courses.models import Course
from apps.vacancies.models import Vacancy

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


class AdminStudentCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('full_name', 'email', 'password', 'group', 'specialty', 'admission_year', 'curator')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['curator'].queryset = User.objects.filter(role=User.Role.CURATOR).order_by('full_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class AdminCuratorCreateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('full_name', 'email', 'password')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.CURATOR
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class AdminVacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = (
            'title', 'company', 'description', 'responsibilities', 'requirements', 'conditions',
            'contacts', 'employment_type', 'format_type', 'direction', 'status'
        )


class AdminCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = (
            'title', 'kind', 'format_type', 'description', 'organization', 'contacts', 'date', 'places', 'status'
        )
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
