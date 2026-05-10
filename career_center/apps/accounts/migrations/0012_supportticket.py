from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_user_curator_contact_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='SupportTicket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('login', 'Проблема со входом'), ('profile', 'Ошибка в личных данных'), ('portfolio', 'Проблема с портфолио'), ('resume', 'Проблема с резюме'), ('courses', 'Проблема с курсом или записью'), ('vacancies', 'Проблема с вакансией или откликом'), ('other', 'Другое')], default='other', max_length=32)),
                ('subject', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('status', models.CharField(choices=[('new', 'Новое'), ('in_progress', 'В работе'), ('resolved', 'Решено'), ('closed', 'Закрыто')], default='new', max_length=32)),
                ('admin_response', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='support_tickets', to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ('-created_at',)},
        ),
    ]
