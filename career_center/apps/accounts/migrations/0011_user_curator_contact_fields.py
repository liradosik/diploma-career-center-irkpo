from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_user_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='contact_availability',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='user',
            name='contact_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='user',
            name='contact_note',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='contact_phone',
            field=models.CharField(blank=True, max_length=32),
        ),
        migrations.AddField(
            model_name='user',
            name='contact_telegram',
            field=models.URLField(blank=True),
        ),
    ]
