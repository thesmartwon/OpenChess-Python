import chess
import constants


class OpenGame():
    """
    OpenGame is a helper class (mostly to mainframe) that
    houses info related to the game state and recieves messages
    whenever it is updated.
    """
    def __init__(self):
        self.board = chess.Board()
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
            print('moveInfo', self.board.fullmove_number)
            self.moveTreeModel.updateAfterMove(move,
                                               self.board.fullmove_number,
                                               not self.board.turn,
                                               self.board.san(move))
            self.board.push(move)
            self.engine.updateAfterMove(move)
            self.boardScene.updatePositionAfterMove(move, castling,
                                                    isEnPassant)
            return True
        return False

    def newGame(self):
        self.board.reset()
        self.engine.reset()
        self.moveTreeModel.reset()
        self.boardScene.reset()
