# Generated by Django 4.2.9 on 2024-01-22 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_heartrate_alter_heartaudio_audio_file_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='heartNavButton',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
    ]