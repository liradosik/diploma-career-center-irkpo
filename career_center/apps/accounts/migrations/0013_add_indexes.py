from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_supportticket'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['role'], name='accounts_user_role_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['academic_status'], name='accounts_user_ac_status_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['study_group'], name='accounts_user_st_group_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['curator'], name='accounts_user_curator_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['is_active'], name='accounts_user_is_active_idx'),
        ),
        migrations.AddIndex(
            model_name='activitylog',
            index=models.Index(fields=['student', '-created_at'], name='accounts_actlog_sc_idx'),
        ),
        migrations.AddIndex(
            model_name='activitylog',
            index=models.Index(fields=['event_type', '-created_at'], name='accounts_actlog_ec_idx'),
        ),
        migrations.AddIndex(
            model_name='supportticket',
            index=models.Index(fields=['student', 'status'], name='accounts_ticket_st_idx'),
        ),
        migrations.AddIndex(
            model_name='supportticket',
            index=models.Index(fields=['status', '-created_at'], name='accounts_ticket_sc_idx'),
        ),
        migrations.AddIndex(
            model_name='supportticket',
            index=models.Index(fields=['category', 'status'], name='accounts_ticket_cs_idx'),
        ),
    ]
