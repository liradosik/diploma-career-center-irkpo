from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_studygroup_course_number_and_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='studygroup',
            name='last_promoted_year',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='academic_status',
            field=models.CharField(
                choices=[('studying', 'Обучается'), ('graduate', 'Выпускник'), ('inactive', 'Неактивен')],
                default='studying',
                max_length=16,
            ),
        ),
    ]
