# Generated by Django 3.1.2 on 2020-11-17 15:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('olms', '0003_auto_20201106_1320'),
    ]

    operations = [
        migrations.CreateModel(
            name='Counts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leaves_this_month', models.IntegerField(default=0)),
                ('total_leaves', models.IntegerField(default=0)),
                ('outings_this_month', models.IntegerField(default=0)),
                ('total_outings', models.IntegerField(default=0)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_count', to='olms.userprofile')),
            ],
        ),
    ]