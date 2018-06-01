# chatchannels

Django app for creating chat channels with:
 - Permitted participants
 - Channel admins
 - Persistent message history
 
## Dependencies
 - Assumes {% static 'vendor/jquery.js' %} to be available

## templates

- ``chatchannels``: Used for debugging

## urls

- ``request_channel``: Expects POST with ``{ is_public : bool }`` body. Creates a ChatChannel object
and returns its id in response: ``{ id: number }``

## routing

- ``connect/<chat_channel_id>``: Establishes ws connection if
channel exists and user is allowed to enter (channel is public,
or user is one of the admins, or user is in the 'allowed_participants'). Does nothing otherwise

## consumer protocol

Once connected to a channel, the client can send and receive messages to/from it. Messages must be in the 
format:

### from client to server

- ``{ type: 'add_admin', username: string }``: Adds an admin named 'username' to channel 
(adds to 'allowed_participants' consequentially). Honored only if issued by an admin
- ``{ type: 'message', message: string }``: Sends a message to the channel
 or is not an admin currently
- ``{ type: 'publicize', public: boolean }``: Sets the channel to public (`set===true`) or to private 
(`set===false`). Only honored if issued by an admin. If set to false, all users not in 'allowed_participants'
will be kicked
- ``{ type: 'allow', username: string }`` adds a user to 'allowed_participants'. Only honored if issued by an
admin (this is done automatically in case a user receives 'admin' status)
- ``{ type: 'disallow', username: string }`` removes a user from 'allowed_participants'. If the user is online,
kicks him too. Does nothing if issued against an admin

#### removed

- ``{ type: 'rm_admin', username: string }``: Removes 'username' from list of admins (but
does not alter 'allowed_participants' list). Does nothing if 'username' does not exist in DB

**There is no way to remove admin status from a user**

### from server to client

- ``{ type: 'message', message: string }``: When a message is received from upstream (sent by the client itself
or other connected client)

**maybe more status-inform messages**