from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QTransform, QPalette
from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QWidget,
                             QApplication)
from game import OpenGame
from widgets.movetree import MoveTreeView, MoveTreeModel
from widgets.board import BoardScene, BoardSceneView


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
        self.moveTreeView = MoveTreeView(self, self.moveTreeModel)

        self.initStaticUI()
        self.initDynamicUI()
        self.show()

    def initStaticUI(self):
        """Creates layout without accounting for sizes"""
        pal = QPalette(self.palette())
        pal.setColor(QPalette.Background, Qt.green)
        self.setAutoFillBackground(True)
        self.setPalette(pal)
        vertLayout = QVBoxLayout(self)
        vertLayout.setSpacing(0)
        vertLayout.addWidget(self.moveTreeView)
        self.vertWidget = QWidget(self)
        self.vertWidget.setLayout(vertLayout)
        horiLayout = QHBoxLayout(self)
        horiLayout.addWidget(self.boardSceneView)
        horiLayout.addWidget(self.vertWidget)
        self.setLayout(horiLayout)

    def initDynamicUI(self):
        """Creates parts of layout that account for sizes.
        Notable is that the boardScene will be a multiple of 8."""
        # TODO: make it so it will pick the largest screen geometry
        screenGeo = QApplication.primaryScreen().availableGeometry()
        lesserDimension = min(screenGeo.width(), screenGeo.height())
        sceneWidth = int(lesserDimension / 8) * 8
        self.initialSceneWidth = sceneWidth
        self.boardScene.initSquares(sceneWidth / 8)
        self.boardScene.setSceneRect(0, 0, sceneWidth, sceneWidth)

    def resizeEvent(self, event):
        print("w", self.width(), 'h', self.height())
        sceneWidth = min(event.size().width(), event.size().height())
        self.boardSceneView.setGeometry(0, 0, sceneWidth, sceneWidth)
        # print('sceneWidth is', sceneWidth)
        trans = QTransform()
        trans.scale(sceneWidth / self.initialSceneWidth,
                    sceneWidth / self.initialSceneWidth)
        self.boardSceneView.setTransform(trans)

    def doMove(self, move):
        isEnPassant = self.openGame.is_en_passant(move)
        castling = 0
        if self.openGame.is_queenside_castling(move):
            castling = 1
        elif self.openGame.is_kingside_castling(move):
            castling = 2
        self.openGame.doMove(move, self.moveTreeModel)
        self.boardScene.updatePositionAfterMove(move, castling,
                                                isEnPassant)
