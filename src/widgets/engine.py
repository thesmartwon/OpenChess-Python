from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QFontMetrics, QFont
import copy
import chess.uci
import constants
import userConfig
import platform


class EngineWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.engineLabel = QLabel(self)
        self.analyzeButton = QPushButton(self)
        self.analyzeButton.clicked.connect(self.toggleAnalyze)
        self.board = None
        self.command = None
        self.longestPv = None
        self.lastLongestPv = None
        self.initLayout()

        self.startTimer(250)

    def initLayout(self):
        self.engineLabel.setWordWrap(True)
        met = QFontMetrics(self.font())
        lineHeight = met.height()
        print('h', lineHeight)
        self.engineLabel.setMinimumHeight(lineHeight * 8)
        self.analyzeButton.setText('Anaylze')
        self.analyzeButton.setCheckable(True)
        layout = QVBoxLayout(self)
        layout.addWidget(self.engineLabel)
        layout.addWidget(self.analyzeButton, 0, Qt.AlignBottom)
        self.setLayout(layout)

    def initEngine(self, board):
        eng = userConfig.config['ENGINES']['mainEngine']
        engPath = eng + '/' +\
            userConfig.config[eng][str(platform.architecture()[0])]
        print(constants.ENGINES_PATH + '/' + engPath)
        self.engine = chess.uci.popen_engine(constants.ENGINES_PATH + '/' +
                                             engPath)
        self.infoHandler = chess.uci.InfoHandler()
        self.engine.info_handlers.append(self.infoHandler)
        self.board = board
        self.engine.position(board)
        self.engine.uci()

    def toggleAnalyze(self):
        self.engine.stop()
        if self.analyzeButton.isChecked():
            self.command = self.engine.go(infinite=True, async_callback=True)

    def updateAfterMove(self, board):
        self.board = board
        self.engine.stop()
        self.command = None
        self.engine.position(board)
        self.toggleAnalyze()
        self.updateText()

    def updateText(self):
        tmpBoard = copy.deepcopy(self.board)
        moveCount = 0
        moveString = ''
        if self.command is not None and 1 in self.infoHandler.info['pv']:
            if (self.longestPv is None or
                    self.infoHandler.info['pv'][1][0] != self.longestPv[0]):
                self.longestPv = self.infoHandler.info['pv'][1]
            elif len(self.infoHandler.info['pv'][1]) > len(self.longestPv):
                self.longestPv = self.infoHandler.info['pv'][1]
            for m in self.longestPv:
                moveString += tmpBoard.san(m) + ' '
                tmpBoard.push(m)
                moveCount += 1
        else:
            self.longestPv = None
            moveString = 'not thinking'
        self.engineLabel.setText(moveString)
        if self.longestPv != self.lastLongestPv and self.longestPv is not None:
            firstMove = self.longestPv[0]
            self.parent().parent().boardScene.addArrow(firstMove)
        self.lastLongestPv = self.longestPv

    def timerEvent(self, event):
        self.updateText()

    def destroyEvent(self):
        print('closing engine')
        self.engine.quit()

    def resizeEvent(self, event):
        self.setMaximumWidth(event.size().width())
