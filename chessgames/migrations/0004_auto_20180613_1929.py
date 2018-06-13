# Generated by Django 2.0.5 on 2018-06-13 22:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chessgames', '0003_auto_20180611_0903'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamesession',
            name='channel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='chatchannels.ChatChannel'),
        ),
        migrations.AlterField(
            model_name='gamesession',
            name='chess_game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='chessgames.ChessGame'),
        ),
    ]
