from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QStandardItem
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
        self.moveItems = []

    def doMove(self, move, moveTreeModel, boardScene, engine):
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
            self.moveItems.append(QStandardItem())
            self.moveItems[-1].setData(QVariant(move))
            self.moveItems[-1].setText(self.board.san(move))
            moveTreeModel.setItem(int(len(self.board.move_stack) / 2),
                                  not self.board.turn, self.moveItems[-1])
            self.board.push(move)
            boardScene.updatePositionAfterMove(move, castling,
                                               isEnPassant)
            engine.updateAfterMove(self.board)
            return True
        return False
