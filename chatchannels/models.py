from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from channels.layers import get_channel_layer
from channels.consumer import async_to_sync


class ChatChannel(models.Model):
    admins = models.ManyToManyField(to=User, related_name='admin_channels')
    is_public = models.BooleanField()
    allowed_participants = \
        models.ManyToManyField(
            to=User, related_name='allowed_channels')  # Empty if 'is_public'


class ChatMessage(models.Model):
    content = models.TextField(max_length=500)
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    chat_channel = models.ForeignKey(
        to=ChatChannel, on_delete=models.CASCADE, related_name='chat_message_set')
    timestamp = models.DateTimeField(auto_now_add=True)


def chat_message_serialize(chat_message):
    return {
        'content': chat_message.content,
        'author': chat_message.author.username,
        'timestamp': chat_message.timestamp.isoformat()
    }


@receiver(pre_delete, sender=ChatChannel, dispatch_uid="warn_open_chat_consumers")
def warn_open_chat_consumers(sender, instance, **kwargs):
    async_to_sync(get_channel_layer().group_send)(
        # group name according to my own undocumented convention
        'ChatChannels_%s' % instance.id,
        {'type': 'g_channel_deleted'}
    )
