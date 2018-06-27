function WebchessBoard(board_id, ui_options, game_options) {
  this.__game_options = game_options;
  this.__ui_options = ui_options;
  this.__board_id = board_id;
  this.__board_el = $('#' + board_id);
  this.__engine = new Chess();

  // don't let the user press buttons while other button clicks are still processing
  this.__is_3D = ui_options.start_3D === false ? false : ChessBoard3.webGLEnabled();

  /**
   * Chessboard(3?).js board for visuals and interaction
   */
  this.__board = this.__create_board();

  this.__adjust_size_debounce_anchor = null;

  this.__on_window_resize = function() {
    this.__adjust_board_size(
      this.__ui_options.intended_width.bind(this.__ui_options),
      this.__ui_options.intended_height.bind(this.__ui_options),
      this.__ui_options.on_resize.bind(this.__ui_options)
    );
  }.bind(this);

  this.is_transitioning = false;
  this.__waiting_moves_queue = [];

  $(window).resize(this.__on_window_resize);
  this.__on_window_resize();

}

WebchessBoard.prototype.__on_drop = function (source, target) {
  if (this.__board.hasOwnProperty('removeGreySquares')
    && typeof this.__board.removeGreySquares === 'function') {
    this.__board.removeGreySquares();
  }

  var promotion = this.__game_options.get_promotion();

  // see if the move is legal
  var move = this.__engine.move({
    from: source,
    to: target,
    promotion: promotion.toLowerCase()
  });

  if (move === null) return 'snapback';

  this.__game_options.on_manual_move(move.from + move.to + (move.promotion || "").toUpperCase());
  // Don't know why, but without timeout the piece was not changed visually in 2D (probably
  // because inside a callback from the library)
  setTimeout(function() {
    this.__board.position(this.__engine.fen(), true);
  }.bind(this), 300);
};

WebchessBoard.prototype.__on_snap_end = function () {
  /* if (!this.__engine.game_over() && this.__engine.turn() !== player) {
      fireEngine();
  } */
};

WebchessBoard.prototype.__on_mouse_over_square = function (square) {
  // get list of possible moves for this square
  var moves = this.__engine.moves({
    square: square,
    verbose: true
  });

  // exit if there are no moves available for this square
  if (moves.length === 0) return;

  if (this.__board.hasOwnProperty('greySquare') && typeof this.__board.greySquare === 'function') {
    // highlight the square they moused over
    this.__board.greySquare(square);

    // highlight the possible squares for this piece
    for (var i = 0; i < moves.length; i++) {
      this.__board.greySquare(moves[i].to);
    }
  }
};

WebchessBoard.prototype.__on_mouse_out_square = function (square, piece) {
  if (this.__board.hasOwnProperty('removeGreySquares')
    && typeof this.__board.removeGreySquares === 'function') {
    this.__board.removeGreySquares();
  }
};

WebchessBoard.prototype.__create_board = function () {
  var cfg = {
    cameraControls: true,
    draggable: true,
    position: 'start',
    onDrop: this.__on_drop.bind(this),
    onMouseoutSquare: this.__on_mouse_out_square.bind(this),
    onMouseoverSquare: this.__on_mouse_over_square.bind(this),
    onSnapEnd: this.__on_snap_end.bind(this),
    pieceTheme: this.__ui_options.piece_2D_set,
    fontData: this.__ui_options.font_file,
    // new settings
    sparePieces: this.__ui_options.spare_pieces,
    onDragStart: this.__ui_options.on_drag_start
  };
  if (this.__is_3D) {
    cfg.pieceSet = this.__ui_options.piece_3D_set;
    return new ChessBoard3(this.__board_id, cfg);
  } else {
    return new ChessBoard(this.__board_id, cfg);
  }
};

