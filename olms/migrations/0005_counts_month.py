# Generated by Django 3.1.3 on 2020-11-19 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('olms', '0004_counts'),
    ]

    operations = [
        migrations.AddField(
            model_name='counts',
            name='month',
            field=models.IntegerField(default=11),
        ),
    ]
