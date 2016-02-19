from widgets.movetree import MoveTreeScene, MoveTreeModel
from widgets.board import BoardScene
from PyQt5.QtCore import QObject, QVariant
from PyQt5.QtGui import QStandardItem
import chess
import globals

class OpenGame(QObject):
    """
    OpenGame houses all objects linked to the board. It's self.game holds the game state.
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
        if move in self.game.legal_moves:
            self.moveItems.append(QStandardItem())
            self.moveItems[-1].setData(QVariant(move))
            self.moveItems[-1].setText(self.game.san(move))
            self.moveTreeModel.setItem(int(len(self.game.move_stack) / 2), not self.game.turn, self.moveItems[-1])
            self.game.push(move)
            globals.turn = self.game.turn
            return True
        return False
