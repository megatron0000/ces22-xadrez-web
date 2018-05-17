from django.urls import path

from gmailbox import views


# Para namespace em "url names"
app_name = 'gmailbox'

urlpatterns = [
    path('set_account/', views.set_account, name='set_account'),
    path('oauth_redirect_internal/', views.oauth_redirect_internal, name='oauth_redirect_internal'),
    path('oauth_redirect/', views.oauth_redirect, name='oauth_redirect')
]
