from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import path

import chatchannels.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AllowedHostsOriginValidator(AuthMiddlewareStack(
        URLRouter([
            path('chatchannels/', URLRouter(
                chatchannels.routing.websocket_urlpatterns
            ))
        ])
    )),
})
