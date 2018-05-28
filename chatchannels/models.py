from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models


# Create your models here.

class ChatChannel(models.Model):
    admins = models.ManyToManyField(to=User, related_name='admin_channels')
    is_public = models.BooleanField()
    history = ArrayField(base_field=models.TextField())
    allowed_participants = \
        models.ManyToManyField(to=User, related_name='allowed_channels')  # Empty if 'is_public'
