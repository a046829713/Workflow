# Generated by Django 4.2.3 on 2024-02-27 03:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('KnowledgeDatabase', '0004_knowledgedatabase_model_last_edit_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='knowledgedatabase_model',
            name='last_edit_time',
            field=models.DateTimeField(auto_now=True, verbose_name='最後修改日期'),
        ),
    ]
