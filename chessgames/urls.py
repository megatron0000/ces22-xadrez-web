from django.urls import path

from chessgames import views

app_name = 'chessgames'

urlpatterns = [
    # path('', views.index, name='index'),  # Debugging only
    path('play/', views.play, name='play'),
    path('play/<game_id>', views.play_game_id, name="play_game_id"),
    path('host_game', views.host_game, name="host_game")
]
