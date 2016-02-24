import sys
from PyQt5.QtCore import Qt, QEvent, QSize, QRect
from PyQt5.QtGui import QIcon, QResizeEvent
from PyQt5.QtWidgets import (QMainWindow, QAction,
                             QApplication, QMessageBox,
                             QDesktopWidget, QFrame,
                             QSplitter)
from widgets.mainframe import MainFrame
import userConfig
import constants


class MainWindow(QMainWindow):
    """
    Houses the menubars and game, which is just
    a QFrame with many widgets.
    """
    def __init__(self):
        super().__init__()
        self.initMenus()
        self.initGeometry()
        width = self.geometry().width()
        height = self.geometry().height() - self.menuBar().height() - \
            self.statusBar().height()
        self.mainFrame = MainFrame(self, QRect(0, 0, width, height))
        self.setCentralWidget(self.mainFrame)
        self.center()
        self.show()

    # Initializes the menus.
    def initMenus(self):
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut(userConfig.config['HOTKEYS']['exit'])
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)
        menubar = self.menuBar()
        menubar.setMaximumHeight(20)
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        self.statusBar().setMaximumHeight(20)
        self.statusBar().showMessage('Ready')

        self.setFocusPolicy(Qt.StrongFocus)
        self.setWindowTitle('Open Chess')
        # TODO: Add an application icon
        # self.setWindowIcon(QIcon('web.png'))

    # Resizes the window to the correct aspect ratio.
    def initGeometry(self):
        screenGeo = QApplication.desktop().screenGeometry()
        idealWidth = constants.IDEAL_RESOLUTION['width']
        idealHeight = constants.IDEAL_RESOLUTION['height']
        widthDisparity = screenGeo.width() - idealWidth
        heightDisparity = screenGeo.height() - idealHeight
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
        print("window geometry is", self.geometry())

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            size = QSize(self.geometry().width(), self.geometry().height())
            newEvent = QResizeEvent(size, size)
            self.resizeEvent(newEvent)

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
