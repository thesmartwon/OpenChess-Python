from PyQt5.QtCore import QVariant, pyqtSignal, Qt, QRectF, QPointF, QPoint
from PyQt5.QtGui import QBrush, QPen, QColor, QRadialGradient
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.QtWidgets import (QGraphicsWidget, QGraphicsRectItem,
                             QGraphicsEllipseItem, QGraphicsItem,
                             QGraphicsScene)
import chess
import userConfig
import constants

bConfig = userConfig.config['BOARD']


# TODO: Performance: make QGraphicsItem and use event filters.
class SquareWidget(QGraphicsWidget):
    """
    Contains a DummySquareItem, PieceItem and possibly other
    effect items.
    """
    Selected, LastMove, ValidMove, ValidMoveHover, \
        InvalidMoveHover, CheckSquare = range(QGraphicsItem.UserType + 20,
                                              QGraphicsItem.UserType + 26)
    pieceReleased = pyqtSignal(int)
    invalidDrop = pyqtSignal()

    def __init__(self, square, squareWidth):
        super().__init__()
        self.square = square
        file = 7 - int(square / 8)
        rank = square % 8
        self.setGeometry(squareWidth * rank, squareWidth * file,
                         squareWidth, squareWidth)
        self.isValidMove = False
        self.isOccupied = False
        self.isLight = bool(chess.BB_SQUARES[int(square)] &
                            chess.BB_LIGHT_SQUARES)
        self.dummyBack = DummySquareItem(self, self.rect(), self.isLight)
        self.graphicEffectItems = []
        self.pieceItem = None
        self.setAcceptHoverEvents(True)

    def boundingRect(self):
        return QRectF(self.pos().x(), self.pos().y(),
                      self.geometry().width(), self.geometry().width())

    def countItem(self, itemType):
        count = 0
        for e in self.graphicEffectItems:
            if e.data(0) == itemType:
                count += 1
        return count

    def clearEffectItems(self):
        for i in range(len(self.graphicEffectItems)):
            self.graphicEffectItems[i].setParentItem(None)
            self.scene().removeItem(self.graphicEffectItems[i])
            self.graphicEffectItems[i] = None
        self.graphicEffectItems.clear()

    def removeEffectItem(self, itemType):
        for g in self.graphicEffectItems:
            assert(g is not None)
            if g.data(0) == itemType:
                g.setParentItem(None)
                self.scene().removeItem(g)
                self.graphicEffectItems.remove(g)
                return

    # Helper method to addEffectItem
    def createEffectItem(self, itemType):
        squareBounds = QRectF(0, 0, self.geometry().width(),
                              self.geometry().width())
        if itemType == SquareWidget.Selected:
            return SelectedGraphicsItem(squareBounds)
        elif itemType == SquareWidget.LastMove:
            return LastMoveGraphicsItem(squareBounds)
        elif itemType == SquareWidget.ValidMoveHover:
            return ValidMoveHoverGraphicsItem(squareBounds)
        elif itemType == SquareWidget.InvalidMoveHover:
            return InvalidMoveHoverGraphicsItem(squareBounds)
        elif itemType == SquareWidget.ValidMove:
            if self.isOccupied:
                if self.isLight:
                    brush = QBrush(QColor(bConfig['lightcolor']))
                    return TakePieceGraphicsItem(brush, squareBounds)
                else:
                    brush = QBrush(QColor(bConfig['darkcolor']))
                    return TakePieceGraphicsItem(brush, squareBounds)
            else:
                return ValidMoveGraphicsItem(squareBounds)
        elif itemType == SquareWidget.CheckSquare:
            if self.isLight:
                brush = QBrush(QColor(bConfig['lightcolor']))
                return InCheckGraphicsItem(brush, squareBounds)
            else:
                brush = QBrush(QColor(bConfig['darkcolor']))
                return InCheckGraphicsItem(brush, squareBounds)
        return None

    def addEffectItem(self, itemType):
        if self.countItem(itemType) > 0:
            print('trying to add', itemType, 'when it already is there')
            return
        effectItem = self.createEffectItem(itemType)
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
        elif (event is None and
                self.countItem(SquareWidget.InvalidMoveHover) == 0):
            self.addEffectItem(SquareWidget.InvalidMoveHover)

    def hoverLeaveEvent(self, event):
        if self.isValidMove:
            self.removeEffectItem(SquareWidget.ValidMoveHover)
            if self.countItem(SquareWidget.ValidMove) == 0:
                self.addEffectItem(SquareWidget.ValidMove)
        elif event is None:
            self.removeEffectItem(SquareWidget.InvalidMoveHover)

    def mousePressEvent(self, event):
        if self.isValidMove:
            self.pieceReleased.emit(self.square)