WebchessBoard.prototype.__adjust_board_size = function (desired_width, desired_height, callback) {
  if (this.__adjust_size_debounce_anchor) {
    clearTimeout(this.__adjust_size_debounce_anchor);
  }
  this.__adjust_size_debounce_anchor = setTimeout(function () {
    if (typeof desired_width === 'function') {
      desired_width = desired_width();
    }
    if (typeof desired_height === 'function') {
      desired_height = desired_height();
    }
    var fudge = 5;
    var windowWidth = $(window).width();
    var windowHeight = $(window).height();
    var desiredBoardWidth = desired_width;
    var desiredBoardHeight = desired_height;
    var board_el = this.__board_el;
    if (this.__is_3D) {
      // Using chessboard3.js.
      // Adjust for 4:3 aspect ratio
      desiredBoardWidth &= 0xFFFC; // mod 4 = 0
      desiredBoardHeight -= (desiredBoardHeight % 3); // m-od 3 = 0
      if (desiredBoardWidth * 0.75 > desiredBoardHeight) {
        desiredBoardWidth = desiredBoardHeight * 4 / 3;
      }
      board_el.css('width', desiredBoardWidth);
      board_el.css('height', (desiredBoardWidth * 0.75));
    } else {
      // This is a chessboard.js board. Adjust for 1:1 aspect ratio
      desiredBoardWidth = Math.min(desiredBoardWidth, desiredBoardHeight);
      board_el.css('width', desiredBoardWidth);
      board_el.css('height', desiredBoardHeight);
    }
    if (this.__board !== undefined) {
      this.__board.resize();
    }
    callback();
  }.bind(this), 100);
};

WebchessBoard.prototype.destroy = function() {
  this.__board.destroy();
  $(window).off('resize', this.__on_window_resize);
};

WebchessBoard.prototype.switch_dimensions = function () {

  if(this.is_transitioning) {
    function switch_dimensions_when_not_transitioning() {
      if (this.is_transitioning) {
        setTimeout(switch_dimensions_when_not_transitioning.bind(this), 1100);
      } else {
        this.switch_dimensions();
      }
    }

    switch_dimensions_when_not_transitioning.apply(this);
    return;
  }

  this.is_transitioning = true;
  var position = this.__board.position();
  var orientation = this.__board.orientation();
  this.__board.destroy();
  this.__is_3D = !this.__is_3D;
  this.__adjust_board_size(
    this.__ui_options.intended_width.bind(this.__ui_options),
    this.__ui_options.intended_height.bind(this.__ui_options),
    function () {
      this.__board = this.__create_board();
      this.__board.orientation(orientation);
      setTimeout(function() {
        this.__board.position(position);
      }.bind(this), 1000);
      setTimeout(function() {
        this.is_transitioning = false;
      }.bind(this), 2000);
    }.bind(this)
  );
};

/**
 * @returns {string} 'w' or 'b'
 */
WebchessBoard.prototype.turn = function () {
  return this.__engine.turn();
};

/**
 * Programmatically moves
 * @param move {string} Four or five characters ("a2a3", "a7a8Q", etc.)
 */
WebchessBoard.prototype.move = function (move, use_animations) {

  if (this.is_transitioning) {
    var move_when_not_transitioning = function () {
      if (this.is_transitioning) {
        setTimeout(move_when_not_transitioning, 200);
      } else {
        this.move(this.__waiting_moves_queue.splice(0, 1)[0]);
      }
    }.bind(this);

    this.__waiting_moves_queue.push(move);
    move_when_not_transitioning.apply(this);
    return;
  }

  this.is_transitioning = true;
  var move_obj = this.__engine.move({
    from: move.substr(0, 2),
    to: move.substr(2, 2),
    promotion: move.length === 5 ? move[4].toLowerCase() : null
  });

  if (move_obj === null) {
    return;
  }

  this.__board.position(this.__engine.fen(), use_animations);
  setTimeout(function() {
    this.is_transitioning = false;
  }.bind(this), 500);
};

WebchessBoard.prototype.in_checkmate = function () {
  return this.__engine.in_checkmate();
};

WebchessBoard.prototype.in_check = function () {
  return this.__engine.in_check();
};

WebchessBoard.prototype.in_stalemate = function () {
  return this.__engine.in_stalemate();
};

/**
 * Merely informational. The game can still be played
 */
WebchessBoard.prototype.insufficient_material = function () {
  return this.__engine.insufficient_material();
};

/**
 * Merely informational. The game can still be played
 */
WebchessBoard.prototype.in_threefold_repetition = function () {
  return this.__engine.in_threefold_repetition();
};

/**
 * true if 50 moves have been made without moving a pawn and without
 * capturing any piece. It is merely informational: the game can still be played
 */
WebchessBoard.prototype.fifty_move_rule = function () {
  return this.__engine.in_draw() && (!this.__engine.in_stalemate())
    && (!this.__engine.insufficient_material()) && (!this.__engine.in_threefold_repetition());
};
