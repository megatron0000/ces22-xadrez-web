/**
 * @interface
 */
class Status {
  /**
   * @type string
   */
  white;
  /**
   * @type string | null
   */
  black;
  /**
   * @type string
   */
  whoami;
  /**
   * 'white' or 'black' or null
   * @type string | null
   */
  turn;
  /**
   * 'white' or 'black' or 'draw' or null
   * @type string | null
   */
  victory;
  /**
   * @type string[]
   */
  moves;
}

/**
 * @interface
 */
class ServerConnection {
  connect(){}
  disconnect(){}
  send(){}

  /**
   *
   * @param msg {Object}
   */
  onreceive(msg){}
}

class GameState {

  /**
   *
   * @param server_endpoint {string}
   * @param webchess_board {WebchessBoard}
   */
  constructor(server_endpoint, webchess_board) {
    this.__ws = new WebSocket(server_endpoint);
    /**
     * @type WebchessBoard
     */
    this.__board = webchess_board;
  }

  /**
   * Constructs an instance of any subclass of GameState
   * @param state_class {GameState.}
   * @param server_endpoint {string}
   * @param webchess_board {WebchessBoard}
   * @returns GameState
   */
  static create(state_class, server_endpoint, webchess_board) {
    return new state_class(server_endpoint, webchess_board);
  }

  /**
   *
   * @param state_class {GameState.}
   */
  switch_state(state_class) {

  }

  on_ws_connect(){}
  on_ws_disconnect(){}
  /**
   * @param status {Status}
   */
  on_server_game_status(status) {}

  /**
   * @param move {string}
   * @param draw_requested {boolean}
   */
  on_server_move(move, draw_requested){}

  /**
   * @param opponent {string} Username of the opponent
   */
  on_server_game_start(opponent){}

  /**
   *
   * @param winner {string} 'black' or 'white' or 'draw'
   * @param timed_out {boolean} true iff game ended because a player took too much time without moving
   */
  on_server_game_end(winner, timed_out){}
  on_server_pending_timeout(){}

  /**
   * @param move {string}
   */
  on_player_move(move){}

  /**
   *
   * @param move {string}
   * @param request_draw {boolean}
   */
  send_move(move, request_draw) {}
}

class MyTurn extends GameState {
  on_player_move(move) {

  }
}
