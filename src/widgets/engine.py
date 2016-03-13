from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout)
from PyQt5.QtGui import QFontMetrics
import chess.uci
import constants
import userConfig
import platform


class EngineWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.board = None
        self.command = None
        self.longestPV = []
        self.lastlongestPV = []
        self.initUI()

        self.startTimer(250)

    def initUI(self):
        self.pvLabel = PVLabel(self)
        self.scoreLabel = ScoreLabel(self)
        self.depthLabel = DepthLabel(self)
        self.analyzeButton = AnalyzeButton(self, self.updateAnalyze)

        horiLayout = QHBoxLayout()
        horiLayout.setSpacing(0)
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

    def syncEngine(self):
        self.engine.stop()
        print('engine stop')
        self.engine.position(self.board)
        self.command = None

    def updateAnalyze(self):
        if self.analyzeButton.isChecked():
            self.engine.isready(self.goInfinite)
        else:
            print('engine stop')
            self.engine.stop()

    def updateAfterMove(self, move):
        if self.longestPV and move == self.longestPV[0]:
            self.longestPV = self.longestPV[1:]
        else:
            self.longestPV = []
        self.syncEngine()
        self.updateAnalyze()
        self.updateText()
        self.updateBoard()

    def updateBoard(self):
        if self.longestPV != self.lastlongestPV:
            boardScene = self.parent().parent().boardScene
            boardScene.updateEngineItems(self.longestPV)

    def createScoreText(self, scoreInfo):
        if scoreInfo[1].mate is not None:
            scoreTxt = 'M' + str(scoreInfo[1].mate)
        else:
            scoreTxt = '{:+4.2f}'.format(scoreInfo[1].cp / 100.0)

            conf = userConfig.config['ENGINES']
            if (not self.board.turn and
                    conf.getboolean('showWhiteCentipawns')):
                if scoreTxt[0] == '-':
                    scoreTxt = '+' + scoreTxt[1:]
                else:
                    scoreTxt = '-' + scoreTxt[1:]
        return scoreTxt

    def createPVText(self, pvInfo, isStale):
        pvTxt = ''
        if isStale:
            pvTxt += '[Stale]'
        try:
            pvTxt += self.board.variation_san(self.longestPV)
        except ValueError:
            pvTxt = 'Invalid variation_san'
        return pvTxt

    def updateText(self):
        pvTxt = 'not thinking'
        scoreTxt = '0'
        depthTxt = '0'
        with self.infoHandler:
            stale = not self.analyzeButton.isChecked()
            if not stale and 1 in self.infoHandler.info['score']:
                scoreTxt = self.createScoreText(self.infoHandler.info['score'])

            if 1 in self.infoHandler.info['pv']:
                pvTxt = self.createPVText(self.infoHandler.info['pv'], stale)

            if not stale and 'depth' in self.infoHandler.info.keys():
                depthTxt = str(self.infoHandler.info['depth'])

        self.scoreLabel.setText(scoreTxt)
        self.pvLabel.setText(pvTxt)
        self.depthLabel.setText(depthTxt)

    def timerEvent(self, event):
        if self.analyzeButton.isChecked():
            with self.infoHandler:
                pvInfo = self.infoHandler.info['pv']
                if 1 in pvInfo:
                    if (not self.longestPV or pvInfo[1][0] != self.longestPV[0]):
                        self.longestPV = self.infoHandler.info['pv'][1]
                    elif len(pvInfo[1]) > len(self.longestPV):
                        self.longestPV = self.infoHandler.info['pv'][1]
        self.updateText()
        self.updateBoard()
        self.lastlongestPV = self.longestPV

    def destroyEvent(self):
        print('closing engine')
        self.engine.quit()

    def reset(self):
        self.analyzeButton.setChecked(False)
        self.syncEngine()
        self.longestPV = []
        self.lastlongestPV = []
        self.updateText()


class ScoreLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        font = self.font()
        font.setPointSize(24)
        met = QFontMetrics(font)
        scoreLineHeight = met.height()
        self.setFont(font)
        self.setMinimumHeight(scoreLineHeight)
        self.setMinimumWidth(met.width('+100.00'))


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
        met = QFontMetrics(font)
        scoreLineHeight = met.height()
        self.setFont(font)
        self.setMinimumHeight(scoreLineHeight)
        self.setMinimumWidth(met.width('30'))


class AnalyzeButton(QPushButton):
    def __init__(self, parent, pushMethod):
        super().__init__(parent)
        self.clicked.connect(pushMethod)
        self.setText('Anaylze')
        self.setCheckable(True)
