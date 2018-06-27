from collections import deque
from collections import namedtuple
from enum import Enum


class Side(Enum):
    """
    Representa um jogador (branco ou preto)
    """
    WHITE = 0
    BLACK = 1

    def opponent(self):
        if self is Side.WHITE:
            return Side.BLACK
        else:
            return Side.WHITE


def generate_name2index():
    """
    Função de ajuda à classe `Square`.
    :return: Um dicionário cujas chaves são nomes de posições no tabuleiro
    (como 'a1') e cujos valores são o índice da tal posição (de 0 a 224)
    """
    out = {}
    for i in range(225):
        out[('x', 'y', 'z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l')
            [i % 15] + str(8 - (i - 45) // 15)] = i
    return out


def generate_index2name():
    """
    Função de ajuda à classe `Square`.
    :return: Uma lista cujos índices representam índices de posições no tabuleiro (de 0 a 224)
    e cujos valores são o nome da posição associada ao índice
    """
    out = {}
    for name, index in generate_name2index().items():
        out[index] = name
    return out


def generate_non_sentinel():
    """
    Função de ajuda à classe `Square`
    :return: Os índices das posições no tabuleiro que sejam válidas. Isso porque nossa representação
    de tabuleiro tem 225 posições, das quais só 64 correspondem ao tabuleiro real (as outras são usadas
    para facilitar codificação)
    """
    out = {}
    indexes = [x for x in range(45, 165) if 2 < x % 15 < 11]
    for i in range(255):
        out[i] = i in indexes
    return out


class Square(object):
    """
    Representa uma posição (casa) no tabuleiro, como 'a1', 'g4', etc.

    Uma instância de `Square` pode ser operada com adição e subtração (por exemplo: Uma instância
    representando 'a1', se somada com 1, retorna o índice da casa 'b1')

    Propriedades (read-only):
        - index: Índice da casa
        - name: Nome da casa ('a1', 'g4', etc.)
        - valid: Se a casa é uma do tabuleiro de jogo real (8 por 8) ou se é uma casa "generalizada"
        usada somente para facilitar codificação

        - rank: Ranque da casa (de 1 a 8)

    """
    __index2valid = generate_non_sentinel()
    __instance_cache = {}
    __name2index = generate_name2index()
    __index2name = generate_index2name()

    def __new__(cls, descriptor, *args, **kwargs):
        """
        Intercepta construção de uma instância de `Square`.

        `descriptor` pode ser um int (representando índice da casa), uma string (nome da casa)
         ou outra instância de `Square` (caso em que o construtor retornará a instância recebida)

         Use o construtor para montar uma instância de `Square` depois de operar aritmeticamente
         alguma casa. Por exemplo, para ter a casa 'd1':

         ```
         sqb1 = Square('b1')
         sqd1 = Square(sqb1 + 2)
         ```
        """
        if cls.__instance_cache.get(descriptor) is not None:
            return cls.__instance_cache[descriptor]
        obj = object.__new__(cls)
        if isinstance(descriptor, int):
            index = descriptor
            valid = cls.__index2valid[index]
            name = cls.__index2name[index]
            rank = int(name[1:])
        else:
            name = descriptor
            index = cls.__name2index[name]
            valid = cls.__index2valid[index]
            rank = int(name[1])
        obj.name = name
        obj.index = index
        obj.rank = rank
        obj.valid = valid
        cls.__instance_cache[name] = obj
        cls.__instance_cache[index] = obj
        cls.__instance_cache[obj] = obj
        return obj

    def __radd__(self, other):
        """
        Opera a casa
        :param other: Outra casa do tabuleiro (representado por int, string ou Square)
        :return: Índice da casa resultante da operação
        """
        return self.index + other

    def __add__(self, other):
        """
        Opera a casa
        :param other: Outra casa do tabuleiro (representado por int, string ou Square)
        :return: Índice da casa resultante da operação
        """
        return self.index + other

    def __sub__(self, other):
        """
        Opera a casa
        :param other: Outra casa do tabuleiro (representado por int, string ou Square)
        :return: Índice da casa resultante da operação
        """
        if isinstance(other, int):
            return self.index - other
        if isinstance(other, Square):
            return self.index - other.index
        return self.index - other

    def __rsub__(self, other):
        """
        Opera a casa
        :param other: Outra casa do tabuleiro (representado por int, string ou Square)
        :return: Índice da casa resultante da operação
        """
        return other - self.index

    def __eq__(self, other):
        """
        Compara-se a outra casa do tabuleiro.

        Exemplos:

        ```
        Square('a1') == Square('a1') # true
        Square('a1') + 1 == Square('b1') # true
        ```
        :param other: Outra casa do tabuleiro
        :return: Se as casas são a mesma no tabuleiro
        """
        return self.index == Square(other).index

    def __hash__(self):
        return self.index

    def __lt__(self, other):
        """
        Diz se a casa do tabuleiro representada pela instância atual vem antes (acima/à esquerda) de
        `other` no tabuleiro
        :param other: Uma casa do tabuleiro
        """
        return self.index < other

    def __gt__(self, other):
        return self.index > other

    def __repr__(self):
        return '<Square(' + self.name + ')>'


class BoardLike:
    """
    Uma representação de um tabuleiro "generalizado", com 225 casas (15 por 15).

    As casas válidas são entre as linhas 4 a 12, colunas 4 a 12. Ou seja, existem 3 linhas
    de casas inválidas acima do tabuleiro e 4 linhas abaixo; 3 colunas de casas inválidas à esquerda
    do tabuleiro e 4 à direita.

    Uma instância de `BoardLike` é imutável
    """

    def __init__(self, datalist):
        """

        :param datalist: Uma lista de 15*15 = 225 elementos. Esses elementos podem ser qualquer coisa.
        """
        if len(datalist) != 15 * 15:
            raise ValueError('datalist should be 15*15 in length')
        self._board = datalist

    def __len__(self):
        """
        Quantas casas no tabuleiro
        :return: 225
        """
        return len(self._board)

    def __getitem__(self, item):
        """
        Acessa casa
        :param item: Uma instância de `Square`, ou um int (índice da casa), ou uma string (nome da casa)
        :return: Elemento guardado em `BoardLike[item]`
        """
        if isinstance(item, int):
            return self._board[item]
        if isinstance(item, Square):
            return self._board[item.index]
        return self._board[Square(item).index]

    def __iter__(self):
        return self._board.__iter__()

    def replace(self, square, newcontent):
        """
        Altera elemento guardado na casa `square`
        :param square: Casa cujo conteúdo será alterado
        :param newcontent: Conteúdo novo a ser associado à casa `square`
        :return: Nova instância de `BoardLike` com a substituição feita
        """
        copylist = list(self._board)
        copylist[Square(square).index] = newcontent
        return self.__class__(copylist)


class Board(BoardLike):
    """
    Representa o tabuleiro de jogo. Mais especificamente, enquanto `BoardLike` poderia armazenar
    qualquer informação associada às casas do tabuleiro, `Board` armazena, invariavelmente, as peças
    que estão em cada casa
    """

    def __init__(self, datalist):
        super().__init__(datalist)
        # { [side: Side]: {[key: Square]: bool?} }
        self.__playersquares = {
            Side.WHITE: {},
            Side.BLACK: {}
        }
        # Quadrados dos reis
        self.__kings = {Side.WHITE: None, Side.BLACK: None}
        for sq, piece in enumerate(self._board):
            if Square(sq).valid and piece.side is not None:
                self.__playersquares[piece.side][Square(sq)] = True
                if piece.kind is King:
                    self.__kings[piece.side] = Square(sq)

    def occuppied(self, side):
        """
        Diz as casas ocupadas pelas peças de um jogador
        :param side: Do tipo `Side`
        :return: `Square`s ocupadas pelo lado `side`
        """
        # Explicitly convert to list. Using an iterator led to bug:
        # I suspect doing and undoing moves in self.moves changed the order of the
        # keys in the iterator midway
        return list(self.__playersquares[side].keys())

    def attacked(self, square, side):
        """
        Diz se alguma peça do jogador `side` pode atacar a casa `square`
        :param square: Do tipo `Square`, ou um int (índice da casa), ou uma string (nome da casa)
        :param side: Do tipo `Side`
        :return: Se existe uma peça do jogador que tenha linha de ataque para a casa `side`.
        Analisa somente pseudo-legalidade, isto é, inclui movimentos que, se fossem executados,
        deixariam o rei do jogador `side` em xeque
        """
        for fromsq in self.__playersquares[side]:
            if self[fromsq].attacks(fromsq, square, self):
                return True
        return False

    def _movepiece(self, fromsq, tosq):
        """
        Função protegida, fornecida somente em casos específicos para instâncias de `MoveExecutor`.

        Move uma peça de `fromsq` para `tosq` e retorna a peça que estava em `tosq` antes da movimentação
        :param fromsq: `Square` onde está a peça a ser movida
        :param tosq: `Square` de destino da peça. `tosq` pode estar ocupado
        :return: `Piece` que estava posicionada em `tosq` antes da movimentação
        """
        fromsq = Square(fromsq)
        tosq = Square(tosq)
        piece = self._board[fromsq.index]
        oldpiece = self._board[tosq.index]
        if oldpiece.kind is not NoPiece:
            self._removepiece(tosq)
        # tabuleiro
        self._board[fromsq.index] = NoPiece()
        self._board[tosq.index] = piece
        # lista de quadrados do jogador
        del self.__playersquares[piece.side][fromsq]
        self.__playersquares[piece.side][tosq] = True
        # lista de reis
        if piece.kind is King:
            self.__kings[piece.side] = tosq
        return oldpiece

    def _addpiece(self, piece, square):
        """
        Função protegida, fornecida somente em casos específicos para instâncias de `MoveExecutor`.

        :param piece: Instância de `Piece` a ser adicionada ao tabuleiro
        :param square: Instância de `Square` (ou um int, ou uma string) onde adicionar a peça `piece`
        """
        square = Square(square)
        # tabuleiro
        self._board[square.index] = piece
        # lista de quadrados do jogador
        # print(piece, piece.side, square)
        self.__playersquares[piece.side][square] = True
        # lista de reis
        if piece.kind is King:
            self.__kings[piece.side] = square

    def _removepiece(self, square):
        """
        Função protegida, fornecida somente em casos específicos para instâncias de `MoveExecutor`.
        :param square: Instância de `Square` (ou int, ou string) de onde retirar uma peça
        :return: Instância de `Piece` que estava em `square` antes de ser retirada
        """
        square = Square(square)
        piece = self._board[square.index]
        side = piece.side
        # tabuleiro
        self._board[square.index] = NoPiece()
        # lista de quadrados do jogador
        del self.__playersquares[side][square]
        # lista de reis
        if piece.kind is King:
            self.__kings[piece.side] = None
        return piece

    def king(self, side):
        """
        Informa a casa do rei do jogador
        :param side: Do tipo `Side`
        :return: Instância de `Square` ocupada pelo rei do jogador `side`
        """
        return self.__kings[side]


"""
Struct usada para armazenar informação contingente sobre o estado do tabuleiro.

Membros:
    - kings: Dicionário. Chave: Instância de `Side`. Valor: Instância de `Square` ocupada pelo rei
    - can_castle: Dicionário. Chave: Instância de `Side`. Valor: Tupla de 2 elementos booleanos.
        O primeiro indica se jogador pode fazer roque pelo lado da rainha; o segundo, pelo lado do rei
    - ep: Instância de `Square`, ou valor `None`. É uma casa do tabuleiro onde um peão pararia caso
        fizesse uma captura "en passant". Este membro só existe no turno exato em que pode ser feita
        uma jogada "en passant"
"""
Context = namedtuple('Context', 'kings can_castle ep')

"""
Struct usada para representar movimentos possíveis de uma peça

Membros:
    - fromsq: Instância de `Square`. A origem do movimento
    - tosq: Instância de `Square`. O destino do movimento
    - kind: Instância de `MoveKind`. 
    - promotion: Instância de `Piece`, ou o valor `None`. Existe somente quando o movimento é do tipo
        promoção de peão. Neste caso, `promotion` armazena` a peça à qual o peão será promovido ao
        realizar o movimento
"""
Move = namedtuple('Move', 'fromsq tosq kind promotion')

"""
Struct usada para representar a "versão invertida" de movimentos. Serve para poder desfazer qualquer
movimento que tenha acabado de ser executado. Os membros são usados internamente.
"""
AntiMove = namedtuple('AntiMove', 'fromsq tosq addpiece addpos kind')


class MoveExecutor:
    """
    Representa um objeto que sabe realizar uma instância de `Move`.
    """

    def exec(self, move, movepiece, addpiece, removepiece):
        """

        :param move: Instância de `Move`
        :param movepiece: Função fornecida por `Board` (ver Board._movepiece)
        :param addpiece: Função fornecida por `Board` (ver Board._addpiece)
        :param removepiece: Função fornecida por `Board` (ver Board._removepiece)
        :return: Instância de `AntiMove` que, se for executada, desfaz o movimento que acabara
        de ser feito por este método
        """
        pass


class MoveQuietExecutor(MoveExecutor):
    """
    Executor de movimentos em que não há captura, nem promoção
    """

    def exec(self, move, movepiece, addpiece, removepiece):
        movepiece(move.fromsq, move.tosq)
        return AntiMove(move.tosq, move.fromsq, None, None, MoveKind.ANTI_QUIET)


class MoveAntiQuietExecutor(MoveExecutor):
    """
    Desfaz movimentos em que não há captura, nem promoção
    """

    def exec(self, move, movepiece, addpiece, removepiece):
        movepiece(move.fromsq, move.tosq)


class MoveEpCaptureExecutor(MoveExecutor):
    """
    Executor de captura en passant
    """
    # Distância ao quadrado onde está a peça que fez en passant e que vai ser capturada
    __captureoffset = {
        -16: -1,
        -14: +1,
        +14: -1,
        +16: +1
    }

    def exec(self, move, movepiece, addpiece, removepiece):
        middlesq = move.fromsq + self.__captureoffset[move.tosq - move.fromsq]
        captured = movepiece(move.fromsq, middlesq)
        movepiece(middlesq, move.tosq)
        return AntiMove(move.tosq, move.fromsq, captured, middlesq, MoveKind.ANTI_EP_CAPTURE)


class MoveAntiEpCaptureExecutor(MoveExecutor):
    """
    Desfaz movimentos de captura "en passant"
    """

    def exec(self, move, movepiece, addpiece, removepiece):
        movepiece(move.fromsq, move.tosq)
        addpiece(move.addpiece, move.addpos)


class MovePawn2Executor(MoveExecutor):
    """
    Executor de movimentos em que um peão avança duas casas de uma vez
    """

    def exec(self, move, movepiece, addpiece, removepiece):
        movepiece(move.fromsq, move.tosq)
        return AntiMove(move.tosq, move.fromsq, None, None, MoveKind.ANTI_PAWN2)


class MoveAntiPawn2Executor(MoveExecutor):
    """
    Desfaz movimentos em que um peão avança duas casas de uma vez
    """

    def exec(self, move, movepiece, addpiece, removepiece):
        movepiece(move.fromsq, move.tosq)


class MoveCaptureExecutor(MoveExecutor):
    """
    Executor de movimentos em que há captura (mas não há promoção)
    """

    def exec(self, move, movepiece, addpiece, removepiece):
        captured = movepiece(move.fromsq, move.tosq)
        return AntiMove(move.tosq, move.fromsq, captured, move.tosq, MoveKind.ANTI_CAPTURE)


class MoveAntiCaptureExecutor(MoveExecutor):
    """
    Desfaz movimentos em que há captura, mas não há promoção
    """

    def exec(self, move, movepiece, addpiece, removepiece):
        movepiece(move.fromsq, move.tosq)
        addpiece(move.addpiece, move.addpos)


class MovePromotionExecutor(MoveExecutor):
    """
    Executor de movimentos de peão em que a peça é promovida, mas não há captura
    """

    def exec(self, move, movepiece, addpiece, removepiece):
        pawn = removepiece(move.fromsq)
        addpiece(move.promotion, move.tosq)
        return AntiMove(move.tosq, move.fromsq, pawn, move.fromsq, MoveKind.ANTI_PROMOTION)


class MoveAntiPromotionExecutor(MoveExecutor):
    """
    Desfaz movimentos de peão em que a peça é promovida, mas não há captura
    """

    def exec(self, move, movepiece, addpiece, removepiece):
        removepiece(move.fromsq)
        addpiece(move.addpiece, move.addpos)


class MovePromotionCaptureExecutor(MoveExecutor):
    """
    Executor de movimentos de peão em que há tanto promoção quanto captura
    """

    def exec(self, move, movepiece, addpiece, removepiece):
        captured = movepiece(move.fromsq, move.tosq)
        addpiece(move.promotion, move.tosq)
        return AntiMove(
            move.tosq, move.fromsq, captured, move.tosq, MoveKind.ANTI_PROMOTION_CAPTURE)


class MoveAntiPromotionCaptureExecutor(MoveExecutor):
    """
    Desfaz movimentos de peão em que há tanto promoção quanto captura
    """

    def exec(self, move, movepiece, addpiece, removepiece):
        side = removepiece(move.fromsq).side
        addpiece(move.addpiece, move.addpos)
        addpiece(Pawn(side), move.tosq)


class MoveCastleKingExecutor(MoveExecutor):
    """
    Executor de Roque pelo lado do rei
    """

    def exec(self, move, movepiece, addpiece, removepiece):
        movepiece(move.fromsq, move.tosq)
        movepiece(move.tosq + 1, move.fromsq + 1)
        return AntiMove(move.tosq, move.fromsq, None, None, MoveKind.ANTI_CASTLE_KING)


class MoveAntiCastleKingExecutor(MoveExecutor):
    """
    Desfaz Roque pelo lado do rei
    """

    def exec(self, move, movepiece, addpiece, removepiece):
        movepiece(move.fromsq, move.tosq)
        movepiece(move.tosq + 1, move.fromsq + 1)


class MoveCastleQueenExecutor(MoveExecutor):
    """
    Executor de Roque pelo lado da rainha
    """

    def exec(self, move, movepiece, addpiece, removepiece):
        movepiece(move.fromsq, move.tosq)
        movepiece(move.tosq - 2, move.tosq + 1)
        return AntiMove(move.tosq, move.fromsq, None, None, MoveKind.ANTI_CASTLE_QUEEN)


class MoveAntiCastleQueenExecutor(MoveExecutor):
    """
    Desfaz Roque pelo lado da rainha
    """

    def exec(self, move, movepiece, addpiece, removepiece):
        movepiece(move.fromsq, move.tosq)
        movepiece(move.tosq - 1, move.fromsq - 2)


class MoveKind(Enum):
    """
    Coleciona todos os possíveis tipos de movimento (e "anti-movimentos") do jogo
    """
    QUIET = MoveQuietExecutor()
    CAPTURE = MoveCaptureExecutor()
    PAWN2 = MovePawn2Executor()
    EP_CAPTURE = MoveEpCaptureExecutor()
    PROMOTION = MovePromotionExecutor()
    PROMOTION_CAPTURE = MovePromotionCaptureExecutor()
    CASTLE_KING = MoveCastleKingExecutor()
    CASTLE_QUEEN = MoveCastleQueenExecutor()
    ANTI_QUIET = MoveAntiQuietExecutor()
    ANTI_CAPTURE = MoveAntiCaptureExecutor()
    ANTI_PAWN2 = MoveAntiPawn2Executor()
    ANTI_EP_CAPTURE = MoveAntiEpCaptureExecutor()
    ANTI_PROMOTION = MoveAntiPromotionExecutor()
    ANTI_PROMOTION_CAPTURE = MoveAntiPromotionCaptureExecutor()
    ANTI_CASTLE_KING = MoveAntiCastleKingExecutor()
    ANTI_CASTLE_QUEEN = MoveAntiCastleQueenExecutor()

    def exec(self, move, movepiece, addpiece, removepiece):
        """Delega ao `exec` de `MoveExecutor`"""
        return self.value.exec(move, movepiece, addpiece, removepiece)


class Piece(object):
    """
    Representa uma peça do jogo. `Piece` não armazena estado, ou seja, não sabe onde está no tabuleiro.

    Atende à DP "flyweight": Existe somente uma instância para cada tipo de peça e lado do jogo. Isso
    significa, por exemplo, que todos os 8 peões brancos são somente 1 instância de `Rook` (subclasse)
    """
    __instance_cache = {}

    def __new__(cls, side, *args, **kwargs):
        if cls.__instance_cache.get((cls, side)) is None:
            cls.__instance_cache[(cls, side)] = object.__new__(cls)
        return cls.__instance_cache[(cls, side)]

    def __init__(self, side):
        self.side = side
        self.kind = self.__class__

    def attacks(self, fromsq, tosq, board):
        """
        Diz se a peça, estando em `fromsq` no tabuleiro `board`, pode ou não atacar a casa `tosq`
        :param fromsq: Casa onde a peça está
        :param tosq: Casa onde se deseja saber se a peça pode atacar
        :param board: Instância de `Board`, o tabuleiro do jogo
        :return: booleana indicando a possibilidade de ataque
        """
        pass

    def plmoves(self, fromsq, board, context):
        """
        Lista os movimentos pseudolegais da peça, supondo que ela esteja em `fromsq` no tabuleiro `board`.

        Um movimento é "pseudolegal" se ele obedece a todas as regras do xadrez, exceto aquela segundo
        a qual um movimento não pode ser realizado caso sua execução deixe o rei do jogador em xeque
        :param fromsq: `Square` onde a peça está
        :param board: `Board`, o tabuleiro do jogo
        :param context: Uma struct (namedtuple `Context`) representando informações contingentes sobre
        o tabuleiro
        :return: Lista de movimentos pseudolegais da peça
        """
        pass


class NoPiece(Piece):
    """
    Representa a ausência de peça. Por exemplo: Dada uma instância de `BoardLike`, acessar
    `BoardLike[Square('b1')]` retornará instância de `NoPiece` caso a casa 'b1' não esteja ocupada
    """

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, None)

    def __init__(self):
        super().__init__(None)

    def attacks(self, fromsq, tosq, board):
        raise TypeError('There is no piece here. It cannot attack')

    def plmoves(self, fromsq, board, context):
        raise TypeError('There is no piece here. It cannot move')


class OutOfBoundsPiece(Piece):
    """
    É o objeto armazenado por uma instância de `Board` nas casas "generalizadas" do tabuleiro,
    isto é, aquelas que foram criadas somente para facilitar codificação, mas não são nenhuma das 64
    casas existentes num tabuleiro real
    """

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, None)

    def __init__(self):
        super().__init__(None)

    def attacks(self, fromsq, tosq, board):
        raise TypeError('This piece represents out-of-the-board. It cannot attack')

    def plmoves(self, fromsq, board, context):
        raise TypeError('This piece represents out-of-the-board. It cannot move')


