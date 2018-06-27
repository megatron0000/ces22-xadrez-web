from django.contrib import admin

# Register your models here.
from chatchannels.models import ChatChannel, ChatMessage

admin.site.register(ChatChannel)
admin.site.register(ChatMessage)
