from django.db import models
from chatchannels.models import ChatChannel


# Create your models here.

class GameSession(models.Model):
    channel = models.ForeignKey(ChatChannel)
    chess_game = models.ForeignKey(ChessGame)
    ready = models.BooleanField(default=False)