class SlidingPiece(Piece):
    """
    Representa bispo, torre e rainha, as 3 peças cujos ataques são "deslizantes", ou seja,
    podem andar mais de uma casa

    Subclasses devem preencher os membros rays e directions
    """
    rays = None
    directions = None

    def attacks(self, fromsq, tosq, board):
        increment = self.rays[15 * 15 // 2 + fromsq - tosq]
        if increment is None:
            return False
        currsq = tosq + increment
        while board[currsq].kind is NoPiece:
            currsq += increment
        if currsq == fromsq:
            return True
        return False

    def plmoves(self, fromsq, board, context):
        moves = []
        for direction in self.directions:
            currindex = fromsq
            while True:
                currindex += direction
                if board[currindex].kind is OutOfBoundsPiece:
                    break
                elif board[currindex].kind is NoPiece:
                    moves.append(Move(fromsq, currindex, MoveKind.QUIET, None))
                    continue
                elif board[currindex].side is not self.side:
                    moves.append(Move(fromsq, currindex, MoveKind.CAPTURE, None))
                break
        return moves


class Rook(SlidingPiece):
    rays = BoardLike((
        None, None, None, None, None, None, None, -15, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, -15, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, -15, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, -15, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, -15, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, -15, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, -15, None, None, None, None, None, None, None,
        -1, -1, -1, -1, -1, -1, -1, None, 1, 1, 1, 1, 1, 1, 1,
        None, None, None, None, None, None, None, 15, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, 15, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, 15, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, 15, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, 15, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, 15, None, None, None, None, None, None, None,
        None, None, None, None, None, None, None, 15, None, None, None, None, None, None, None
    ))

    directions = (-1, -15, 1, 15)


class Bishop(SlidingPiece):
    rays = BoardLike((
        -16, None, None, None, None, None, None, None, None, None, None, None, None, None, -14,
        None, -16, None, None, None, None, None, None, None, None, None, None, None, -14, None,
        None, None, -16, None, None, None, None, None, None, None, None, None, -14, None, None,
        None, None, None, -16, None, None, None, None, None, None, None, -14, None, None, None,
        None, None, None, None, -16, None, None, None, None, None, -14, None, None, None, None,
        None, None, None, None, None, -16, None, None, None, -14, None, None, None, None, None,
        None, None, None, None, None, None, -16, None, -14, None, None, None, None, None, None,
        None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
        None, None, None, None, None, None, 14, None, 16, None, None, None, None, None, None,
        None, None, None, None, None, 14, None, None, None, 16, None, None, None, None, None,
        None, None, None, None, 14, None, None, None, None, None, 16, None, None, None, None,
        None, None, None, 14, None, None, None, None, None, None, None, 16, None, None, None,
        None, None, 14, None, None, None, None, None, None, None, None, None, 16, None, None,
        None, 14, None, None, None, None, None, None, None, None, None, None, None, 16, None,
        14, None, None, None, None, None, None, None, None, None, None, None, None, None, 16,
    ))

    directions = (-16, -14, 16, 14)


class Queen(SlidingPiece):
    rays = BoardLike((
        -16, None, None, None, None, None, None, -15, None, None, None, None, None, None, -14,
        None, -16, None, None, None, None, None, -15, None, None, None, None, None, -14, None,
        None, None, -16, None, None, None, None, -15, None, None, None, None, -14, None, None,
        None, None, None, -16, None, None, None, -15, None, None, None, -14, None, None, None,
        None, None, None, None, -16, None, None, -15, None, None, -14, None, None, None, None,
        None, None, None, None, None, -16, None, -15, None, -14, None, None, None, None, None,
        None, None, None, None, None, None, -16, -15, -14, None, None, None, None, None, None,
        -1, -1, -1, -1, -1, -1, -1, None, 1, 1, 1, 1, 1, 1, 1,
        None, None, None, None, None, None, 14, 15, 16, None, None, None, None, None, None,
        None, None, None, None, None, 14, None, 15, None, 16, None, None, None, None, None,
        None, None, None, None, 14, None, None, 15, None, None, 16, None, None, None, None,
        None, None, None, 14, None, None, None, 15, None, None, None, 16, None, None, None,
        None, None, 14, None, None, None, None, 15, None, None, None, None, 16, None, None,
        None, 14, None, None, None, None, None, 15, None, None, None, None, None, 16, None,
        14, None, None, None, None, None, None, 15, None, None, None, None, None, None, 16,
    ))

    directions = (-1, -16, -15, -14, 1, 16, 15, 14)


class Knight(Piece):
    offsets = (-17, -31, -29, -13, 17, 31, 29, 13)

    def attacks(self, fromsq, tosq, board):
        return tosq - fromsq in self.offsets

    def plmoves(self, fromsq, board, context):
        moves = []
        for offset in self.offsets:
            sq = fromsq + offset
            if board[sq].kind is NoPiece:
                moves.append(Move(fromsq, sq, MoveKind.QUIET, None))
            elif board[sq].kind is not OutOfBoundsPiece and board[sq].side is not self.side:
                moves.append(Move(fromsq, sq, MoveKind.CAPTURE, None))
        return moves


class Pawn(Piece):
    attackoffsets = {
        Side.WHITE: (-16, -14),
        Side.BLACK: (14, 16)
    }

    walkoffset = {
        Side.WHITE: -15,
        Side.BLACK: 15
    }

    initialrank = {
        Side.WHITE: 2,
        Side.BLACK: 7
    }

    def attacks(self, fromsq, tosq, board):
        return tosq - fromsq in self.attackoffsets[self.side]

    def plmoves(self, fromsq, board, context):
        moves = []
        canpromote = False
        # Double move
        if Square(fromsq).rank == self.initialrank[self.side] \
                and board[fromsq + self.walkoffset[self.side]].kind is NoPiece \
                and board[fromsq + 2 * self.walkoffset[self.side]].kind is NoPiece:
            moves.append(
                Move(fromsq, fromsq + 2 * self.walkoffset[self.side], MoveKind.PAWN2, None))
        # Promotion without capture
        if Square(fromsq).rank == self.initialrank[self.side.opponent()] \
                and board[fromsq + self.walkoffset[self.side]].kind is NoPiece:
            for piece in (Queen(self.side), Rook(self.side), Bishop(self.side), Knight(self.side)):
                moves.append(
                    Move(fromsq, fromsq + self.walkoffset[self.side], MoveKind.PROMOTION, piece))
            canpromote = True
        # En passant capture
        if context.ep is not None and context.ep - fromsq in self.attackoffsets[self.side]:
            moves.append(Move(fromsq, context.ep, MoveKind.EP_CAPTURE, None))
        # Normal move
        if not canpromote and board[fromsq + self.walkoffset[self.side]].kind is NoPiece:
            moves.append(Move(fromsq, fromsq + self.walkoffset[self.side], MoveKind.QUIET, None))
        # Capture and maybe promotion
        for attackoffset in self.attackoffsets[self.side]:
            if board[fromsq + attackoffset].kind is not NoPiece \
                    and board[fromsq + attackoffset].kind is not OutOfBoundsPiece \
                    and board[fromsq + attackoffset].side is not self.side:
                if Square(fromsq).rank == self.initialrank[self.side.opponent()]:
                    for promotion in (Queen(self.side),
                                      Rook(self.side), Bishop(self.side), Knight(self.side)):
                        moves.append(Move(
                            fromsq,
                            fromsq + attackoffset,
                            MoveKind.PROMOTION_CAPTURE,
                            promotion))
                else:
                    moves.append(Move(fromsq, fromsq + attackoffset, MoveKind.CAPTURE, None))
                pass

        return moves


class King(Piece):
    offsets = (-1, -16, -15, -14, 1, 16, 15, 14)

    def attacks(self, fromsq, tosq, board):
        return tosq - fromsq in self.offsets

    def plmoves(self, fromsq, board, context):
        moves = []
        # Quiet and capture moves
        for offset in self.offsets:
            if board[fromsq + offset].kind is NoPiece:
                moves.append(Move(fromsq, fromsq + offset, MoveKind.QUIET, None))
            elif board[fromsq + offset].kind is not OutOfBoundsPiece \
                    and board[fromsq + offset].side is not self.side:
                moves.append(Move(fromsq, fromsq + offset, MoveKind.CAPTURE, None))
        # Castling queen
        if context.can_castle[self.side][0] \
                and board[fromsq - 1].kind is NoPiece \
                and board[fromsq - 2].kind is NoPiece \
                and board[fromsq - 3].kind is NoPiece \
                and not board.attacked(fromsq, self.side.opponent()) \
                and not board.attacked(fromsq - 1, self.side.opponent()) \
                and not board.attacked(fromsq - 2, self.side.opponent()):
            moves.append(Move(fromsq, fromsq - 2, MoveKind.CASTLE_QUEEN, None))
        # Castling king
        if context.can_castle[self.side][1] \
                and board[fromsq + 1].kind is NoPiece \
                and board[fromsq + 2].kind is NoPiece \
                and not board.attacked(fromsq, self.side.opponent()) \
                and not board.attacked(fromsq + 1, self.side.opponent()) \
                and not board.attacked(fromsq + 2, self.side.opponent()):
            moves.append(Move(fromsq, fromsq + 2, MoveKind.CASTLE_KING, None))
        return moves


class Game:
    """
    Representa um jogo de xadrez ativo. Esta (junto com a classe `Side`, as subclasses de `Piece` e
    a classe `Square`)
    é a única classe que pode ser instanciada por um consumidor da engine de xadrez.
    Todas as outras classes são "internas" à engine.
    """

    class GameBoard(Board):

        def movepiece(self, fromsq, tosq):
            return self._movepiece(fromsq, tosq)

        def addpiece(self, piece, square):
            return self._addpiece(piece, square)

        def removepiece(self, square):
            return self._removepiece(square)

    Snapshot = namedtuple('Snapshot', 'turn can_castle ep antimove')

    initialrank = {
        Side.WHITE: '1',
        Side.BLACK: '8'
    }

    PIECES_INIT = {
        "a1": Rook(Side.WHITE), "b1": Knight(Side.WHITE), "c1": Bishop(Side.WHITE),
        "d1": Queen(Side.WHITE), "e1": King(Side.WHITE), "f1": Bishop(Side.WHITE),
        "g1": Knight(Side.WHITE), "h1": Rook(Side.WHITE), "a2": Pawn(Side.WHITE),
        "b2": Pawn(Side.WHITE), "c2": Pawn(Side.WHITE), "d2": Pawn(Side.WHITE),
        "e2": Pawn(Side.WHITE), "f2": Pawn(Side.WHITE), "g2": Pawn(Side.WHITE),
        "h2": Pawn(Side.WHITE), "a8": Rook(Side.BLACK), "b8": Knight(Side.BLACK),
        "c8": Bishop(Side.BLACK), "d8": Queen(Side.BLACK), "e8": King(Side.BLACK),
        "f8": Bishop(Side.BLACK), "g8": Knight(Side.BLACK), "h8": Rook(Side.BLACK),
        "a7": Pawn(Side.BLACK), "b7": Pawn(Side.BLACK), "c7": Pawn(Side.BLACK),
        "d7": Pawn(Side.BLACK), "e7": Pawn(Side.BLACK), "f7": Pawn(Side.BLACK),
        "g7": Pawn(Side.BLACK), "h7": Pawn(Side.BLACK),
    }

    @staticmethod
    def default_game():
        positions = []
        for c in "abcdefgh":
            for i in range(1, 9):
                positions.append(c + str(9 - i))
        listgame = []
        for i in range(8):
            for j in range(8):
                piece = Game.PIECES_INIT.get(positions[i + 8 * j])
                if piece is None:
                    listgame.append(NoPiece())
                else:
                    listgame.append(piece)
        return Game(listgame, {Side.WHITE: (True, True), Side.BLACK: (True, True)}, None, Side.WHITE)

    def __init__(self, board_array, castle_rights, ep_square, turn):
        """

        :param board_array: Lista com 64 elementos. Cada elemento de ser uma instância de `Piece` (
        na verdade, uma instância de alguma subclasse de `Piece`, como `Rook`)
        :param castle_rights: Dicionário. Chave: Uma instância de `Side`. Valor: Uma tupla de 2 elementos
        booleanos. O primeiro indica se é legal fazer um roque pelo lado da rainha; o segundo, pelo
        lado do rei
        :param ep_square: Uma instância de `Square`, ou o valor `None`. Representa a casa do tabuleiro
        na qual um peão pararia caso executasse um movimento de captura "en passant". Por isso,
        `ep_square` pode ser não-nulo somente no caso de o jogo já começar numa configuração de peças
        em que seja possível ao jogador da vez fazer uma jogada "en passant"
        :param turn: Instância de `Side`. Indica qual jogador está prestes a jogar inicialmente
        """
        if len(board_array) != 64:
            raise ValueError('Can only construct a Game with a 8 * 8 array')
        if OutOfBoundsPiece in [x.kind for x in board_array]:
            raise ValueError('Cannot construct a game board with OutOfBoundsPiece in the middle')
        board = ([OutOfBoundsPiece()] * 15) * 3
        for row in range(8):
            board += [OutOfBoundsPiece()] * 3 + board_array[8 * row:8 * row + 8] + \
                     [OutOfBoundsPiece()] * 4
        board += ([OutOfBoundsPiece()] * 15) * 4
        self.__board = self.GameBoard(board)
        self.__context = Context({
            Side.WHITE: self.__board.king(Side.WHITE),
            Side.BLACK: self.__board.king(Side.BLACK)
        }, castle_rights, ep_square)
        self.__turn = turn
        self.__history = deque()

    def turn(self):
        """

        :return: Instância de `Side` representando qual é o jogador da vez
        """
        return self.__turn

    def get(self, square):
        """

        :param square: Instância de `Square`, ou um int (índice da casa) ou uma string (nome da casa, como
        'a1', 'b4', etc.)
        :return: Instância de `Piece` representando a peça posicionada na casa `square` (será uma instância
        de `NoPiece` caso não haja peça na tal casa)
        """
        if Square(square).valid is False:
            raise ValueError('Square named ' + Square(square).name +
                             'is not a valid chessboard position')
        return self.__board[square]

    def check(self):
        """

        :return: booleana indicando se o jogador da vez está em xeque
        """
        return self.__board.attacked(self.__board.king(self.__turn), self.__turn.opponent())

    def moves(self, square=None):
        """
        Lista movimentos legais que o jogador da vez pode executar, usando sua peça que está na casa
        `square` (o método não deve ser chamada caso o jogador não tenha peça sua na casa `square`).

        Caso se passe `square` como `None`, todos os movimentos legais do jogador, a partir de qualquer
        casa do tabuleiro, serão listados

        :param square: Instância de `Square` (ou int, ou string), ou ainda o valor `None`
        :return: Lista de movimentos legais que o jogador da vez pode executar a partir da casa
        `square`, ou a lista de todos os movimentos legais, a partir de qualquer casa, caso `square`
        seja passado como `None`.
        """
        if square is None:
            moves = []
            for square in self.__board.occuppied(self.__turn):
                moves += self.moves(square)
            return moves
        if self.__board[square].side is not self.__turn:
            return []
        legalmoves = []
        piece = self.__board[square]
        moves = piece.plmoves(square, self.__board, self.__context)
        # print(moves)
        for move in moves:
            antimove = move.kind.exec(
                move, self.__board.movepiece, self.__board.addpiece, self.__board.removepiece)
            if not self.check():
                legalmoves.append(move)
            antimove.kind.exec(
                antimove, self.__board.movepiece, self.__board.addpiece, self.__board.removepiece)
        return legalmoves

    def checkmate(self):
        """

        :return: booleana indicando se o jogador da vez está em xequemate
        """
        if not self.check():
            return False
        return self.moves() == []

    def stalemate(self):
        """

        :return: booleana indicando se o jogador da vez está em condição de "stalemate". Essa é uma
        condição em que o jogador não está em xeque, mas qualquer movimento que ele fizesse o deixaria
        em xeque, não havendo movimentos legais, portanto.
        """
        if self.check():
            return False
        return self.moves() == []

    def inflate(self, movestr):
        if len(movestr) > 5:
            raise ValueError('move string must be either 4 or 5 characters long')
        fromsq = Square(movestr[0:2])
        tosq = Square(movestr[2:4])
        side = self.__board[fromsq].side
        promotion = {
            'N': Knight(side), 'R': Rook(side), 'Q': Queen(side), 'B': Bishop(side)
        }[movestr[4]] if \
            len(movestr) == 5 else None
        existent = [x for x in self.__board[fromsq].plmoves(fromsq, self.__board, self.__context)
                    if x.tosq == tosq and x.promotion == promotion]
        return existent[0]

    def make(self, move):
        """
        Realiza um movimento no jogo
        :param move: Uma instância de `Move` ou uma string representativa de um movimento. No caso
        de ser uma string, ela deve especificar a casa de origem e a de destino. Por exemplo: "a1b1"
        move a peça de a1 para b1. Se o movimento for de promoção, a promoção é especificada por
        último na string. Por exemplo: "a7a8N" move um peão de a7 para a8 e o promove a cavalo (as siglas
        são: N para cavalo, B para bispo, Q para rainha e R para torre)
        :return: Tupla com instância de alguma subclasse de `Piece` representando a peça que
        foi capturada (instância de `NoPiece` caso não seja movimento de captura) e com a casa do tabuleiro
        em que ela foi capturada (ou `None` caso não seja movimento de captura)
        """
        if isinstance(move, str):
            move = self.inflate(move)
        antimove = move.kind.exec(
            move, self.__board.movepiece, self.__board.addpiece, self.__board.removepiece)
        if self.check() or self.__board[move.tosq].side is not self.__turn:
            antimove.kind.exec(
                antimove, self.__board.movepiece, self.__board.addpiece, self.__board.removepiece)
            raise RuntimeError('Tried to execute illegal move: ' + str(move))
        self.__history.append(self.Snapshot(self.__turn, {
            Side.WHITE: self.__context.can_castle[Side.WHITE],
            Side.BLACK: self.__context.can_castle[Side.BLACK]
        }, self.__context.ep, antimove))
        # castling
        kind = self.__board[move.tosq].kind
        if kind is King:
            self.__context.can_castle[self.__turn] = (False, False)
        # queen side
        elif self.__context.can_castle[self.__turn][0] and Square(move.fromsq) == Square(
                'a' + self.initialrank[self.__turn]):
            self.__context.can_castle[self.__turn] = (False, self.__context.can_castle[self.__turn][1])
        # king side
        elif self.__context.can_castle[self.__turn][1] and Square(move.fromsq) == Square(
                'h' + self.initialrank[self.__turn]):
            self.__context.can_castle[self.__turn] = (self.__context.can_castle[self.__turn][0], False)
        # en passant
        ep = (move.fromsq + move.tosq) / 2 if move.kind is MoveKind.PAWN2 else None
        self.__context = self.__context._replace(ep=ep)
        self.__turn = self.__turn.opponent()
        if move.kind in (MoveKind.CAPTURE, MoveKind.EP_CAPTURE, MoveKind.PROMOTION_CAPTURE):
            return antimove.addpiece, antimove.addpos
        else:
            return NoPiece(), None

    def unmake(self):
        """
        Desfaz o último movimento feito no jogo
        """
        if len(self.__history) == 0:
            raise RuntimeError('Tried to unmake a move, but no moves had been made previously')
        last = self.__history.pop()
        last.antimove.kind.exec(
            last.antimove, self.__board.movepiece, self.__board.addpiece, self.__board.removepiece)
        self.__context = self.__context._replace(ep=last.ep, can_castle=last.can_castle)
        self.__turn = last.turn

    def getboard(self):
        """
        Não recomendável que se use. `Game` tem todos os métodos suficientes para jogar.
        :return: Representação interna do tabuleiro de jogo
        """
        return self.__board
