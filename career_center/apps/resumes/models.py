from django.conf import settings
from django.db import models


class ResumeSettings(models.Model):
    class Template(models.TextChoices):
        CLASSIC = 'classic', 'Классический'
        COMPACT = 'compact', 'Компактный'
        MODERN = 'modern', 'Современный'
        ACADEMIC = 'academic', 'Академический'

    class PhotoSource(models.TextChoices):
        # Оставлено только для обратной совместимости со старыми записями в БД.
        # В форме этот вариант больше не показывается.
        PROFILE = 'profile', 'Из профиля студента'

        ACCOUNT = 'account', 'Фото из аккаунта'
        CUSTOM = 'custom', 'Отдельное фото для резюме'
        HIDDEN = 'hidden', 'Не показывать фото'

    class FontSize(models.TextChoices):
        SMALL = 'small', 'Компактный'
        STANDARD = 'standard', 'Стандартный'
        LARGE = 'large', 'Крупный'

    student = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resume_settings')
    title = models.CharField(max_length=255, default='Студент')
    about = models.TextField(blank=True)
    selected_sections = models.JSONField(default=list, blank=True)
    template = models.CharField(max_length=64, choices=Template.choices, default=Template.CLASSIC)
    font_size = models.CharField(max_length=32, choices=FontSize.choices, default=FontSize.STANDARD)
    is_public = models.BooleanField(default=True)
    photo_source = models.CharField(max_length=32, choices=PhotoSource.choices, default=PhotoSource.ACCOUNT)
    photo = models.ImageField(upload_to='resume_photos/', blank=True, null=True)

    def __str__(self):
        return f'Резюме: {self.student.full_name}'