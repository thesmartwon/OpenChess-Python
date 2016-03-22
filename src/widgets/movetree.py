from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import (QGraphicsView, QGraphicsScene, QPalette,
                         QFontMetrics, QGraphicsItem)
from PyQt5.QtWidgets import QMenu
import strings


class MoveTreeView(QGraphicsView):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.setModel(model)
        self.initUI()

    def initUI(self):
        pal = QPalette(self.palette())
        pal.setColor(QPalette.Background, Qt.red)
        self.setAutoFillBackground(True)
        self.setPalette(pal)
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
        self.customContextMenuRequested.connect(self.displayContextMenu)

    def resizeEvent(self, event):
        if self.verticalScrollBar().isVisible():
            extra = self.vScrollBarWidth / 2 + 1 + 9
        else:
            extra = 8
        self.setColumnWidth(0, int(self.width() / 2 - extra))
        self.setColumnWidth(1, int(self.width() / 2 - extra))

    def displayContextMenu(self, point):
        index = self.indexAt(point)
        if index.isValid():
            # self.model().itemFromIndex(index)
            menu = QMenu(self)
            flipAction = menu.addAction("Flip board")
            newGameAction = menu.addAction("New game")
            action = menu.popup(self.mapToGlobal(point))


class MoveTreeScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.moveItems = []

    def updateAfterMove(self, gameNode):
        # TODO: implement positioning and going through tree
        turn = gameNode.parent.board().turn
        pass

    def reset(self, newGame):
        # TODO: implement
        pass

    def itemClicked(self, current):
        if current.isValid():
            moveItem = self.itemFromIndex(current)
            # current.model().itemFromIndex(current)
            if type(moveItem) == MoveTreeItem:
                self.moveItemClicked.emit(moveItem.plyNumber)


class MoveTreeItem(QGraphicsItem):
    """
    Creates the text associated with a move
    from a game state. The gameNode must have
    a parent (ie don't sent the root node).
    """
    Type = QGraphicsItem.UserType + 11

    def __init__(self, gameNode, width):
        super().__init__()
        fullMoveNum = gameNode.parent.board().fullmove_number
        turn = gameNode.parent.board().turn
        moveSan = gameNode.parent.board().san(gameNode.move)
        if turn:
            self.moveText = str(fullMoveNum)
        else:
            self.moveText = ''
        self.moveText += ' ' + moveSan
        self.width = width

    def clicked(self, event):
        print('item', str(self), 'clicked')

    def type(self):
        return self.Type

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.width)

    def paint(self, painter, option, widget):
        pass
