from chessgames.models import ChessGame
from chatchannels.views import create_channel
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, Http404, redirect
from chessgames.models import GameSession
from django.http import JsonResponse


def host_game(request):
    """
    Under POST, creates a game in DB and returns its id (only authenticated users)
    """
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
    """
    Under GET:
        For authenticated users, renders play page for game identified by 'game_id'
        (404 if 'game_id' is not in DB)
    Under POST:
        For an authenticated user, sets him as the opponent in game identified by 'game_id'
        (which had already been opened earlier by another user with POST to 'host_game').
        Disallows same user from hosting and playing as his own opponent.
        Returns id of the game
    """
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

        if obj.chess_game.white.id == request.user.id:
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
