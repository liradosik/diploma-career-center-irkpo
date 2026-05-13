from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0002_vacancy_indexes'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentFavoriteVacancy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_vacancies', to=settings.AUTH_USER_MODEL)),
                ('vacancy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by_students', to='vacancies.vacancy')),
            ],
        ),
        migrations.AddConstraint(
            model_name='studentfavoritevacancy',
            constraint=models.UniqueConstraint(fields=('student', 'vacancy'), name='uniq_student_favorite_vacancy'),
        ),
    ]
