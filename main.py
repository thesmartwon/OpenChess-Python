import sys
from PyQt5.QtWidgets import (QMainWindow, QAction,
                             QApplication, QMessageBox,
                             QDesktopWidget, QFrame,
                             QGraphicsView, QSplitter,
                             QGraphicsScene)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtOpenGL import QGL, QGLFormat, QGLWidget
import userConfig
from widgets.board import OpenGame


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setGeometry(0, 30, 1200, 896 + 43)
        self.game = OpenGame()
        self.view = QGraphicsView(self.game.boardScene, self)
        if QGLFormat.hasOpenGL():
            self.view.setViewport(QGLWidget(QGLFormat(QGL.SampleBuffers)))
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setGeometry(0, 0, 896, 896)
        self.initUI()

    def initUI(self):
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut(userConfig.config['HOTKEYS']['exit'])
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        righttop = QFrame(self)
        rightbot = QFrame(self)

        splitter1 = QSplitter(Qt.Vertical)
        splitter1.addWidget(righttop)
        splitter1.addWidget(rightbot)

        splitter2 = QSplitter(Qt.Horizontal)
        splitter2.addWidget(self.view)
        splitter2.addWidget(splitter1)
        splitter2.setSizes([902, self.width() - 902])

        self.statusBar().showMessage('Ready')

        self.center()
        self.setWindowTitle('Open Chess')
        # TODO: Add an icon
        # self.setWindowIcon(QIcon('web.png'))
        self.setCentralWidget(splitter2)
        self.show()

    def closeEvent(self, event):
        # TODO: Implement saving before close
        # reply = QMessageBox.question(self, 'Message',
        #                              "Are you sure to quit?", QMessageBox.Yes |
        #                              QMessageBox.No, QMessageBox.No)
        # if reply == QMessageBox.Yes:
        #     event.accept()
        # else:
        #     event.ignore()
        userConfig.saveFile('settings.ini')

    def center(self):
        # TODO: Add option for setting startup xy and saving layout in general
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
