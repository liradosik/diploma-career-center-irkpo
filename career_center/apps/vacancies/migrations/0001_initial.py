from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Vacancy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('company', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('responsibilities', models.TextField(blank=True)),
                ('requirements', models.TextField(blank=True)),
                ('conditions', models.TextField(blank=True)),
                ('contacts', models.CharField(max_length=255)),
                ('employment_type', models.CharField(max_length=120)),
                ('format_type', models.CharField(max_length=120)),
                ('direction', models.CharField(max_length=120)),
                ('status', models.CharField(choices=[('active', 'Active'), ('hidden', 'Hidden'), ('archive', 'Archive')], default='active', max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='VacancyResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('resume_link_snapshot', models.URLField(blank=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vacancy_responses', to=settings.AUTH_USER_MODEL)),
                ('vacancy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='vacancies.vacancy')),
            ],
            options={'unique_together': {('student', 'vacancy')}},
        ),
    ]
