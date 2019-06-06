from datetime import datetime
from threading import Timer

from chessgames.common.group_msgs import GroupMsgs, group_send
from chessgames.models import ChessGame


def __win_by_timer(game_id, move_count, winning_player):
    try:
        game = ChessGame.objects.get(pk=game_id)
    except ChessGame.DoesNotExist:
        return

    if len(game.history) != move_count:
        return

    # Avoid overwriting ended games
    if (game.win in ('white', 'black', 'draw')):
        return

    game.win = winning_player
    game.end = datetime.now()
    game.alive = False
    game.save()
    group_send(game_id, GroupMsgs.g_game_end(winning_player, out_of_time=True))


def run_timer(game_id, move_count, winning_player):
    Timer(600, __win_by_timer, args=(game_id, move_count, winning_player)).start()
