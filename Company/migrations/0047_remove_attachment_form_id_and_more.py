# Generated by Django 4.2.3 on 2024-07-04 02:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Company', '0046_richtext'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='attachment',
            name='form_id',
        ),
        migrations.RemoveField(
            model_name='attachment',
            name='form_name',
        ),
    ]
