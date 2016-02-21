from PyQt5.QtCore import QVariant, pyqtSignal, Qt, QRectF, QPointF, QPoint
from PyQt5.QtGui import QBrush, QPen, QColor, QRadialGradient
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.QtWidgets import (QGraphicsWidget, QGraphicsRectItem,
                             QGraphicsEllipseItem, QGraphicsItem,
                             QGraphicsScene)
import chess
import userConfig
import constants

# TODO: remove all .config['BOARD']['squareWidth'] so as to allow different
# widths
bConfig = userConfig.config['BOARD']


class SquareWidget(QGraphicsWidget):
    """
    Contains a DummySquareItem, PieceItem and possibly other
    effect items.
    """
    Selected, LastMove, ValidMove, ValidMoveHover, \
        InvalidMoveHover, CheckSquare = range(6)
    pieceReleased = pyqtSignal(int)
    invalidDrop = pyqtSignal()

    def __init__(self, square, width, height):
        super().__init__()
        self.square = square
        self.isValidMove = False
        self.isOccupied = False
        self.isLight = bool(chess.BB_SQUARES[int(square)] &
                            chess.BB_LIGHT_SQUARES)
        self.setGeometry(0, 0, width, height)
        self.SquareWidget = DummySquareItem(self.isLight)
        self.SquareWidget.setRect(self.rect())
        self.SquareWidget.setZValue(0)
        self.SquareWidget.setParentItem(self)
        # graphicEffectItems are QGraphicsItems
        self.graphicEffectItems = []
        self.pieceItem = None
        self.deleteScene = QGraphicsScene()
        self.setAcceptHoverEvents(True)

    def countItem(self, itemType):
        count = 0
        for e in self.graphicEffectItems:
            if e.data(0) == itemType:
                count += 1
        return count

    def clearEffectItems(self):
        for i in range(len(self.graphicEffectItems)):
            self.graphicEffectItems[i].setParentItem(None)
            self.deleteScene.addItem(self.graphicEffectItems[i])
            self.deleteScene.clear()
            self.graphicEffectItems[i] = None
        self.graphicEffectItems.clear()

    def removeEffectItem(self, itemType):
        for g in self.graphicEffectItems:
            assert(g is not None)
            if g.data(0) == itemType:
                g.setParentItem(None)
                self.deleteScene.addItem(g)
                self.deleteScene.clear()
                self.graphicEffectItems.remove(g)
                return

    def addEffectItem(self, itemType):
        if self.countItem(itemType) > 0:
            print('trying to add', itemType, 'when it already is there')
            return
        effectItem = None
        squareBounds = self.boundingRect()
        if itemType in [SquareWidget.Selected, SquareWidget.LastMove,
                        SquareWidget.ValidMoveHover,
                        SquareWidget.InvalidMoveHover]:
            effectItem = QGraphicsRectItem()
            c = QColor(bConfig['selectedColor'])
            c.setAlphaF(float(bConfig['effectsAlpha']))
            if itemType == SquareWidget.LastMove:
                c = QColor(bConfig['lastMoveColor'])
                c.setAlphaF(float(bConfig['effectsAlpha']))
            elif itemType == SquareWidget.ValidMoveHover:
                c = QColor(bConfig['hoverColor'])
                c.setAlphaF(float(bConfig['effectsAlpha']))
            elif itemType == SquareWidget.InvalidMoveHover:
                c = QColor(bConfig['invalidHoverColor'])
                c.setAlphaF(float(bConfig['weakEffectsAlpha']))
            effectItem.setBrush(QBrush(c))
            effectItem.setPen(QPen(Qt.NoPen))
            effectItem.setRect(squareBounds)
        elif itemType == SquareWidget.ValidMove:
            if self.isOccupied:
                if self.isLight:
                    brush = QBrush(QColor(bConfig['lightcolor']))
                    effectItem = TakePieceGraphicsItem(brush, squareBounds)
                else:
                    brush = QBrush(QColor(bConfig['darkcolor']))
                    effectItem = TakePieceGraphicsItem(brush, squareBounds)
            else:
                effectItem = QGraphicsEllipseItem()
                c = QColor(bConfig['selectedColor'])
                c.setAlphaF(float(bConfig['effectsAlpha']))
                effectItem.setBrush(QBrush(c))
                effectItem.setPen(QPen(Qt.NoPen))
                width = squareBounds.width()
                effectItem.setRect(width * .75 / 2, width * .75 / 2,
                                   width * .25, width * .25)

        elif itemType == SquareWidget.CheckSquare:
            if self.isLight:
                brush = QBrush(QColor(bConfig['lightcolor']))
                effectItem = InCheckGraphicsItem(brush, squareBounds)
            else:
                brush = QBrush(QColor(bConfig['darkcolor']))
                effectItem = InCheckGraphicsItem(brush, squareBounds)

        if effectItem is not None:
            effectItem.setData(0, QVariant(itemType))
            effectItem.setZValue(1)
            effectItem.setParentItem(self)
            self.graphicEffectItems.append(effectItem)
        else:
            print('tried to add an invalid effect item', itemType)

    def addPiece(self, piece):
        piece.square = self.square
        piece.setParentItem(self)
        piece.setZValue(5)
        self.pieceItem = piece
        self.isOccupied = True

    def removePiece(self, delete=False):
        if self.pieceItem is not None:
            self.pieceItem.setParentItem(None)
            if delete:
                self.deleteScene.addItem(self.pieceItem)
                self.deleteScene.clear()
            self.pieceItem = None
            self.isOccupied = False

    def hoverEnterEvent(self, event):
        if (self.isValidMove and
                self.countItem(SquareWidget.ValidMoveHover) == 0):
            self.removeEffectItem(SquareWidget.ValidMove)
            self.addEffectItem(SquareWidget.ValidMoveHover)

    def hoverLeaveEvent(self, event):
        if self.isValidMove:
            self.removeEffectItem(SquareWidget.ValidMoveHover)
            self.addEffectItem(SquareWidget.ValidMove)

    def mousePressEvent(self, event):
        if self.isValidMove:
            self.pieceReleased.emit(self.square)

    def dragEnterEvent(self, event):
        if (self.isValidMove and
                self.countItem(SquareWidget.ValidMoveHover) == 0):
            self.addEffectItem(SquareWidget.ValidMoveHover)
        elif self.countItem(SquareWidget.InvalidMoveHover) == 0:
            self.addEffectItem(SquareWidget.InvalidMoveHover)

    def dragLeaveEvent(self, event):
        if self.isValidMove:
            self.removeEffectItem(SquareWidget.ValidMoveHover)
        else:
            self.removeEffectItem(SquareWidget.InvalidMoveHover)

    def mouseReleaseEvent(self, event):
        if self.isValidMove:
            self.pieceReleased.emit(self.square)
        else:
            fix_check_after = self.countItem(SquareWidget.CheckSquare) != 0
            self.clearEffectItems()
            if fix_check_after:
                self.addEffectItem(SquareWidget.CheckSquare)
            self.invalidDrop.emit()


