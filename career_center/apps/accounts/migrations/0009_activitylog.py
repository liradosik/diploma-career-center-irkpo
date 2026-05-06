from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_academic_status_values_update'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('portfolio_created', 'Добавлена запись портфолио'), ('portfolio_pending', 'Ожидает проверки'), ('portfolio_approved', 'Запись портфолио подтверждена'), ('portfolio_rejected', 'Запись портфолио отклонена'), ('course_registered', 'Запись на курс'), ('course_cancelled', 'Отмена записи на курс'), ('vacancy_applied', 'Отклик на вакансию')], max_length=32)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('related_model', models.CharField(blank=True, max_length=64)),
                ('related_object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activity_logs', to='accounts.user')),
            ],
            options={'ordering': ('-created_at',)},
        ),
    ]
