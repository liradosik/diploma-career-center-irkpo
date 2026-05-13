from django.conf import settings
from django.db import models


class Vacancy(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        HIDDEN = 'hidden', 'Hidden'
        ARCHIVE = 'archive', 'Archive'

    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    description = models.TextField()
    responsibilities = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    conditions = models.TextField(blank=True)
    contacts = models.CharField(max_length=255)
    employment_type = models.CharField(max_length=120)
    format_type = models.CharField(max_length=120)
    direction = models.CharField(max_length=120)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', '-created_at'], name='vacancy_status_created_idx'),
        ]

    def __str__(self):
        return f'{self.title} ({self.company})'


class VacancyResponse(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vacancy_responses')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='responses')
    created_at = models.DateTimeField(auto_now_add=True)
    resume_link_snapshot = models.URLField(blank=True)

    class Meta:
        unique_together = ('student', 'vacancy')

    def __str__(self):
        return f'{self.student} -> {self.vacancy}'


class StudentFavoriteVacancy(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorite_vacancies')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='favorited_by_students')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('student', 'vacancy'), name='uniq_student_favorite_vacancy'),
        ]

    def __str__(self):
        return f'{self.student} ♥ {self.vacancy}'
