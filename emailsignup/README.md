# emailsignup

Depends on django.contrib.auth app

## Assertions

- Email is unique (one email, one user instance)
- Activation tokens work only once

## urls

- ``signup/``: Displays a form for signing up if
    GET, or processes the form if POST
- ``account_activation_sent/``:  Renders template 
    ``registration/account_activation_sent.html``
- ``activate/<uidb64>/<token>/``: Activates an
    inactive account when accessed via GET
- ``resend_activation_email/``: In GET, renders the
    template ``registration/resend_activation_email.html``,
    containing a form (template variable ``form``)
    for selecting the email to which the
    activation link will be resent. In POST,
    takes the supplied form and either:
    -   Sends the email and redirects to
    ``account_activation_sent/``
    -   Finds out there is no registered user
    with supplied email (or other error),
    rerendering the form with an error 
    message contained in the form field
    

## Attribution

https://github.com/sibtc/simple-signup
