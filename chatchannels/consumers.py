from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.contrib.auth.models import User
from django.core import serializers
from django.utils.html import escape

from chatchannels.models import ChatChannel, ChatMessage, chat_message_serialize

class ChatChannelConsumer(JsonWebsocketConsumer):
    """
    private (__*) methods are for receiving from downstream (but the entry poiny
    from downstream is receive_json.
    g_* methods are for receiving from channel group
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel_id = None  # Number of the channel in DB
        self.channel_inst = None  # Instance of a ChatChannel model
        self.user = None  # Instance of downstream User object
        self.username = None  # username of downstream user
        self.channel_group_name = None  # Channel-layer level group name
        self.sync_group_send = None
        self.sync_unique_send = None

    def __isadmin(self):
        """
        Must be a method because adding an admin can change this object's flag
        """
        return self.channel_inst.admins.filter(username=self.username).exists()

    def connect(self):
        self.sync_group_send = async_to_sync(self.channel_layer.group_send)
        self.sync_unique_send = async_to_sync(self.channel_layer.send)

        self.channel_id = self.scope['url_route']['kwargs']['chat_channel_id']
        try:
            self.channel_inst = ChatChannel.objects.get(pk=self.channel_id)
        except ChatChannel.DoesNotExist:
            return self.close(code=404)

        self.user = self.scope['user']
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

        self.group_send({
            'type': 'g_entered',
            'username': self.username,
            'channel': self.channel_name
        })

    def disconnect(self, close_code):
        # Leave room group
        if self.channel_group_name is None:
            return

        self.group_send({
            'type': 'g_exit',
            'username': self.username
        })

        async_to_sync(self.channel_layer.group_discard)(
            self.channel_group_name,
            self.channel_name
        )

    def group_send(self, dictionary):
        self.sync_group_send(self.channel_group_name, dictionary)

    def unique_send(self, channel_name, dictionary):
        self.sync_unique_send(channel_name, dictionary)

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
        # No local-cache divergences
        self.channel_inst.admins.add(related_user)
        self.channel_inst.allowed_participants.add(related_user)

    def __message(self, content):
        try:
            message = content['message']
        except KeyError:
            return
        if not isinstance(message, str):
            return

        # Sanitization
        message = escape(message)
        content = None

        msg_obj = ChatMessage(
            content=message, author=self.user, chat_channel=self.channel_inst)
        msg_obj.save()
        self.channel_inst.chat_message_set.add(msg_obj)
        self.channel_inst.save()

        # Send message to room group
        self.group_send({
            'type': 'g_chat_message',
            'message': chat_message_serialize(msg_obj)
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

    def __latest(self, content):
        """
        Gets the latest 'limit' messages when 'offset' messages are skipped
        """
        try:
            limit = content['limit']
            offset = content['offset']
        except KeyError:
            return

        if not isinstance(offset, int) or not isinstance(limit, int):
            return

        if limit < 0 or offset < 0:
            return

        objs = ChatMessage.objects.filter(chat_channel=self.channel_inst).order_by(
            '-timestamp')[offset:offset + limit]

        self.send_json({
            'type': 'latest',
            'offset': offset,
            'limit': limit,
            'messages': list(chat_message_serialize(msg) for msg in objs)
        })

    def receive_json(self, event, **kwargs):
        """
        Receives message directly from associated client
        """
        try:
            msg_type = event['type']
        except KeyError:
            return
        if msg_type == 'add_admin':
            self.__add_admin(event)
        elif msg_type == 'message':
            self.__message(event)
        elif msg_type == 'rm_admin':
            return  # Deprecated
        elif msg_type == 'allow':
            self.__allow(event)
        elif msg_type == 'disallow':
            self.__disallow(event)
        elif msg_type == 'publicize':
            self.__publicize(event)
        elif msg_type == 'latest':
            self.__latest(event)

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
        # Send message to WebSocket
        self.send_json({
            'type': 'message',
            'message': event['message']
        })

    def g_privatized(self, event):
        """
        Kicks user from the channel if it is set to 'private' and user
        does not belong to 'allowed_participants'
        :return: None
        """
        if not self.channel_inst.allowed_participants.filter(username=self.username).exists():
            return self.close(403)

    def g_entered(self, event):
        self.send_json({
            'type': 'entered',
            'username': event['username']
        })
        self.unique_send(event['channel'], {
            'type': 'g_i_am_here',
            'username': self.username
        })

    def g_i_am_here(self, event):
        self.send_json({
            'type': 'i_am_here',
            'username': event['username']
        })

    def g_exit(self, event):
        self.send_json({
            'type': 'exit',
            'username': event['username']
        })

    def g_channel_deleted(self, event):
        """
        Sent (maybe not exclusively) from pre_delete signal of ChatChannel
        """
        self.close()
