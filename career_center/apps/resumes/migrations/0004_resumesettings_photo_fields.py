from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resumes', '0003_resumesettings_font_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='resumesettings',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='resume_photos/'),
        ),
        migrations.AddField(
            model_name='resumesettings',
            name='photo_source',
            field=models.CharField(
                choices=[
                    ('profile', 'Из профиля студента'),
                    ('account', 'Из аккаунта пользователя'),
                    ('custom', 'Отдельное фото для резюме'),
                    ('hidden', 'Не показывать фото'),
                ],
                default='profile',
                max_length=32,
            ),
        ),
    ]
