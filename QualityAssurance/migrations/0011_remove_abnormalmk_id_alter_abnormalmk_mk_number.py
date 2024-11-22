# Generated by Django 4.2.3 on 2023-11-15 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QualityAssurance', '0010_remove_abnormalmk_total_price_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='abnormalmk',
            name='id',
        ),
        migrations.AlterField(
            model_name='abnormalmk',
            name='mk_number',
            field=models.CharField(max_length=100, primary_key=True, serialize=False, verbose_name='MK單號'),
        ),
    ]
