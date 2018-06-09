from chessgames.models import ChessGame
from chatchannels.views import _request_channel
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from chessgames.models import GameSession
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



@login_required()
def play(request):
    return render(request,'chessgames/list.html')

def play_game_id(request, game_id):
    if request.method == "GET":
        return render(request,'chessgames/play.html',{"id":game_id})
    if request.method != "POST":
        return
    if not request.user.is_authenticated:
        return JsonResponse({"id":None})
    try:
        obj = GameSession.objects.get(pk=game_id, ready=False)

    except:

        return JsonResponse({"id": None})

    obj.ready = True
    channel = obj.channel
    channel.admins.add(request.user)
    channel.allowed_participants.add(request.user)
    channel.save()
    game = obj.chess_game
    game.black = request.user
    game.alive = True
    game.save()
    obj.save()
    return JsonResponse({"id": obj.id})
