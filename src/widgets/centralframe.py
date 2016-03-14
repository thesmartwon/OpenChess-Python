from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QWidget,
                             QDesktopWidget)
from game import OpenGame
from widgets.movetree import MoveTreeView, MoveTreeModel
from widgets.board import BoardScene, BoardSceneView
from widgets.engine import EngineWidget


class CentralFrame(QFrame):
    """
    Takes up the center of the screen and
    communicates between all of the widgets there.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.openGame = OpenGame()
        self.boardScene = BoardScene(self)
        self.boardSceneView = BoardSceneView(self, self.boardScene)
        self.moveTreeModel = MoveTreeModel()
        self.moveTreeModel.moveItemClicked.connect(self.openGame.scrollToPly)
        self.moveTreeView = MoveTreeView(self, self.moveTreeModel)
        self.moveTreeView.clicked.connect(self.moveTreeModel.itemClicked)
        self.engineWidget = EngineWidget(self)
        self.openGame.setWeakRefs(self.boardScene, self.moveTreeModel,
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
        vertLayout = QVBoxLayout(self)
        vertLayout.setSpacing(0)
        vertLayout.setContentsMargins(0, 0, 0, 0)
        vertLayout.addWidget(self.moveTreeView)
        vertLayout.addWidget(self.engineWidget)
        self.vertWidget = QWidget(self)
        self.vertWidget.setLayout(vertLayout)
        horiLayout = QHBoxLayout(self)
        horiLayout.setSpacing(0)
        horiLayout.setContentsMargins(0, 0, 0, 0)
        horiLayout.addWidget(self.boardSceneView)
        horiLayout.addWidget(self.vertWidget)
        self.setLayout(horiLayout)
