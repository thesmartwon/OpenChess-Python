from PyQt5.QtCore import Qt, pyqtSignal, QObject, QBasicTimer
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout,
                             QHBoxLayout)
from PyQt5.QtGui import QFontMetrics
import platform
import copy
import chess.uci
import constants
import userConfig


class EngineWidget(QWidget):
    pvChanged = pyqtSignal(list)

    def __init__(self, parent):
        super().__init__(parent)
        self.board = None
        self.command = None
        self.longestPV = []
        self.lastlongestPV = []
        self.initUI()
        self.timer = QBasicTimer()
        self.timer.start(100, self)

    def initUI(self):
        self.pvLabel = PVLabel(self)
        self.scoreLabel = ScoreLabel(self)
        self.depthLabel = DepthLabel(self)
        self.analyzeButton = AnalyzeButton(self, self.analyzeClicked)

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
        self.infoHandler = EngineInfoHandler(self)
        self.infoHandler.newInfo.connect(self.newInfoRecieved)
        self.engine.info_handlers.append(self.infoHandler)
        self.board = copy.deepcopy(board)
        self.engine.uci()
        self.engine.isready(self.stopAndSync)

    def goInfinite(self, stuff=None):
        print('engine infinite thinking')
        self.command = self.engine.go(infinite=True, async_callback=True)

    def startEngineActions(self):
        if self.analyzeButton.isChecked():
            assert self.command is None
            self.engine.isready(self.goInfinite)
        # TODO: Add timed engine

    def stopEngine(self, callback=None):
        print('engine stopping')
        self.engine.stop(callback)
        self.command = None

    def analyzeClicked(self):
        if self.analyzeButton.isChecked():
            self.readyAndGo()
        else:
            self.stopEngine(None)

    # TODO: prettier way for these callbacks?
    def positionAndGo(self, stuff=None):
        print('engine syncing position', self.board.fen())
        if self.board.fen() == chess.STARTING_FEN:
            self.engine.ucinewgame()
        self.engine.position(self.board)
        self.startEngineActions()

    def readyAndGo(self, stuff=None):
        self.engine.isready(self.positionAndGo)

    def stopAndSync(self, stuff=None):
        self.stopEngine(self.readyAndGo)

    def updateAfterMove(self, newNode):
        self.board = copy.deepcopy(newNode.board())
        move = self.board.move_stack[-1]
        if self.longestPV and self.longestPV[0] == move:
            self.longestPV = self.longestPV[1:]
        else:
            self.longestPV.clear()
        if self.analyzeButton.isChecked():
            self.stopAndSync()

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

    def createPVText(self, isStale):
        if isStale:
            pvTxt = '[Off]'
        else:
            try:
                pvTxt = self.board.variation_san(self.longestPV)
            except ValueError:
                pvTxt = 'Invalid variation_san'
        return pvTxt

    def createText(self):
        pvTxt = 'not thinking'
        scoreTxt = '0'
        depthTxt = '0'
        with self.infoHandler:
            stale = not self.analyzeButton.isChecked()
            if not stale and 1 in self.infoHandler.info['score']:
                scoreTxt = self.createScoreText(self.infoHandler.info['score'])

            if 1 in self.infoHandler.info['pv']:
                pvTxt = self.createPVText(stale)
            if not stale and 'depth' in self.infoHandler.info.keys():
                depthTxt = str(self.infoHandler.info['depth'])

        self.scoreLabel.setText(scoreTxt)
        self.pvLabel.setText(pvTxt)
        self.depthLabel.setText(depthTxt)

    def createBoardSceneGraphics(self):
        if self.longestPV != self.lastlongestPV:
            self.pvChanged.emit(self.longestPV)

    # newInfoRecieved can be called so many times in a row right after
    # an engine receives a new position that the thread locks up.
    def timerEvent(self, event):
        if self.longestPV != self.lastlongestPV:
            self.createText()
            self.createBoardSceneGraphics()
            self.lastlongestPV = copy.deepcopy(self.longestPV)

    def newInfoRecieved(self):
        with self.infoHandler:
            pvInfo = self.infoHandler.info['pv']
            if 1 in pvInfo:
                if (not self.longestPV or pvInfo[1][0] != self.longestPV[0]):
                    self.longestPV = pvInfo[1]
                elif len(pvInfo[1]) > len(self.longestPV):
                    self.longestPV = pvInfo[1]

    def reset(self, newNode, turnOffEngine=False):
        self.board = copy.deepcopy(newNode.board())
        self.longestPV = []
        self.lastlongestPV = []
        self.createText()
        if turnOffEngine:
            self.analyzeButton.setChecked(False)
        else:
            self.stopAndSync()

    def destroyEvent(self):
        print('closing engine')
        self.engine.quit()


class EngineInfoHandler(QObject, chess.uci.InfoHandler):
    newInfo = pyqtSignal()

    def __init__(self, parent):
        super(chess.uci.InfoHandler, self).__init__()
        super(QObject, self).__init__(parent)

    def post_info(self):
        super().post_info()
        self.newInfo.emit()


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
        self.setMaximumHeight(pvLineHeight * 12)
        self.setMinimumHeight(pvLineHeight * 12)
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
