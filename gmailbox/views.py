from django.utils.translation import gettext as _
import google_auth_oauthlib.flow
from django.urls import reverse
from django.shortcuts import redirect, render
from gmailbox.models import UserToken
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required


def __getflow(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        settings.GMAIL_CLIENT_SECRET_PATH,
        scopes=['https://www.googleapis.com/auth/gmail.modify'])

    # Indicate where the API server will redirect the user after the user completes
    # the authorization flow. The redirect URI is required.
    flow.redirect_uri = request.build_absolute_uri(reverse('gmailbox:oauth_redirect_internal'))
    return flow


@staff_member_required
def set_account(request):
    # Use the client_secret.json file to identify the application requesting
    # authorization. The client ID (from that file) and access scopes are required.
    flow = __getflow(request)

    # Generate URL for request to Google's OAuth 2.0 server.
    # Use kwargs to set optional request parameters.
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    return redirect(authorization_url)


def oauth_redirect_internal(request):
    flow = __getflow(request)
    # catch situations where, for example, user denied access
    try:
        flow.fetch_token(authorization_response=request.get_full_path())
        credentials = flow.credentials
    except:
        message = 'An error occurred'
        return redirect(reverse('gmailbox:oauth_redirect') + '?message=' + message)
    try:
        # refresh_token only comes on first authorization
        # repeated auth requests return None
        if credentials.refresh_token is not None:
            instance = UserToken.objects.get()
            instance.token = credentials.token,
            instance.refresh_token = credentials.refresh_token,
            instance.token_uri = credentials.token_uri,
            instance.client_id = credentials.client_id,
            instance.client_secret = credentials.client_secret,
            instance.scopes = credentials.scopes
            instance.save()
    except UserToken.DoesNotExist:
        instance = UserToken(
            token=credentials.token,
            refresh_token=credentials.refresh_token,
            token_uri=credentials.token_uri,
            client_id=credentials.client_id,
            client_secret=credentials.client_secret,
            scopes=credentials.scopes
        )
        instance.save()
    finally:
        message = _('You setup your email as the server\'s email')
        return redirect(reverse('gmailbox:oauth_redirect') + '?message=' + message)


def oauth_redirect(request):
    return render(request, 'gmailbox/oauth_redirect.html', context={
        'message': request.GET.get('message', '')
    })
