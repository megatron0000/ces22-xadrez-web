from chessgames.models import ChessGame
from chatchannels.views import create_channel
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, Http404, redirect
from chessgames.models import GameSession
from django.http import JsonResponse


def host_game(request):
    if request.method != 'POST':
        return JsonResponse({"id": None})
    if not request.user.is_authenticated:
        return JsonResponse({"id": None})

    channel = create_channel(admins=[request.user], is_public=True)
    game = ChessGame(history=[], white=request.user)
    channel.save()
    game.save()
    session = GameSession(channel=channel, chess_game=game)
    session.save()
    return JsonResponse({"id": session.id})


@login_required()
def play(request):
    return render(request, 'chessgames/list.html')


def play_game_id(request, game_id):
    # Render page if game exists (ready or not); else 404
    if request.method == "GET":
        if not request.user.is_authenticated:
            return redirect('login/')
        try:
            GameSession.objects.get(pk=game_id)
        except GameSession.DoesNotExist:
            raise Http404
        return render(request, 'chessgames/play.html', {"id": game_id})
    # Register second player and ready=True
    elif request.method == 'POST':
        try:
            obj = GameSession.objects.get(pk=game_id, ready=False)
        except GameSession.DoesNotExist:
            obj = None

        if obj is None or not request.user.is_authenticated:
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
