from widgets.movetree import MoveTreeScene, MoveTreeModel
from widgets.board import BoardScene
from PyQt5.QtCore import QObject, QVariant
from PyQt5.QtGui import QStandardItem
import chess
import globals

class OpenGame(QObject):
    """
    OpenGame houses all objects linked to the game state. It's self.game holds the game state.
    """
    def __init__(self):
        super().__init__()
        self.game = chess.Board()
        self.boardScene = BoardScene(self)
        self.moveTreeScene = MoveTreeScene()
        self.moveTreeModel = MoveTreeModel()
        self.moveItems = []
        self.moveTreeModel.setHorizontalHeaderLabels(['White', 'Black'])
        self.moveTreeScene.setModel(self.moveTreeModel)
        globals.turn = self.game.turn

    def doMove(self, move):
        """
        Updates the board state and notifies appropriate objects.
        :param move: just a to square and from square. OpenGame will handle special moves
        :return:
        """
        if self.game.piece_at(move.from_square).piece_type == chess.PAWN and chess.rank_index(move.to_square) in [0, 7]:
            move.promotion = chess.QUEEN
        if move in self.game.legal_moves:
            self.moveItems.append(QStandardItem())
            self.moveItems[-1].setData(QVariant(move))
            self.moveItems[-1].setText(self.game.san(move))
            self.moveTreeModel.setItem(int(len(self.game.move_stack) / 2), not self.game.turn, self.moveItems[-1])
            self.game.push(move)
            self.boardScene.updatePositionAfterMove(move, self.game.ep_square)
            globals.turn = self.game.turn
            return True
        print('illegal move attempted...bad programming')
        return False
