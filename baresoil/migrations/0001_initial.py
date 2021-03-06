# Generated by Django 3.0.3 on 2020-07-05 14:05

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PreviousQueries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mnth', models.IntegerField()),
                ('yr', models.IntegerField()),
                ('ndvi', models.FloatField()),
                ('ndvi_low', models.FloatField()),
                ('request_datetime', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('nelat', models.FloatField()),
                ('nelng', models.FloatField()),
                ('swlat', models.FloatField()),
                ('swlng', models.FloatField()),
            ],
        ),
    ]
