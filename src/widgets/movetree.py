from PyQt5.QtCore import Qt, QRectF, pyqtSignal
from PyQt5.QtGui import (QPalette, QFontMetrics, QBrush, QColor)
from PyQt5.QtWidgets import QWidget, QMenu, QScrollArea
from chess import pgn
import strings
import userConfig
import constants


class MoveTree(QScrollArea):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        pal = QPalette(self.palette())
        pal.setColor(QPalette.Background, Qt.red)
        self.setPalette(pal)
        self.setAutoFillBackground(True)
        met = QFontMetrics(self.font())
        maxFileWidth = max([met.width(c) for c in strings.FILE_NAMES])
        maxRankWidth = max([met.width(c) for c in strings.RANK_NAMES])
        maxPieceWidth = max([met.width(c) for c in strings.PIECE_SYMBOLS])
        maxEndWidth = max([met.width(c) for c in ['+', '#']])
        maxTakeWidth = met.width('x')
        maxColWidth = maxPieceWidth + maxRankWidth * 2 + maxFileWidth * 2 +\
            maxTakeWidth + maxEndWidth
        self.vScrollBarWidth = 17
        self.setMinimumWidth(maxColWidth * 2 + 17)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.displayContextMenu)

    def resizeEvent(self, event):
        if self.verticalScrollBar().isVisible():
            extra = self.vScrollBarWidth / 2 + 1 + 9
        else:
            extra = 8
        self.setColumnWidth(0, int(self.width() / 2 - extra))
        self.setColumnWidth(1, int(self.width() / 2 - extra))

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        flipAction = menu.addAction("scrollarea1")
        newGameAction = menu.addAction("scrollarea2")
        action = menu.popup(event.globalPos())

    def updateAfterMove(self, gameNode):
        # TODO: implement just tweaking parts of tree that changed
        for v in gameNode.variations:
            if v.is_main_line():
                turn = gameNode.parent.board().turn
                if turn:
                    fullMoveNum = self.gameNode.parent.board().fullmove_number
                    HeaderWidget(self, str(fullMoveNum))
                MoveWidget(self, v)
                if not v.is_end():
                    self.updateAfterMove(v)
            else:
                VariationWidget(self, v)

    def reset(self, newGame):
        for c in self.children():
            c.close()
        self.updateAfterMove(newGame.root())



class HeaderWidget(QWidget):
    """
    The move number or opening title.
    """
    def __init__(self, parent, text, boldText=''):
        super().__init__(parent)
        self.text = text
        self.boldText = boldText
        col = QColor(userConfig.config['MOVETREE']['moveheadercolor'])
        self.setBrush(QBrush(col))

    def paint(self, painter, option, widget):
        painter.setBrush(self.brush())
        painter.drawRect(0, 0, self.width(), self.height())
        met = QFontMetrics(self.font())
        x = (self.width() - met.width(self.text)) / 2.0
        y = (self.height() - met.height(self.text)) / 2.0
        painter.drawText()


class MoveWidget(QWidget):
    """
    The text associated with a move
    from a game state. The gameNode must have
    a parent (ie don't sent the root node).
    """
    def __init__(self, parent, gameNode):
        super().__init__(parent)
        self.gameNode = gameNode
        col = QColor(userConfig.config['MOVETREE']['movetilecolor'])
        self.setBrush(QBrush(col))
        self.setHoverEnabled(True)

    def clicked(self, event):
        self.parent().scrollToMove.emit(self.gameNode)
        print('item', str(self), 'clicked')

    def paint(self, painter, option, widget):
        moveText = self.gameNode.parent.board().san(self.gameNode.move)
        painter.setBrush(self.brush())
        painter.drawRect(0, 0, self.width(), self.height())
        x = constants.MOVE_ITEM_PADDING
        y = int((self.height() - self.font().pointSize()) / 2.0)
        painter.drawText(x, y, moveText)

    def displayContextMenu(self, point):
        menu = QMenu(self)
        menu.addAction("Dummy1")
        menu.addAction("Dummy2")
        menu.popup(self.mapToGlobal(point))

    def hoverEnterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)

    def hoverLeaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)

class VariationWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
