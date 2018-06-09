from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from chatchannels.models import ChatChannel


# Create your models here.
class ChessGame(models.Model):
    history = ArrayField(base_field=models.TextField())
    white = models.ForeignKey(User, related_name="white_games")
    black = models.ForeignKey(User, related_name="white_games", blank=True)
    start = models.DateTimeField(auto_now_add=True)
    end = models.DateTimeField(blank=True)
    win = models.CharField(max_length=10, blank=10)
    alive = models.BooleanField(default=False)

class GameSession(models.Model):
    channel = models.ForeignKey(ChatChannel)
    chess_game = models.ForeignKey(ChessGame)
    ready = models.BooleanField(default=False)
