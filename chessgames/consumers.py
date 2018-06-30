from datetime import datetime

from channels.consumer import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from chessgames.common.chessengine import Game
from chessgames.common.group_msgs import GroupMsgs
from chessgames.common.move_timer import run_timer
from chessgames.models import ChessGame


class ServerMsgs:
    """
    Messages sent from server to client. Refer to README
    """

    @staticmethod
    def pending_timeout():
        return {'type': 'pending_timeout'}

    @staticmethod
    def move(move, draw_requested):
        return {'type': 'move', 'move': move, 'draw_requested': draw_requested}

    @staticmethod
    def game_end(winner, out_of_time):
        return {'type': 'game_end', 'winner': winner, 'out_of_time': out_of_time}

    @staticmethod
    def game_status(status):
        return {'type': 'game_status', 'status': status}

    @staticmethod
    def game_start(opponent):
        """
        :param opponent: The opponent player (username) that has just entered the game
        """
        return {'type': 'game_start', 'opponent': opponent}


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
        self.engine = None
        self.accept_draw_validity = False

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

        self.reset_engine()

    def reset_engine(self):
        self.engine = Game.default_game()
        for move in self.game_inst.history:
            self.engine.make(move)

    def disconnect(self, close_code):
        # Leave room group
        if self.channel_group_name is None:
            return

        async_to_sync(self.channel_layer.group_discard)(
            self.channel_group_name,
            self.channel_name
        )

    def __move(self, move, request_draw):
        if not self.myturn():
            return

        # I moved, which means I have not accepted my opponent's draw
        # request, if any
        self.accept_draw_validity = False

        # Validate and execute
        try:
            self.engine.make(move)
        except:
            return

        self.game_inst.history.append(move)
        self.game_inst.save()

        me = 'white' if self.is_first_player else 'black'

        if self.engine.checkmate():
            self.game_inst.end = datetime.now()
            self.game_inst.win = me
            self.game_inst.alive = False
            self.game_inst.save()
            # Cannot request draw if the move checkmates the opponent
            self.group_send(GroupMsgs.g_move(move=move, draw_requested=False))
            self.group_send(GroupMsgs.g_game_end(winner=me, out_of_time=False))
        # Forced draw
        elif self.engine.stalemate():
            self.game_inst.win = "draw"
            self.game_inst.end = datetime.now()
            self.game_inst.alive = False
            self.game_inst.save()
            # Cannot request draw because draw is enforced anyway
            self.group_send(GroupMsgs.g_move(move=move, draw_requested=False))
            self.group_send(GroupMsgs.g_game_end(winner="draw", out_of_time=False))
        else:
            self.group_send(GroupMsgs.g_move(move=move, draw_requested=request_draw))
            run_timer(self.game_inst.id, move_count=len(self.game_inst.history), winning_player=me)

    def __draw_accept(self):
        if not self.myturn():
            return
        if self.accept_draw_validity is not True:
            return
        self.game_inst.win = "draw"
        self.game_inst.end = datetime.now()
        self.game_inst.alive = False
        self.game_inst.save()
        self.group_send(GroupMsgs.g_game_end(winner="draw", out_of_time=False))

    def __status_prompt(self):
        white = self.game_inst.white.username
        black_user = self.game_inst.black
        black = None if black_user is None else black_user.username
        if black_user is None or self.game_inst.end is not None:
            turn = None
        elif len(self.game_inst.history) % 2 == 0:
            turn = "white"
        else:
            turn = "black"
        self.send_json(ServerMsgs.game_status({
            "white": white,
            "black": black,
            "turn": turn,
            "whoami": self.username,
            "victory": self.game_inst.win,
            "moves": self.game_inst.history
        }))

    def myturn(self):
        """
        Helper to determine if I am a player and it is now my turn (and if game is not over)
        :return: True if it is my turn. False otherwise
        """
        if self.game_inst.end is not None:
            return False
        if not self.is_first_player and not self.is_second_player:
            return False
        count = len(self.game_inst.history) % 2
        return (self.is_first_player and count == 0) or (self.is_second_player and count == 1)

    def receive_json(self, event, **kwargs):
        """
        Receives message directly from associated client
        """
        try:
            msg_type = event['type']
        except KeyError:
            return

        if msg_type == 'move':
            try:
                move = event['move']
                request_draw = event['request_draw']
            except KeyError:
                return
            self.__move(move, request_draw)
        elif msg_type == "draw_accept":
            self.__draw_accept()
        elif msg_type == "status_prompt":
            self.__status_prompt()

    def g_model_deleted(self, event):
        self.send_json(ServerMsgs.pending_timeout())

    def g_game_end(self, event):
        self.send_json(ServerMsgs.game_end(event['winner'], event['out_of_time']))

    def g_move(self, event):
        self.send_json(ServerMsgs.move(event['move'], event['draw_requested']))

        # If opponent requested draw (now is my turn), I can accept the request
        if self.myturn() and event["draw_requested"]:
            self.accept_draw_validity = True

    def g_game_start(self, event):
        self.send_json(ServerMsgs.game_start(event['opponent']))

    def g_model_changed(self, event):
        """
        Only synchronizes moves
        """
        oldmoves_length = len(self.game_inst.history)

        self.game_inst.refresh_from_db()

        while oldmoves_length < len(self.game_inst.history):
            self.engine.make(self.game_inst.history[oldmoves_length])
            oldmoves_length += 1
