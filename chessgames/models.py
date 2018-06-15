from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from chatchannels.models import ChatChannel
from django.dispatch import receiver
from django.db.models.signals import post_delete, pre_delete
from channels.layers import get_channel_layer
from channels.consumer import async_to_sync


class ChessGame(models.Model):
    history = ArrayField(base_field=models.TextField())
    "Users cannot be deleted as of now. No games will vanish because of this"
    white = models.ForeignKey(User, related_name="white_games", on_delete=models.CASCADE)
    black = models.ForeignKey(
        User, related_name="black_games", blank=True, null=True, on_delete=models.CASCADE)
    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(blank=True, null=True)
    win = models.CharField(max_length=10, blank=10)
    alive = models.BooleanField(default=False)


class GameSession(models.Model):
    channel = models.ForeignKey(ChatChannel, models.CASCADE)
    chess_game = models.ForeignKey(ChessGame, models.CASCADE)
    ready = models.BooleanField(default=False)


@receiver(post_delete, sender=GameSession, dispatch_uid="delete_game_session_associates")
def delete_game_session_associates(sender, instance, **kwargs):
    """
    A GameSession owns a channel and a chess_game.
    Delete the session and everything goes away
    """
    instance.channel.delete()
    instance.chess_game.delete()


@receiver(pre_delete, sender=ChessGame, dispatch_uid="warn_open_chessgame_consumers")
def warn_open_chessgame_consumers(sender, instance, **kwargs):
    async_to_sync(get_channel_layer().group_send)(
        'ChessGame_%s' % instance.id,  # group name according to my own undocumented convention
        {'type': 'g_model_deleted'}
    )
