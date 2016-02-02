from PyQt5 import QtCore, QtGui, QtSvg, QtWidgets
from PyQt5.QtWidgets import (QGraphicsRectItem, QGraphicsWidget,
    QGraphicsEllipseItem, QGraphicsItem, QGraphicsScene)
import chess
import userConfig
import constants
import globals


bConfig = userConfig.config['BOARD']


class SquareWidget(QGraphicsWidget):
    """
    Contains a SquareItem and PieceItem and possibly other effects added to it.
    """
    Normal, Selected, LastMove, PossibleMove, PossibleMoveHover, MoveHover = range(6)
    pieceReleased = QtCore.pyqtSignal(int)

    def __init__(self, square, occupied):
        super().__init__()
        self.square = square
        self.state = SquareWidget.Normal
        self.isValidMove = False
        self.occupied = occupied
        self.isLight = bool(chess.BB_SQUARES[int(square)] & chess.BB_LIGHT_SQUARES)
        self.setGeometry(0, 0, int(bConfig['squareWidth']), int(bConfig['squareWidth']))
        self.squareItem = SquareItem(self.isLight)
        self.squareItem.setRect(self.geometry())
        self.squareItem.setZValue(0)
        self.squareItem.setParentItem(self)
        self.effectItem = None
        self.pieceItem = None
        self.previousState = SquareWidget.Normal
        self.deleteScene = QGraphicsScene()
        self.setAcceptDrops(True)
        self.setAcceptHoverEvents(True)

    def removeEffectItem(self):
        if self.effectItem is not None:
            self.effectItem.setParentItem(None)
            self.deleteScene.addItem(self.effectItem)
            self.deleteScene.clear()
            self.effectItem = None

    def setState(self, state):
        self.isValidMove = False
        if self.state == state:
            return
        self.previousState = self.state
        self.state = state
        self.removeEffectItem()
        if state == SquareWidget.Normal:
            return
        elif state == SquareWidget.Selected:
            self.effectItem = QGraphicsRectItem()
            c = QtGui.QColor(bConfig['highlightedcolor'])
            c.setAlphaF(float(bConfig['effectsAlpha']))
            self.effectItem.setBrush(QtGui.QBrush(c))
            self.effectItem.setPen(QtGui.QPen(QtCore.Qt.NoPen))
            self.effectItem.setRect(0, 0, int(bConfig['squareWidth']), int(bConfig['squareWidth']))
        elif state == SquareWidget.LastMove:
            self.effectItem = QGraphicsRectItem()
            c = QtGui.QColor(bConfig['lastMoveColor'])
            c.setAlphaF(float(bConfig['effectsAlpha']))
            self.effectItem.setBrush(QtGui.QBrush(c))
            self.effectItem.setPen(QtGui.QPen(QtCore.Qt.NoPen))
            self.effectItem.setRect(0, 0, int(bConfig['squareWidth']), int(bConfig['squareWidth']))
        elif state == SquareWidget.PossibleMove:
            self.isValidMove = True
            if self.occupied:
                customRect = QtCore.QRect(0, 0, int(bConfig['squareWidth']), int(bConfig['squareWidth']))
                if self.isLight:
                    self.effectItem = CustomEffectItem(QtGui.QBrush(QtGui.QColor(bConfig['lightcolor'])),
                                                       customRect)
                else:
                    self.effectItem = CustomEffectItem(QtGui.QBrush(QtGui.QColor(bConfig['darkcolor'])),
                                                       customRect)
                    # self.effectItem.setRect(customRect)
            else:
                self.effectItem = QGraphicsEllipseItem()
                c = QtGui.QColor(bConfig['highlightedcolor'])
                c.setAlphaF(float(bConfig['effectsAlpha']))
                self.effectItem.setBrush(QtGui.QBrush(c))
                self.effectItem.setPen(QtGui.QPen(QtCore.Qt.NoPen))
                self.effectItem.setRect(int(bConfig['squareWidth']) * .75 / 2,
                                        int(bConfig['squareWidth']) * .75 / 2,
                                        int(bConfig['squareWidth']) * .25,
                                        int(bConfig['squareWidth']) * .25)
        elif state == SquareWidget.PossibleMoveHover:
            self.effectItem = QGraphicsRectItem()
            c = QtGui.QColor(bConfig['hoverColor'])
            c.setAlphaF(float(bConfig['effectsAlpha']))
            self.effectItem.setBrush(QtGui.QBrush(c))
            self.effectItem.setPen(QtGui.QPen(QtCore.Qt.NoPen))
            self.effectItem.setRect(0, 0, int(bConfig['squareWidth']), int(bConfig['squareWidth']))
        elif state == SquareWidget.MoveHover:
            self.effectItem = QGraphicsRectItem()
            c = QtGui.QColor(bConfig['invalidHoverColor'])
            c.setAlphaF(float(bConfig['weakEffectsAlpha']))
            self.effectItem.setBrush(QtGui.QBrush(c))
            self.effectItem.setPen(QtGui.QPen(QtCore.Qt.NoPen))
            self.effectItem.setRect(0, 0, int(bConfig['squareWidth']), int(bConfig['squareWidth']))
        self.effectItem.setZValue(1)
        self.effectItem.setParentItem(self)

    def dropEvent(self, event):
        if self.isValidMove and event.mimeData().hasFormat('application/x-dnditemdata'):
            # print("hey", event.mimeData())
            self.pieceReleased.emit(self.square)

    def hoverEnterEvent(self, event):
        if self.isValidMove:
            self.setState(SquareWidget.PossibleMoveHover)
            self.isValidMove = True

    def hoverLeaveEvent(self, event):
        if self.isValidMove:
            self.setState(self.previousState)

    def dragEnterEvent(self, event):
        if self.isValidMove:
            self.setState(SquareWidget.PossibleMoveHover)
            self.isValidMove = True
        elif self.state == SquareWidget.Normal:
            self.setState(SquareWidget.MoveHover)

    def dragLeaveEvent(self, event):
        if self.state != SquareWidget.Selected:
            self.setState(self.previousState)

    def addPiece(self, piece):
        piece.setParentItem(self)
        piece.setZValue(2)
        self.pieceItem = piece
        self.occupied = True

    def removePiece(self):
        if self.pieceItem is not None:
            self.pieceItem.deleteLater()
            self.pieceItem = None
            self.occupied = False

    def mousePressEvent(self, event):
        if self.isValidMove:
            self.pieceReleased.emit(self.square)


