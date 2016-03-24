from PyQt5.QtCore import Qt, QRectF, pyqtSignal
from PyQt5.QtGui import (QPalette, QFontMetrics, QBrush, QColor)
from PyQt5.QtWidgets import QWidget, QMenu, QScrollArea, QLabel, QGridLayout
import strings
import userConfig
import constants


class MoveTreeWidget(QScrollArea):
    def __init__(self, parent, gameRoot):
        super().__init__(parent)
        self.gameRoot = gameRoot
        self.initUI()

    def initUI(self):
        pal = QPalette(self.palette())
        pal.setColor(QPalette.Background, Qt.blue)
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

        layout = QGridLayout()
        self.header = HeaderWidget(self, 'A00', " King's Pawn")
        #                             r  c rspan cspan
        layout.addWidget(self.header, 0, 0, 3, 1)
        #self.header2 = HeaderWidget(self, '1.')
        #layout.addWidget(self.header2, 4, 4, 1, 1)
        # self.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.displayContextMenu)

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


class HeaderWidget(QLabel):
    """
    The move number or opening title.
    """
    def __init__(self, parent, text, boldText=''):
        super().__init__(parent)
        pal = self.palette()
        col = QColor(userConfig.config['MOVETREE']['moveheadercolor'])
        pal.setColor(QPalette.Background, col)
        self.setAutoFillBackground(True)
        self.setPalette(pal)
        myText = "<span style='font-size:18pt; font-weight:600; color:" +\
                 "#aa0000;'>" + text + "</span><span style='font-size:10pt;" +\
                 "font-weight:600; color:#00aa00;'>" + boldText + "</span>"
        self.setText(myText)


class MoveWidget(QLabel):
    """
    The text associated with a move
    from a game state. The gameNode must have
    a parent (ie don't sent the root node).
    """
    def __init__(self, parent, gameNode, isVariation=False):
        super().__init__(parent)
        self.gameNode = gameNode
        pal = self.palette()
        col = QColor(userConfig.config['MOVETREE']['movetilecolor'])
        pal.setColor(QPalette.Background, col)
        self.setAutoFillBackground(True)
        self.setPalette(pal)

        moveText = self.gameNode.parent.board().san(self.gameNode.move)
        self.setText(moveText)

        self.setHoverEnabled(True)

    def clicked(self, event):
        self.parent().scrollToMove.emit(self.gameNode)
        print('item', str(self), 'clicked')

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
