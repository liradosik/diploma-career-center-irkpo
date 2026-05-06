from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='courseregistration',
            name='status',
            field=models.CharField(choices=[('registered', 'Записан'), ('cancelled', 'Отменена')], default='registered', max_length=16),
        ),
        migrations.AlterUniqueTogether(
            name='courseregistration',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='courseregistration',
            constraint=models.UniqueConstraint(condition=models.Q(('status', 'registered')), fields=('student', 'course'), name='uniq_active_course_registration'),
        ),
    ]
