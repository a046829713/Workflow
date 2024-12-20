# Generated by Django 4.2.3 on 2023-11-15 02:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('QualityAssurance', '0007_delete_abnormalfactna'),
    ]

    operations = [
        migrations.CreateModel(
            name='AbnormalFactna',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('form_id', models.CharField(max_length=100)),
                ('item', models.CharField(max_length=100)),
                ('factoryno', models.CharField(max_length=100, verbose_name='加工廠商編號')),
                ('factoryname', models.CharField(max_length=100, verbose_name='加工廠商名稱')),
                ('makeno', models.CharField(max_length=100, verbose_name='加工製程編號')),
                ('makename', models.CharField(max_length=100, verbose_name='加工製程')),
            ],
            options={
                'unique_together': {('form_id', 'item')},
            },
        ),
    ]
