from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (QMainWindow, QAction,
                             QApplication, QDesktopWidget)
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

        self.center()
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

        # Widget
        self.centralWidget = CentralWidget()
        self.setCentralWidget(self.centralWidget)

        # Menus (some dependent on widget)
        menubar = self.menuBar()

        fileMenu = menubar.addMenu('&File')
        newGameAction = QAction(QIcon('new.png'), '&New Game', self)
        newGameAction.setShortcut(userConfig.config['HOTKEYS']['newGame'])
        newGameAction.setStatusTip('Start a new game')
        newGameAction.triggered.connect(self.centralWidget.openGame.newGame)
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut(userConfig.config['HOTKEYS']['exit'])
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)

        fileMenu.addAction(newGameAction)
        fileMenu.addAction(exitAction)

        boardMenu = menubar.addMenu('&Board')
        editAction = QAction(QIcon('edit.png'), '&Setup a position', self)
        editAction.setStatusTip('Change the current position')
        editAction.triggered.connect(self.centralWidget.boardScene.editBoard)
        flipAction = QAction(QIcon('flip.png'), '&Flip', self)
        flipAction.setStatusTip('Flip the current board')
        flipAction.triggered.connect(self.centralWidget.boardScene.flipBoard)

        boardMenu.addAction(flipAction)
        boardMenu.addAction(editAction)

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

    def center(self):
        # TODO: Add option for setting startup xy and saving layout in general
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

# TODO: when finished put main below
if __name__ == '__main__':
    main()
