from django.urls import path
from emailsignup import views

app_name = 'emailsignup'

urlpatterns = [
    path('signup/', views.signup, name="signup"),
    path('account_activation_sent/', views.account_activation_sent, name='account_activation_sent'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('resend_activation_email/', views.resend_activation_email, name='resend_activation_email')
]
