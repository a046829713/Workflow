# Generated by Django 4.2.3 on 2023-08-22 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Company', '0042_attachment_form_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='form_id',
            field=models.CharField(default='', max_length=255),
        ),
    ]