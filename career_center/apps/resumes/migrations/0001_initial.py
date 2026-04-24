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
            name='ResumeSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Студент', max_length=255)),
                ('about', models.TextField(blank=True)),
                ('selected_sections', models.JSONField(blank=True, default=list)),
                ('template', models.CharField(default='classic', max_length=64)),
                ('is_public', models.BooleanField(default=True)),
                ('student', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='resume_settings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
