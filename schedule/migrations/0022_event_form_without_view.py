# Generated by Django 4.2.3 on 2024-05-14 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0021_visitor_creator'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='form_without_view',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='form_without_view'),
        ),
    ]
