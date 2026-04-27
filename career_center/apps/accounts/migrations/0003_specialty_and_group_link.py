from django.db import migrations, models
import django.db.models.deletion


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


def seed_specialties_and_link_groups(apps, schema_editor):
    Specialty = apps.get_model('accounts', 'Specialty')
    StudyGroup = apps.get_model('accounts', 'StudyGroup')

    for code, name, letter in SPECIALTIES:
        Specialty.objects.get_or_create(
            code=code,
            letter_code=letter,
            defaults={'name': name, 'is_active': True},
        )

    for group in StudyGroup.objects.filter(specialty_ref__isnull=True):
        specialty = Specialty.objects.filter(name=group.specialty).first()
        if specialty:
            group.specialty_ref = specialty
            group.save(update_fields=['specialty_ref'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_studygroup_user_study_group'),
    ]

    operations = [
        migrations.CreateModel(
            name='Specialty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=32, unique=True)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('letter_code', models.CharField(max_length=4, unique=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('code', 'name'),
            },
        ),
        migrations.AddField(
            model_name='studygroup',
            name='specialty_ref',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='study_groups', to='accounts.specialty'),
        ),
        migrations.RunPython(seed_specialties_and_link_groups, migrations.RunPython.noop),
    ]
