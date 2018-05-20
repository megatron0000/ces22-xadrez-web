# gmailbox

A django app that allows use of an existing
gmail account for communication with a web
server's users.

## Setup

This app depends on the settings:

- ``GMAIL_CLIENT_SECRET_PATH``: Path to
the local file containing client secret 
generated from google (see their docs)

Some urls are provided: ``set_account/``, 
``oauth_redirect/``, ``oauth_redirect_internal``.
 The first is used for
directing the user to google for permission
approval;  The third is where the user
will be brought back to the server after
approving access to his account; The 
second is another redirect, done 
immediatly after the second, where a template called
``gmailbox/oauth_redirect.html`` will be served with a 
 context variable ``message``(you should 
provide this template)

The overall flow goes like:

- The user accesses ``prefix/set_account``
- He is redirected to google for granting
access
- Google redirects him back to ``prefix/oauth_redirect_internal``
- This app collects access and refresh tokens (or not, should an error happen)
- This app redirects the user to ``prefix/oauth_redirect`` 

