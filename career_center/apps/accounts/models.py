import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models


class Specialty(models.Model):
    code = models.CharField(max_length=32)
    name = models.CharField(max_length=255)
    letter_code = models.CharField(max_length=4)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('code', 'name')
        constraints = [
            models.UniqueConstraint(fields=('code', 'letter_code'), name='accounts_specialty_code_letter_uniq')
        ]

    def __str__(self):
        return f'{self.code} — {self.name}'


class StudyGroup(models.Model):
    name = models.CharField(max_length=64, unique=True)
    specialty = models.CharField(max_length=255)
    specialty_ref = models.ForeignKey(
        Specialty, null=True, blank=True, on_delete=models.SET_NULL, related_name='study_groups'
    )
    admission_year = models.PositiveIntegerField()
    course_number = models.PositiveSmallIntegerField(default=1)
    curator = models.ForeignKey('User', null=True, blank=True, on_delete=models.SET_NULL, related_name='managed_study_groups')
    is_active = models.BooleanField(default=True)

    @property
    def specialty_name(self):
        return self.specialty_ref.name if self.specialty_ref else self.specialty

    @property
    def specialty_letter(self):
        return self.specialty_ref.letter_code if self.specialty_ref else ''

    def __str__(self):
        return self.name


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
    study_group = models.ForeignKey(StudyGroup, null=True, blank=True, on_delete=models.SET_NULL, related_name='students')

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
