from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_specialty_and_group_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='studygroup',
            name='course_number',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='studygroup',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
