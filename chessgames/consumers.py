from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from chessgames.models import ChessGame
import time


class GroupMsgs:
    """
    Messages exchanged via channel layer (intra-server)
    """

    @staticmethod
    def g_entered(username):
        return {'type': 'g_entered', 'username': username}

    @staticmethod
    def g_exited(username):
        return {'type': 'g_exited', 'username': username}

    @staticmethod
    def g_move(move, request_draw):
        """
        :param move: string defining move
        :param request_draw: boolean indicating whether user requested draw
        """
        return {'type': 'g_move', 'move': move, 'request_draw': request_draw}

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
    def g_play_timer_ended(consumer_channel, turn_id):
        """
        Emitted by a timer thread when 60 seconds elapse since the beggining of a player's
        turn. The consumer receiving the message can then forfeit the game if the player has
        not moved in time
        :param consumer_channel: channel name of the consumer that originally started the timer (so
        that the timer knows who to send information back to)
        :param turn_id: Unique identifier of the turn the player was in when the timer started
        """
        return {'type': 'g_play_timer_ended', 'turn_id': turn_id}


class ServerMsgs:
    """
    Messages sent from server to client. Refer to README
    """

    @staticmethod
    def pending_timeout():
        return {'type': 'pending_timeout'}

    @staticmethod
    def move(move, draw_requested):
        return {'type': 'move', 'move': move, draw_requested: 'draw_requested'}

    @staticmethod
    def game_end(winner, out_of_time):
        return {'type': 'game_end', 'winner': winner, 'out_of_time': out_of_time}

    @staticmethod
    def game_status(status):
        return {'type': 'game_status', 'status': status}


class ChessGameConsumer(JsonWebsocketConsumer):
    """
    private (__*) methods are for receiving from downstream (but the entry point
    from downstream is receive_json.
    g_* methods are for receiving from channel group
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_inst = None  # Instance of a ChessGame model
        self.username = None  # username of downstream user
        self.channel_group_name = None  # Channel-layer level group name
        self.sync_group_send = None  # Internal helper. Use self.group_send instead
        self.is_first_player = None  # Whether this is the hosting player
        self.is_second_player = None  # Whether this is the opponent of the hosting player
        self.turn_id = None  # Unique id generated for every turn of the player

    def group_send(self, dictionary):
        """
        Helper to send any message to the group
        :param dictionary: Data to be sent ('type' key will decide method to execute on receivers
        according to django-channels docs)
        """
        self.sync_group_send(self.channel_group_name, dictionary)

    def connect(self):
        self.sync_group_send = async_to_sync(self.channel_layer.group_send)

        game_id = self.scope['url_route']['kwargs']['chess_game_id']
        try:
            self.game_inst = ChessGame.objects.get(pk=game_id)
        except ChessGame.DoesNotExist:
            return self.close(code=404)

        self.username = self.scope['user'].username

        self.is_first_player = self.username == self.game_inst.white.username
        self.is_second_player = self.game_inst.black and self.username == self.game_inst.black.username

        self.channel_group_name = 'ChessGame_%s' % game_id

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.channel_group_name,
            self.channel_name
        )

        self.accept()

        self.group_send(GroupMsgs.g_entered(username=self.username))

    def disconnect(self, close_code):
        # Leave room group
        if self.channel_group_name is None:
            return

        self.group_send(GroupMsgs.g_exited(username=self.username))

        async_to_sync(self.channel_layer.group_discard)(
            self.channel_group_name,
            self.channel_name
        )

    def receive_json(self, event, **kwargs):
        """
        Receives message directly from associated client
        """
        try:
            msg_type = event['type']
        except KeyError:
            return
        if msg_type == 'bla':
            'ble'
        elif msg_type == 'bli':
            'blo'

    def g_model_deleted(self):
        self.send_json(ServerMsgs.pending_timeout())

    def g_play_timer_ended(self, event):
        if self.turn_id != event["turn_id"]:
            return
        if self.is_first_player:
            win = "black"
        else:
            win = "white"
        self.game_inst.win = win
        self.game_inst.end = time.time()
        self.game_inst.alive = False
        self.game_inst.save()
        self.group_send(GroupMsgs.g_game_end(win, True))

    def g_game_end(self, event):
        time_out = event["out_of_time"]
        win = event["winner"]
        self.send_json(ServerMsgs.game_end(win, time_out))