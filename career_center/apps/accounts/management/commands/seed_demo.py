from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.forms import sync_student_with_group
from apps.accounts.models import ActivityLog, Specialty, StudentProfile, StudyGroup, User
from apps.courses.models import Course, CourseRegistration
from apps.portfolio.models import PortfolioEntry
from apps.resumes.models import ResumeSettings
from apps.vacancies.models import Vacancy, VacancyResponse

DEMO_PASSWORD = 'Demo12345!'


class Command(BaseCommand):
    help = 'Создает демо-данные для презентации проекта (безопасно для повторного запуска).'

    demo_admin_email = 'admin.demo@irkpo.ru'
    demo_curator_emails = ['curator.1@irkpo.ru', 'curator.2@irkpo.ru']
    demo_student_emails = [f'student.{i}@irkpo.ru' for i in range(1, 13)]

    @property
    def demo_all_emails(self):
        return [self.demo_admin_email, *self.demo_curator_emails, *self.demo_student_emails]

    @transaction.atomic
    def handle(self, *args, **options):
        self._cleanup_demo_data()
        demo_objects = self._create_demo_data()
        self._print_summary(demo_objects)

    def _cleanup_demo_data(self):
        demo_users = User.objects.filter(email__in=self.demo_all_emails)

        ActivityLog.objects.filter(student__in=demo_users).delete()
        VacancyResponse.objects.filter(student__in=demo_users).delete()
        CourseRegistration.objects.filter(student__in=demo_users).delete()
        PortfolioEntry.objects.filter(student__in=demo_users).delete()
        ResumeSettings.objects.filter(student__in=demo_users).delete()
        StudentProfile.objects.filter(user__in=demo_users).delete()

        StudyGroup.objects.filter(name__in=['ИСП-22-1', 'ДЗ-22-1', 'ЭБ-22-1']).update(curator=None)
        demo_users.delete()

        VacancyResponse.objects.filter(vacancy__title__in=self._vacancy_titles()).delete()
        Vacancy.objects.filter(title__in=self._vacancy_titles()).delete()

        CourseRegistration.objects.filter(course__title__in=self._course_titles()).delete()
        Course.objects.filter(title__in=self._course_titles()).delete()

        Specialty.objects.filter(
            code__in=['09.02.07', '54.02.01', '38.02.01'],
            letter_code__in=['ИСП', 'ДЗ', 'ЭБ'],
        ).delete()

    def _create_demo_data(self):
        specialties = {
            'isp': Specialty.objects.create(code='09.02.07', name='Информационные системы и программирование', letter_code='ИСП'),
            'design': Specialty.objects.create(code='54.02.01', name='Дизайн', letter_code='ДЗ'),
            'eco': Specialty.objects.create(code='38.02.01', name='Экономика и бухгалтерский учёт', letter_code='ЭБ'),
        }

        admin = User.objects.create_user(
            email=self.demo_admin_email,
            full_name='Демо Администратор',
            role=User.Role.ADMIN,
            is_staff=True,
            is_superuser=True,
            password=DEMO_PASSWORD,
        )

        curators = [
            User.objects.create_user(email='curator.1@irkpo.ru', full_name='Куратор Ирина Петрова', role=User.Role.CURATOR, password=DEMO_PASSWORD),
            User.objects.create_user(email='curator.2@irkpo.ru', full_name='Куратор Павел Смирнов', role=User.Role.CURATOR, password=DEMO_PASSWORD),
        ]

        groups = {
            'ИСП-22-1': StudyGroup.objects.create(
                name='ИСП-22-1', specialty='Информационные системы и программирование', specialty_ref=specialties['isp'], admission_year=2022,
                course_number=4, curator=curators[0], is_active=True
            ),
            'ДЗ-22-1': StudyGroup.objects.create(
                name='ДЗ-22-1', specialty='Дизайн', specialty_ref=specialties['design'], admission_year=2022,
                course_number=4, curator=curators[0], is_active=True
            ),
            'ЭБ-22-1': StudyGroup.objects.create(
                name='ЭБ-22-1', specialty='Экономика и бухгалтерский учёт', specialty_ref=specialties['eco'], admission_year=2022,
                course_number=4, curator=curators[1], is_active=True
            ),
        }

        student_specs = [
            ('student.1@irkpo.ru', 'Алексей Волков', 'ИСП-22-1', User.AcademicStatus.STUDYING),
            ('student.2@irkpo.ru', 'Мария Иванова', 'ИСП-22-1', User.AcademicStatus.STUDYING),
            ('student.3@irkpo.ru', 'Денис Козлов', 'ИСП-22-1', User.AcademicStatus.ACADEMIC_LEAVE),
            ('student.4@irkpo.ru', 'София Орлова', 'ДЗ-22-1', User.AcademicStatus.STUDYING),
            ('student.5@irkpo.ru', 'Илья Морозов', 'ДЗ-22-1', User.AcademicStatus.EXPELLED),
            ('student.6@irkpo.ru', 'Кира Лебедева', 'ДЗ-22-1', User.AcademicStatus.GRADUATED),
            ('student.7@irkpo.ru', 'Артём Фролов', 'ЭБ-22-1', User.AcademicStatus.STUDYING),
            ('student.8@irkpo.ru', 'Екатерина Соколова', 'ЭБ-22-1', User.AcademicStatus.STUDYING),
            ('student.9@irkpo.ru', 'Олег Никитин', 'ЭБ-22-1', User.AcademicStatus.ACADEMIC_LEAVE),
            ('student.10@irkpo.ru', 'Анна Белова', 'ИСП-22-1', User.AcademicStatus.STUDYING),
            ('student.11@irkpo.ru', 'Никита Романов', 'ДЗ-22-1', User.AcademicStatus.STUDYING),
            ('student.12@irkpo.ru', 'Юлия Павлова', 'ЭБ-22-1', User.AcademicStatus.GRADUATED),
        ]

        students = []
        for i, (email, full_name, group_name, academic_status) in enumerate(student_specs, start=1):
            student = User.objects.create_user(email=email, full_name=full_name, role=User.Role.STUDENT, academic_status=academic_status, password=DEMO_PASSWORD)
            sync_student_with_group(student, groups[group_name])
            student.contact_phone = f'+7 (900) 000-00-{i:02d}'
            student.contact_email = email
            student.contact_note = 'Готов к предложениям по практике и стажировке.'
            student.save()
            StudentProfile.objects.create(user=student, city='Иркутск', phone=student.contact_phone, about=f'{full_name}, студент группы {group_name}.')
            students.append(student)

        self._seed_resumes(students)
        vacancies = self._seed_vacancies()
        courses = self._seed_courses()
        portfolio_entries = self._seed_portfolio(students, curators)
        self._seed_course_registrations(students, courses)
        self._seed_vacancy_responses(students, vacancies)
        self._seed_activity_log(students, portfolio_entries, courses, vacancies)

        return {
            'admin': admin,
            'curators': curators,
            'students': students,
            'vacancies_count': len(vacancies),
            'courses_count': len(courses),
            'portfolio_count': len(portfolio_entries),
        }

    def _seed_resumes(self, students):
        ResumeSettings.objects.create(
            student=students[0], title='Стажёр Python-разработчик', is_public=True, template=ResumeSettings.Template.CLASSIC,
            about='Изучаю Django и PostgreSQL, хочу развиваться в backend-разработке.',
            selected_sections=['about', 'skills', 'experience', 'education', 'contacts']
        )
        ResumeSettings.objects.create(
            student=students[1], title='Junior UI/UX Designer', is_public=False, template=ResumeSettings.Template.MODERN,
            about='Развиваюсь в веб-дизайне, люблю создавать понятные интерфейсы.',
            selected_sections=['about', 'skills', 'experience', 'education', 'contacts']
        )
        ResumeSettings.objects.create(
            student=students[2], title='Помощник системного администратора', is_public=True,
            about='Настраивал локальную сеть в учебной лаборатории.', selected_sections=['about', 'skills', 'contacts']
        )
        for student in students[3:8]:
            ResumeSettings.objects.create(student=student, title='Начинающий специалист', is_public=True, about='Готов к практике.')

    def _seed_vacancies(self):
        vacancies_data = [
            ('Стажёр Python-разработчик', 'ТехСофт', 'active', 'Удалённо', 'Стажировка'),
            ('Помощник веб-дизайнера', 'DesignLab', 'active', 'Очно', 'Частичная занятость'),
            ('Контент-менеджер', 'MediaPoint', 'hidden', 'Гибрид', 'Полная занятость'),
            ('Junior Frontend Developer', 'WebLine', 'active', 'Гибрид', 'Полная занятость'),
            ('Помощник системного администратора', 'СетьПлюс', 'active', 'Очно', 'Стажировка'),
            ('Оператор 1С', 'БухСервис', 'archive', 'Очно', 'Полная занятость'),
            ('SMM-специалист', 'МаркетПро', 'hidden', 'Удалённо', 'Частичная занятость'),
            ('Тестировщик веб-приложений', 'QA Studio', 'active', 'Удалённо', 'Стажировка'),
            ('Ассистент аналитика', 'DataBridge', 'archive', 'Гибрид', 'Частичная занятость'),
        ]
        result = []
        for idx, (title, company, status, format_type, employment_type) in enumerate(vacancies_data, start=1):
            result.append(Vacancy.objects.create(
                title=title, company=company, status=status, format_type=format_type, employment_type=employment_type,
                direction='IT / Digital', description='Полноценная вакансия для демонстрации карточек и фильтров.',
                responsibilities='Выполнение задач наставника, участие в командных активностях, отчётность.',
                requirements='Базовые профильные навыки, ответственность, желание учиться.',
                conditions='Гибкий график, наставник, возможность трудоустройства.',
                contacts=f'hr{idx}@demo-company.ru',
            ))
        return result

    def _seed_courses(self):
        today = date.today()
        courses_data = [
            ('Подготовка к собеседованию', Course.Kind.COURSE, Course.Format.OFFLINE, 25, 'active', 7),
            ('Основы Git и GitHub', Course.Kind.COURSE, Course.Format.ONLINE, 0, 'active', 10),
            ('Практикум по созданию резюме', Course.Kind.PRACTICE, Course.Format.OFFLINE, 3, 'active', 14),
            ('Встреча с работодателем', Course.Kind.SEMINAR, Course.Format.OFFLINE, 2, 'active', 21),
            ('Мини-курс по Figma', Course.Kind.COURSE, Course.Format.ONLINE, 0, 'hidden', 28),
            ('Карьерная консультация', Course.Kind.SEMINAR, Course.Format.OFFLINE, 0, 'archive', -5),
            ('Основы тестирования', Course.Kind.COURSE, Course.Format.ONLINE, 0, 'active', 35),
            ('Портфолио для начинающего специалиста', Course.Kind.PRACTICE, Course.Format.OFFLINE, 1, 'active', 42),
        ]
        result = []
        for title, kind, format_type, places, status, offset in courses_data:
            result.append(Course.objects.create(
                title=title, kind=kind, format_type=format_type,
                description='Демо-курс для демонстрации каталога, карточки и регистрации.',
                organization='Центр карьеры ИРКПО', contacts='courses.demo@irkpo.ru',
                date=today + timedelta(days=offset), places=places, status=status,
            ))
        return result

    def _seed_portfolio(self, students, curators):
        now = timezone.now()
        entries_data = [
            (students[0], 'Лендинг для учебного проекта', 'pending', ''),
            (students[1], 'Макет личного кабинета в Figma', 'pending', ''),
            (students[3], 'Django-приложение для учёта заявок', 'pending', ''),
            (students[4], 'Сайт-визитка', 'approved', 'Хорошая структура и аккуратная верстка.'),
            (students[6], 'Курсовой проект по базам данных', 'approved', 'Работа соответствует требованиям.'),
            (students[7], 'Дизайн афиши для мероприятия', 'rejected', 'Нужно улучшить читаемость текста и контраст.'),
        ]
        entries = []
        for idx, (student, title, status, comment) in enumerate(entries_data, start=1):
            reviewed_by = curators[0] if status in (PortfolioEntry.Status.APPROVED, PortfolioEntry.Status.REJECTED) else None
            reviewed_at = now - timedelta(days=idx) if reviewed_by else None
            entries.append(PortfolioEntry.objects.create(
                student=student, type='project', title=title,
                description='Описание работы для демонстрации портфолио.',
                date=date.today() - timedelta(days=idx * 4),
                link=f'https://portfolio-demo.example/work-{idx}', status=status,
                curator_comment=comment, reviewed_by=reviewed_by, reviewed_at=reviewed_at,
            ))
        return entries

    def _seed_course_registrations(self, students, courses):
        by_title = {course.title: course for course in courses}
        CourseRegistration.objects.create(student=students[0], course=by_title['Подготовка к собеседованию'], status=CourseRegistration.Status.REGISTERED)
        CourseRegistration.objects.create(student=students[1], course=by_title['Подготовка к собеседованию'], status=CourseRegistration.Status.REGISTERED)
        CourseRegistration.objects.create(student=students[2], course=by_title['Подготовка к собеседованию'], status=CourseRegistration.Status.CANCELLED)

        full_course = by_title['Практикум по созданию резюме']
        CourseRegistration.objects.create(student=students[3], course=full_course, status=CourseRegistration.Status.REGISTERED)
        CourseRegistration.objects.create(student=students[4], course=full_course, status=CourseRegistration.Status.REGISTERED)
        CourseRegistration.objects.create(student=students[5], course=full_course, status=CourseRegistration.Status.REGISTERED)

        CourseRegistration.objects.create(student=students[6], course=by_title['Встреча с работодателем'], status=CourseRegistration.Status.REGISTERED)
        CourseRegistration.objects.create(student=students[7], course=by_title['Встреча с работодателем'], status=CourseRegistration.Status.CANCELLED)

    def _seed_vacancy_responses(self, students, vacancies):
        for student, vacancy in [(students[0], vacancies[0]), (students[1], vacancies[3]), (students[6], vacancies[7])]:
            VacancyResponse.objects.create(student=student, vacancy=vacancy, resume_link_snapshot='https://demo.irkpo.ru/resume/public')

    def _seed_activity_log(self, students, portfolio_entries, courses, vacancies):
        ActivityLog.objects.create(student=students[0], event_type=ActivityLog.EventType.COURSE_REGISTERED, title='Запись на курс', description='Студент записался на курс «Подготовка к собеседованию».', related_model='Course', related_object_id=courses[0].id)
        ActivityLog.objects.create(student=students[2], event_type=ActivityLog.EventType.COURSE_CANCELLED, title='Отмена записи', description='Студент отменил запись на курс «Подготовка к собеседованию».', related_model='Course', related_object_id=courses[0].id)
        ActivityLog.objects.create(student=students[0], event_type=ActivityLog.EventType.PORTFOLIO_CREATED, title='Добавлена работа в портфолио', description='Добавлена работа «Лендинг для учебного проекта».', related_model='PortfolioEntry', related_object_id=portfolio_entries[0].id)
        ActivityLog.objects.create(student=students[1], event_type=ActivityLog.EventType.PORTFOLIO_APPROVED, title='Работа одобрена куратором', description='Куратор одобрил работу в портфолио.', related_model='PortfolioEntry', related_object_id=portfolio_entries[3].id)
        ActivityLog.objects.create(student=students[0], event_type=ActivityLog.EventType.VACANCY_APPLIED, title='Отклик на вакансию', description='Студент откликнулся на вакансию «Стажёр Python-разработчик».', related_model='Vacancy', related_object_id=vacancies[0].id)

    def _print_summary(self, demo):
        self.stdout.write(self.style.SUCCESS('Демо-данные созданы.'))
        self.stdout.write(f'Пароль для всех аккаунтов: {DEMO_PASSWORD}\n')
        self.stdout.write('Администратор:')
        self.stdout.write(demo['admin'].email + '\n')
        self.stdout.write('Кураторы:')
        for curator in demo['curators']:
            self.stdout.write(curator.email)
        self.stdout.write('\nСтуденты:')
        for student in demo['students']:
            self.stdout.write(student.email)

        self.stdout.write('\nРоли:')
        self.stdout.write(f"- Администратор: {demo['admin'].email}")
        for curator in demo['curators']:
            self.stdout.write(f'- Куратор: {curator.email}')
        for student in demo['students']:
            self.stdout.write(f'- Студент: {student.email}')

        self.stdout.write('\nСтатистика:')
        self.stdout.write(f"- Студентов: {len(demo['students'])}")
        self.stdout.write(f"- Вакансий: {demo['vacancies_count']}")
        self.stdout.write(f"- Курсов/мероприятий: {demo['courses_count']}")
        self.stdout.write(f"- Работ в портфолио: {demo['portfolio_count']}")

    def _vacancy_titles(self):
        return [
            'Стажёр Python-разработчик', 'Помощник веб-дизайнера', 'Контент-менеджер', 'Junior Frontend Developer',
            'Помощник системного администратора', 'Оператор 1С', 'SMM-специалист', 'Тестировщик веб-приложений',
            'Ассистент аналитика',
        ]

    def _course_titles(self):
        return [
            'Подготовка к собеседованию', 'Основы Git и GitHub', 'Практикум по созданию резюме', 'Встреча с работодателем',
            'Мини-курс по Figma', 'Карьерная консультация', 'Основы тестирования', 'Портфолио для начинающего специалиста',
        ]
