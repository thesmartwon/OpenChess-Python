from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QStandardItem
import chess
import constants


class OpenGame(chess.Board):
    """
    OpenGame is a helper class (mostly to mainframe) that
    houses info related to the game state and recieves messages
    whenever it is updated.
    """
    def __init__(self):
        super().__init__()
        constants.GAME_STATE = self
        self.moveItems = []

    def doMove(self, move, moveTreeModel):
        """
        Updates the board state and notifies appropriate objects.
        If the move is a promotion, this widget will ask for it.
        :param move: a chess.Move without promotion
        :return: True if the move was able to be made, False
        otherwise
        """
        if (self.piece_at(move.from_square).piece_type == chess.PAWN and
                chess.rank_index(move.to_square) in [0, 7]):
            # TODO: ask for a real promotion piece
            move.promotion = chess.QUEEN
        assert(move in self.legal_moves)
        if move in self.legal_moves:
            self.moveItems.append(QStandardItem())
            self.moveItems[-1].setData(QVariant(move))
            self.moveItems[-1].setText(self.san(move))
            self.updateMoveTreeModel(moveTreeModel)
            self.push(move)
            return True
        return False

    def updateMoveTreeModel(self, moveTreeModel):
        moveTreeModel.setItem(int(len(self.move_stack) / 2),
                              not self.turn, self.moveItems[-1])