class CustomEffectItem(QGraphicsItem):
    def __init__(self, brush, rect):
        super().__init__()
        self.rect = QtCore.QRectF(rect)
        self.brush = brush

    def boundingRect(self):
        return self.rect

    def paint(self, QPainter, QStyleOptionGraphicsItem, QWidget_widget=None):
        QPainter.setClipRect(self.rect)
        col = QtGui.QColor(bConfig['highlightedcolor'])
        col.setAlphaF(float(bConfig['effectsAlpha']))
        QPainter.setBrush(QtGui.QBrush(col))
        QPainter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        QPainter.drawRect(0, 0, int(bConfig['squareWidth']), int(bConfig['squareWidth']))
        QPainter.setBrush(self.brush)
        p = QtCore.QPoint(int(bConfig['squareWidth']) / 2, int(bConfig['squareWidth']) / 2)
        QPainter.drawEllipse(p, int(bConfig['squareWidth']) / 2 + 8, int(bConfig['squareWidth']) / 2 + 8)


class SquareItem(QGraphicsRectItem):
    """
    Just a visual dummy rectangle that is dark or light.
    """
    def __init__(self, isLight):
        super().__init__()
        if isLight:
            self.setBrush(QtGui.QBrush(QtGui.QColor(bConfig['lightcolor'])))
        else:
            self.setBrush(QtGui.QBrush(QtGui.QColor(bConfig['darkcolor'])))
        if int(bConfig['squareOutlineWidth']) == 0:
            self.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        else:
            self.setPen(QtGui.QPen(QtGui.QColor(bConfig['outlineColor']),
                                   int(bConfig['squareOutlineWidth'])))


class PieceItem(QtSvg.QGraphicsSvgItem):
    pieceClicked = QtCore.pyqtSignal(int)

    def __init__(self, piece, square):
        self.path = 'resources/pieceSprites/' + userConfig.config['PIECES']['pieceType'] + '/' +\
                    constants.PIECE_TYPE_FILE_DICT[piece.symbol()]
        super(QtSvg.QGraphicsSvgItem, self).__init__(self.path)
        self.piece = piece
        self.square = square
        self.curs = QtGui.QPixmap("resources/cursor.png")
        self.curs2 = QtCore.Qt.ArrowCursor
        self.curs3 = QtCore.Qt.PointingHandCursor
        self.lastButton = QtCore.Qt.NoButton
        # self.setFlag(QtSvg.QGraphicsSvgItem.ItemIsMovable, True)
        self.setAcceptDrops(False)
        self.setAcceptHoverEvents(True)
        # self.setFlag(QtSvg.QGraphicsSvgItem.ItemIsSelectable, False)
        # self.setFlag(QtSvg.QGraphicsSvgItem.ItemIsFocusable, False)

    def __str__(self):
        return '<PieceWidget %s>' % self.piece

    def mousePressEvent(self, event):
        self.lastButton = event.button()
        if event.button() == QtCore.Qt.LeftButton:
            self.pieceClicked.emit(self.square)

    def mouseMoveEvent(self, event):
        if self.piece.color != globals.turn or self.lastButton != QtCore.Qt.LeftButton:
            return
        drag = QtGui.QDrag(self)
        width = int(self.boundingRect().width() * self.scale())
        pieceImg = QtGui.QPixmap(width, width)
        pieceImg.fill(QtGui.QColor(0, 0, 0, 0))
        painter = QtGui.QPainter(pieceImg)
        self.renderer().render(painter)
        painter.end()
        itemData = QtCore.QByteArray()
        mime = QtCore.QMimeData()
        mime.setData('application/x-dnditemdata', itemData)
        self.setOpacity(0.5)
        drag.setPixmap(pieceImg)
        drag.setHotSpot(QtCore.QPoint(width / 2 - 16, width / 2 - 6))
        drag.setDragCursor(self.curs, QtCore.Qt.MoveAction)
        drag.setMimeData(mime)
        drag.exec_(QtCore.Qt.MoveAction)
        self.setOpacity(1)

    def hoverEnterEvent(self, event):
        if self.piece.color == globals.turn:
            self.setCursor(self.curs3)
        else:
            self.setCursor(self.curs2)