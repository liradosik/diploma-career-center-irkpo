from datetime import date, timedelta

from django.core.management.base import BaseCommand

from apps.accounts.forms import sync_student_with_group
from apps.accounts.models import Specialty, StudentProfile, StudyGroup, User
from apps.courses.models import Course, CourseRegistration
from apps.portfolio.models import PortfolioEntry
from apps.resumes.models import ResumeSettings
from apps.vacancies.models import Vacancy, VacancyResponse


SPECIALTIES = [
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


class Command(BaseCommand):
    help = 'Создает демонстрационные данные для дипломного проекта.'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Очистить старые тестовые демо-данные перед созданием.')

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_demo_data()

        for code, name, letter in SPECIALTIES:
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

        curator_specs = [
            ('Ласкутина Клара Севастьяновна', 'laskutina@irkpo.local'),
            ('Якубович Данила Игнатьевич', 'yakubovich@irkpo.local'),
            ('Сергеева Анна Викторовна', 'sergeeva@irkpo.local'),
        ]
        curators = []
        for name, email in curator_specs:
            curator, _ = User.objects.get_or_create(email=email, defaults={'full_name': name, 'role': User.Role.CURATOR})
            curator.set_password('Curator12345!')
            curator.save()
            curators.append(curator)

        groups_data = [
            ('И-422', 'И', 2022, 4, curators[0]),
            ('Н-121/1', 'Н', 2024, 1, curators[1]),
            ('Н-121/2', 'Н', 2024, 1, curators[1]),
            ('Б-222', 'Б', 2023, 2, curators[2]),
            ('Ф-324', 'Ф', 2023, 3, curators[2]),
        ]
        groups = {}
        for name, letter, year, course, curator in groups_data:
            specialty = Specialty.objects.filter(letter_code=letter).first()
            group, _ = StudyGroup.objects.update_or_create(
                name=name,
                defaults={
                    'specialty_ref': specialty,
                    'specialty': specialty.name if specialty else '',
                    'admission_year': year,
                    'course_number': course,
                    'curator': curator,
                    'is_active': True,
                },
            )
            groups[name] = group

        students_data = [
            ('Дашинова Валерия Михайловна', 'dashinova@irkpo.local', 'Н-121/1'),
            ('Яненко Сюзанна Кирилловна', 'yanenko@irkpo.local', 'Н-121/2'),
            ('Примакова Полина Прохоровна', 'primakova@irkpo.local', 'И-422'),
            ('Воропаева Марьямна Ивановна', 'voropaeva@irkpo.local', 'И-422'),
            ('Тимяряев Афанасий Прокопьевич', 'timyaryaev@irkpo.local', 'Б-222'),
            ('Лебедева Мария Олеговна', 'lebedeva@irkpo.local', 'Б-222'),
            ('Фёдоров Никита Андреевич', 'fedorov@irkpo.local', 'Ф-324'),
            ('Павлова Алина Романовна', 'pavlova@irkpo.local', 'Ф-324'),
            ('Крылова Дарья Ильинична', 'krylova@irkpo.local', 'Н-121/1'),
            ('Романов Егор Степанович', 'romanov@irkpo.local', 'Н-121/2'),
        ]

        students = []
        for full_name, email, group_name in students_data:
            student, _ = User.objects.get_or_create(
                email=email,
                defaults={'full_name': full_name, 'role': User.Role.STUDENT, 'academic_status': User.AcademicStatus.STUDYING},
            )
            student.set_password('Student12345!')
            sync_student_with_group(student, groups[group_name])
            student.save()
            StudentProfile.objects.get_or_create(user=student, defaults={'city': 'Иркутск', 'about': 'Студент ИРКПО'})
            ResumeSettings.objects.get_or_create(student=student, defaults={'title': 'Студент / Начинающий специалист'})
            students.append(student)

        vacancies_data = [
            ('Помощник педагога-организатора', 'Колледж ИРКПО'),
            ('Стажёр по web-дизайну', 'Digital Studio'),
            ('Ассистент по цифровым материалам', 'EdTech Lab'),
            ('Вожатый в детский центр', 'Детский центр «Орион»'),
            ('Помощник воспитателя', 'Детский сад №12'),
        ]
        vacancies = []
        for idx, (title, company) in enumerate(vacancies_data, start=1):
            vacancy, _ = Vacancy.objects.update_or_create(
                title=title,
                company=company,
                defaults={
                    'description': 'Поддержка основной команды и участие в проектах.',
                    'responsibilities': 'Помощь в подготовке материалов и сопровождении активностей.',
                    'requirements': 'Ответственность и базовые профильные навыки.',
                    'conditions': 'Гибкий график.',
                    'contacts': f'hr{idx}@career.local',
                    'employment_type': 'Стажировка',
                    'format_type': 'Гибридный',
                    'direction': 'Образование',
                    'status': Vacancy.Status.ACTIVE,
                },
            )
            vacancies.append(vacancy)

        courses_data = [
            ('Мастер-класс по резюме', Course.Kind.SEMINAR),
            ('Семинар «Как пройти собеседование»', Course.Kind.SEMINAR),
            ('Практикум по оформлению портфолио', Course.Kind.PRACTICE),
            ('Карьерная встреча с работодателем', Course.Kind.COURSE),
        ]
        courses = []
        for i, (title, kind) in enumerate(courses_data, start=1):
            course, _ = Course.objects.update_or_create(
                title=title,
                defaults={
                    'kind': kind,
                    'format_type': Course.Format.OFFLINE if i % 2 else Course.Format.ONLINE,
                    'description': 'Практическое событие для развития карьерных навыков.',
                    'organization': 'Центр карьеры ИРКПО',
                    'contacts': 'courses@irkpo.local',
                    'date': date.today() + timedelta(days=i * 5),
                    'places': 25,
                    'status': Course.Status.ACTIVE,
                },
            )
            courses.append(course)

        for i, student in enumerate(students[:6]):
            PortfolioEntry.objects.get_or_create(
                student=student,
                title=f'Достижение студента {i + 1}',
                defaults={
                    'type': 'project',
                    'description': 'Проект в рамках учебной программы.',
                    'date': date.today() - timedelta(days=15 + i),
                    'status': PortfolioEntry.Status.APPROVED,
                },
            )

        for student in students[:5]:
            for vacancy in vacancies[:2]:
                VacancyResponse.objects.get_or_create(
                    student=student,
                    vacancy=vacancy,
                    defaults={'resume_link_snapshot': 'https://example.local/resume'},
                )
            for course in courses[:2]:
                CourseRegistration.objects.get_or_create(student=student, course=course)

        self.stdout.write(self.style.SUCCESS('Демо-данные успешно созданы.'))

    def clear_demo_data(self):
        demo_student_emails = list(
            User.objects.filter(email__startswith='student', email__endswith='@irkpo.local').values_list('email', flat=True)
        )
        demo_student_emails += list(
            User.objects.filter(email__endswith='@irkpo.local', full_name__startswith='Студент ').values_list('email', flat=True)
        )

        demo_students = User.objects.filter(email__in=set(demo_student_emails), role=User.Role.STUDENT)
        VacancyResponse.objects.filter(student__in=demo_students).delete()
        CourseRegistration.objects.filter(student__in=demo_students).delete()
        PortfolioEntry.objects.filter(student__in=demo_students).delete()
        StudentProfile.objects.filter(user__in=demo_students).delete()
        ResumeSettings.objects.filter(student__in=demo_students).delete()
        demo_students.delete()

        VacancyResponse.objects.filter(vacancy__title__startswith='Вакансия ').delete()
        Vacancy.objects.filter(title__startswith='Вакансия ').delete()

        CourseRegistration.objects.filter(course__title__startswith='Событие ').delete()
        Course.objects.filter(title__startswith='Событие ').delete()

        self.stdout.write(self.style.WARNING('Старые демонстрационные данные очищены (--clear).'))
