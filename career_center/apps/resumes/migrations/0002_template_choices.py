from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resumes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resumesettings',
            name='template',
            field=models.CharField(choices=[('classic', 'Классический'), ('compact', 'Компактный'), ('modern', 'Современный'), ('academic', 'Академический')], default='classic', max_length=64),
        ),
    ]
