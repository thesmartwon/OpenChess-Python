import sys
from PyQt5.QtWidgets import (QMainWindow, QAction,
                             QApplication, QMessageBox,
                             QDesktopWidget, QFrame,
                             QGraphicsView, QSplitter)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtOpenGL import QGL, QGLFormat, QGLWidget
from game import OpenGame
import userConfig
import constants


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game = OpenGame()
        self.view = QGraphicsView(self.game.boardScene, self)
        if QGLFormat.hasOpenGL():
            self.view.setViewport(QGLWidget(QGLFormat(QGL.SampleBuffers)))
        self.initUI()
        self.setFocusPolicy(Qt.StrongFocus)

    def initUI(self):
        screenGeo = QApplication.desktop().screenGeometry()
        widthDisparity = screenGeo.width() - 1200
        heightDisparity = screenGeo.height() - 939
        if widthDisparity < 0 and widthDisparity < heightDisparity:
            self.setGeometry(0, 0, 1200 + widthDisparity,
                             int(float(939)/1200*(1200+widthDisparity)))
        elif heightDisparity < 0 and heightDisparity < widthDisparity:
            self.setGeometry(0, 0, int(float(1200)/939*(939+heightDisparity)),
                             939 + heightDisparity)
        else:
            self.setGeometry(0, 0, 1200, 939)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setGeometry(0, 0, 896, 896)
        self.game.boardScene.setSceneRect(0, 0, 896, 896)

        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut(userConfig.config['HOTKEYS']['exit'])
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

        righttop = self.game.moveTreeScene
        self.game.moveTreeScene.setColumnWidth(0, (self.width() - 902) / 2 - 9)
        self.game.moveTreeScene.setColumnWidth(1, (self.width() - 902) / 2 - 9)
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
        # TODO: Add an application icon
        # self.setWindowIcon(QIcon('web.png'))
        self.setCentralWidget(splitter2)
        self.show()

    def closeEvent(self, event):
        # TODO: Implement saving before close
        # reply = QMessageBox.question(self, 'Message',
        #                              "Are you sure to quit?",
        #                              QMessageBox.Yes | QMessageBox.No,
        #                              QMessageBox.No)
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


def changedFocusSlot(old, now):
    if now is None and old is not None:
        constants.HAS_FOCUS = False
    elif old is None and now is not None:
        constants.HAS_FOCUS = True

def main():
    app = QApplication(sys.argv)
    app.focusChanged.connect(changedFocusSlot)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
