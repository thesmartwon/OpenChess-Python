from PyQt5.QtCore import QVariant, pyqtSignal, Qt, QRect, QRectF, QPointF, QByteArray, QMimeData, QPoint
from PyQt5.QtGui import QBrush, QPen, QColor, QRadialGradient, QPixmap, QDrag, QPainter
from PyQt5.QtSvg import QGraphicsSvgItem
from PyQt5.QtWidgets import (QGraphicsRectItem, QGraphicsWidget,
    QGraphicsEllipseItem, QGraphicsItem, QGraphicsScene)
import chess
import userConfig
import constants
import globals

# TODO: remove all .config['BOARD']['squareWidth'] so as to allow different widths
bConfig = userConfig.config['BOARD']


class SquareWidget(QGraphicsWidget):
    """
    Contains a SquareItem and PieceItem and possibly other effects added to it.
    """
    Selected, LastMove, ValidMove, ValidMoveHover, InvalidMoveHover, CheckSquare = range(6)
    pieceReleased = pyqtSignal(int)
    invalidDrop = pyqtSignal()

    def __init__(self, square):
        super().__init__()
        self.square = square
        self.isValidMove = False
        self.isSelected = False
        self.isOccupied = False
        self.isLight = bool(chess.BB_SQUARES[int(square)] & chess.BB_LIGHT_SQUARES)
        self.setGeometry(0, 0, int(bConfig['squareWidth']), int(bConfig['squareWidth']))
        self.squareItem = SquareItem(self.isLight)
        self.squareItem.setRect(self.geometry())
        self.squareItem.setZValue(0)
        self.squareItem.setParentItem(self)
        # graphicEffectItems are QGraphicsItems
        self.graphicEffectItems = []
        self.pieceItem = None
        self.deleteScene = QGraphicsScene()
        self.setAcceptDrops(True)
        self.setAcceptHoverEvents(True)

    def countItem(self, item):
        count = 0
        for e in self.graphicEffectItems:
            if e.data(0) == item:
                count += 1
        return count

    def clearEffectItems(self):
        for i in range(len(self.graphicEffectItems)):
            self.graphicEffectItems[i].setParentItem(None)
            self.deleteScene.addItem(self.graphicEffectItems[i])
            self.deleteScene.clear()
            self.graphicEffectItems[i] = None
        self.graphicEffectItems.clear()

    def removeEffectItem(self, type):
        for i in range(len(self.graphicEffectItems)):
            if self.graphicEffectItems[i].data(0) == type:
                self.graphicEffectItems[i].setParentItem(None)
                self.deleteScene.addItem(self.graphicEffectItems[i])
                self.deleteScene.clear()
                self.graphicEffectItems[i] = None
                del self.graphicEffectItems[i]
                i -= 1

    def addEffectItem(self, type):
        if len(self.graphicEffectItems) > 0:
            pass
        effectItem = None
        width = self.boundingRect().width()
        if type == SquareWidget.Selected:
            effectItem = QGraphicsRectItem()
            c = QColor(bConfig['selectedColor'])
            c.setAlphaF(float(bConfig['effectsAlpha']))
            effectItem.setBrush(QBrush(c))
            effectItem.setPen(QPen(Qt.NoPen))
            effectItem.setRect(0, 0, width, width)
        elif type == SquareWidget.LastMove:
            effectItem = QGraphicsRectItem()
            c = QColor(bConfig['lastMoveColor'])
            c.setAlphaF(float(bConfig['effectsAlpha']))
            effectItem.setBrush(QBrush(c))
            effectItem.setPen(QPen(Qt.NoPen))
            effectItem.setRect(0, 0, width, width)
        elif type == SquareWidget.ValidMove:
            if self.isOccupied:
                if self.isLight:
                    effectItem = TakePieceGraphicsItem(QBrush(QColor(bConfig['lightcolor'])),
                                                       QRect(0, 0, width, width))
                else:
                    effectItem = TakePieceGraphicsItem(QBrush(QColor(bConfig['darkcolor'])),
                                                       QRect(0, 0, width, width))
            else:
                effectItem = QGraphicsEllipseItem()
                c = QColor(bConfig['selectedColor'])
                c.setAlphaF(float(bConfig['effectsAlpha']))
                effectItem.setBrush(QBrush(c))
                effectItem.setPen(QPen(Qt.NoPen))
                effectItem.setRect(width * .75 / 2, width * .75 / 2, width * .25, width * .25)
        elif type == SquareWidget.ValidMoveHover:
            effectItem = QGraphicsRectItem()
            c = QColor(bConfig['hoverColor'])
            c.setAlphaF(float(bConfig['effectsAlpha']))
            effectItem.setBrush(QBrush(c))
            effectItem.setPen(QPen(Qt.NoPen))
            effectItem.setRect(0, 0, width, width)
        elif type == SquareWidget.InvalidMoveHover:
            effectItem = QGraphicsRectItem()
            c = QColor(bConfig['invalidHoverColor'])
            c.setAlphaF(float(bConfig['weakEffectsAlpha']))
            effectItem.setBrush(QBrush(c))
            effectItem.setPen(QPen(Qt.NoPen))
            effectItem.setRect(0, 0, width, width)
        elif type == SquareWidget.CheckSquare:
            customRect = QRect(0, 0, width, width)
            if self.isLight:
                effectItem = InCheckGraphicsItem(QBrush(QColor(bConfig['lightcolor'])),
                                                      customRect)
            else:
                effectItem = InCheckGraphicsItem(QBrush(QColor(bConfig['darkcolor'])),
                                                      customRect)
        if effectItem is not None:
            effectItem.setData(0, QVariant(type))
            effectItem.setZValue(1)
            effectItem.setParentItem(self)
            self.graphicEffectItems.append(effectItem)

    def addPiece(self, piece):
        piece.setParentItem(self)
        piece.setZValue(2)
        self.pieceItem = piece
        self.isOccupied = True

    def removePiece(self):
        if self.pieceItem is not None:
            self.pieceItem.setParent(None)
            self.pieceItem.deleteLater()
            self.pieceItem = None
            self.isOccupied = False

    def dropEvent(self, event):
        if self.isValidMove and event.mimeData().hasFormat('application/x-dnditemdata'):
            self.pieceReleased.emit(self.square)
        else:
            fix_check_after = False
            if self.countItem(SquareWidget.CheckSquare) != 0:
                fix_check_after = True
            self.clearEffectItems()
            if fix_check_after:
                self.addEffectItem(SquareWidget.CheckSquare)
            self.invalidDrop.emit()

    def hoverEnterEvent(self, event):
        if self.isValidMove and self.countItem(SquareWidget.ValidMoveHover) == 0:
            self.removeEffectItem(SquareWidget.ValidMove)
            self.addEffectItem(SquareWidget.ValidMoveHover)

    def hoverLeaveEvent(self, event):
        if self.isValidMove:
            self.removeEffectItem(SquareWidget.ValidMoveHover)
            self.addEffectItem(SquareWidget.ValidMove)

    def dragEnterEvent(self, event):
        if self.isValidMove and self.countItem(SquareWidget.InvalidMoveHover) == 0:
            self.removeEffectItem(SquareWidget.ValidMove)
            self.addEffectItem(SquareWidget.ValidMoveHover)
        elif self.countItem(SquareWidget.InvalidMoveHover) == 0 and not self.isSelected:
            self.addEffectItem(SquareWidget.InvalidMoveHover)

    def dragLeaveEvent(self, event):
        if self.isValidMove:
            self.removeEffectItem(SquareWidget.ValidMoveHover)
            self.addEffectItem(SquareWidget.ValidMove)
        else:
            self.removeEffectItem(SquareWidget.InvalidMoveHover)

    def mousePressEvent(self, event):
        if self.isValidMove:
            self.pieceReleased.emit(self.square)


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
        grad = QRadialGradient(center, float(self.rect.width() * 0.58929), focalPoint)
        col = QColor(bConfig['checkColor'])
        grad.setColorAt(0, col)
        grad.setColorAt(1, self.brush.color())
        col = QColor(bConfig['checkColor'])
        col.setAlphaF(float(bConfig['effectsAlpha']))
        QPainter.setBrush(QBrush(col))
        QPainter.setPen(QPen(Qt.NoPen))
        QPainter.fillRect(self.rect,  grad)


