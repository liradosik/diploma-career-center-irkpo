import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Студент'
        CURATOR = 'curator', 'Куратор'
        ADMIN = 'admin', 'Администратор'

    username = None
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    group = models.CharField(max_length=64, blank=True)
    specialty = models.CharField(max_length=255, blank=True)
    admission_year = models.PositiveIntegerField(null=True, blank=True)
    curator = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='students')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.full_name or self.email


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    phone = models.CharField(max_length=32, blank=True)
    city = models.CharField(max_length=128, blank=True)
    about = models.TextField(blank=True)
    public_resume_token = models.CharField(max_length=64, unique=True, blank=True)
    photo = models.ImageField(upload_to='students/photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.public_resume_token:
            self.public_resume_token = secrets.token_urlsafe(24)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'Профиль: {self.user.full_name}'
