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
        choices=ResumeSettings.PhotoSource.choices,
        label='Источник фото',
        help_text='Выберите, откуда брать фото для публичного резюме.',
    )

    class Meta:
        model = ResumeSettings
        fields = ('title', 'about', 'is_public', 'template', 'font_size', 'photo_source', 'photo', 'selected_sections')
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
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.selected_sections:
            self.initial['selected_sections'] = self.instance.selected_sections

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

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.selected_sections = self.cleaned_data.get('selected_sections', [])

        if commit:
            instance.save()

        return instance
