from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt5.QtGui import QFontMetrics
import copy
import chess.uci
import constants
import userConfig
import platform


class EngineWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.scoreLabel = QLabel(self)
        self.pvLabel = QLabel(self)
        self.analyzeButton = QPushButton(self)
        self.analyzeButton.clicked.connect(self.toggleAnalyze)
        self.board = None
        self.command = None
        self.longestPv = None
        self.lastLongestPv = None
        self.initLayout()

        self.startTimer(250)

    def initLayout(self):
        self.pvLabel = PVLabel(self)
        self.scoreLabel = ScoreLabel(self)

        self.analyzeButton.setText('Anaylze')
        self.analyzeButton.setCheckable(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.scoreLabel, 0, Qt.AlignTop)
        layout.addWidget(self.pvLabel)
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
        pvString = 'not thinking'
        scoreString = '0'
        if self.command is not None:
            info = self.infoHandler.info
            if 1 in info['score']:
                if info['score'][1].mate is not None:
                    scoreString = 'M' + str(info['score'][1].mate)
                else:
                    scoreString = str(info['score'][1].cp)
                    if scoreString[0] != '-':
                        scoreString = '+.' + scoreString
                    else:
                        scoreString = '-.' + scoreString[1:]

            if 1 in info['pv']:
                pvString = ''
                if (self.longestPv is None or
                        info['pv'][1][0] != self.longestPv[0]):
                    self.longestPv = info['pv'][1]
                elif len(info['pv'][1]) > len(self.longestPv):
                    self.longestPv = info['pv'][1]
                for m in self.longestPv:
                    pvString += tmpBoard.san(m) + ' '
                    tmpBoard.push(m)
                    moveCount += 1
        else:
            self.longestPv = None

        self.scoreLabel.setText(scoreString)
        self.pvLabel.setText(pvString)
        if self.longestPv != self.lastLongestPv and self.longestPv is not None:
            firstMove = self.longestPv[0]
            self.parent().parent().boardScene.addArrow(firstMove)
        self.lastLongestPv = self.longestPv

    def timerEvent(self, event):
        self.updateText()

    def resizeEvent(self, event):
        self.setMaximumWidth(event.size().width())

    def destroyEvent(self):
        print('closing engine')
        self.engine.quit()


class ScoreLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        font = self.font()
        font.setPointSize(24)
        scoreMet = QFontMetrics(font)
        scoreLineHeight = scoreMet.height()
        self.setFont(font)
        self.setMinimumHeight(scoreLineHeight)


class PVLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        pvMet = QFontMetrics(self.font())
        pvLineHeight = pvMet.height()
        self.setMinimumHeight(pvLineHeight * 8)
        self.setWordWrap(True)
