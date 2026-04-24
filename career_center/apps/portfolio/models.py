from django.conf import settings
from django.db import models


class PortfolioEntry(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает проверки'
        APPROVED = 'approved', 'Подтверждено'
        REJECTED = 'rejected', 'Отклонено'

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portfolio_entries')
    type = models.CharField(max_length=64)
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    link = models.URLField(blank=True)
    file = models.FileField(upload_to='portfolio/files/', blank=True, null=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    curator_comment = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_portfolio_entries'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
