from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QTransform, QPalette
from PyQt5.QtWidgets import QFrame, QSplitter
from game import OpenGame
from widgets.movetree import MoveTreeView, MoveTreeModel
from widgets.board import BoardScene, BoardSceneView


class MainFrame(QFrame):
    """
    Takes up the center of the screen and
    communicates between all of the widgets there.
    """
    def __init__(self, parent, geometry):
        super().__init__(parent)
        print("frame geometry is", geometry)
        self.openGame = OpenGame()
        self.boardScene = BoardScene(self)
        self.boardSceneView = BoardSceneView(self, self.boardScene)
        self.moveTreeModel = MoveTreeModel()
        self.moveTreeView = MoveTreeView(self, self.moveTreeModel)
        self.vertSplitter = QSplitter(Qt.Vertical, self)
        self.horiSplitter = QSplitter(self)

        self.setGeometry(geometry)
        self.initStaticUI()
        self.initDynamicUI()
        self.horiSplitter.setGeometry(self.geometry())
        self.horiSplitter.show()
        self.show()

    def initStaticUI(self):
        pal = QPalette(self.palette())
        pal.setColor(QPalette.Background, Qt.green)
        self.setAutoFillBackground(True)
        self.setPalette(pal)
        self.vertSplitter.addWidget(self.moveTreeView)
        self.vertSplitter.addWidget(QFrame(self))
        self.horiSplitter.setBaseSize(self.width(), self.height())
        self.horiSplitter.addWidget(self.boardSceneView)
        self.horiSplitter.addWidget(self.vertSplitter)

    def initDynamicUI(self):
        lesserDimension = min(self.width(), self.height())
        sceneWidth = int(lesserDimension / 8) * 8
        print("init", sceneWidth)
        self.initialSceneWidth = sceneWidth
        self.boardScene.initSquares(sceneWidth / 8)
        self.boardScene.setSceneRect(0, 0, sceneWidth, sceneWidth)
        self.boardSceneView.setGeometry(0, 0, sceneWidth, sceneWidth)
        self.moveTreeView.setGeometry(0, 0, self.width() - sceneWidth -
                                      self.horiSplitter.handleWidth(),
                                      self.height() - 50)
        split = [sceneWidth + self.horiSplitter.handleWidth(),
                 self.width() - sceneWidth - self.horiSplitter.handleWidth()]
        self.horiSplitter.setSizes(split)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        lesserDimension = min(self.width() - self.moveTreeView.width(),
                              self.height())
        sceneWidth = lesserDimension
        print('sceneWidth is', sceneWidth)
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
