from datetime import date, timedelta

from django.core.management.base import BaseCommand

from apps.accounts.models import Specialty, StudentProfile, StudyGroup, User
from apps.courses.models import Course, CourseRegistration
from apps.portfolio.models import PortfolioEntry
from apps.resumes.models import ResumeSettings
from apps.vacancies.models import Vacancy, VacancyResponse


class Command(BaseCommand):
    help = 'Создает демо-данные для дипломного проекта.'

    def handle(self, *args, **options):
        specialties = [
            ('09.02.07', 'Информационные системы и программирование', 'И'),
            ('44.02.01', 'Дошкольное образование', 'Д'),
            ('44.02.02', 'Преподавание в начальных классах', 'Н'),
            ('44.02.03', 'Педагогика дополнительного образования (ИЗО и ДПИ)', 'Х'),
            ('44.02.03', 'Педагогика дополнительного образования (Хореография)', 'Б'),
            ('44.02.03', 'Педагогика дополнительного образования (Сценическая деятельность)', 'А'),
            ('44.02.03', 'Педагогика дополнительного образования (Техническая направленность)', 'Т'),
            ('44.02.03', 'Педагогика дополнительного образования (Социально-гуманитарная направленность)', 'О'),
            ('44.02.04', 'Специальное дошкольное образование', 'С'),
            ('49.02.01', 'Физическая культура', 'Ф'),
            ('53.02.01', 'Музыкальное образование', 'М'),
            ('53.02.02', 'Музыкальное искусство эстрады', 'В'),
        ]
        for code, name, letter in specialties:
            Specialty.objects.update_or_create(
                code=code,
                letter_code=letter,
                defaults={'name': name, 'is_active': True},
            )

        admin, _ = User.objects.get_or_create(
            email='admin@irkpo.local',
            defaults={'full_name': 'Администратор ИРКПО', 'role': User.Role.ADMIN, 'is_staff': True, 'is_superuser': True},
        )
        admin.set_password('Admin12345!')
        admin.save()

        curator, _ = User.objects.get_or_create(
            email='curator@irkpo.local', defaults={'full_name': 'Куратор ИРКПО', 'role': User.Role.CURATOR}
        )
        curator.set_password('Curator12345!')
        curator.save()

        default_specialty = Specialty.objects.filter(letter_code='И').first()
        study_group, _ = StudyGroup.objects.get_or_create(
            name='И-422',
            defaults={
                'specialty': default_specialty.name if default_specialty else 'Информационные системы и программирование',
                'specialty_ref': default_specialty,
                'admission_year': 2022,
                'course_number': 4,
                'curator': curator,
                'is_active': True,
            },
        )

        students = []
        for i in range(1, 6):
            student, _ = User.objects.get_or_create(
                email=f'student{i}@irkpo.local',
                defaults={
                    'full_name': f'Студент {i}',
                    'role': User.Role.STUDENT,
                    'group': 'И-422',
                    'specialty': 'Информационные системы и программирование',
                    'admission_year': 2022,
                    'curator': curator,
                    'study_group': study_group,
                },
            )
            student.set_password('Student12345!')
            student.save()
            StudentProfile.objects.get_or_create(user=student, defaults={'city': 'Иркутск', 'about': 'Студент ИРКПО'})
            ResumeSettings.objects.get_or_create(student=student, defaults={'title': 'Студент / Начинающий специалист'})
            students.append(student)

        statuses = [PortfolioEntry.Status.PENDING, PortfolioEntry.Status.APPROVED, PortfolioEntry.Status.REJECTED]
        for idx, student in enumerate(students):
            for j, status in enumerate(statuses):
                PortfolioEntry.objects.get_or_create(
                    student=student,
                    title=f'Достижение {j+1} студента {idx+1}',
                    defaults={
                        'type': 'Учебное достижение',
                        'description': 'Описание достижения для демонстрации проверки.',
                        'date': date.today() - timedelta(days=30 * (j + 1)),
                        'status': status,
                        'curator_comment': 'Проверено куратором.' if status != PortfolioEntry.Status.PENDING else '',
                        'reviewed_by': curator if status != PortfolioEntry.Status.PENDING else None,
                    },
                )

        for i in range(1, 13):
            Vacancy.objects.get_or_create(
                title=f'Вакансия {i}',
                company=f'Компания {i}',
                defaults={
                    'description': 'Описание вакансии для студентов.',
                    'responsibilities': 'Выполнение задач под руководством наставника.',
                    'requirements': 'Базовые профильные навыки.',
                    'conditions': 'Гибкий график.',
                    'contacts': f'hr{i}@company.local',
                    'employment_type': 'Стажировка',
                    'format_type': 'Гибридный',
                    'direction': 'IT',
                    'status': Vacancy.Status.ACTIVE,
                },
            )

        for i in range(1, 13):
            Course.objects.get_or_create(
                title=f'Событие {i}',
                kind=Course.Kind.COURSE if i % 3 == 0 else (Course.Kind.SEMINAR if i % 3 == 1 else Course.Kind.PRACTICE),
                defaults={
                    'format_type': Course.Format.OFFLINE if i % 2 else Course.Format.ONLINE,
                    'description': 'Описание курса/семинара/практики.',
                    'organization': 'Центр карьеры ИРКПО',
                    'contacts': 'courses@irkpo.local',
                    'date': date.today() + timedelta(days=i * 3),
                    'places': 20,
                    'status': Course.Status.ACTIVE,
                },
            )

        active_vacancies = list(Vacancy.objects.filter(status=Vacancy.Status.ACTIVE)[:3])
        active_courses = list(Course.objects.filter(status=Course.Status.ACTIVE)[:3])
        for student in students[:3]:
            for vacancy in active_vacancies:
                VacancyResponse.objects.get_or_create(student=student, vacancy=vacancy, defaults={'resume_link_snapshot': 'https://example.local/resume'})
            for course in active_courses:
                CourseRegistration.objects.get_or_create(student=student, course=course)

        self.stdout.write(self.style.SUCCESS('Демо-данные успешно созданы.'))
