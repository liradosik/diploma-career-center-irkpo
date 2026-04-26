from django import forms

from .models import PortfolioEntry


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

    class Meta:
        model = PortfolioEntry
        fields = ('type', 'title', 'description', 'date', 'link', 'file')
        extra_kwargs = {
            'link': {'required': False},
            'file': {'required': False},
        }
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'title': forms.TextInput(attrs={'placeholder': 'Название достижения или проекта'}),
            'description': forms.Textarea(attrs={'placeholder': 'Опишите результат, роль и ключевые детали'}),
            'link': forms.URLInput(attrs={'placeholder': 'Ссылка (необязательно)'}),
        }
        labels = {
            'type': 'Тип записи',
            'title': 'Название',
            'description': 'Описание',
            'date': 'Дата',
            'link': 'Ссылка',
            'file': 'Файл',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type'] = forms.ChoiceField(choices=self.TYPE_CHOICES, label='Тип записи')
        self.fields['link'].required = False
        self.fields['file'].required = False
