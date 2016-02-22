from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableView
import chess


class MoveTreeView(QTableView):
    def __init__(self):
        super().__init__()

    def resizeEvent(self, event):
        self.setColumnWidth(0, self.width() / 2 - 9)
        self.setColumnWidth(1, self.width() / 2 - 9)


class MoveTreeModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
