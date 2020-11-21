# Generated by Django 3.0.5 on 2020-11-12 14:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('my_class', '0003_profile_city'),
    ]

    operations = [
        migrations.CreateModel(
            name='Class',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('teacher', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='my_class.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='ProfileClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_join', models.DateTimeField(auto_now_add=True)),
                ('current_class', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_class.Class', unique=True)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_class.Profile', unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='classes',
            field=models.ManyToManyField(through='my_class.ProfileClass', to='my_class.Class', verbose_name='Классы'),
        ),
    ]
