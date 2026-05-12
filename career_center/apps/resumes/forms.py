from django import forms

from .models import ResumeSettings


class ResumeSettingsForm(forms.ModelForm):
    TEMPLATE_CHOICES = [
        ('classic', 'Классический'),
        ('compact', 'Компактный'),
        ('modern', 'Современный'),
        ('academic', 'Академический'),
    ]

    FONT_SIZE_CHOICES = [
        ('small', 'Компактный'),
        ('standard', 'Стандартный'),
        ('large', 'Крупный'),
    ]

    SECTION_CHOICES = [
        ('contacts', 'Контактная информация'),
        ('education', 'Образование'),
        ('skills', 'Навыки'),
        ('projects', 'Проекты и работы'),
        ('achievements', 'Достижения'),
        ('certificates', 'Сертификаты и курсы'),
        ('recommendations', 'Отзывы и рекомендации'),
    ]

    PHOTO_SOURCE_CHOICES = [
        (ResumeSettings.PhotoSource.ACCOUNT, 'Фото из аккаунта'),
        (ResumeSettings.PhotoSource.CUSTOM, 'Отдельное фото для резюме'),
        (ResumeSettings.PhotoSource.HIDDEN, 'Не показывать фото'),
    ]

    selected_sections = forms.MultipleChoiceField(
        choices=SECTION_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Разделы резюме',
    )

    template = forms.ChoiceField(
        choices=TEMPLATE_CHOICES,
        label='Шаблон',
    )

    font_size = forms.ChoiceField(
        choices=FONT_SIZE_CHOICES,
        label='Размер шрифта',
    )

    photo_source = forms.ChoiceField(
        choices=PHOTO_SOURCE_CHOICES,
        label='Источник фото',
        help_text='Выберите, какое фото показывать в публичном резюме.',
    )

    class Meta:
        model = ResumeSettings
        fields = (
            'title',
            'about',
            'is_public',
            'template',
            'font_size',
            'photo_source',
            'photo',
            'selected_sections',
        )
        labels = {
            'title': 'Заголовок',
            'about': 'О себе',
            'is_public': 'Публичное резюме',
            'template': 'Шаблон',
            'font_size': 'Размер шрифта',
            'photo': 'Отдельное фото резюме',
        }
        help_texts = {
            'photo': 'Используется только если выбран источник «Отдельное фото для резюме».',
        }
        widgets = {
            'about': forms.Textarea(attrs={'rows': 6}),
            'photo': forms.FileInput(attrs={
                'accept': 'image/*',
                'class': 'student-resume-photo-native',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.selected_sections:
            self.initial['selected_sections'] = self.instance.selected_sections

        if self.instance and self.instance.photo_source == ResumeSettings.PhotoSource.PROFILE:
            self.initial['photo_source'] = ResumeSettings.PhotoSource.ACCOUNT

        self.fields['title'].widget.attrs.update({
            'data-preview': 'title',
            'placeholder': 'Например: Начинающий web-дизайнер',
        })
        self.fields['about'].widget.attrs.update({
            'data-preview': 'about',
            'placeholder': 'Кратко расскажите о себе, навыках, интересах и опыте.',
        })
        self.fields['template'].widget.attrs.update({'data-preview': 'template'})
        self.fields['font_size'].widget.attrs.update({'data-preview': 'font-size'})
        self.fields['photo_source'].widget.attrs.update({'class': 'student-resume-photo-select'})
        self.fields['photo'].widget.attrs.update({'class': 'student-resume-photo-input'})

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.selected_sections = self.cleaned_data.get('selected_sections', [])

        if commit:
            instance.save()

        return instance