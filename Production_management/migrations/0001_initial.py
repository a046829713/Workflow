# Generated by Django 4.2.3 on 2024-03-22 01:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HistoryDailyConsume',
            fields=[
                ('date', models.DateField(primary_key=True, serialize=False)),
                ('data', models.TextField()),
            ],
        ),
    ]
