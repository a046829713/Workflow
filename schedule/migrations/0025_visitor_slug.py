# Generated by Django 4.2.3 on 2024-05-14 04:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0024_rename_form_event_form_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='visitor',
            name='slug',
            field=models.CharField(default=1, max_length=50, verbose_name='Data Base Slug'),
            preserve_default=False,
        ),
    ]
