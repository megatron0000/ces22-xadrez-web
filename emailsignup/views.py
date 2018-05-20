"""
Attribution: Simple is Better Than Complex
"""

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from emailsignup.forms import SignUpForm
from emailsignup.tokens import account_activation_token
from django.utils.translation import gettext as _
from emailsignup.forms import ResendActivationEmailForm


def _send_activation_mail(request, user):
    current_site = get_current_site(request)
    subject = _('Activate Your Webxadrez Account')
    message = render_to_string('registration/account_activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
        'token': account_activation_token.make_token(user),
    })
    user.email_user(subject, message)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            _send_activation_mail(request, user)
            return redirect(reverse('emailsignup:account_activation_sent') + '?email=' +
                            form.cleaned_data['email'])
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def resend_activation_email(request):
    if request.method == 'GET':
        form = ResendActivationEmailForm()
        return render(request, 'registration/resend_activation_email.html', context={
            'form': form
        })
    elif request.method == 'POST':
        form = ResendActivationEmailForm(request.POST)
        if form.is_valid():
            user = User.objects.get(email=form.cleaned_data['email'])
            print(':: email is ', form.cleaned_data['email'], '::')
            print(':: user is', user, '::')
            _send_activation_mail(request, user)
            return redirect('emailsignup:account_activation_sent')
        else:
            return render(request, 'registration/resend_activation_email.html', context={
                'form': form
            })


def account_activation_sent(request):
    return render(request, 'registration/account_activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        return render(request, 'registration/account_activation_done.html')
    else:
        return render(request, 'registration/account_activation_invalid.html')
