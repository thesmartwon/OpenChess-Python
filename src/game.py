from widgets.movetree import MoveTreeView, MoveTreeModel
from widgets.board import BoardScene
from PyQt5.QtCore import QObject, QVariant
from PyQt5.QtGui import QStandardItem
import chess
import constants


class OpenGame(QObject):
    """
    OpenGame houses all objects linked to the game state.
    It's self.game holds the game state.
    """
    def __init__(self):
        super().__init__()
        self.game = chess.Board()
        self.boardScene = BoardScene(self)
        self.moveTreeScene = MoveTreeView()
        self.moveTreeModel = MoveTreeModel()
        self.moveItems = []
        self.moveTreeModel.setHorizontalHeaderLabels(['White', 'Black'])
        self.moveTreeScene.setModel(self.moveTreeModel)
        constants.GAME_STATE = self.game

    def doMove(self, move):
        """
        Updates the board state and notifies appropriate objects.
        :param move: a chess.Move without promotion
        :return:
        """
        if (self.game.piece_at(move.from_square).piece_type == chess.PAWN and
                chess.rank_index(move.to_square) in [0, 7]):
            # TODO: ask for a real promotion piece
            move.promotion = chess.QUEEN
        assert(move in self.game.legal_moves)
        if move in self.game.legal_moves:
            self.moveItems.append(QStandardItem())
            self.moveItems[-1].setData(QVariant(move))
            self.moveItems[-1].setText(self.game.san(move))
            self.moveTreeModel.setItem(int(len(self.game.move_stack) / 2),
                                       not self.game.turn, self.moveItems[-1])
            isEnPassant = self.game.is_en_passant(move)
            castling = 0
            if self.game.is_queenside_castling(move):
                castling = 1
            elif self.game.is_kingside_castling(move):
                castling = 2
            self.game.push(move)
            self.boardScene.updatePositionAfterMove(move, castling,
                                                    isEnPassant)
            return True
        return False
