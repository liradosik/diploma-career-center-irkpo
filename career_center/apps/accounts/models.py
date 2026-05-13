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
    last_promoted_year = models.PositiveIntegerField(null=True, blank=True)
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

    class AcademicStatus(models.TextChoices):
        STUDYING = 'studying', 'Обучается'
        ACADEMIC_LEAVE = 'academic_leave', 'Академический отпуск'
        EXPELLED = 'expelled', 'Отчислен'
        GRADUATED = 'graduated', 'Выпускник'

    username = None
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STUDENT)
    group = models.CharField(max_length=64, blank=True)
    specialty = models.CharField(max_length=255, blank=True)
    admission_year = models.PositiveIntegerField(null=True, blank=True)
    academic_status = models.CharField(max_length=16, choices=AcademicStatus.choices, default=AcademicStatus.STUDYING)
    curator = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='students')
    study_group = models.ForeignKey(StudyGroup, null=True, blank=True, on_delete=models.SET_NULL, related_name='students')
    photo = models.ImageField(upload_to='users/photos/', blank=True, null=True)
    contact_phone = models.CharField(max_length=32, blank=True)
    contact_telegram = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_note = models.TextField(blank=True)
    contact_availability = models.CharField(max_length=255, blank=True)
    # NOTE: Поля group/specialty сохранены для legacy-совместимости (старые импорты/данные).
    # Каноническая нормализованная связь: User.study_group -> StudyGroup -> Specialty.
    # После полной миграции исторических данных эти текстовые поля можно вывести из эксплуатации.

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        indexes = [
            models.Index(fields=['role'], name='accounts_user_role_idx'),
            models.Index(fields=['academic_status'], name='accounts_user_ac_status_idx'),
            models.Index(fields=['study_group'], name='accounts_user_st_group_idx'),
            models.Index(fields=['curator'], name='accounts_user_curator_idx'),
            models.Index(fields=['is_active'], name='accounts_user_is_active_idx'),
        ]

    def __str__(self):
        return self.full_name or self.email


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    phone = models.CharField(max_length=32, blank=True)
    city = models.CharField(max_length=128, blank=True)
    contact_link = models.CharField(max_length=255, blank=True)
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


class ActivityLog(models.Model):
    class EventType(models.TextChoices):
        PORTFOLIO_CREATED = 'portfolio_created', 'Добавлена запись портфолио'
        PORTFOLIO_PENDING = 'portfolio_pending', 'Ожидает проверки'
        PORTFOLIO_APPROVED = 'portfolio_approved', 'Запись портфолио подтверждена'
        PORTFOLIO_REJECTED = 'portfolio_rejected', 'Запись портфолио отклонена'
        COURSE_REGISTERED = 'course_registered', 'Запись на курс'
        COURSE_CANCELLED = 'course_cancelled', 'Отмена записи на курс'
        VACANCY_APPLIED = 'vacancy_applied', 'Отклик на вакансию'

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    event_type = models.CharField(max_length=32, choices=EventType.choices)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    related_model = models.CharField(max_length=64, blank=True)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['student', '-created_at'], name='accounts_actlog_sc_idx'),
            models.Index(fields=['event_type', '-created_at'], name='accounts_actlog_ec_idx'),
        ]

    def __str__(self):
        return f'{self.student} — {self.get_event_type_display()}'


class SupportTicket(models.Model):
    class Category(models.TextChoices):
        LOGIN = 'login', 'Проблема со входом'
        PROFILE = 'profile', 'Ошибка в личных данных'
        PORTFOLIO = 'portfolio', 'Проблема с портфолио'
        RESUME = 'resume', 'Проблема с резюме'
        COURSES = 'courses', 'Проблема с курсом или записью'
        VACANCIES = 'vacancies', 'Проблема с вакансией или откликом'
        NO_ACCOUNT = 'no_account', 'Нет аккаунта'
        WRONG_PASSWORD = 'wrong_password', 'Неверный пароль'
        OTHER = 'other', 'Другое'


    class RequesterType(models.TextChoices):
        STUDENT = 'student', 'Студент'
        CURATOR = 'curator', 'Куратор'
        UNKNOWN = 'unknown', 'Другое'

    class Source(models.TextChoices):
        ACCOUNT = 'account', 'Личный кабинет'
        PUBLIC = 'public', 'Публичная форма'

    class Status(models.TextChoices):
        NEW = 'new', 'Новое'
        IN_PROGRESS = 'in_progress', 'В работе'
        RESOLVED = 'resolved', 'Решено'
        CLOSED = 'closed', 'Закрыто'

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets', null=True, blank=True)
    requester = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='requested_support_tickets', null=True, blank=True)
    category = models.CharField(max_length=32, choices=Category.choices, default=Category.OTHER)

    requester_type = models.CharField(max_length=16, choices=RequesterType.choices, default=RequesterType.STUDENT)
    source = models.CharField(max_length=16, choices=Source.choices, default=Source.ACCOUNT)
    public_full_name = models.CharField(max_length=255, blank=True)
    public_email = models.EmailField(blank=True)
    public_contact = models.CharField(max_length=255, blank=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.NEW)
    admin_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = [
            models.Index(fields=['student', 'status'], name='accounts_ticket_st_idx'),
            models.Index(fields=['status', '-created_at'], name='accounts_ticket_sc_idx'),
            models.Index(fields=['category', 'status'], name='accounts_ticket_cs_idx'),
            models.Index(fields=['source', 'status'], name='accounts_ticket_ss_idx'),
            models.Index(fields=['requester_type', 'status'], name='accounts_ticket_rs_idx'),
        ]


    @property
    def author_label(self):
        if self.requester_id:
            role_label = self.requester.get_role_display()
            return f"{self.requester.full_name} ({role_label})"
        if self.public_full_name:
            return f"{self.public_full_name} (без входа)"
        if self.student_id:
            return f"{self.student.full_name} (Студент)"
        return 'Не указан'

    def __str__(self):
        return f'{self.author_label}: {self.subject}'

