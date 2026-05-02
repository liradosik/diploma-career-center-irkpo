from django.db import migrations, models


def forward_map_statuses(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    User.objects.filter(academic_status='graduate').update(academic_status='graduated')
    User.objects.filter(academic_status='inactive').update(academic_status='expelled')


def backward_map_statuses(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    User.objects.filter(academic_status='graduated').update(academic_status='graduate')
    User.objects.filter(academic_status='expelled').update(academic_status='inactive')


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_user_options_alter_user_managers_and_more'),
    ]

    operations = [
        migrations.RunPython(forward_map_statuses, backward_map_statuses),
        migrations.AlterField(
            model_name='user',
            name='academic_status',
            field=models.CharField(
                choices=[
                    ('studying', 'Обучается'),
                    ('academic_leave', 'Академический отпуск'),
                    ('expelled', 'Отчислен'),
                    ('graduated', 'Выпускник'),
                ],
                default='studying',
                max_length=16,
            ),
        ),
    ]
