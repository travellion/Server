# Generated by Django 4.0.4 on 2023-11-24 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgets', '0002_group_email_group_invite_code_group_invited_emails'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='invite_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]