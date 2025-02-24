# Generated by Django 5.1.5 on 2025-02-18 22:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faculty', '0004_remove_facultyprofile_created_at_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='schedule',
            old_name='date',
            new_name='end_date',
        ),
        migrations.RemoveField(
            model_name='schedule',
            name='description',
        ),
        migrations.AddField(
            model_name='schedule',
            name='duration',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='schedule',
            name='start_date',
            field=models.DateField(default='2025-02-18'),
        ),
    ]
