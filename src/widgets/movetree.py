from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import (QStandardItemModel, QStandardItem, QPalette,
                         QFontMetrics)
from PyQt5.QtWidgets import QTableView, QMenu
import strings


class MoveTreeView(QTableView):
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
        maxFile = max([met.width(c) for c in strings.FILE_NAMES])
        maxRank = max([met.width(c) for c in strings.RANK_NAMES])
        maxPiece = max([met.width(c) for c in strings.PIECE_SYMBOLS])
        maxEnd = max([met.width(c) for c in ['+', '#']])
        maxTake = met.width('x')
        maxColWidth = maxPiece + maxRank * 2 + maxFile * 2 + maxTake + maxEnd
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


class MoveTreeModel(QStandardItemModel):
    moveItemClicked = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setHorizontalHeaderLabels([strings.COLOR_FIRST,
                                        strings.COLOR_SECOND])

    def updateAfterMove(self, move, fullMoveNum, turn, moveSan):
        newItem = MoveTreeItem(fullMoveNum * 2 + int(not turn) - 2)
        newItem.setText(moveSan)
        print('setting', fullMoveNum - 1, ',', int(not turn))
        self.setItem(fullMoveNum - 1, int(not turn), newItem)

    def reset(self):
        self.clear()
        self.setHorizontalHeaderLabels([strings.COLOR_FIRST,
                                        strings.COLOR_SECOND])

    def eraseAfterPly(self, plyNumber):
        rowNumber = int(plyNumber / 2) + 1
        numToErase = self.rowCount() - int(plyNumber / 2) - 1
        self.removeRows(rowNumber, numToErase)
        if plyNumber % 2 == 0:
            self.setItem(int(plyNumber) / 2, 1, QStandardItem())

    def itemClicked(self, current):
        if current.isValid():
            moveItem = self.itemFromIndex(current)
            # current.model().itemFromIndex(current)
            if type(moveItem) == MoveTreeItem:
                self.moveItemClicked.emit(moveItem.plyNumber)


class MoveTreeItem(QStandardItem):
    def __init__(self, plyNumber):
        super().__init__()
        self.plyNumber = plyNumber

    def clicked(self, event):
        print('yea')
