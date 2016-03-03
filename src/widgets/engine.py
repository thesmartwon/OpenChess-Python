from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout)
from PyQt5.QtGui import QFontMetrics
import copy
import chess.uci
import constants
import userConfig
import platform


class EngineWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
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
        self.depthLabel = DepthLabel(self)

        self.analyzeButton.setText('Anaylze')
        self.analyzeButton.setCheckable(True)
        # verticalLayoutWidget = QWidget(self)
        # verticalLayoutWidget.setGeometry()

        horiLayout = QHBoxLayout()
        horiLayout.addWidget(self.scoreLabel)
        horiLayout.addWidget(self.depthLabel)

        vertiLayout = QVBoxLayout(self)
        vertiLayout.addLayout(horiLayout)
        vertiLayout.addWidget(self.pvLabel)
        vertiLayout.addWidget(self.analyzeButton)
        # self.setLayout(vertiLayout)

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
        depthString = '0'
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
                    if not self.board.turn:
                        if scoreString[0] == '-':
                            scoreString = '+' + scoreString[1:]
                        else:
                            scoreString = '-' + scoreString[1:]

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
                depthString = str(info['depth'])
        else:
            self.longestPv = None

        self.scoreLabel.setText(scoreString)
        self.pvLabel.setText(pvString)
        self.depthLabel.setText(depthString)
        if self.longestPv != self.lastLongestPv and self.longestPv is not None:
            boardScene = self.parent().parent().boardScene
            boardScene.updateEngineItems(self.longestPv)
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


class DepthLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        font = self.font()
        font.setPointSize(16)
        scoreMet = QFontMetrics(font)
        scoreLineHeight = scoreMet.height()
        self.setFont(font)
        self.setMinimumHeight(scoreLineHeight)
