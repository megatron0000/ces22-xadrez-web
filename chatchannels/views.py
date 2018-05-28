import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

from chatchannels.models import ChatChannel


def index(request):
    return render(request, 'chatchannels/debug.html', {
        'create_channel_endpoint': reverse('chatchannels:request_channel'),
        'connect_channel_endpoint': '/chatchannels/connect/'
    })


def _request_channel(admins, is_public):
    """Internal use. For creating channels not necessarily from an HttpRequest"""
    # No 'allowed_participants' yet
    channel = ChatChannel(is_public=is_public, history=[])
    channel.save()
    channel.admins.add(*admins)
    return channel


@login_required
def request_channel(request):
    """
    Instantiates a channel and responds with its id
    POST body: { 'is_public' : bool }
    """
    if request.method == 'POST':
        return JsonResponse({
            'id': _request_channel([request.user], is_public=
            json.loads(request.POST.get('is_public', False))).id
        })
