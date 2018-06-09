from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth.models import User

from chatchannels.models import ChatChannel


class ChatChannelConsumer(JsonWebsocketConsumer):
    """
    private (__*) methods are for receiving from downstream
    g_* methods are for receiving from channel group
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_id = None  # Number of the channel in DB
        self.channel_inst = None  # Instance of a ChatChannel model
        self.username = None  # username of downstream user
        self.channel_group_name = None  # Channel-layer level group name
        self.sync_group_send = None

    def __isadmin(self):
        """
        Must be a method because adding an admin can change this object's flag
        """
        return self.channel_inst.admins.filter(username=self.username).exists()

    def connect(self):
        self.sync_group_send = async_to_sync(self.channel_layer.group_send)
        self.channel_group_name = None
        self.channel_id = self.scope['url_route']['kwargs']['chat_channel_id']
        try:
            self.channel_inst = ChatChannel.objects.get(pk=self.channel_id)
        except ChatChannel.DoesNotExist:
            return self.close(code=400)

        self.username = self.scope['user'].username
        if not self.channel_inst.is_public \
                and not self.__isadmin() \
                and not self.channel_inst.allowed_participants.filter(pk=self.scope['user'].id).exists():
            return self.close(code=403)

        self.channel_group_name = 'ChatChannel_%s' % self.channel_id

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.channel_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        if self.channel_group_name is None:
            return
        async_to_sync(self.channel_layer.group_discard)(
            self.channel_group_name,
            self.channel_name
        )

    def group_send(self, dictionary):
        self.sync_group_send(self.channel_group_name, dictionary)

    def __add_admin(self, content):
        if not self.__isadmin():
            return
        try:
            username = content['username']
        except KeyError:
            return
        try:
            related_user = User.objects.get(username=username)
        except:
            return
        self.channel_inst.admins.add(related_user)  # No local-cache divergences
        self.channel_inst.allowed_participants.add(related_user)

    def __message(self, content):
        try:
            message = content['message']
        except KeyError:
            return
        if not isinstance(message, str):
            return
        message = self.username + ': ' + message
        self.channel_inst.history += [message]
        self.channel_inst.save()
        # Send message to room group
        self.group_send({
            'type': 'g_chat_message',
            'message': message
        })

    def __rm_admin(self, content):
        """
        :deprecated:
        :param content: json from downstream
        :return: None
        """
        if not self.__isadmin():
            return
        try:
            username = content['username']
        except KeyError:
            return
        try:
            user = User.objects.get(username=username)
        except:
            return
        self.channel_inst.admins.remove(user)

    def __allow(self, content):
        """
        Adds a user to list of allowed participants. Is idempotent.
        Only honored if issued by an admin
        :param content: json from downstream
        :return: None
        """
        if not self.__isadmin():
            return
        try:
            username = content['username']
        except:
            return
        try:
            user = User.objects.get(username=username)
        except:
            return
        self.channel_inst.allowed_participants.add(user)

    def __disallow(self, content):
        """
        Removes user from allowed participants. Has no
        effect if user is admin. Only honored if issuer is admin
        :param content:
        :return:
        """
        if not self.__isadmin():
            return
        try:
            username = content['username']
            user = User.objects.get(username=username)
        except:
            return
        if self.channel_inst.admins.filter(username=username).exists():
            return
        self.channel_inst.allowed_participants.remove(user)
        self.group_send({
            'type': 'g_disallow',
            'username': username
        })

    def __publicize(self, content):
        """
        Switches channel from public to private (vice-versa). Only honored
        if issued by an admin
        :param content: json containing new channel public-status
        :return: None
        """
        if not self.__isadmin():
            return
        try:
            public_status = content['public']
        except KeyError:
            return
        if not isinstance(public_status, bool):
            return
        self.channel_inst.is_public = public_status
        self.channel_inst.save()
        if public_status is False:  # Broadcast to group for kicking users not allowed
            self.group_send({
                'type': 'g_privatized'
            })

    # Receive message from WebSocket
    def receive_json(self, content, **kwargs):
        try:
            msg_type = content['type']
        except KeyError:
            return
        if msg_type == 'add_admin':
            self.__add_admin(content)
        elif msg_type == 'message':
            self.__message(content)
        elif msg_type == 'rm_admin':
            return  # Deprecated
        elif msg_type == 'allow':
            self.__allow(content)
        elif msg_type == 'disallow':
            self.__disallow(content)
        elif msg_type == 'publicize':
            self.__publicize(content)

    def g_disallow(self, event):
        """
        Receives message broadcasted in channel group, removing itself
        from connected clients if self.username is the target of the disallow
        :param event: json containing username disallowed
        :return: None
        """
        if self.username == event['username']:
            self.close(code=403)

    def g_chat_message(self, event):
        """
        Receives message from channel group and sends it downstream
        :param event: json containing message
        :return: None
        """
        message = event['message']
        # Send message to WebSocket
        self.send_json({
            'message': message
        })

    def g_privatized(self, content):
        """
        Kicks user from the channel if it is set to 'private' and user
        does not belong to 'allowed_participants'
        :return: None
        """
        if not self.channel_inst.allowed_participants.filter(username=self.username).exists():
            return self.close(403)
