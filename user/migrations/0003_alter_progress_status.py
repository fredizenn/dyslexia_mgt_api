# Generated by Django 5.1 on 2024-09-21 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_progress'),
    ]

    operations = [
        migrations.AlterField(
            model_name='progress',
            name='status',
            field=models.CharField(choices=[('not_started', 'Not Started'), ('in_progress', 'In Progress'), ('completed', 'Completed')], max_length=50),
        ),
    ]
