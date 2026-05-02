from datetime import date
import re

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.forms import sync_student_with_group
from apps.accounts.models import StudyGroup, User


AUTO_NAME_PATTERN = re.compile(r'^([А-ЯA-Z])-?(\d)(\d{2})(?:/(\d+))?$')


class Command(BaseCommand):
    help = 'Переводит активные группы на следующий курс. Используйте --dry-run или --apply.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Показать изменения без записи в БД')
        parser.add_argument('--apply', action='store_true', help='Применить изменения')

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        apply_changes = options['apply']
        if dry_run == apply_changes:
            self.stdout.write(self.style.ERROR('Укажите ровно один режим: --dry-run или --apply.'))
            return

        current_year = date.today().year
        groups = StudyGroup.objects.filter(is_active=True).select_related('specialty_ref', 'curator')
        summary = {'promoted': 0, 'graduated': 0, 'skipped': 0}

        for group in groups:
            if group.last_promoted_year == current_year:
                summary['skipped'] += 1
                self.stdout.write(f'Пропуск {group.name}: уже переведена в {current_year}.')
                continue

            if group.course_number >= 4:
                summary['graduated'] += 1
                self.stdout.write(f'Выпускная группа: {group.name} -> станет неактивной.')
                if apply_changes:
                    with transaction.atomic():
                        group.is_active = False
                        group.last_promoted_year = current_year
                        group.save(update_fields=['is_active', 'last_promoted_year'])
                        students = User.objects.filter(role=User.Role.STUDENT, study_group=group)
                        for student in students:
                            student.academic_status = User.AcademicStatus.GRADUATED
                            sync_student_with_group(student, group)
                            student.save(update_fields=['academic_status', 'study_group', 'group', 'specialty', 'admission_year', 'curator'])
                continue

            summary['promoted'] += 1
            next_course = group.course_number + 1
            new_name = group.name
            match = AUTO_NAME_PATTERN.match(group.name or '')
            if match and group.specialty_ref:
                subgroup = f"/{match.group(4)}" if match.group(4) else ''
                new_name = f"{group.specialty_ref.letter_code}-{next_course}{str(group.admission_year)[-2:]}{subgroup}"
            self.stdout.write(f'Перевод: {group.name} -> курс {next_course}, имя {new_name}.')

            if apply_changes:
                with transaction.atomic():
                    group.course_number = next_course
                    group.name = new_name
                    group.last_promoted_year = current_year
                    group.save(update_fields=['course_number', 'name', 'last_promoted_year'])
                    students = User.objects.filter(role=User.Role.STUDENT, study_group=group)
                    for student in students:
                        student.academic_status = User.AcademicStatus.STUDYING
                        sync_student_with_group(student, group)
                        student.save(update_fields=['academic_status', 'study_group', 'group', 'specialty', 'admission_year', 'curator'])

        self.stdout.write(self.style.SUCCESS(
            f"Итог: переведено {summary['promoted']}, выпускных {summary['graduated']}, пропущено {summary['skipped']}."
        ))
