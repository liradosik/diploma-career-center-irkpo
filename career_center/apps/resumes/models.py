from django.conf import settings
from django.db import models


class ResumeSettings(models.Model):
    class Template(models.TextChoices):
        CLASSIC = 'classic', 'Классический'
        COMPACT = 'compact', 'Компактный'
        MODERN = 'modern', 'Современный'
        ACADEMIC = 'academic', 'Академический'

    student = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resume_settings')
    title = models.CharField(max_length=255, default='Студент')
    about = models.TextField(blank=True)
    selected_sections = models.JSONField(default=list, blank=True)
    template = models.CharField(max_length=64, choices=Template.choices, default=Template.CLASSIC)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return f'Резюме: {self.student.full_name}'
