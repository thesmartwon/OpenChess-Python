from PyQt5.QtGui import (QStandardItemModel, QStandardItem, QPalette,
                         QFontMetrics, QFont)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableView
import strings


class MoveTreeView(QTableView):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.setModel(model)
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
        maxWidth = maxPiece + maxRank * 2 + maxFile * 2 + maxTake + maxEnd
        self.setMinimumWidth(maxWidth * 2 + 18 +
                             self.verticalScrollBar().width())
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def resizeEvent(self, event):
        self.setColumnWidth(0, self.width() / 2 - 9 -
                            self.verticalScrollBar().width() / 2)
        self.setColumnWidth(1, self.width() / 2 - 9 -
                            self.verticalScrollBar().width() / 2)


class MoveTreeModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.setHorizontalHeaderLabels([strings.COLOR_FIRST,
                                        strings.COLOR_SECOND])
