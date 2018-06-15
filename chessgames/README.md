# chessgames

Django app for playing chess games online.

## urls

All urls require authentication.

- ``POST host_game/``: Creates a GameSession object and returns the ids of its associated ChatChannel and ChessGame. An opponent has 60 seconds to connect before the created objects are deleted for staying too much time in pending state.

- ``play/``: Renders template `chessgames/list.html` (inteded to allow a user to host his own game or select an offered one to play)

- ``GET play/<game_id>``: Renders `chessgames/play.html` supplying context variables `chessgame_id` and `chatchannel_id` corresponding to the associated objects of a GameSession with id `game_id` (if the latter does not exist, 404es).

- ``POST play/<game_id>``: If there is a GameSession record which still has only one player (no opponent), associates the requesting user as the second player of such game (lifting the initial 60 seconds pending timeout from `host_game`)

## routing

- ``connect/<game_id>``: Connects to a websocket consumer for playing or watching a game associated to a ChessGame record (only if `game_id` identifies an existent record of mentioned model)

## Websocket protocol

Once the client connects to a chess game, messages can be exchanged:

### From client to server

- ``{ type: 'move', move: string, request_draw: boolean }``: Requests that a move be made in the game. The execution is not immediate: the server will respond accepting or denying the move. Only works if emitted by the player of the current turn. Set `request_draw==true` to request
a draw from the opponent.

- ``{ type: 'draw_accept' }``: Works only if emitted by a player the turn after the opponent made a move while requesting a draw (identified by `request_draw==true` in `move` message)

- ``{ type: 'status_prompt' }``: Prompts a response from the server containing the game's current status

### From server to client

- ``{ type: 'pending_timeout' }``: When the game stays too much time in "pending" state (in which there is still only 1 player; the second is still to enter the game). The game is erased from database and no 'game_end' message is sent.

- ``{ type : 'move', move: string, draw_requested: boolean }``: When a move has been accepted by the server and executed on the game. If `draw_requested==true`, the next player can either: send `draw_accept` to draw the game; send `move` to reject the draw and keep playing.

- ``{ type: 'game_end', winner: 'white' | 'black' | 'draw', out_of_time: boolean }``: When the game ends. If a player accepts the draw offer of another, this message will contain `reason=="draw"` after the draw is executed on the server. If a player does not move within time, `out_of_time==true` and said player loses.

- ``{ type: 'game_status', status: GameStatus }``: Emitted as response to `status_prompt` request. See below for GameStatus interface

- ``{ type: 'game_start', opponent: string }``: Emitted if the game was in "pending" state (there was only one player) and a second player appears to be the opponent

````ts
interface GameStatus {
	white: string // username of the white player
	black: string | null, // null if no opponent appeared to take the role of black player yet
	whoami: string, // username of requesting user
	turn: 'white' | 'black' | null, // null if the game hasn't started or has ended
	victory: 'white' | 'black' | 'draw' | null // null if the game hasn't started
}
````
