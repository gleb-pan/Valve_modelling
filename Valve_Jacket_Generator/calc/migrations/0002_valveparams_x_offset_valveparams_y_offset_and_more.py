# Generated by Django 4.1.7 on 2023-03-25 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calc', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='valveparams',
            name='X_offset',
            field=models.CharField(default=0, max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='valveparams',
            name='Y_offset',
            field=models.CharField(default=0, max_length=10),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='valveparams',
            name='hole_offset',
            field=models.CharField(default=0, max_length=10),
            preserve_default=False,
        ),
    ]