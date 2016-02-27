import sys
from PyQt5.QtCore import Qt, QEvent, QSize, QMargins
from PyQt5.QtGui import QIcon, QResizeEvent
from PyQt5.QtWidgets import (QFrame, QAction,
                             QApplication, QMessageBox,
                             QDesktopWidget, QFrame,
                             QSplitter, QPushButton,
                             QWidget, QStyle, QHBoxLayout,
                             QSizeGrip, QVBoxLayout,
                             QSpacerItem, QSizePolicy)
from widgets.centralframe import CentralFrame
import userConfig
import constants


class MainWindow(QFrame):
    """
    Houses the menubars and game, which is just
    a QFrame with many widgets.
    """
    def __init__(self):
        super().__init__()
        self.initMenus()
        self.initGeometry()
        self.initLayout()

        self.center()
        self.show()

    def initMenus(self):
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut(userConfig.config['HOTKEYS']['exit'])
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)
        self.titleBar = TitleBar(self)
        self.titleBar.maxButton.clicked.connect(self.showMaximized)
        self.titleBar.minButton.clicked.connect(self.showMinimized)
        self.titleBar.normalButton.clicked.connect(self.showNormal)
        self.titleBar.closeButton.clicked.connect(self.close)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle('Open Chess')
        # TODO: Add an application icon
        # self.setWindowIcon(QIcon('web.png'))

    def initGeometry(self):
        """This will make the window the correct aspect ratio"""
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

    def initLayout(self):
        self.mainFrame = CentralFrame(self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        sizeGrip = QSizeGrip(self)
        layout.addWidget(self.titleBar, 0)
        layout.addWidget(self.mainFrame, 9)
        layout.addWidget(sizeGrip, 0, Qt.AlignBottom | Qt.AlignRight)
        self.setLayout(layout)
        # self.setCentralWidget(layoutWidget)

    def toggleMaximizeMinimize(self):
        if self.windowState() & Qt.WindowNoState:
            self.showMaximized()
        elif self.windowState() & Qt.WindowMaximized:
            self.showMinimized()

    def showMaximized(self):
        self.lastGeo = self.geometry()
        super().showMaximized()
        self.titleBar.toggleMaxNormalButton()

    def showNormal(self):
        super().showNormal()
        self.titleBar.toggleMaxNormalButton()

    # Resizes after maxamize/minimize
    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            size = QSize(self.geometry().width(), self.geometry().height())
            newEvent = QResizeEvent(size, size)
            self.resizeEvent(newEvent)

    def mousePressEvent(self, event):
        self.oldMousePos = event.globalPos()
        self.oldMouseLocalPos = event.pos()

    def mouseMoveEvent(self, event):
        if self.windowState() & Qt.WindowMaximized:
            self.showNormal()
            self.move(event.globalPos().x(), event.globalPos().y())
            return
        delta = event.globalPos() - self.oldMousePos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldMousePos = event.globalPos()

    def closeEvent(self, event):
        print('closing')
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
        event.accept()

    def center(self):
        # TODO: Add option for setting startup xy and saving layout in general
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        style = QApplication.style()
        self.closeIcon = style.standardIcon(QStyle.SP_TitleBarCloseButton)
        self.minIcon = style.standardIcon(QStyle.SP_TitleBarMinButton)
        self.maxIcon = style.standardIcon(QStyle.SP_TitleBarMaxButton)
        self.normalIcon = style.standardIcon(QStyle.SP_TitleBarNormalButton)

        topRightButtonWidth = 42
        self.minButton = QPushButton(self)
        self.minButton.setIcon(self.minIcon)
        self.minButton.setMinimumWidth(topRightButtonWidth)
        self.maxButton = QPushButton(self)
        self.maxButton.setIcon(self.maxIcon)
        self.maxButton.setMinimumWidth(topRightButtonWidth)
        self.normalButton = QPushButton(self)
        self.normalButton.setIcon(self.normalIcon)
        self.normalButton.setMinimumWidth(topRightButtonWidth)
        self.closeButton = QPushButton(self)
        self.closeButton.setIcon(self.closeIcon)
        self.closeButton.setMinimumWidth(topRightButtonWidth)
        layout = QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Expanding,
                                         QSizePolicy.Minimum))
        layout.addWidget(self.minButton)
        layout.addWidget(self.maxButton)
        layout.addWidget(self.normalButton)
        layout.addWidget(self.closeButton)
        if self.isMaximized():
            self.maxButton.hide()
        else:
            self.normalButton.hide()
        self.setLayout(layout)

    def toggleMaxNormalButton(self):
        if self.maxButton.isVisible():
            self.maxButton.hide()
            self.normalButton.show()
        else:
            self.maxButton.show()
            self.normalButton.hide()


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
