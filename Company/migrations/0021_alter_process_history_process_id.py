# Generated by Django 4.2.1 on 2023-07-03 01:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Company', '0020_alter_process_history_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='process_history',
            name='process_id',
            field=models.CharField(max_length=100),
        ),
    ]
