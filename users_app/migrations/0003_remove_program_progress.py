# Generated by Django 5.1.2 on 2024-11-23 15:12

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users_app", "0002_remove_program_goal_type"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="program",
            name="progress",
        ),
    ]