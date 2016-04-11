from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QWidget,
                             QDesktopWidget)
from game import OpenChessGame
from widgets.movetree import MoveTreeModel, MoveTreeView
from widgets.board import BoardScene, BoardSceneView
from widgets.engine import EngineWidget


class CentralWidget(QFrame):
    """
    Takes up the center of the screen and initializes
    communications between all of the widgets there.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.chessGame = OpenChessGame(self)
        self.boardScene = BoardScene(self, self.chessGame.board)
        self.boardSceneView = BoardSceneView(self, self.boardScene)
        self.moveTreeModel = MoveTreeModel(self)
        self.moveTreeView = MoveTreeView(self, self.moveTreeModel)
        self.engineWidget = EngineWidget(self)
        self.engineWidget.initEngine(self.chessGame.board)

        self.wireWidgets()
        self.initUI()
        self.show()

    def wireWidgets(self):
        self.chessGame.moveDone.connect(self.moveTreeModel.updateAfterMove)
        self.chessGame.moveDone.connect(self.boardScene.updateAfterMove)
        self.chessGame.moveDone.connect(self.engineWidget.updateAfterMove)
        self.chessGame.positionChanged.connect(self.boardScene.reset)
        self.chessGame.positionChanged.connect(self.engineWidget.reset)
        self.chessGame.positionChanged.connect(self.moveTreeModel.reset)
        self.chessGame.positionScrolled.connect(self.moveTreeView.entryScrolled)
        self.chessGame.positionScrolled.connect(self.boardScene.reset)
        self.chessGame.positionScrolled.connect(self.engineWidget.reset)
        self.boardScene.moveInputted.connect(self.chessGame.doMove)
        self.boardSceneView.mouseWheelScrolled.connect(self.chessGame.scrollInDirection)
        self.moveTreeView.moveItemScrolled.connect(self.chessGame.scrollToNode)
        self.moveTreeModel.moveItemAdded.connect(self.moveTreeView.entryScrolled)
        self.engineWidget.pvChanged.connect(self.boardScene.updatePVItems)

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
        self.vertLayout.addWidget(self.moveTreeView)
        self.vertLayout.addWidget(self.engineWidget)
        self.vertWidget = QWidget(self)
        self.vertWidget.setLayout(self.vertLayout)
        horiLayout = QHBoxLayout(self)
        horiLayout.setSpacing(0)
        horiLayout.setContentsMargins(0, 0, 0, 0)
        horiLayout.addWidget(self.boardSceneView)
        horiLayout.addWidget(self.vertWidget)
        self.setLayout(horiLayout)
