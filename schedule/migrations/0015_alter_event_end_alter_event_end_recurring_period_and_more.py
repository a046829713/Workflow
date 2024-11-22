# Generated by Django 4.2.3 on 2024-05-02 01:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0014_use_autofields_for_pk'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end',
            field=models.DateTimeField(db_index=True, verbose_name='end'),
        ),
        migrations.AlterField(
            model_name='event',
            name='end_recurring_period',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='end recurring period'),
        ),
        migrations.AlterField(
            model_name='event',
            name='rule',
            field=models.ForeignKey(blank=True, help_text='目前暫無設計無須填寫', null=True, on_delete=django.db.models.deletion.SET_NULL, to='schedule.rule', verbose_name='rule'),
        ),
    ]