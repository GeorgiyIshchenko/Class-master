# Generated by Django 3.0.5 on 2020-12-26 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_class', '0026_class_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentanswer',
            name='edit_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]