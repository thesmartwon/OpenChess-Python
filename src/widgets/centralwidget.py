from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QWidget,
                             QDesktopWidget)
from game import OpenGame
from widgets.movetree import MoveTreeWidget
from widgets.board import BoardScene, BoardSceneView
from widgets.engine import EngineWidget
import chess


class CentralWidget(QFrame):
    """
    Takes up the center of the screen and initializes
    communications between all of the widgets there.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.openGame = OpenGame()
        self.boardScene = BoardScene(self)
        self.boardSceneView = BoardSceneView(self, self.boardScene)
        self.moveTree = MoveTreeWidget(self, self.openGame.game)
        self.engineWidget = EngineWidget(self)
        self.openGame.setWeakRefs(self, self.boardScene, self.moveTree,
                                  self.engineWidget)
        self.engineWidget.initEngine(self.openGame.board)

        self.initUI()
        self.show()

    def initUI(self):
        """Creates parts of layout that account for sizes.
        Notable is that the boardScene squares will be a multiple of 8."""
        screens = [QDesktopWidget().availableGeometry(i) for i in
                   range(QDesktopWidget().screenCount())]
        assert screens
        maxWidth = max(min(s.width(), s.height()) for s in screens)
        sceneWidth = int(maxWidth / 8) * 8
        self.boardScene.initSquares(sceneWidth / 8)
        self.boardScene.setSceneRect(0, 0, sceneWidth, sceneWidth)
        self.boardSceneView.initUI(sceneWidth)

        """Creates layout without accounting for sizes"""
        pal = QPalette(self.palette())
        pal.setColor(QPalette.Background, Qt.green)
        self.setAutoFillBackground(True)
        self.setPalette(pal)
        self.vertLayout = QVBoxLayout(self)
        self.vertLayout.setSpacing(0)
        self.vertLayout.setContentsMargins(0, 0, 0, 0)
        self.vertLayout.addWidget(self.moveTree)
        self.vertLayout.addWidget(self.engineWidget)
        self.vertWidget = QWidget(self)
        self.vertWidget.setLayout(self.vertLayout)
        horiLayout = QHBoxLayout(self)
        horiLayout.setSpacing(0)
        horiLayout.setContentsMargins(0, 0, 0, 0)
        horiLayout.addWidget(self.boardSceneView)
        horiLayout.addWidget(self.vertWidget)
        self.setLayout(horiLayout)
