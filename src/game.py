import chess
from chess import pgn
import constants


class OpenGame():
    """
    OpenGame is a helper class that houses the game state and
    recieves/sends messages whenever it is updated.
    Must call setWeakRefs before doMove.
    """
    def __init__(self):
        self.game = pgn.Game()
        self.board = self.game.board()
        constants.GAME_STATE = self.board
        constants.HERO = chess.WHITE

    def setWeakRefs(self, boardScene, moveTreeModel, engine):
        self.moveTreeModel = moveTreeModel
        self.boardScene = boardScene
        self.engine = engine

    def doMove(self, move):
        """
        Updates the board state and notifies appropriate objects.
        If the move is a promotion, this widget will ask for it.
        :param move: a chess.Move without promotion
        :return: True if the move was able to be made, False
        otherwise
        """
        if (self.board.piece_at(move.from_square).piece_type == chess.PAWN and
                chess.rank_index(move.to_square) in [0, 7]):
            # TODO: ask for a real promotion piece
            move.promotion = chess.QUEEN
        assert(move in self.board.legal_moves)
        if move in self.board.legal_moves:
            isEnPassant = self.board.is_en_passant(move)
            castling = 0
            if self.board.is_queenside_castling(move):
                castling = 1
            elif self.board.is_kingside_castling(move):
                castling = 2
            self.moveTreeModel.updateAfterMove(move,
                                               self.board.fullmove_number,
                                               self.board.turn,
                                               self.board.san(move))
            self.board.push(move)
            self.engine.updateAfterMove(move)
            self.boardScene.updatePositionAfterMove(move, castling,
                                                    isEnPassant)
            return True
        return False

    def newGame(self):
        print('new game')
        self.board.reset()
        self.game.setup(self.board)
        self.engine.reset(True)
        self.moveTreeModel.reset()
        self.boardScene.reset()

    def scrollToPly(self, plyNumber):
        curPly = self.board.fullmove_number * 2 + int(not self.board.turn) - 2
        assert curPly >= plyNumber
        if curPly == plyNumber:
            return
        print('scrolling to', plyNumber)
        for i in range(curPly - plyNumber - 1):
            self.board.pop()
        self.engine.reset()
        self.moveTreeModel.eraseAfterPly(plyNumber)
        self.boardScene.reset()

    def editBoard(self):
        print('editing board')
        self.board.reset()
        self.board.clear_board()
