from django import forms

from .models import PortfolioAttachment, PortfolioEntry


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if not data:
            return []

        if isinstance(data, (list, tuple)):
            result = []
            for file in data:
                result.append(super(MultipleFileField, self).clean(file, initial))
            return result

        return [super().clean(data, initial)]


class PortfolioEntryForm(forms.ModelForm):
    TYPE_CHOICES = [
        ('academic', 'Учебные достижения'),
        ('project', 'Проекты и работы'),
        ('skill', 'Навыки'),
        ('recommendation', 'Отзывы и рекомендации'),
        ('creative', 'Творческая деятельность'),
        ('sport', 'Спортивная деятельность'),
        ('social', 'Общественная деятельность'),
    ]

    attachments = MultipleFileField(
        required=False,
        label='Вложения',
        widget=MultipleFileInput(
            attrs={
                'multiple': True,
                'accept': '.pdf,.jpg,.jpeg,.png,.doc,.docx,.zip',
            }
        ),
        help_text='Можно прикрепить несколько файлов: PDF, JPG/JPEG/PNG, DOC/DOCX, ZIP.',
    )

    class Meta:
        model = PortfolioEntry
        fields = ('type', 'title', 'description', 'date', 'link')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'title': forms.TextInput(attrs={'placeholder': 'Название достижения или проекта'}),
            'description': forms.Textarea(attrs={'placeholder': 'Опишите результат, роль и ключевые детали'}),
            'link': forms.URLInput(attrs={'placeholder': 'Ссылка (необязательно)'}),
        }
        labels = {
            'type': 'Раздел портфолио',
            'title': 'Название',
            'description': 'Описание',
            'date': 'Дата / год',
            'link': 'Ссылка',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'] = forms.ChoiceField(choices=self.TYPE_CHOICES, label='Раздел портфолио')
        self.fields['link'].required = False

    def clean_attachments(self):
        files = self.files.getlist('attachments')
        validator = PortfolioAttachment._meta.get_field('file').validators[0]

        for file in files:
            validator(file)

        return files