from django import forms
from django.contrib.auth.forms import AuthenticationForm

from apps.courses.models import Course
from apps.vacancies.models import Vacancy

from .models import StudentProfile, StudyGroup, User


RUS_STATUS_CHOICES = [
    ('active', 'Активно'),
    ('hidden', 'Скрыто'),
    ('archive', 'Архив'),
]
RUS_KIND_CHOICES = [
    ('course', 'Курс'),
    ('seminar', 'Семинар'),
    ('practice', 'Практика'),
]
RUS_FORMAT_CHOICES = [
    ('online', 'Онлайн'),
    ('offline', 'Очно'),
]


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
    password = forms.CharField(
        label='Временный пароль',
        help_text='Используйте минимум 8 символов.',
        widget=forms.PasswordInput(attrs={'placeholder': 'Минимум 8 символов'}),
    )

    class Meta:
        model = User
        fields = ('full_name', 'email', 'password', 'study_group')
        labels = {
            'full_name': 'ФИО',
            'email': 'Email',
            'study_group': 'Учебная группа',
        }
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Например, Дашинова Валерия Михайловна'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Например, student@irkpo.ru'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['study_group'].queryset = StudyGroup.objects.select_related('curator').order_by('name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        user.set_password(self.cleaned_data['password'])
        group = self.cleaned_data.get('study_group')
        if group:
            user.group = group.name
            user.specialty = group.specialty
            user.admission_year = group.admission_year
            user.curator = group.curator
        if commit:
            user.save()
        return user


class AdminStudentUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('full_name', 'email', 'study_group', 'is_active')
        labels = {
            'full_name': 'ФИО',
            'email': 'Email',
            'study_group': 'Учебная группа',
            'is_active': 'Активен',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['study_group'].queryset = StudyGroup.objects.select_related('curator').order_by('name')

    def save(self, commit=True):
        user = super().save(commit=False)
        group = self.cleaned_data.get('study_group')
        if group:
            user.group = group.name
            user.specialty = group.specialty
            user.admission_year = group.admission_year
            user.curator = group.curator
        if commit:
            user.save()
        return user


class AdminCuratorCreateForm(forms.ModelForm):
    password = forms.CharField(
        label='Временный пароль',
        help_text='Используйте минимум 8 символов.',
        widget=forms.PasswordInput(attrs={'placeholder': 'Минимум 8 символов'}),
    )

    class Meta:
        model = User
        fields = ('full_name', 'email', 'password')
        labels = {
            'full_name': 'ФИО',
            'email': 'Email',
        }
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Например, Иванова Ольга Сергеевна'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Например, curator@irkpo.ru'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.CURATOR
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class AdminCuratorUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('full_name', 'email', 'is_active')
        labels = {
            'full_name': 'ФИО',
            'email': 'Email',
            'is_active': 'Активен',
        }


class AdminVacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = (
            'title', 'company', 'description', 'responsibilities', 'requirements', 'conditions',
            'contacts', 'employment_type', 'format_type', 'direction', 'status'
        )
        labels = {
            'title': 'Название',
            'company': 'Компания',
            'description': 'Описание',
            'responsibilities': 'Обязанности',
            'requirements': 'Требования',
            'conditions': 'Условия',
            'contacts': 'Контакты',
            'employment_type': 'Тип занятости',
            'format_type': 'Формат',
            'direction': 'Направление',
            'status': 'Статус',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = RUS_STATUS_CHOICES


class AdminCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = (
            'title', 'kind', 'format_type', 'description', 'organization', 'contacts', 'date', 'places', 'status'
        )
        labels = {
            'title': 'Название',
            'kind': 'Тип',
            'format_type': 'Формат',
            'description': 'Описание',
            'organization': 'Организация',
            'contacts': 'Контакты',
            'date': 'Дата',
            'places': 'Количество мест',
            'status': 'Статус',
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = RUS_STATUS_CHOICES
        self.fields['kind'].choices = RUS_KIND_CHOICES
        self.fields['format_type'].choices = RUS_FORMAT_CHOICES
