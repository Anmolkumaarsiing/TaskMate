# Generated by Django 3.1.3 on 2025-01-09 19:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0011_task_deadline'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='deadline',
        ),
    ]
