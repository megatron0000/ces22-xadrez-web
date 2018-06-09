from django.shortcuts import render
from chessgames.models import ChessGame, GameSession
from chatchannels.models import ChatChannel
from chatchannels.views import _request_channel
from django.http import JsonResponse


def host_game(request):
    if not request.user.is_authenticated:
        return JsonResponse({"id": None})
    channel = _request_channel(admins=[request.user], is_public=True)
    game = ChessGame(history=[], white=request.user)
    channel.save()
    game.save()
    session = GameSession(channel=channel, chess_game=game)
    session.save()
    return JsonResponse({"id": session.id})
