# Generated by Django 4.2.1 on 2023-07-04 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Company', '0027_alter_process_real_endorsement_allow'),
    ]

    operations = [
        migrations.AddField(
            model_name='process_real',
            name='endorsement_count',
            field=models.IntegerField(default=0, null=True),
        ),
    ]