# Generated by Django 4.2.3 on 2024-06-24 02:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('KnowledgeDatabase', '0005_alter_knowledgedatabase_model_last_edit_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='knowledgedatabase_model',
            name='privacy',
            field=models.CharField(max_length=50, null=True, verbose_name='隱私'),
        ),
    ]
