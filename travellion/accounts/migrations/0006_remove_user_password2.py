# Generated by Django 4.2.4 on 2023-08-28 18:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_remove_user_point_user_password2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='password2',
        ),
    ]