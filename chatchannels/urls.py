from django.urls import path

from chatchannels import views

app_name = 'chatchannels'

urlpatterns = [
    # path('', views.index, name='index'),  # Debugging only
    path('request_channel/', views.request_channel, name='request_channel')
]
