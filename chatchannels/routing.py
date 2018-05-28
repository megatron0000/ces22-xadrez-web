from django.urls import path

from chatchannels import consumers

app_name = 'chatchannels'

websocket_urlpatterns = [
    path('connect/<chat_channel_id>', consumers.ChatChannelConsumer, name="connect")
]

