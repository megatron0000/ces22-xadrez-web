# Generated by Django 2.0.5 on 2018-06-27 16:25

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('chatchannels', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChessGame',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('history', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), size=None)),
                ('start', models.DateTimeField(auto_now_add=True)),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('win', models.CharField(blank=True, max_length=10)),
                ('alive', models.BooleanField(default=False)),
                ('black', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='black_games', to=settings.AUTH_USER_MODEL)),
                ('white', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='white_games', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GameSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ready', models.BooleanField(default=False)),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatchannels.ChatChannel')),
                ('chess_game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chessgames.ChessGame')),
            ],
        ),
    ]