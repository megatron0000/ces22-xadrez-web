from django.contrib import admin

# Register your models here.
from chessgames.models import *

admin.site.register(GameSession)
admin.site.register(ChessGame)
