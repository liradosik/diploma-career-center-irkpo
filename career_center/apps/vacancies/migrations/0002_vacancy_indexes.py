from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vacancies', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='vacancy',
            index=models.Index(fields=['status', '-created_at'], name='vacancy_status_created_idx'),
        ),
    ]
