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
        self.analyzeButton = QPushButton(self)
        self.analyzeButton.clicked.connect(self.toggleAnalyze)
        self.analyzeButton.setText('Anaylze')
        self.analyzeButton.setCheckable(True)

        horiLayout = QHBoxLayout()
        horiLayout.addWidget(self.scoreLabel)
        horiLayout.addWidget(self.depthLabel, 0, Qt.AlignRight)

        vertiLayout = QVBoxLayout(self)
        vertiLayout.addLayout(horiLayout)
        vertiLayout.addWidget(self.pvLabel)
        vertiLayout.addWidget(self.analyzeButton)

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
        self.engine.isready()

    def goInfinite(self, stuff):
        print('engine infinite thinking')
        self.command = self.engine.go(infinite=True, async_callback=True)

    def toggleAnalyze(self):
        if self.analyzeButton.isChecked():
            self.engine.isready(self.goInfinite)
        else:
            print('engine stop')
            self.engine.stop()

    def updateAfterMove(self, board):
        self.board = board
        self.engine.stop()
        self.command = None
        self.engine.position(board)
        if self.analyzeButton.isChecked():
            self.engine.isready(self.goInfinite)
        self.updateText()
        self.updateBoard()

    def updateBoard(self):
        if self.longestPv != self.lastLongestPv:
            boardScene = self.parent().parent().boardScene
            boardScene.updateEngineItems(self.longestPv)

    def updateText(self):
        if self.command is None:
            return
        tmpBoard = copy.deepcopy(self.board)
        moveCount = 0
        pvString = 'not thinking'
        scoreString = '0'
        depthString = '0'

        info = self.infoHandler.info
        if 1 in info['score']:
            if info['score'][1].mate is not None:
                scoreString = 'M' + str(info['score'][1].mate)
            else:
                scoreString = '{:+4.2f}'.format(info['score'][1].cp / 100.0)

                conf = userConfig.config['ENGINES']
                if (not self.board.turn and
                        conf.getboolean('showWhiteCentipawns')):
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

        self.scoreLabel.setText(scoreString)
        self.pvLabel.setText(pvString)
        self.depthLabel.setText(depthString)

    def timerEvent(self, event):
        self.updateText()
        self.updateBoard()
        self.lastLongestPv = self.longestPv

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
