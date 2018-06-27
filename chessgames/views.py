from chessgames.models import ChessGame
from chessgames.common.group_msgs import GroupMsgs, group_send
from chessgames.common.move_timer import run_timer
from chatchannels.views import create_channel
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, Http404, redirect
from chessgames.models import GameSession
from django.http import JsonResponse
from django.conf import settings
from threading import Timer


def __delete_game_session_after_timeout(gamesession_id):
    try:
        session = GameSession.objects.get(id=gamesession_id)
        if session.ready is False:
            session.delete()  # Internal signal listeners will delete game and channel
    except GameSession.DoesNotExist:
        pass

    # from django.db import connection
    # connection.close()


def host_game(request):
    """
    POST with authentication:
        Creates a game session in DB and returns its id.
        The stored game session is maintained for only 60 seconds. At the end of this period,
        if no opponent appeared (i.e. session.ready==False), the record is deleted from DB along
        with its ChessGame and ChatChannel
    """
    if request.method != 'POST':
        return JsonResponse({"game_id": None})

    if not request.user.is_authenticated:
        return JsonResponse({"game_id": None})

    channel = create_channel(admins=[request.user], is_public=True)
    game = ChessGame(history=[], white=request.user)
    channel.save()
    game.save()
    session = GameSession(channel=channel, chess_game=game)
    session.save()

    Timer(60.0, __delete_game_session_after_timeout, args=[session.id]).start()

    return JsonResponse({"game_id": session.id})


@login_required()
def play(request):
    pending_games = []
    for session in GameSession.objects.filter(ready=False).all():
        pending_games.append({
            'session_id': session.id,
            'white': session.chess_game.white.username,
            'black': None,
            'history': []
        })

    running_games = []
    for session in GameSession.objects.filter(ready=True, chess_game__win='').all():
        running_games.append({
            'session_id': session.id,
            'white': session.chess_game.white.username,
            'black': session.chess_game.black.username,
            'history': session.chess_game.history
        })

    return render(request, 'chessgames/list.html', {
        'pending_games': pending_games,
        'running_games': running_games
    })


def play_game_id(request, game_id):
    """
    Under GET:
        For authenticated users, renders play page for game session identified by 'game_id'
        (404 if 'game_id' is not in DB)
    Under POST:
        For an authenticated user, sets him as the opponent in game identified by 'game_id'
        (which had already been opened earlier by another user with POST to 'host_game').
        Disallows same user from hosting and playing as his own opponent.
        Returns id of the GameSession
    """

    # Render page if game exists (ready or not); else 404
    if request.method == "GET":
        if not request.user.is_authenticated:
            return redirect(settings.LOGIN_URL)
        try:
            session = GameSession.objects.get(pk=game_id)
        except GameSession.DoesNotExist:
            raise Http404
        # TODO: Really bad ! Channels has no url reversing mechanism like django does
        return render(request, 'chessgames/play.html', {
            "chessgame_ws_endpoint": "chessgames/play/" + str(session.chess_game.id),
            "chatchannel_ws_endpoint": "chatchannels/connect/" + str(session.channel.id),
            "game_id": game_id
        })

    # Register second player and ready=True
    elif request.method == 'POST':
        try:
            session = GameSession.objects.get(pk=game_id, ready=False)
        except GameSession.DoesNotExist:
            session = None

        if session is None or not request.user.is_authenticated:
            return JsonResponse({"game_id": None})

        if session.chess_game.white.id == request.user.id:
            return JsonResponse({"game_id": None})

        session.ready = True
        channel = session.channel
        channel.admins.add(request.user)
        channel.allowed_participants.add(request.user)
        channel.save()
        game = session.chess_game
        game.black = request.user
        game.alive = True
        game.save()
        session.save()

        # White has a fixed time to move. Else, black (current request.user) wins
        run_timer(game.id, move_count=0, winning_player='black')
        group_send(game.id, GroupMsgs.g_game_start(
            opponent=request.user.username))

        return JsonResponse({"game_id": session.id})
