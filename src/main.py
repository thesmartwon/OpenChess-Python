from PyQt5.QtGui import QIcon, QFont, QKeySequence
from PyQt5.QtWidgets import (QMainWindow, QAction,
                             QApplication, QDesktopWidget, QStyle)
import sys
import userConfig
import constants
from widgets.centralwidget import CentralWidget


class MainWindow(QMainWindow):
    """
    Houses the menubars and CentralWidget
    """
    def __init__(self):
        super().__init__()
        self.initUI()
        self.show()

    def initUI(self):
        # Look and feel
        antiAliasedFont = QApplication.font()
        antiAliasedFont.setStyleStrategy(QFont.PreferAntialias)
        QApplication.setFont(antiAliasedFont)

        self.setWindowTitle('Open Chess')
        # TODO: Add an application icon
        # self.setWindowIcon(QIcon('web.png'))

        # Geometry
        """This will make the window the correct aspect ratio"""
        screenGeo = QDesktopWidget().availableGeometry()
        idealWidth = constants.IDEAL_RESOLUTION['width']
        idealHeight = constants.IDEAL_RESOLUTION['height']
        # TODO: maybe there is a good way to get this value?
        guessedFrame = 2
        titlebarHeight = QApplication.style().pixelMetric(
                            QStyle.PM_TitleBarHeight) + guessedFrame
        widthDisparity = screenGeo.width() - idealWidth
        heightDisparity = screenGeo.height() - idealHeight
        if widthDisparity < 0 and widthDisparity < heightDisparity:
            width = idealWidth + widthDisparity
            ratio = float(idealHeight) / idealWidth
            height = int(ratio * (idealWidth + widthDisparity))
            self.setGeometry(0, 0, width - guessedFrame * 2,
                             height - titlebarHeight)
        elif heightDisparity < 0 and heightDisparity < widthDisparity:
            ratio = float(idealWidth) / idealHeight
            width = int(ratio * (idealHeight + heightDisparity))
            height = idealHeight + heightDisparity
            self.setGeometry(0, 0, width - guessedFrame * 2,
                             height - titlebarHeight)
        else:
            self.setGeometry(0, 0, idealWidth, idealHeight)
        print("window geometry is", self.geometry())

        # Widget
        self.centralWidget = CentralWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.createActions()
        self.createMenus()

        # Center the window on the desktop
        # TODO: Add option for setting startup xy and saving layout in general
        # qr = self.frameGeometry()
        # cp = QDesktopWidget().geometry().center()
        # qr.moveCenter(cp)
        frameGeo = self.geometry()
        frameGeo.setHeight(frameGeo.height() + titlebarHeight + guessedFrame)
        frameGeo.setWidth(frameGeo.width() + guessedFrame * 2)
        self.move(QDesktopWidget().screenGeometry().center() - frameGeo.center())

    def createActions(self):
        self.newGameAction = QAction('&New Game', self)
        self.newGameAction.setShortcut(QKeySequence.New)
        self.newGameAction.setStatusTip('Start a new game')
        self.newGameAction.triggered.connect(self.centralWidget.chessGame.newGame)
        self.openGameAction = QAction('&Open a Game', self)
        self.openGameAction.setShortcut(QKeySequence.Open)
        self.openGameAction.setStatusTip('Start a new game')
        self.openGameAction.triggered.connect(self.centralWidget.chessGame.openGame)
        self.exitAction = QAction('&Quit', self)
        self.exitAction.setShortcut(QKeySequence.Quit)
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(self.close)

        keyConfig = userConfig.config['HOTKEYS']
        self.editAction = QAction('&Setup a position', self)
        self.editAction.setShortcut(keyConfig['editboard'])
        self.editAction.setStatusTip('Change the current position')
        self.editAction.triggered.connect(self.centralWidget.boardScene.editBoard)
        self.flipAction = QAction('&Flip', self)
        self.flipAction.setShortcut(keyConfig['flipboard'])
        self.flipAction.setStatusTip('Flip the current board')
        self.flipAction.triggered.connect(self.centralWidget.boardScene.flipBoard)

    def createMenus(self):
        # Menus (some dependent on widgets)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(self.newGameAction)
        fileMenu.addAction(self.openGameAction)
        fileMenu.addAction(self.exitAction)
        boardMenu = menubar.addMenu('&Board')
        boardMenu.addAction(self.flipAction)
        boardMenu.addAction(self.editAction)


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
        self.centralWidget.engineWidget.destroyEvent()
        userConfig.saveFile(constants.CONFIG_PATH)
        event.accept()


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

# TODO: when finished put main below
if __name__ == '__main__':
    main()
