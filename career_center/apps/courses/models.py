from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Course(models.Model):
    class Kind(models.TextChoices):
        COURSE = 'course', 'Курс'
        SEMINAR = 'seminar', 'Семинар'
        PRACTICE = 'practice', 'Практика'

    class Format(models.TextChoices):
        ONLINE = 'online', 'Онлайн'
        OFFLINE = 'offline', 'Очно'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        HIDDEN = 'hidden', 'Hidden'
        ARCHIVE = 'archive', 'Archive'

    title = models.CharField(max_length=255)
    kind = models.CharField(max_length=16, choices=Kind.choices)
    format_type = models.CharField(max_length=16, choices=Format.choices)
    description = models.TextField()
    organization = models.CharField(max_length=255)
    contacts = models.CharField(max_length=255)
    date = models.DateField()
    places = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def occupied_places(self):
        return self.registrations.count()

    @property
    def has_available_places(self):
        if self.format_type == self.Format.ONLINE:
            return True
        return self.occupied_places < self.places

    def __str__(self):
        return self.title


class CourseRegistration(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_registrations')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='registrations')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def clean(self):
        if self.course.format_type == Course.Format.OFFLINE and not self.course.has_available_places:
            raise ValidationError('На очный курс больше нет мест.')

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)
