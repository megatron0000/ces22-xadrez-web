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
    history = ArrayField(base_field=models.TextField())
    allowed_participants = \
        models.ManyToManyField(to=User, related_name='allowed_channels')  # Empty if 'is_public'


@receiver(pre_delete, sender=ChatChannel, dispatch_uid="warn_open_chat_consumers")
def warn_open_chat_consumers(sender, instance, **kwargs):
    async_to_sync(get_channel_layer().group_send)(
        'ChatChannels_%s' % instance.id,  # group name according to my own undocumented convention
        {'type': 'g_channel_deleted'}
    )
