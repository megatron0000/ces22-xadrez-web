from django.urls import path

from . import views


# Para namespace em "url names"
app_name = 'polls'

urlpatterns = [
    path('', views.index, name='index')
]
