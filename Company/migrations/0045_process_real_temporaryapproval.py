# Generated by Django 4.2.3 on 2023-11-23 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Company', '0044_form_relationshipnumber'),
    ]

    operations = [
        migrations.AddField(
            model_name='process_real',
            name='temporaryapproval',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
