# Generated by Django 4.2.3 on 2024-03-06 05:18

import ckeditor_uploader.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Company', '0045_process_real_temporaryapproval'),
    ]

    operations = [
        migrations.CreateModel(
            name='RichText',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', ckeditor_uploader.fields.RichTextUploadingField(null=True, verbose_name='內容')),
                ('form', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rich_text_attachments', to='Company.form')),
            ],
            options={
                'db_table': 'Company_RichText',
            },
        ),
    ]
