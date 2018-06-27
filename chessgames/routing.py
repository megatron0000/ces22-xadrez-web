from django.urls import path

from chessgames import consumers

app_name = 'chessgames'

websocket_urlpatterns = [
    path('play/<chess_game_id>', consumers.ChessGameConsumer, name="connect")
]

