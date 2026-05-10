from django import forms

from .models import ResumeSettings


class ResumeSettingsForm(forms.ModelForm):
    SECTION_CHOICES = [
        ('contacts', 'Контакты'),
        ('education', 'Образование'),
        ('skills', 'Навыки'),
        ('projects', 'Проекты и работы'),
        ('achievements', 'Учебные достижения'),
        ('certificates', 'Сертификаты и курсы'),
        ('recommendations', 'Отзывы и рекомендации'),
    ]

    selected_sections = forms.MultipleChoiceField(
        choices=SECTION_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Разделы резюме',
    )

    class Meta:
        model = ResumeSettings
        fields = ('title', 'about', 'is_public', 'selected_sections')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.selected_sections:
            self.initial['selected_sections'] = self.instance.selected_sections

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.selected_sections = self.cleaned_data.get('selected_sections', [])
        if commit:
            instance.save()
        return instance
