# Generated by Django 2.0.5 on 2018-05-15 23:34

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.TextField()),
                ('refresh_token', models.TextField()),
                ('token_uri', models.TextField()),
                ('client_id', models.TextField()),
                ('client_secret', models.TextField()),
                ('scopes', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), size=None)),
            ],
        ),
    ]