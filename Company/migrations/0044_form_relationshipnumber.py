# Generated by Django 4.2.3 on 2023-09-11 05:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Company', '0043_attachment_form_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='relationshipnumber',
            field=models.CharField(default='', max_length=100),
        ),
    ]
