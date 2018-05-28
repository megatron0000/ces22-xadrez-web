# chatchannels

Django app for creating chat channels with:
 - Permitted participants
 - Channel admins
 - Persistent message history
 
## Dependencies
 - Assumes {% static 'vendor/jquery.js' %} to be available

## `templates/chatchannels`

Used for debugging

## urls

- ``request_channel``: Expects POST with ``{ is_public : bool }`` body. Creates a ChatChannel object
and returns its id in response: ``{ id: number }``

## routing

- ``connect/<chat_channel_id>``: Establishes ws connection if
channel exists and user is allowed to enter (channel is public,
or user is one of the admins, or user is in the 'allowed_participants')

