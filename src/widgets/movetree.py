from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QPalette
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

    def resizeEvent(self, event):
        self.setColumnWidth(0, self.width() / 2 - 9)
        self.setColumnWidth(1, self.width() / 2 - 9)


class MoveTreeModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
        self.setHorizontalHeaderLabels([strings.COLOR_FIRST,
                                        strings.COLOR_SECOND])
