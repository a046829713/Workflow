# Generated by Django 4.2.3 on 2023-07-25 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Company', '0035_alter_level_limited_time_alter_level_station_manager'),
    ]

    operations = [
        migrations.AlterField(
            model_name='level',
            name='endorsement_manager',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='level',
            name='endorsement_mode',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]
