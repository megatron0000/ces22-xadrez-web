from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError


def uniquemail_validator(value):
    try:
        User.objects.get(email=value)
        raise ValidationError(_('A user already exists with this email'), code='duplicate')
    except User.DoesNotExist:
        return


def mailexists_validator(value):
    try:
        User.objects.get(email=value)
    except User.DoesNotExist:
        raise ValidationError(_('No user is registered with this email'))


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254,
                             help_text=_('Required. Inform a valid email address.'),
                             validators=[uniquemail_validator])

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',)


class ResendActivationEmailForm(forms.Form):
    email = forms.EmailField(label='The email you registered with',
                             validators=[mailexists_validator])
