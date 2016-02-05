from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableView
import chess


class MoveTreeScene(QTableView):
    def __init__(self):
        super().__init__()


class MoveTreeModel(QStandardItemModel):
    def __init__(self):
        super().__init__()
