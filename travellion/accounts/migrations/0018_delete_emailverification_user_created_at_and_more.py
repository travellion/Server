# Generated by Django 4.0.4 on 2023-09-23 17:11

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_remove_emailverification_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='EmailVerification',
        ),
        migrations.AddField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='user',
            name='verification_code',
            field=models.CharField(default=11, max_length=6),
            preserve_default=False,
        ),
    ]