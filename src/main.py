from PyQt5.QtGui import QIcon, QFont, QKeySequence
from PyQt5.QtWidgets import (QMainWindow, QAction,
                             QApplication, QDesktopWidget, QStyle)
import sys
import userConfig
import constants
import strings
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
        path = constants.RESOURCES_PATH + '/icon.png'
        self.setWindowIcon(QIcon(path))

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
        self.newGameAction = QAction(strings.MENU_NEW, self)
        self.newGameAction.setShortcut(QKeySequence.New)
        self.newGameAction.setToolTip(strings.MENU_NEW_TIP)
        self.newGameAction.triggered.connect(self.centralWidget.chessGame.newGame)
        self.openGameAction = QAction(strings.MENU_OPEN, self)
        self.openGameAction.setShortcut(QKeySequence.Open)
        self.openGameAction.setToolTip(strings.MENU_OPEN_TIP)
        self.openGameAction.triggered.connect(self.centralWidget.chessGame.openGame)
        self.saveGameAction = QAction(strings.MENU_SAVE, self)
        self.saveGameAction.setShortcut(QKeySequence.Save)
        self.saveGameAction.setToolTip(strings.MENU_SAVE_TIP)
        self.saveGameAction.triggered.connect(self.centralWidget.chessGame.saveGame)
        self.saveGameAsAction = QAction(strings.MENU_SAVEAS, self)
        self.saveGameAsAction.setShortcut(QKeySequence.SaveAs)
        self.saveGameAsAction.setToolTip(strings.MENU_SAVEAS_TIP)
        self.saveGameAsAction.triggered.connect(self.centralWidget.chessGame.saveGameAs)
        self.exitAction = QAction(strings.MENU_QUIT, self)
        self.exitAction.setShortcut(QKeySequence.Quit)
        self.exitAction.setToolTip(strings.MENU_QUIT_TIP)
        self.exitAction.triggered.connect(self.close)

        keyConfig = userConfig.config['HOTKEYS']
        self.editAction = QAction(strings.MENU_EDITBOARD, self)
        self.editAction.setShortcut(keyConfig['editboard'])
        self.editAction.setToolTip(strings.MENU_EDITBOARD_TIP)
        self.editAction.triggered.connect(self.centralWidget.chessGame.editBoard)
        self.flipAction = QAction(strings.MENU_FLIP, self)
        self.flipAction.setShortcut(keyConfig['flipboard'])
        self.flipAction.setToolTip(strings.MENU_FLIP_TIP)
        self.flipAction.triggered.connect(self.centralWidget.boardScene.flipBoard)

    def createMenus(self):
        # Menus (some dependent on widgets)
        menubar = self.menuBar()
        fileMenu = menubar.addMenu(strings.MENU_FILE)
        fileMenu.addAction(self.newGameAction)
        fileMenu.addAction(self.openGameAction)
        fileMenu.addAction(self.saveGameAction)
        fileMenu.addAction(self.saveGameAsAction)
        fileMenu.addAction(self.exitAction)
        boardMenu = menubar.addMenu(strings.MENU_BOARD)
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