class SquareItem(QGraphicsRectItem):
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

    def __init__(self, piece, square):
        self.path = 'resources/pieceSprites/' + userConfig.config['PIECES']['pieceType'] + '/' +\
                    constants.PIECE_TYPE_FILE_DICT[piece.symbol()]
        super(QGraphicsSvgItem, self).__init__(self.path)
        self.piece = piece
        self.square = square
        self.curs = QPixmap("resources/cursor.png")
        self.curs2 = Qt.ArrowCursor
        self.curs3 = Qt.PointingHandCursor
        self.lastButton = Qt.NoButton
        # self.setFlag(QGraphicsSvgItem.ItemIsMovable, True)
        self.setAcceptDrops(False)
        self.setAcceptHoverEvents(True)
        # self.setFlag(QGraphicsSvgItem.ItemIsSelectable, False)
        # self.setFlag(QGraphicsSvgItem.ItemIsFocusable, False)

    def __str__(self):
        return '<PieceWidget %s>' % self.piece

    def mousePressEvent(self, event):
        self.lastButton = event.button()
        if event.button() == Qt.LeftButton:
            self.pieceClicked.emit(self.square)

    def mouseMoveEvent(self, event):
        if self.piece.color != globals.turn or self.lastButton != Qt.LeftButton:
            return
        drag = QDrag(self)
        width = int(self.boundingRect().width() * self.scale())
        pieceImg = QPixmap(width, width)
        pieceImg.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pieceImg)
        self.renderer().render(painter)
        painter.end()
        itemData = QByteArray()
        mime = QMimeData()
        mime.setData('application/x-dnditemdata', itemData)
        self.setOpacity(0.5)
        drag.setPixmap(pieceImg)
        drag.setHotSpot(QPoint(width / 2 - 16, width / 2 - 6))
        drag.setDragCursor(self.curs, Qt.MoveAction)
        drag.setMimeData(mime)
        drag.exec_(Qt.MoveAction)
        self.setOpacity(1)

    def hoverEnterEvent(self, event):
        if self.piece.color == globals.turn:
            self.setCursor(self.curs3)
        else:
            self.setCursor(self.curs2)
