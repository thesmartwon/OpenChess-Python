# http://zetcode.com/gui/pyqt5/firstprograms/
import sys
from PyQt5.QtWidgets import QWidget, QMessageBox, QPushButton, QApplication, QToolTip, QDesktopWidget
from PyQt5.QtGui import QIcon, QFont

class Example(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        QToolTip.setFont(QFont('SansSerif', 10))
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Message box')
        self.setWindowIcon(QIcon('web.png'))
        self.setToolTip('This is a <b>QWidget</b> widget')

        qbtn = QPushButton('Quit', self)
        qbtn.setToolTip('This is a <b>QWidget</b> widget')
        qbtn.resize(qbtn.sizeHint())
        qbtn.move(50, 50)
        qbtn.clicked.connect(self.closeEvent)

        self.center()
        self.show()

    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())
