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
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('kind', models.CharField(choices=[('course', 'Курс'), ('seminar', 'Семинар'), ('practice', 'Практика')], max_length=16)),
                ('format_type', models.CharField(choices=[('online', 'Онлайн'), ('offline', 'Очно')], max_length=16)),
                ('description', models.TextField()),
                ('organization', models.CharField(max_length=255)),
                ('contacts', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('places', models.PositiveIntegerField(default=0)),
                ('status', models.CharField(choices=[('active', 'Active'), ('hidden', 'Hidden'), ('archive', 'Archive')], default='active', max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='CourseRegistration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='courses.course')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_registrations', to=settings.AUTH_USER_MODEL)),
            ],
            options={'unique_together': {('student', 'course')}},
        ),
    ]
