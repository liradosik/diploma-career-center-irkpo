from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_add_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='supportticket',
            name='public_contact',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='supportticket',
            name='public_email',
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='supportticket',
            name='public_full_name',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='supportticket',
            name='requester',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='requested_support_tickets', to='accounts.user'),
        ),
        migrations.AddField(
            model_name='supportticket',
            name='requester_type',
            field=models.CharField(choices=[('student', 'Студент'), ('curator', 'Куратор'), ('unknown', 'Другое')], default='student', max_length=16),
        ),
        migrations.AddField(
            model_name='supportticket',
            name='source',
            field=models.CharField(choices=[('account', 'Личный кабинет'), ('public', 'Публичная форма')], default='account', max_length=16),
        ),
        migrations.AlterField(
            model_name='supportticket',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='support_tickets', to='accounts.user'),
        ),
        migrations.AddIndex(
            model_name='supportticket',
            index=models.Index(fields=['source', 'status'], name='accounts_ticket_ss_idx'),
        ),
        migrations.AddIndex(
            model_name='supportticket',
            index=models.Index(fields=['requester_type', 'status'], name='accounts_ticket_rs_idx'),
        ),
        migrations.RunSQL(
            sql="UPDATE accounts_supportticket SET requester_id = student_id, requester_type = 'student', source = 'account' WHERE requester_id IS NULL AND student_id IS NOT NULL;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
