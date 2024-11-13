# Generated by Django 5.1 on 2024-11-13 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_exercise_exercise_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='exercise',
            name='learning_style',
            field=models.CharField(choices=[('visual', 'Visual'), ('auditory', 'Auditory'), ('kinesthetic', 'Kinesthetic')], default='visual', max_length=100),
        ),
    ]