class PieceItem(QGraphicsSvgItem):
    pieceClicked = pyqtSignal(int)
    pieceDragStarting = pyqtSignal(int)
    pieceDragHappening = pyqtSignal(QPointF)
    pieceDragStopping = pyqtSignal(int, QPointF)

    def __init__(self, piece):
        self.path = constants.RESOURCES_PATH + '/pieceSprites/' + \
                    userConfig.config['PIECES']['pieceType'] + '/' + \
                    constants.PIECE_TYPE_FILE_DICT[piece.symbol()]
        super(QGraphicsSvgItem, self).__init__(self.path)
        self.piece = piece
        self.square = -1
        self.isStartingDrag = False
        self.setAcceptHoverEvents(True)

    def mousePressEvent(self, event):
        if (event.button() == Qt.LeftButton):
            self.pieceClicked.emit(self.square)

    def mouseMoveEvent(self, event):
        gameTurn = constants.GAME_STATE.turn
        if (self.piece.color == gameTurn and
                bool(event.buttons() & Qt.LeftButton)):
            hotSpot = QPointF(self.boundingRect().width() +
                              constants.PIECE_PADDING_RIGHT,
                              self.boundingRect().height() +
                              constants.PIECE_PADDING_BOT)
            newPos = event.scenePos() - hotSpot
            self.setPos(newPos)
            if not self.isStartingDrag:
                self.isStartingDrag = True
                self.pieceDragStarting.emit(self.square)
            else:
                self.pieceDragHappening.emit(QPointF(event.scenePos()))

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


class DummySquareItem(QGraphicsRectItem):
    """
    Just a visual dummy rectangle that is dark or light.
    """
    def __init__(self, parent, rect, isLight):
        super().__init__(parent)
        self.setRect(rect)
        if isLight:
            self.setBrush(QBrush(QColor(bConfig['lightcolor'])))
        else:
            self.setBrush(QBrush(QColor(bConfig['darkcolor'])))
        if int(bConfig['squareOutlineWidth']) == 0:
            self.setPen(QPen(Qt.NoPen))
        else:
            self.setPen(QPen(QColor(bConfig['outlineColor']),
                        int(bConfig['squareOutlineWidth'])))
        self.setZValue(0)


class ValidMoveGraphicsItem(QGraphicsEllipseItem):
    def __init__(self, squareBounds):
        super().__init__()
        c = QColor(bConfig['selectedColor'])
        c.setAlphaF(float(bConfig['effectsAlpha']))
        self.setBrush(QBrush(c))
        self.setPen(QPen(Qt.NoPen))
        width = squareBounds.width()
        self.setRect(width * .75 / 2, width * .75 / 2,
                     width * .25, width * .25)


class InvalidMoveHoverGraphicsItem(QGraphicsRectItem):
    def __init__(self, squareBounds):
        super().__init__()
        c = QColor(bConfig['invalidHoverColor'])
        c.setAlphaF(float(bConfig['weakEffectsAlpha']))
        self.setBrush(QBrush(c))
        self.setPen(QPen(Qt.NoPen))
        self.setRect(squareBounds)


class ValidMoveHoverGraphicsItem(QGraphicsRectItem):
    def __init__(self, squareBounds):
        super().__init__()
        c = QColor(bConfig['hoverColor'])
        c.setAlphaF(float(bConfig['effectsAlpha']))
        self.setBrush(QBrush(c))
        self.setPen(QPen(Qt.NoPen))
        self.setRect(squareBounds)


class SelectedGraphicsItem(QGraphicsRectItem):
    def __init__(self, squareBounds):
        super().__init__()
        c = QColor(bConfig['selectedColor'])
        c.setAlphaF(float(bConfig['effectsAlpha']))
        self.setBrush(QBrush(c))
        self.setPen(QPen(Qt.NoPen))
        self.setRect(squareBounds)


class LastMoveGraphicsItem(QGraphicsRectItem):
    def __init__(self, squareBounds):
        super().__init__()
        c = QColor(bConfig['lastMoveColor'])
        c.setAlphaF(float(bConfig['effectsAlpha']))
        self.setBrush(QBrush(c))
        self.setPen(QPen(Qt.NoPen))
        self.setRect(squareBounds)


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
