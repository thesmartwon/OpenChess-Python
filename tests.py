import sys
from PyQt5.QtWidgets import (QMainWindow, QApplication,
    QGraphicsView, QGraphicsScene, QGraphicsWidget, QGraphicsRectItem)
from PyQt5.QtCore import (QMimeData, Qt, QByteArray, QCoreApplication,
    QEvent, QPoint)
from PyQt5.QtGui import QBrush, QColor, QDrag, QPen, QKeyEvent


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scene = CustomScene()
        self.view = QGraphicsView(self.scene, self)
        self.setGeometry(100, 100, 600, 600)
        self.view.setGeometry(0, 0, 500, 500)
        self.show()


class CustomScene(QGraphicsScene):
    def __init__(self):
        super().__init__()
        self.customWidgets = []
        for i in range(5):
            newItem = CustomDragWidget()
            self.addItem(newItem)
            self.customWidgets.append(newItem)
            newItem.setGeometry(i * 50, i * 50, 50, 50)

    def dragLeaveEvent(self, event):
        # Work your magic here. I've tried the following:
        QCoreApplication.sendEvent(self, QKeyEvent(QEvent.KeyPress, Qt.Key_Escape, Qt.NoModifier))


class CustomDragWidget(QGraphicsWidget):
    def __init__(self,):
        super().__init__()
        self.squareItem = QGraphicsRectItem()
        self.squareItem.setBrush(QBrush(QColor(Qt.blue)))
        self.squareItem.setPen(QPen(QColor(Qt.black), 2))
        self.squareItem.setRect(0, 0, 50, 50)
        self.squareItem.setParentItem(self)
        self.setAcceptDrops(True)

    def mousePressEvent(self, event):
        mime = QMimeData()
        itemData = QByteArray()
        mime.setData('application/x-dnditemdata', itemData)
        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.MoveAction)

    def dropEvent(self, event):
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())