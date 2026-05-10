from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0002_portfolioattachment'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='portfolioentry',
            index=models.Index(fields=['student', 'status'], name='portfolio_entry_ss_idx'),
        ),
        migrations.AddIndex(
            model_name='portfolioentry',
            index=models.Index(fields=['student', '-created_at'], name='portfolio_entry_sc_idx'),
        ),
        migrations.AddIndex(
            model_name='portfolioentry',
            index=models.Index(fields=['status', '-created_at'], name='portfolio_entry_stc_idx'),
        ),
    ]
