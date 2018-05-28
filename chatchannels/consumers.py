from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json

from django.contrib.auth.models import User
from django.db.models import F

from chatchannels.models import ChatChannel


class ChatChannelConsumer(WebsocketConsumer):
    def connect(self):
        self.channel_group_name = None
        self.channel_id = self.scope['url_route']['kwargs']['chat_channel_id']
        try:
            self.channel_inst = ChatChannel.objects.get(pk=self.channel_id)
        except ChatChannel.DoesNotExist:
            return self.close(code=400)

        self.is_admin = self.channel_inst.admins.filter(pk=self.scope['user'].id).exists()
        if not self.channel_inst.is_public \
                and not self.is_admin \
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

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)

        if text_data_json['type'] == 'add_admin':
            try:
                self.channel_inst.admins.add(User.objects.get(username=text_data_json['username']).id)
            except:
                pass
        elif text_data_json['type'] == 'message':
            message = text_data_json['message']
            # Send message to room group
            async_to_sync(self.channel_layer.group_send)(
                self.channel_group_name,
                {
                    'type': 'chat_message',
                    'message': message
                }
            )

    # Receive message from room group
    def chat_message(self, event):
        # Prepend username
        message = self.scope['user'].username + ':: ' + event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))
        self.channel_inst.history += [message]
        self.channel_inst.save()
