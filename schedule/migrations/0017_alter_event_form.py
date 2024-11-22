# Generated by Django 4.2.3 on 2024-05-08 02:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Company', '0046_richtext'),
        ('schedule', '0016_event_form'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='form',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Company.form', verbose_name='form'),
        ),
    ]
