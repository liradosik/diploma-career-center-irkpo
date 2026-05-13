from django import forms
from django.contrib.auth.forms import AuthenticationForm

from apps.courses.models import Course
from apps.vacancies.models import Vacancy

from .models import Specialty, StudentProfile, StudyGroup, SupportTicket, User


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
        fields = ('phone', 'city', 'contact_link', 'about')
        labels = {
            'phone': 'Телефон',
            'city': 'Город',
            'contact_link': 'Дополнительный контакт',
            'about': 'О себе',
        }
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+7 (900) 123-45-67'}),
            'city': forms.TextInput(attrs={'placeholder': 'Например, Иркутск'}),
            'contact_link': forms.TextInput(attrs={'placeholder': 'VK, Telegram, ссылка или другой контакт'}),
            'about': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Кратко расскажите о себе, интересах и профессиональных целях'}),
        }


class UserStudentForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('full_name', 'photo')
        labels = {'full_name': 'ФИО', 'photo': 'Фото'}


class UserProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'full_name',
            'photo',
            'contact_phone',
            'contact_telegram',
            'contact_email',
            'contact_note',
            'contact_availability',
        )
        labels = {
            'full_name': 'ФИО',
            'photo': 'Фото',
            'contact_phone': 'Телефон',
            'contact_telegram': 'ВКонтакте или ссылка для связи',
            'contact_email': 'Контактный email',
            'contact_note': 'Комментарий для студентов',
            'contact_availability': 'Когда удобно писать',
        }
        widgets = {
            'contact_phone': forms.TextInput(attrs={'placeholder': '+7 (900) 123-45-67'}),
            'contact_telegram': forms.URLInput(attrs={'placeholder': 'https://t.me/username'}),
            'contact_email': forms.EmailInput(attrs={'placeholder': 'contact@irkpo.ru'}),
            'contact_note': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Например: Пишите по вопросам портфолио и учебного статуса'}),
            'contact_availability': forms.TextInput(attrs={'placeholder': 'Например: По будням с 9:00 до 18:00'}),
        }




class StudentAcademicReadonlyForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('group', 'specialty', 'admission_year', 'academic_status')
        labels = {
            'group': 'Группа',
            'specialty': 'Специальность',
            'admission_year': 'Год поступления',
            'academic_status': 'Учебный статус',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.disabled = True

def sync_student_with_group(user, study_group):
    user.study_group = study_group
    if study_group:
        user.group = study_group.name
        user.specialty = study_group.specialty_name
        user.admission_year = study_group.admission_year
        user.curator = study_group.curator


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
            'full_name': forms.TextInput(attrs={'placeholder': 'Например, Шадрина Нонна Ивановна'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Например, student@irkpo.ru'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['study_group'].queryset = (
            StudyGroup.objects.filter(is_active=True).select_related('curator', 'specialty_ref').order_by('name')
        )
        self.fields['study_group'].required = True
        self.fields['study_group'].empty_label = 'Выберите группу студента'
        self.fields['study_group'].widget.attrs['data-placeholder'] = 'Выберите группу студента'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        user.academic_status = User.AcademicStatus.STUDYING
        user.set_password(self.cleaned_data['password'])
        sync_student_with_group(user, self.cleaned_data.get('study_group'))
        if commit:
            user.save()
        return user


class AdminStudentUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('full_name', 'email', 'study_group', 'academic_status', 'is_active')
        labels = {
            'full_name': 'ФИО',
            'email': 'Email',
            'study_group': 'Учебная группа',
            'academic_status': 'Учебный статус',
            'is_active': 'Активен',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['study_group'].queryset = (
            StudyGroup.objects.filter(is_active=True).select_related('curator', 'specialty_ref').order_by('name')
        )
        self.fields['study_group'].empty_label = 'Выберите группу студента'
        self.fields['study_group'].widget.attrs['data-placeholder'] = 'Выберите группу студента'

    def save(self, commit=True):
        user = super().save(commit=False)
        sync_student_with_group(user, self.cleaned_data.get('study_group'))
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


class CuratorStudentAcademicStatusForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('academic_status',)
        labels = {
            'academic_status': 'Учебный статус',
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


class AdminSpecialtyForm(forms.ModelForm):
    class Meta:
        model = Specialty
        fields = ('code', 'name', 'letter_code', 'is_active')
        labels = {
            'code': 'Код специальности',
            'name': 'Название/профиль',
            'letter_code': 'Буквенный код группы',
            'is_active': 'Активна',
        }
        widgets = {
            'code': forms.TextInput(attrs={'placeholder': 'Например, 44.02.02'}),
            'name': forms.TextInput(attrs={'placeholder': 'Например, Преподавание в начальных классах'}),
            'letter_code': forms.TextInput(attrs={'placeholder': 'Например, Н'}),
        }

    def clean_letter_code(self):
        return self.cleaned_data['letter_code'].strip().upper()

    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get('code')
        letter_code = cleaned_data.get('letter_code')
        if code and letter_code:
            qs = Specialty.objects.filter(code=code, letter_code=letter_code)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Пара «код специальности + буквенный код группы» должна быть уникальной.')
        return cleaned_data


class SupportTicketCreateForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ('category', 'subject', 'message')
        labels = {
            'category': 'Категория',
            'subject': 'Тема',
            'message': 'Описание проблемы',
        }




class PublicSupportTicketCreateForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ('public_full_name', 'public_email', 'public_contact', 'requester_type', 'category', 'subject', 'message')
        labels = {
            'public_full_name': 'ФИО',
            'public_email': 'Email',
            'public_contact': 'Телефон или другой контакт',
            'requester_type': 'Кто обращается',
            'category': 'Категория',
            'subject': 'Тема',
            'message': 'Описание проблемы',
        }
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
            'public_contact': forms.TextInput(attrs={'placeholder': '+7 (900) 123-45-67 / ВКонтакте'}),
        }

class SupportTicketAdminUpdateForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ('status', 'admin_response')
        labels = {
            'status': 'Статус',
            'admin_response': 'Ответ администратора',
        }
        widgets = {
            'admin_response': forms.Textarea(attrs={'rows': 5}),
        }


class AdminStudyGroupForm(forms.ModelForm):
    class Meta:
        model = StudyGroup
        fields = ('name', 'specialty_ref', 'admission_year', 'course_number', 'curator', 'is_active')
        labels = {
            'name': 'Название группы',
            'specialty_ref': 'Специальность',
            'admission_year': 'Год поступления',
            'course_number': 'Курс',
            'curator': 'Куратор',
            'is_active': 'Активна',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Например, Н-121/1 или И-422'}),
            'admission_year': forms.NumberInput(attrs={'placeholder': 'Например, 2024'}),
            'course_number': forms.NumberInput(attrs={'placeholder': '1, 2, 3 или 4', 'min': 1, 'max': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['specialty_ref'].queryset = Specialty.objects.filter(is_active=True).order_by('code', 'name')
        self.fields['curator'].queryset = User.objects.filter(role=User.Role.CURATOR, is_active=True).order_by('full_name')
        self.fields['curator'].empty_label = 'Выберите куратора группы'
        self.fields['name'].required = False

    def clean_name(self):
        name = (self.cleaned_data.get('name') or '').strip()
        if name:
            return name

        specialty = self.cleaned_data.get('specialty_ref')
        admission_year = self.cleaned_data.get('admission_year')
        course_number = self.cleaned_data.get('course_number')
        if specialty and admission_year and course_number:
            return f'{specialty.letter_code}{course_number}{str(admission_year)[-2:]}'
        raise forms.ValidationError('Укажите название группы или заполните специальность, курс и год поступления для автозаполнения.')


class StudentImportForm(forms.Form):
    import_file = forms.FileField(label='Файл со студентами (CSV/XLSX)')


class CuratorImportForm(forms.Form):
    import_file = forms.FileField(label='Файл с кураторами (CSV/XLSX)')


class GroupImportForm(forms.Form):
    import_file = forms.FileField(label='Файл с группами (CSV/XLSX)')
