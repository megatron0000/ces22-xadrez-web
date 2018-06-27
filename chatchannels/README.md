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

- ``request_channel/``: Expects POST with ``{ is_public : bool }`` body. Creates a ChatChannel object
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
(adds to 'allowed_participants' consequently). Honored only if issued by an admin

- ``{ type: 'message', message: string }``: Sends a message to the channel
 or is not an admin currently

- ``{ type: 'publicize', public: boolean }``: Sets the channel to public (`public===true`) or to private
(`public===false`). Only honored if issued by an admin. If set to false, all users not in 'allowed_participants'
will be kicked

- ``{ type: 'allow', username: string }`` adds a user to 'allowed_participants' (this is done automatically in case a user receives 'admin' status). Only honored if issued by an admin

- ``{ type: 'disallow', username: string }`` removes a user from 'allowed_participants'. If the user is online,
kicks him too. Does nothing if issued against an admin

- ``{ type: 'latest', offset: number, limit: number }`` issues response containing the `limit` latest messages when `offset` messages are disconsidered.

#### removed

- ``{ type: 'rm_admin', username: string }``: Removes 'username' from list of admins (but
does not alter 'allowed_participants' list). Does nothing if 'username' does not exist in DB

**There is no way to remove admin status from a user**

### from server to client

- ``{ type: 'message', message: Message }``: When a message is received from upstream (sent by the client itself
or other connected client). See below for `Message` interface

- ``{ type: 'entered', username: string }``: When someone enters the channel

- ``{ type: 'exit', username: string }``: When someone exits the channel

- ``{ type: 'i_am_here', username: string }``: When a new consumer is opened, all other active consumers send this message to it (this way, the new client may know all other connected clients)

- ``{ type: 'latest', offset: number, limit: number, messages: Message[] }``: When a client previously issued a `latest` request. `offset` and `limit` are echoes from the client, and `messages` are the messages the client requested.

````ts
interface Message {
    content: string // text from the author
    author: string // username of author
    timestamp: string // iso format string describing time of creation
}
````