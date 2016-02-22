import sys
from PyQt5.QtWidgets import (QMainWindow, QAction,
                             QApplication, QMessageBox,
                             QDesktopWidget, QFrame,
                             QGraphicsView, QSplitter)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QTransform
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
        self.vertSplitter = QSplitter(Qt.Vertical)
        self.horiSplitter = QSplitter()
        self.initialSceneWidth = 0
        self.initStaticUI()
        self.initDynamicUI()

    def initGeometry(self, maxWidth, maxHeight):
        idealWidth = constants.IDEAL_RESOLUTION['width']
        idealHeight = constants.IDEAL_RESOLUTION['height']
        widthDisparity = maxWidth - idealWidth
        heightDisparity = maxHeight - idealHeight
        if widthDisparity < 0 and widthDisparity < heightDisparity:
            width = idealWidth + widthDisparity
            ratio = float(idealHeight) / idealWidth
            height = int(ratio * (idealWidth + widthDisparity))
            self.setGeometry(0, 0, width, height)
        elif heightDisparity < 0 and heightDisparity < widthDisparity:
            ratio = float(idealWidth) / idealHeight
            width = int(ratio * (idealHeight + heightDisparity))
            height = idealHeight + heightDisparity
            self.setGeometry(0, 0, width, height)
        else:
            self.setGeometry(0, 0, idealWidth, idealHeight)
        print("geometry is", self.geometry())
        print("bars are", self.statusBar().height(), self.menuBar().height())

    def initDynamicUI(self):
        screenGeo = QApplication.desktop().screenGeometry()
        self.initGeometry(screenGeo.width(), screenGeo.height())
        print("best width", self.width(), "best height", self.height() -
              self.statusBar().height() - self.menuBar().height())
        limitDimension = min(self.width(), self.height() - self.statusBar().
                             height() - self.menuBar().height())
        sceneWidth = int(limitDimension / 8) * 8
        print("sceneWidth is", sceneWidth, "squares", sceneWidth / 8)
        self.initialSceneWidth = sceneWidth
        self.game.boardScene.initSquares(sceneWidth / 8)
        self.game.boardScene.setSceneRect(0, 0, sceneWidth, sceneWidth)
        self.view.setGeometry(0, 0, sceneWidth, sceneWidth)
        userConfig.config['BOARD']['squareWidth'] = str(int(sceneWidth / 8))
        split = [sceneWidth + self.horiSplitter.handleWidth(),
                 self.width() - sceneWidth - self.horiSplitter.handleWidth()]
        print("split is", split)
        self.horiSplitter.setSizes(split)
        self.setCentralWidget(self.horiSplitter)
        self.center()
        self.show()

    def initStaticUI(self):
        rightTopWidget = self.game.moveTreeScene
        rightBotWidget = QFrame(self)
        self.vertSplitter.addWidget(rightTopWidget)
        self.vertSplitter.addWidget(rightBotWidget)
        self.horiSplitter.addWidget(self.view)
        self.horiSplitter.addWidget(self.vertSplitter)
        # self.horiSplitter.setHandleWidth(0)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut(userConfig.config['HOTKEYS']['exit'])
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)
        menubar = self.menuBar()
        menubar.setMaximumHeight(20)
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        self.statusBar().showMessage('Ready')
        self.statusBar().setMaximumHeight(20)

        self.setFocusPolicy(Qt.StrongFocus)
        self.center()
        self.setWindowTitle('Open Chess')
        # TODO: Add an application icon
        # self.setWindowIcon(QIcon('web.png'))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        limitDimension = min(self.width() - self.horiSplitter.sizes()[1] - 2,
                             self.height() - self.statusBar().height() -
                             self.menuBar().height())
        sceneWidth = int(limitDimension / 8) * 8
        trans = QTransform()
        trans.scale(sceneWidth / self.initialSceneWidth,
                    sceneWidth / self.initialSceneWidth)
        self.view.setTransform(trans)

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