class TakePieceGraphicsItem(QGraphicsItem):
    def __init__(self, brush, rect):
        super().__init__()
        self.rect = QRectF(rect)
        self.brush = brush

    def boundingRect(self):
        return self.rect

    def paint(self, QPainter, QStyleOptionGraphicsItem, QWidget_widget=None):
        QPainter.setClipRect(self.rect)
        col = QColor(bConfig['selectedColor'])
        col.setAlphaF(float(bConfig['effectsAlpha']))
        QPainter.setBrush(QBrush(col))
        QPainter.setPen(QPen(Qt.NoPen))
        width = self.boundingRect().width()
        QPainter.drawRect(0, 0, width, width)
        QPainter.setBrush(self.brush)
        p = QPoint(width / 2, width / 2)
        QPainter.drawEllipse(p, width / 2 + 8, width / 2 + 8)


class InCheckGraphicsItem(QGraphicsItem):
    def __init__(self, brush, rect):
        super().__init__()
        self.rect = QRectF(rect)
        self.brush = brush

    def boundingRect(self):
        return self.rect

    def paint(self, QPainter, QStyleOptionGraphicsItem, QWidget_widget=None):
        QPainter.setClipRect(self.rect)
        center = QPointF(self.rect.width() / 2, self.rect.height() / 2)
        focalPoint = center
        grad = QRadialGradient(center, float(self.rect.width() * 0.58929),
                               focalPoint)
        col = QColor(bConfig['checkColor'])
        grad.setColorAt(0, col)
        grad.setColorAt(1, self.brush.color())
        col = QColor(bConfig['checkColor'])
        col.setAlphaF(float(bConfig['effectsAlpha']))
        QPainter.setBrush(QBrush(col))
        QPainter.setPen(QPen(Qt.NoPen))
        QPainter.fillRect(self.rect,  grad)


