# Generated by Django 4.2.3 on 2024-10-01 08:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0028_remove_visitor_identification_document_number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='visitor',
            name='vehicle_license_plate',
        ),
    ]
