# Generated by Django 3.0.5 on 2020-12-19 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_class', '0023_auto_20201216_1650'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentanswer',
            name='mark_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='studentanswer',
            name='send_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]