class DummySquareItem(QGraphicsRectItem):
    """
    Just a visual dummy rectangle that is dark or light.
    """
    def __init__(self, isLight):
        super().__init__()
        if isLight:
            self.setBrush(QBrush(QColor(bConfig['lightcolor'])))
        else:
            self.setBrush(QBrush(QColor(bConfig['darkcolor'])))
        if int(bConfig['squareOutlineWidth']) == 0:
            self.setPen(QPen(Qt.NoPen))
        else:
            self.setPen(QPen(QColor(bConfig['outlineColor']),
                        int(bConfig['squareOutlineWidth'])))


class PieceItem(QGraphicsSvgItem):
    pieceClicked = pyqtSignal(int)
    pieceDragStarting = pyqtSignal(int)
    pieceDragStopping = pyqtSignal(int, QPointF)

    def __init__(self, piece):
        self.path = constants.RESOURCES_PATH + '\\pieceSprites\\' + \
                    userConfig.config['PIECES']['pieceType'] + '\\' + \
                    constants.PIECE_TYPE_FILE_DICT[piece.symbol()]
        super(QGraphicsSvgItem, self).__init__(self.path)
        self.piece = piece
        self.square = -1
        self.isStartingDrag = False
        self.setAcceptHoverEvents(True)

    def __str__(self):
        return '<PieceWidget %s>' % self.piece

    def mousePressEvent(self, event):
        gameTurn = constants.GAME_STATE.turn
        if (self.piece.color == gameTurn and
                event.button() == Qt.LeftButton):
            self.pieceClicked.emit(self.square)

    def mouseMoveEvent(self, event):
        gameTurn = constants.GAME_STATE.turn
        if (self.piece.color == gameTurn and
                bool(event.buttons() & Qt.LeftButton)):
            newPos = event.scenePos() - QPointF(self.boundingRect().width() +
                                                constants.PIECE_PADDING_RIGHT,
                                                self.boundingRect().height() +
                                                constants.PIECE_PADDING_BOT)
            self.setPos(newPos)
            if not self.isStartingDrag:
                self.isStartingDrag = True
                self.pieceDragStarting.emit(self.square)

    #     # drag = QDrag(self)
    #     # width = int(self.boundingRect().width() * self.scale())
    #
    #     # itemData = QByteArray()
    #     # mime = QMimeData()
    #     # mime.setData('application/x-dnditemdata', itemData)
    #     # self.setOpacity(0.5)
    #     # drag.setPixmap(pieceImg)
    #     # drag.setHotSpot(QPoint(width / 2 - 16, width / 2 - 6))
    #     # drag.setDragCursor(self.customCursor, Qt.MoveAction)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.isStartingDrag:
                self.isStartingDrag = False
                self.setPos(QPoint(0, 0))
                self.pieceDragStopping.emit(self.square,
                                            QPointF(event.scenePos()))

    def hoverEnterEvent(self, event):
        gameTurn = constants.GAME_STATE.turn
        if self.piece.color == gameTurn:
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
