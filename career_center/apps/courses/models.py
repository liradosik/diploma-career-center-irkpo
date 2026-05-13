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

    class Meta:
        indexes = [
            models.Index(fields=['status', 'date'], name='course_status_date_idx'),
            models.Index(fields=['kind', 'status'], name='course_kind_status_idx'),
            models.Index(fields=['format_type', 'status'], name='course_format_status_idx'),
        ]

    @property
    def occupied_places(self):
        return self.registrations.filter(status=CourseRegistration.Status.REGISTERED).count()

    @property
    def has_available_places(self):
        if self.format_type == self.Format.ONLINE:
            return True
        return self.occupied_places < self.places

    def __str__(self):
        return self.title


class CourseRegistration(models.Model):
    class Status(models.TextChoices):
        REGISTERED = 'registered', 'Записан'
        CANCELLED = 'cancelled', 'Отменена'

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='course_registrations')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='registrations')
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.REGISTERED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('student', 'course'), condition=models.Q(status='registered'), name='uniq_active_course_registration'),
        ]

    def clean(self):
        if self.course.format_type == Course.Format.OFFLINE and not self.course.has_available_places:
            raise ValidationError('На очный курс больше нет мест.')

    def save(self, *args, **kwargs):
        self.clean()
        return super().save(*args, **kwargs)


class StudentFavoriteCourse(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorite_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='favorited_by_students')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('student', 'course'), name='uniq_student_favorite_course'),
        ]

    def __str__(self):
        return f'{self.student} ♥ {self.course}'
