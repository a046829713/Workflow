# Generated by Django 4.2.3 on 2023-08-22 03:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Company', '0041_form_resourcenumber'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='form_name',
            field=models.CharField(default='', max_length=255),
        ),
    ]