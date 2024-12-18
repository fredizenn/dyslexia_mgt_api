# Generated by Django 5.1 on 2024-09-12 20:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Progress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='in_progress', max_length=50)),
                ('score', models.FloatField(default=0.0)),
                ('time_spent', models.DurationField(blank=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('exercise', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.exercise')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'exercise')},
            },
        ),
    ]
