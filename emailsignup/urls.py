from django.urls import path
from emailsignup import views

app_name = 'emailsignup'

# TODO: 'profile' and 'reset' have nothing to do with signup.
# Should be moved to another app

urlpatterns = [
    path('profile/', views.profile, name="profile"),
    path('signup/', views.signup, name="signup"),
    path('account_activation_sent/', views.account_activation_sent,
         name='account_activation_sent'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('resend_activation_email/', views.resend_activation_email,
         name='resend_activation_email'),
    path('reset/<uidb64>/<token>/', views.EmailSignupPasswordResetConfirmView.as_view(),
         name="password_reset_confirm")
]
