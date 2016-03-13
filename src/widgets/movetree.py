from PyQt5.QtGui import (QStandardItemModel, QStandardItem, QPalette,
                         QFontMetrics, QFont)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableView
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

    def resizeEvent(self, event):
        if self.verticalScrollBar().isVisible():
            extra = self.vScrollBarWidth / 2 + 1 + 9
        else:
            extra = 8
        self.setColumnWidth(0, int(self.width() / 2 - extra))
        self.setColumnWidth(1, int(self.width() / 2 - extra))


class MoveTreeModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.setHorizontalHeaderLabels([strings.COLOR_FIRST,
                                        strings.COLOR_SECOND])

    def updateAfterMove(self, move, moveNum, turn, moveSan):
        newItem = MoveTreeItem(move)
        newItem.setText(moveSan)
        self.setItem(int(moveNum / 2), turn, newItem)

    def reset(self):
        self.clear()
        self.setHorizontalHeaderLabels([strings.COLOR_FIRST,
                                        strings.COLOR_SECOND])

    def gotoMove(self, current):
        if current.isValid():
            moveItem = self.itemFromIndex(current)
            print(moveItem, current.model().itemFromIndex(current))
            if type(moveItem) == MoveTreeItem:
                print('going to', moveItem.plyNumber)


class MoveTreeItem(QStandardItem):
    def __init__(self, plyNumber):
        super().__init__()
        self.plyNumber = plyNumber

    def clicked(self, event):
        print('yea')
