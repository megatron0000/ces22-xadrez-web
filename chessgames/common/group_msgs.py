from channels.layers import get_channel_layer
from channels.consumer import async_to_sync

class GroupMsgs:
    """
    Messages exchanged via channel layer (intra-server)
    """

    """ @staticmethod
    def g_entered(username):
        return {'type': 'g_entered', 'username': username}

    @staticmethod
    def g_exited(username):
        return {'type': 'g_exited', 'username': username} """

    @staticmethod
    def g_move(move, draw_requested):
        """
        :param move: string defining move
        :param draw_requested: boolean indicating whether user requested draw
        """
        return {'type': 'g_move', 'move': move, 'draw_requested': draw_requested}

    @staticmethod
    def g_game_end(winner, out_of_time):
        """
        :param winner: 'white' or 'black' or 'draw'
        :param out_of_time: boolean. True if game ended because a player
        did not move in time during his turn
        """
        return {'type': 'g_game_end', 'winner': winner, 'out_of_time': out_of_time}

    @staticmethod
    def g_model_deleted():
        """
        Emitted when the ChessGame record corresponding to this game is deleted (for any reason
        whatsoever)
        """
        return {'type': 'g_model_deleted'}

    @staticmethod
    def g_model_changed():
        """
        Emitted when a ChessGame record corresponding to the group changes.
        """
        return {'type': 'g_model_changed'}

    @staticmethod
    def g_game_start(opponent):
        return {'type': 'g_game_start', 'opponent': opponent}


def group_send(game_id, dictionary):
    async_to_sync(get_channel_layer().group_send)(
        'ChessGame_%s' % game_id, dictionary
    )
