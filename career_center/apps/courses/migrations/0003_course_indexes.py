from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_registration_status'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='course',
            index=models.Index(fields=['status', 'date'], name='course_status_date_idx'),
        ),
        migrations.AddIndex(
            model_name='course',
            index=models.Index(fields=['kind', 'status'], name='course_kind_status_idx'),
        ),
        migrations.AddIndex(
            model_name='course',
            index=models.Index(fields=['format_type', 'status'], name='course_format_status_idx'),
        ),
    ]
